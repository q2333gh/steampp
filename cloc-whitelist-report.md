# mess,but work~
不完全是 `C#` / `.NET` 的问题，更多是这个项目的工程演化方式比较“重实用、轻边界”。

像这个仓库这么混，一般是几种因素叠加出来的：

1. 历史包袱重  
这个项目同时有 `source/` 里的旧工程和 `src/` 里的新工程，明显经历过多代技术栈并存、渐进迁移，而不是一次性重构。

2. 团队偏向“先跑起来”  
很多上游代码不是通过 NuGet 之类依赖管理，而是直接拷一份源码进仓库改。这么做短期很高效，方便打补丁、跨平台兼容、绕版本冲突，但长期就会让边界越来越糊。

3. 产品形态复杂  
它同时覆盖桌面、移动端、Avalonia、Xamarin/Maui、代理、打包工具、测试、旧版兼容。业务一复杂，工程如果缺少强约束，很容易变成“大一统仓库 + 各种特例”。

4. 缺少明确的“第三方代码管理规范”  
你这里不是完全乱，而是“能看出作者知道自己在做什么，但不太在意结构洁癖”。比如很多文件会标注 upstream 来源，这说明不是无意识乱拷；但没有把这些代码系统性隔离出去，说明工程治理不够强。

所以我的判断是：

- 不是 `.NET` 天生导致的。
- 也不一定能简单骂成“开发者习惯极差”。
- 更像是“小团队/长期项目/高交付压力”下，架构治理被实用主义压过去了。

换句话说，这类仓库通常代表：
- 开发能力未必差
- 工程纪律比较弱
- 仓库维护策略偏临时性、补丁式
- 对“能发布、能兼容、能修 bug”的优先级，高于“结构清晰、边界干净、统计可审计”

如果你愿意，我可以继续帮你把这个仓库按“原创代码 / 改写上游 / 纯第三方 / 资源与构建脚本”四类完整分层列出来，这样你会更直观看出它到底是“乱”到什么程度。

# cloc: 

PS X:\code\steampp> cloc src source tests packaging .github/workflows resources/ProjectPathUtil.cs `
>>   --fullpath --timeout=0 `
>>   --exclude-dir=references,.VSCodeCounter,ISSUE_TEMPLATE,Avalonia.Desktop,Avalonia.Diagnostics,Avalonia.Native,Avalonia.Skia.Internals,Avalonia.Themes.Default,Avalonia.Themes.Fluent,Avalonia.WebView2,Avalonia.Win32,Avalonia.X11,Microsoft.Net.Http.Headers,dotnet-core-uninstall,NuGet.Versioning,SteamTool.Steam4NET,SteamTool.Steam4NET.Test
    2424 text files.
    2403 unique files.
     312 files ignored.

github.com/AlDanial/cloc v 2.08  T=8.88 s (270.6 files/s, 37773.2 lines/s)
------------------------------------------------------------------------------------
Language                          files          blank        comment           code
------------------------------------------------------------------------------------
C#                                 1670          26745          35081         143943
XML                                 343           1886           4658          42851
C# Designer                          27           6948           9685          24860
XAML                                 98            667            934           9164
AXAML                                71            569           1345           8263
MSBuild script                       91            648            370           7324
JavaScript                            2            569            295           2795
Kotlin                               34            249            998           1296
YAML                                  4            122             29            532
PowerShell                            3             64             27            311
JSON                                 11              0              0            310
Visual Studio Solution                1              1              1            306
Markdown                             16             38              0            293
Bourne Shell                          4             36             22            205
Gradle                                6             26              5            192
Text                                  6             91              0            191
XSD                                   2              0              2            160
SVG                                   4              0              0            106
DOS Batch                             2             23              2             60
Java                                  4             16             22             48
Properties                            2              0             16              7
ProGuard                              2              6             36              0
------------------------------------------------------------------------------------
SUM:                               2403          38704          53528         243217
------------------------------------------------------------------------------------
PS X:\code\steampp> 