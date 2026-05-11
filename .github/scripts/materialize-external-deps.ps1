param(
  [string]$RepoRoot = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

$pinnedRefs = @{
  "references/AvaloniaGif" = @{
    Type = "commit"
    Ref = "5f5459e46fe3e2e427e313d40ee4943893759cfd"
    RequiredPath = "AvaloniaGif/AvaloniaGif.csproj"
  }
  "references/ArchiSteamFarm" = @{
    Type = "commit"
    Ref = "a427f628e1b1d8b5ecfd66a16fd8ae3518934b53"
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
  "references/Depressurizer" = @{
    Type = "commit"
    Ref = "7267ff264a14f6c9e8399365a9844e01887c4409"
  }
  "references/FluentAvalonia" = @{
    Type = "commit"
    Ref = "50c719a4b9620b400d0686693f3da69022043977"
    RequiredPath = "FluentAvalonia/FluentAvalonia.csproj"
  }
  "references/MetroRadiance" = @{
    Type = "commit"
    Ref = "f6cbd3d421f298a06f866a21a18ed801eeae1056"
  }
  "references/Steam4NET" = @{
    Type = "commit"
    Ref = "8dcff45ab4eb569173c48313ca241799a3b3aed5"
    RequiredPath = "Steam4NET/Steam4NET.csproj"
  }
  "references/Titanium-Web-Proxy" = @{
    Type = "commit"
    Ref = "42a23d61a23c6a94da4df00aeef8b902b59a2201"
    RequiredPath = "src/Titanium.Web.Proxy/Titanium.Web.Proxy.csproj"
  }
  "references/WinAuth" = @{
    Type = "commit"
    Ref = "3942d43ce8df3046ed37156567ff8325c517110b"
    RequiredPath = "Authenticator/Authenticator.csproj"
  }
  "references/dotnet-packaging" = @{
    Type = "commit"
    Ref = "3f7bd3c61a00ce2c51f4f53f34d149b0ce5f8fdd"
  }
  "references/reactive" = @{
    Type = "commit"
    Ref = "d53a04fa440bac462affa00fb28cbd93af55fde4"
    FullHistory = $true
    RequiredPath = "Rx.NET/Source/src/System.Reactive/System.Reactive.csproj"
  }
  "references/sqlite-net" = @{
    Type = "commit"
    Ref = "b923e8ec43069974871f90dfc88711f188c96e79"
  }
}

${fullHistoryPaths} = @(
  "references/reactive"
)

$requiredRepoPaths = @{
  "references/FluentAvalonia" = "FluentAvalonia/FluentAvalonia.csproj"
  "references/reactive" = "Rx.NET/Source/src/System.Reactive/System.Reactive.csproj"
}

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
      # For pinned commits, use a normal clone then checkout to avoid
      # "unadvertised object" fetch failures on hosted providers.
      Invoke-Git -Arguments @("-c", "core.longpaths=true", "clone", $Url, $Path)
      Invoke-Git -Arguments @("-C", $Path, "checkout", "--detach", $Pin.Ref)
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
    $requiredRepoPath = $requiredRepoPaths[$repo.path]

    if ($pin) {
      if ($pin.ContainsKey("RequiredPath")) {
        $requiredPath = Join-Path $repo.path $pin.RequiredPath
        if ((Test-Path $repo.path) -and -not (Test-Path $requiredPath)) {
          Write-Host "Resetting $($repo.path) because '$requiredPath' is missing"
          Remove-Item -Recurse -Force $repo.path
        }
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

      if ($pin.ContainsKey("RequiredPath")) {
        $requiredPath = Join-Path $repo.path $pin.RequiredPath
        if (-not (Test-Path $requiredPath)) {
          throw "Pinned checkout for '$($repo.path)' is missing '$requiredPath'"
        }
      }
      continue
    }

    if (Test-Path $repo.path) {
      if ($requiredRepoPath) {
        $requiredPath = Join-Path $repo.path $requiredRepoPath
        if (-not (Test-Path $requiredPath)) {
          Write-Host "Resetting $($repo.path) because '$requiredPath' is missing"
          Remove-Item -Recurse -Force $repo.path
        }
      }
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

    if ($requiredRepoPath) {
      $requiredPath = Join-Path $repo.path $requiredRepoPath
      if (-not (Test-Path $requiredPath)) {
        throw "Checkout for '$($repo.path)' is missing '$requiredPath'"
      }
    }
  }
}
finally {
  Pop-Location
}
