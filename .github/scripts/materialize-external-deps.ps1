param(
  [string]$RepoRoot = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

$pinnedRefs = @{
  "references/AvaloniaGif" = @{
    Type = "commit"
    Ref = "e3d8985151d2cea5fc8de4ca5d459759a44bb0b7"
    RequiredPath = "AvaloniaGif/AvaloniaGif.csproj"
  }
  "references/ArchiSteamFarm" = @{
    Type = "branch"
    Ref = "v5.2.7.7-library"
    RequiredPath = "ArchiSteamFarm.Library/ArchiSteamFarm.Library.csproj"
  }
  "references/Gameloop.Vdf" = @{
    Type = "commit"
    Ref = "6bf1500c95472e15ab0637f34a2bba65556d529a"
    RequiredPath = "Gameloop.Vdf/Gameloop.Vdf.csproj"
  }
  "references/SteamAchievementManager" = @{
    Type = "commit"
    Ref = "99ce54cac5cf5dc650bbca794dd1650df445d8bf"
    RequiredPath = "SAM.API/SAM.API.csproj"
  }
}

${fullHistoryPaths} = @(
  "references/reactive"
)

function Invoke-Git {
  param(
    [Parameter(Mandatory = $true)]
    [string[]]$Arguments
  )

  $psi = [System.Diagnostics.ProcessStartInfo]::new()
  $psi.FileName = "git"
  foreach ($argument in $Arguments) {
    [void]$psi.ArgumentList.Add($argument)
  }
  $psi.UseShellExecute = $false
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.CreateNoWindow = $true

  $process = [System.Diagnostics.Process]::new()
  $process.StartInfo = $psi

  [void]$process.Start()
  $stdout = $process.StandardOutput.ReadToEnd()
  $stderr = $process.StandardError.ReadToEnd()
  $process.WaitForExit()

  if ($stdout) {
    Write-Host $stdout.TrimEnd()
  }

  if ($stderr) {
    Write-Host $stderr.TrimEnd()
  }

  if ($process.ExitCode -ne 0) {
    throw "git $($Arguments -join ' ') failed with exit code $($process.ExitCode)"
  }
}

function Clone-PinnedRepo {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Url,
    [Parameter(Mandatory = $true)]
    [string]$Path,
    [Parameter(Mandatory = $true)]
    [hashtable]$Pin
  )

  switch ($Pin.Type) {
    "branch" {
      $arguments = @("-c", "core.longpaths=true", "clone")
      $useFullHistory = $Pin.ContainsKey("FullHistory") -and $Pin.FullHistory
      if (-not $useFullHistory) {
        $arguments += @("--depth", "1")
      }
      $arguments += @("--branch", $Pin.Ref, $Url, $Path)
      Invoke-Git -Arguments $arguments
    }
    "tag" {
      $arguments = @("-c", "core.longpaths=true", "clone")
      $useFullHistory = $Pin.ContainsKey("FullHistory") -and $Pin.FullHistory
      if (-not $useFullHistory) {
        $arguments += @("--depth", "1")
      }
      $arguments += @("--branch", $Pin.Ref, $Url, $Path)
      Invoke-Git -Arguments $arguments
    }
    "commit" {
      New-Item -ItemType Directory -Force -Path $Path | Out-Null
      Invoke-Git -Arguments @("-C", $Path, "init")
      Invoke-Git -Arguments @("-C", $Path, "config", "core.longpaths", "true")
      Invoke-Git -Arguments @("-C", $Path, "remote", "add", "origin", $Url)
      $fetchArguments = @("-C", $Path, "fetch")
      $useFullHistory = $Pin.ContainsKey("FullHistory") -and $Pin.FullHistory
      if (-not $useFullHistory) {
        $fetchArguments += @("--depth", "1")
      }
      $fetchArguments += @("origin", $Pin.Ref)
      Invoke-Git -Arguments $fetchArguments
      Invoke-Git -Arguments @("-C", $Path, "checkout", "--detach", "FETCH_HEAD")
    }
    default {
      throw "Unsupported pin type '$($Pin.Type)' for '$Path'"
    }
  }
}

function Get-GitHeadRevision {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path
  )

  if (-not (Test-Path (Join-Path $Path ".git"))) {
    return $null
  }

  try {
    $revision = & git -C $Path rev-parse HEAD 2>$null
    if ($LASTEXITCODE -ne 0) {
      return $null
    }

    return $revision.Trim()
  }
  catch {
    return $null
  }
}

function Sync-PinnedRepo {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Url,
    [Parameter(Mandatory = $true)]
    [string]$Path,
    [Parameter(Mandatory = $true)]
    [hashtable]$Pin
  )

  if (-not (Test-Path $Path)) {
    Clone-PinnedRepo -Url $Url -Path $Path -Pin $Pin
    return
  }

  switch ($Pin.Type) {
    "commit" {
      $headRevision = Get-GitHeadRevision -Path $Path
      if ($headRevision -eq $Pin.Ref) {
        return
      }

      if (-not (Test-Path (Join-Path $Path ".git"))) {
        throw "Pinned repository '$Path' exists but is not a git checkout."
      }

      Write-Host "Updating $Path to commit $($Pin.Ref)"
      Invoke-Git -Arguments @("-C", $Path, "fetch", "--depth", "1", "origin", $Pin.Ref)
      Invoke-Git -Arguments @("-C", $Path, "checkout", "--detach", "FETCH_HEAD")
    }
    default {
      return
    }
  }
}

Push-Location $RepoRoot

try {
  if (-not (Test-Path ".gitmodules")) {
    throw "Missing .gitmodules in '$RepoRoot'"
  }

  $content = Get-Content ".gitmodules"
  $repos = @()
  $current = $null

  foreach ($line in $content) {
    if ($line -match '^\[submodule "(.*)"\]$') {
      if ($null -ne $current -and $current.path -and $current.url) {
        $repos += [PSCustomObject]$current
      }

      $current = @{
        name = $Matches[1]
        path = $null
        url = $null
      }
      continue
    }

    if ($null -eq $current) {
      continue
    }

    if ($line -match '^\s*path = (.+)$') {
      $current.path = $Matches[1]
      continue
    }

    if ($line -match '^\s*url = (.+)$') {
      $current.url = $Matches[1]
    }
  }

  if ($null -ne $current -and $current.path -and $current.url) {
    $repos += [PSCustomObject]$current
  }

  foreach ($repo in $repos) {
    $pin = $pinnedRefs[$repo.path]

    if ($pin) {
      $requiredPath = Join-Path $repo.path $pin.RequiredPath
      if ((Test-Path $repo.path) -and -not (Test-Path $requiredPath)) {
        Write-Host "Resetting $($repo.path) because '$requiredPath' is missing"
        Remove-Item -Recurse -Force $repo.path
      }
    }

    if ($pin) {
      if (Test-Path $repo.path) {
        Write-Host "Validating pinned dependency $($repo.path)"
      }
      else {
        Write-Host "Cloning $($repo.url) -> $($repo.path) at $($pin.Type) $($pin.Ref)"
      }

      Sync-PinnedRepo -Url $repo.url -Path $repo.path -Pin $pin

      $requiredPath = Join-Path $repo.path $pin.RequiredPath
      if (-not (Test-Path $requiredPath)) {
        throw "Pinned checkout for '$($repo.path)' is missing '$requiredPath'"
      }
      continue
    }

    if (Test-Path $repo.path) {
      Write-Host "Using existing $($repo.path)"
      continue
    }

    Write-Host "Cloning $($repo.url) -> $($repo.path)"
    $arguments = @("-c", "core.longpaths=true", "clone")
    if ($repo.path -notin $fullHistoryPaths) {
      $arguments += @("--depth", "1")
    }
    $arguments += @($repo.url, $repo.path)
    Invoke-Git -Arguments $arguments
  }
}
finally {
  Pop-Location
}
