param(
  [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path $PSScriptRoot -Parent
$mainProject = Join-Path $repoRoot "src\ST.Client.Desktop.Avalonia.App\ST.Client.Avalonia.App.csproj"
$publishDir = Join-Path $repoRoot "src\ST.Client.Desktop.Avalonia.App\bin\$Configuration\Publish\win-x64"
$artifactsRoot = Join-Path $repoRoot "artifacts\green-zip"
$stagingRoot = Join-Path $artifactsRoot "staging"
$packageRootName = "WattToolkit-win-x64-green"
$stagingDir = Join-Path $stagingRoot $packageRootName
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$gitSha = ""
$allowedSatelliteLanguages = @("en", "zh-CN", "zh-Hans")
$excludedTopLevelDirectories = @("AppData", "Cache")
$allowedTopLevelDirectories = @("Assets") + $allowedSatelliteLanguages

try {
  $gitSha = (& git -C $repoRoot rev-parse --short HEAD 2>$null).Trim()
} catch {
  $gitSha = ""
}

if ([string]::IsNullOrWhiteSpace($gitSha)) {
  $zipName = "$packageRootName-$timestamp.zip"
} else {
  $zipName = "$packageRootName-$timestamp-$gitSha.zip"
}

$zipPath = Join-Path $artifactsRoot $zipName
$entryExe = Join-Path $publishDir "Steam++.exe"
$assetsDir = Join-Path $publishDir "Assets"

Add-Type -AssemblyName System.IO.Compression.FileSystem

function New-ZipFromDirectory {
  param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDirectory,
    [Parameter(Mandatory = $true)]
    [string]$DestinationPath,
    [bool]$IncludeBaseDirectory = $false
  )

  for ($attempt = 1; $attempt -le 3; $attempt++) {
    try {
      if (Test-Path $DestinationPath) {
        Remove-Item $DestinationPath -Force
      }

      [System.IO.Compression.ZipFile]::CreateFromDirectory(
        $SourceDirectory,
        $DestinationPath,
        [System.IO.Compression.CompressionLevel]::Optimal,
        $IncludeBaseDirectory)

      return
    }
    catch {
      if ($attempt -eq 3) {
        throw
      }

      Start-Sleep -Seconds 2
    }
  }
}

function Assert-AllowedSatelliteResources {
  param(
    [Parameter(Mandatory = $true)]
    [string]$PublishDirectory,
    [string[]]$AllowedLanguages = @()
  )

  $satelliteDirs = Get-ChildItem -Path $PublishDirectory -Directory | Where-Object {
    Get-ChildItem -Path $_.FullName -Filter *.resources.dll -File -ErrorAction SilentlyContinue | Select-Object -First 1
  }

  $invalidDirs = $satelliteDirs | Where-Object { $_.Name -notin $AllowedLanguages }
  if ($invalidDirs) {
    $invalidNames = ($invalidDirs | Select-Object -ExpandProperty Name) -join ", "
    throw "Publish output contains unsupported satellite resource directories: $invalidNames"
  }
}

Write-Host "Materializing pinned external dependencies..."
& (Join-Path $repoRoot ".github\scripts\materialize-external-deps.ps1")
if ($LASTEXITCODE) { exit $LASTEXITCODE }

Write-Host "Restoring main app..."
& dotnet restore $mainProject -p:Configuration=$Configuration
if ($LASTEXITCODE) { exit $LASTEXITCODE }

if (Test-Path $publishDir) {
  Remove-Item $publishDir -Recurse -Force
}

Write-Host "Publishing main app..."
& dotnet publish $mainProject -c $Configuration -p:PublishProfile=win-x64 -p:ExtraDefineConstants=win-x64 --no-restore --nologo
if ($LASTEXITCODE) { exit $LASTEXITCODE }

if (-not (Test-Path $publishDir)) {
  throw "Main publish output directory was not found: $publishDir"
}

if (-not (Test-Path $entryExe)) {
  throw "Main executable was not found: $entryExe"
}

if (-not (Test-Path $assetsDir)) {
  throw "Assets directory was not found: $assetsDir"
}

Assert-AllowedSatelliteResources -PublishDirectory $publishDir -AllowedLanguages $allowedSatelliteLanguages

New-Item -ItemType Directory -Force -Path $artifactsRoot | Out-Null

if (Test-Path $stagingDir) {
  Remove-Item $stagingDir -Recurse -Force
}

if (Test-Path $zipPath) {
  Remove-Item $zipPath -Force
}

Write-Host "Preparing staging directory..."
New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null

Get-ChildItem -Path $publishDir -Force | Where-Object {
  if (-not $_.PSIsContainer) {
    return $true
  }

  if ($_.Name -in $excludedTopLevelDirectories) {
    return $false
  }

  return $_.Name -in $allowedTopLevelDirectories
} | ForEach-Object {
  Copy-Item -Path $_.FullName -Destination (Join-Path $stagingDir $_.Name) -Recurse -Force
}

Write-Host "Creating green zip package..."
Start-Sleep -Seconds 2
New-ZipFromDirectory -SourceDirectory $stagingDir -DestinationPath $zipPath -IncludeBaseDirectory $true

Write-Host ""
Write-Host "Green zip package created:"
Write-Host "  $zipPath"
