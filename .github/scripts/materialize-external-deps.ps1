param(
  [string]$RepoRoot = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$pinnedRefs = @{
  "references/AvaloniaGif" = @{
    Type = "branch"
    Ref = "Avalonia-11.0"
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

  & git @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
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

    if (Test-Path $repo.path) {
      Write-Host "Using existing $($repo.path)"
      continue
    }

    if ($pin) {
      Write-Host "Cloning $($repo.url) -> $($repo.path) at $($pin.Type) $($pin.Ref)"
      Clone-PinnedRepo -Url $repo.url -Path $repo.path -Pin $pin

      $requiredPath = Join-Path $repo.path $pin.RequiredPath
      if (-not (Test-Path $requiredPath)) {
        throw "Pinned checkout for '$($repo.path)' is missing '$requiredPath'"
      }
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
