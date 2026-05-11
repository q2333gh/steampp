# Windows Main Build Stabilization Summary

Last updated: 2026-03-24

## Scope

This document summarizes the recent multi-round CI and local build stabilization work for the Windows main build.

Primary goal:

- Make the Windows desktop mainline build succeed locally and in CI first
- Defer non-Windows platforms and non-essential feature paths until the main artifact is stable

Primary project/build entry points:

- Main CI workflow: `.github/workflows/dotnet.yml`
- Main desktop app project: `src/ST.Client.Desktop.Avalonia.App/ST.Client.Avalonia.App.csproj`
- Shared Windows SDK settings: `WindowsPlatform.props`

## What We Learned Across The Debugging Rounds

### 1. The main CI was not triggering on `master`

The main workflows originally listened to `main` and `develop`, while active development/pushes were happening on `master`.

Result:

- `Build` did not start on normal `master` pushes

Action taken:

- Updated the relevant workflow branch filters to include `master`

### 2. The repository is not a simple self-contained .NET solution

The build depends on a mix of:

- first-party projects under `src/`
- old projects under `source/`
- vendored/upstream code under `references/`
- pinned source dependencies that are required for successful restore/build

Important consequence:

- CI cannot assume that `references/*` is always already materialized correctly

### 3. Earlier CI failures were mostly environment and dependency-shape failures

The repeated failing points were not one single bug. They came from several layers:

- outdated GitHub Actions artifact upload action
- workflows too broad for the current state of the repo
- missing local NuGet source directory
- missing materialized `references/*` source dependencies
- incompatible upstream HEADs in some vendored repositories
- inconsistent Windows SDK package versions
- JumpList dependency chain forcing incompatible Windows SDK/runtime pack versions
- CI tests that were not hermetic enough for the reduced mainline path

### 4. The main Windows app can be built without solving every historical edge

A key design decision was to optimize for:

- successful Windows main artifact generation

instead of:

- immediately restoring every platform and every test project

That led to a much more reliable first-stage build strategy.

## Implemented Repository Changes

### 1. External dependency materialization is now pin-aware

File:

- `.github/scripts/materialize-external-deps.ps1`

What changed:

- The script now validates pinned repositories even when the folder already exists
- Commit-pinned repositories are updated if the current HEAD does not match the required revision
- Git invocation was hardened to avoid PowerShell error handling problems from git progress output

Pinned revisions currently used:

- `references/SteamAchievementManager` -> `99ce54c`
- `references/Gameloop.Vdf` -> `6bf1500`
- `references/AvaloniaGif` -> `e3d8985`

Why this mattered:

- upstream HEADs had drifted and some of them now targeted newer frameworks such as `net10.0`
- the main repo still targets `.NET 6`

### 2. Windows SDK settings were unified

Files:

- `WindowsPlatform.props`
- `src/ST.Client.Desktop.Avalonia.App/ST.Client.Avalonia.App.csproj`

What changed:

- The main app project stopped carrying a conflicting per-project Windows SDK package version
- The main app now explicitly imports `WindowsPlatform.props`

Why this mattered:

- mixed versions such as `10.0.19041.24`, `10.0.19041.26`, and newer transitive versions were causing build instability and SDK conflicts

### 3. JumpList was temporarily taken out of the critical path

Files:

- `src/ST.Client.Desktop.Avalonia.App/ST.Client.Avalonia.App.csproj`
- `src/Startup.cs`

What changed:

- `ST.Client.JumpList.Avalonia` was commented out from the main app project references
- `services.AddJumpListService();` was commented out in startup

Why this mattered:

- the JumpList path pulled in an external package chain that raised the Windows SDK/runtime pack level and triggered `NETSDK1148`
- this path is useful, but not required for first-stage validation of the main desktop artifact

### 4. CI was narrowed to a minimal Windows mainline

File:

- `.github/workflows/dotnet.yml`

What changed:

- only `windows-latest` is kept active
- only `Release` remains active on the main path
- NuGet package caching was added
- restore/build/test sequencing now uses explicit restore followed by `--no-restore`
- unstable or incomplete test legs were temporarily commented out

Current CI intent:

- materialize pinned source dependencies
- restore the main app
- build the main app
- run the stable common unit tests
- upload the main Windows build output

## Key Effective Commands Used

The following commands were the most useful and repeatable ones during stabilization.

### CI inspection

```powershell
gh run list --limit 5
```

Used to quickly confirm whether the latest `master` push actually triggered the intended workflow and to check current status.

Typical follow-up during failure analysis:

```powershell
gh run view <run-id> --log-failed
```

Used repeatedly during earlier rounds to inspect the real failing step instead of guessing.

### Materialize pinned source dependencies

```powershell
.\.github\scripts\materialize-external-deps.ps1
```

This is now a core preparation step for both CI and local reproduction.

### Clean repo-local build outputs before validation

```powershell
dotnet clean .\src\ST.Client.Desktop.Avalonia.App\ST.Client.Avalonia.App.csproj -c Release
dotnet clean .\tests\Common.UnitTest\Common.UnitTest.csproj -c Release
dotnet clean .\tests\ST.Client.UnitTest\ST.Client.UnitTest.csproj -c Release
dotnet clean .\tests\ST.Client.Desktop.UnitTest\ST.Client.Desktop.UnitTest.csproj -c Release
```

### Main app restore

```powershell
dotnet restore .\src\ST.Client.Desktop.Avalonia.App\ST.Client.Avalonia.App.csproj -p:Configuration=Release
```

This is intentionally separate from `build` so dependency-resolution failures are isolated early.

### Main app build

```powershell
dotnet build .\src\ST.Client.Desktop.Avalonia.App\ST.Client.Avalonia.App.csproj -c Release --no-restore
```

This command now succeeds locally on the stabilized Windows path.

### Stable unit test leg

```powershell
dotnet test .\tests\Common.UnitTest\Common.UnitTest.csproj -c Release --no-restore
```

This currently passes and is kept in the reduced CI path.

### Source control steps used to publish the stabilization work

```powershell
git add .github/scripts/materialize-external-deps.ps1 .github/workflows/dotnet.yml src/ST.Client.Desktop.Avalonia.App/ST.Client.Avalonia.App.csproj src/Startup.cs
git commit -m "Stabilize Windows main build on .NET 6"
git push origin master
```

## Local Verification Result

At the end of this stabilization round:

- `dotnet restore` for the main Windows desktop app succeeds
- `dotnet build` for the main Windows desktop app succeeds
- `Common.UnitTest` succeeds
- the reduced `Build` workflow on `master` starts successfully after push

## Known Deferred Items

These were intentionally not forced into the mainline success path yet.

### 1. `ST.Client.UnitTest`

Current issue:

- depends on host file expectations that do not hold consistently in CI

Recommended next step:

- either make the tests hermetic
- or isolate the environment-sensitive subset

### 2. `ST.Client.Desktop.UnitTest`

Current issue:

- depends on missing `SevenZipSharp` test data assets in the current reduced materialization path

Recommended next step:

- explicitly materialize those test assets
- or gate those tests behind a separate fuller test workflow

### 3. JumpList feature path

Current issue:

- external package chain currently conflicts with the chosen `.NET 6 + Windows SDK 19041.26` mainline

Recommended next step:

- first try to downgrade the JumpList package chain to a compatible version
- only consider broader SDK/toolchain upgrades if no compatible version exists

## Recommended Current Build Procedure

For anyone reproducing the stabilized Windows mainline locally:

```powershell
.\.github\scripts\materialize-external-deps.ps1
dotnet restore .\src\ST.Client.Desktop.Avalonia.App\ST.Client.Avalonia.App.csproj -p:Configuration=Release
dotnet build .\src\ST.Client.Desktop.Avalonia.App\ST.Client.Avalonia.App.csproj -c Release --no-restore
dotnet test .\tests\Common.UnitTest\Common.UnitTest.csproj -c Release --no-restore
```

## Local Green Zip Package

The repo now supports a first-stage local Windows green package flow that does not depend on the full official publish pipeline.

Input directory:

- `src/ST.Client.Desktop.Avalonia.App/bin/Release/Publish/win-x64`

Output directory:

- `artifacts/green-zip`

Main command:

```powershell
.\packaging\build-green-zip.ps1
```

What it does:

- materializes pinned external dependencies
- restores the main desktop app
- publishes the main desktop app in `Release` using `win-x64.pubxml`
- validates that the main executable and `Assets` directory exist
- validates that satellite resource directories only include `en`, `zh-CN`, and `zh-Hans`
- excludes `AppData` and `Cache` from the distributable zip so machine-local state is not shipped
- copies the publish output into a clean staging directory under `WattToolkit-win-x64-green`
- creates a user-facing Windows green zip package

Current packaging boundaries:

- Windows x64 only
- based on the local `publish/win-x64` output
- no signing, installer generation, release metadata, or cloud publish steps
- JumpList remains intentionally disabled in this package path

Current smoke standard:

- the app must stay alive for at least 30 seconds from the publish directory and from the extracted zip
- there must be no new `.NET Runtime 1023`, `Application Error 1000`, or `Windows Error Reporting 1001` events for `Steam++.exe`
- there must be no new `Steam++.exe.*.dmp` crash dump generated during the smoke run

Startup isolation flags available for local crash triage:

- `STEAMPP_SKIP_APPCENTER=1`
- `STEAMPP_SKIP_NOTIFYICON=1`
- `STEAMPP_SKIP_WEBVIEW2_INIT=1`
- `STEAMPP_SKIP_STARTUP_BACKGROUND=1`
- `STEAMPP_SKIP_REVERSE_PROXY_STARTUP=1`

## Notes

- This summary intentionally focuses on the Windows main artifact path
- The goal of this round was not to restore every historical workflow
- Once the mainline stays green consistently, the next phase should restore deferred tests and optional platform-specific features one by one
