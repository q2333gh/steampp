# Code Count Notes

The repository-wide `34w` figure is too broad to describe project code size. It includes many non-source files such as references, resources, and documentation.

To get a more meaningful code-size number, this document uses a narrower scope:

whilielist of: 

source/
src/
tests/
packaging/
.github/workflows/

This scope is intended to reflect handwritten source code and build/release automation, while excluding third-party references and resource files.

## How This Count Was Generated

Tool version:

- `cloc 2.08`

Command used:

```powershell
& 'C:\Users\12531\AppData\Local\Microsoft\WinGet\Packages\AlDanial.Cloc_Microsoft.Winget.Source_8wekyb3d8bbwe\cloc.exe' source src tests packaging .github/workflows --fullpath --timeout=0 --report-file='cloc-focused-report.txt'
```

Notes:

- `--fullpath` keeps file paths explicit in the report.
- `--timeout=0` disables per-file timeout guards so large files are fully counted.
- The report file `cloc-focused-report.txt` was written in the repository root.

## Focused Count Result

- `2725` files
- `290792` lines of code
- `55549` comment lines
- `46527` blank lines
- `392868` total lines

## Language Breakdown

| Language | Files | Blank | Comment | Code |
| --- | ---: | ---: | ---: | ---: |
| C# | 1980 | 34486 | 36932 | 191126 |
| XML | 345 | 1908 | 4754 | 42997 |
| C# Designer | 29 | 6972 | 9755 | 24964 |
| XAML | 98 | 667 | 934 | 9164 |
| AXAML | 71 | 569 | 1345 | 8263 |
| MSBuild script | 98 | 682 | 374 | 7455 |
| JavaScript | 2 | 569 | 295 | 2795 |
| Kotlin | 34 | 249 | 998 | 1296 |
| YAML | 4 | 122 | 29 | 532 |
| PowerShell | 3 | 64 | 27 | 311 |
| JSON | 11 | 0 | 0 | 310 |
| Visual Studio Solution | 1 | 1 | 1 | 306 |
| Markdown | 17 | 40 | 0 | 304 |
| Bourne Shell | 4 | 36 | 22 | 205 |
| Gradle | 6 | 26 | 5 | 192 |
| Text | 6 | 91 | 0 | 191 |
| XSD | 2 | 0 | 2 | 160 |
| SVG | 4 | 0 | 0 | 106 |
| DOS Batch | 2 | 23 | 2 | 60 |
| Java | 4 | 16 | 22 | 48 |
| Properties | 2 | 0 | 16 | 7 |
| ProGuard | 2 | 6 | 36 | 0 |

## Why This Scope Is Better

If you want to explain project size, this focused count is more accurate than a repository-wide number because it avoids inflating the total with:

- third-party or reference code
- assets and resource files
- documentation
- generated or auxiliary files

If you need an even stricter number, the next step would be to count only `source/` and `src/`, and optionally add `tests/` separately.



New-Item -ItemType Directory -Force -Path "X:\code\steampp\cloc-split" | Out-Null

cloc "X:\code\steampp\src" --fullpath --timeout=0 --exclude-dir=references,.VSCodeCounter,ISSUE_TEMPLATE,Avalonia.Desktop,Avalonia.Diagnostics,Avalonia.Native,Avalonia.Skia.Internals,Avalonia.Themes.Default,Avalonia.Themes.Fluent,Avalonia.WebView2,Avalonia.Win32,Avalonia.X11,Microsoft.Net.Http.Headers,dotnet-core-uninstall,NuGet.Versioning --report-file="X:\code\steampp\cloc-split\01-src.txt"

cloc "X:\code\steampp\source" --fullpath --timeout=0 --exclude-dir=references,.VSCodeCounter,ISSUE_TEMPLATE,SteamTool.Steam4NET,SteamTool.Steam4NET.Test --report-file="X:\code\steampp\cloc-split\02-source.txt"

cloc "X:\code\steampp\tests" --fullpath --timeout=0 --exclude-dir=references,.VSCodeCounter,ISSUE_TEMPLATE --report-file="X:\code\steampp\cloc-split\03-tests.txt"

cloc "X:\code\steampp\packaging" --fullpath --timeout=0 --exclude-dir=references,.VSCodeCounter,ISSUE_TEMPLATE --report-file="X:\code\steampp\cloc-split\04-packaging.txt"

cloc "X:\code\steampp\.github\workflows" "X:\code\steampp\resources\ProjectPathUtil.cs" --fullpath --timeout=0 --report-file="X:\code\steampp\cloc-split\05-meta.txt"
