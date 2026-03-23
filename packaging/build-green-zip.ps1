param(
  [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path $PSScriptRoot -Parent
$mainProject = Join-Path $repoRoot "src\ST.Client.Desktop.Avalonia.App\ST.Client.Avalonia.App.csproj"
$sourceDir = Join-Path $repoRoot "src\ST.Client.Desktop.Avalonia.App\bin\$Configuration\net6.0-windows10.0.19041.0\win7-x64"
$artifactsRoot = Join-Path $repoRoot "artifacts\green-zip"
$stagingDir = Join-Path $artifactsRoot "staging\WattToolkit-win-x64-green"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$gitSha = ""

try {
  $gitSha = (& git -C $repoRoot rev-parse --short HEAD 2>$null).Trim()
} catch {
  $gitSha = ""
}

if ([string]::IsNullOrWhiteSpace($gitSha)) {
  $zipName = "WattToolkit-win-x64-green-$timestamp.zip"
} else {
  $zipName = "WattToolkit-win-x64-green-$timestamp-$gitSha.zip"
}

$zipPath = Join-Path $artifactsRoot $zipName
$entryExe = Join-Path $sourceDir "Steam++.exe"
$assetsDir = Join-Path $sourceDir "Assets"

Add-Type -AssemblyName System.IO.Compression.FileSystem

function New-ZipFromDirectory {
  param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDirectory,
    [Parameter(Mandatory = $true)]
    [string]$DestinationPath
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
        $false)

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

Write-Host "Materializing pinned external dependencies..."
& (Join-Path $repoRoot ".github\scripts\materialize-external-deps.ps1")
if ($LASTEXITCODE) { exit $LASTEXITCODE }

Write-Host "Restoring main app..."
& dotnet restore $mainProject -p:Configuration=$Configuration
if ($LASTEXITCODE) { exit $LASTEXITCODE }

Write-Host "Building main app..."
& dotnet build $mainProject -c $Configuration --no-restore
if ($LASTEXITCODE) { exit $LASTEXITCODE }

if (-not (Test-Path $sourceDir)) {
  throw "Main build output directory was not found: $sourceDir"
}

if (-not (Test-Path $entryExe)) {
  throw "Main executable was not found: $entryExe"
}

if (-not (Test-Path $assetsDir)) {
  throw "Assets directory was not found: $assetsDir"
}

New-Item -ItemType Directory -Force -Path $artifactsRoot | Out-Null

if (Test-Path $stagingDir) {
  Remove-Item $stagingDir -Recurse -Force
}

if (Test-Path $zipPath) {
  Remove-Item $zipPath -Force
}

Write-Host "Preparing staging directory..."
New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null
Copy-Item -Path (Join-Path $sourceDir "*") -Destination $stagingDir -Recurse -Force

Write-Host "Creating green zip package..."
Start-Sleep -Seconds 2
New-ZipFromDirectory -SourceDirectory $stagingDir -DestinationPath $zipPath

Write-Host ""
Write-Host "Green zip package created:"
Write-Host "  $zipPath"
