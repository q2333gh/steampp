已经把 Gitee 同步整个注释掉了，在 [sync-gitee.yml](x:\code\steampp\.github\workflows\sync-gitee.yml)。

这个仓库如果分“主要工程构建”和“主要发布打包”来看，结论是：

`CI` 里主要的常规构建是 [dotnet.yml](x:\code\steampp\.github\workflows\dotnet.yml)。它在主分支/开发分支上跑 restore、build、test，所以这是日常主构建 workflow。真正被构建的核心工程是 [ST.Client.Avalonia.App.csproj](x:\code\steampp\src\ST.Client.Desktop.Avalonia.App\ST.Client.Avalonia.App.csproj)，对应步骤就是 `Build AvaloniaApp`。

如果说“最终产物的主入口”，那不是 workflow 本身，而是 [build.ps1](x:\code\steampp\packaging\build.ps1)。`dotnet.yml` 和 [publish.yml](x:\code\steampp\.github\workflows\publish.yml) 最后都是调用它来做多平台 `publish/package`。所以可以这么理解：

- 日常主构建：[`dotnet.yml`](x:\code\steampp\.github\workflows\dotnet.yml)
- 核心主工程：[`src/ST.Client.Desktop.Avalonia.App/ST.Client.Avalonia.App.csproj`](x:\code\steampp\src\ST.Client.Desktop.Avalonia.App\ST.Client.Avalonia.App.csproj)
- 最终主打包入口：[`packaging/build.ps1`](x:\code\steampp\packaging\build.ps1)
- `publish.yml` 只是 tag 发布时调用这套打包流程的发布版 workflow
- `xamarin.yml` 更像旧移动端补充构建，不是现在的主线

如果你要，我下一步可以继续帮你把这几个 workflow 精简成“主线 / 历史遗留 / 可删”三类。