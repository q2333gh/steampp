# Watt Toolkit 🧰 (原名 Steam++)



[English](./README.en.md) | 简体中文

「Watt Toolkit」是一个开源跨平台的多功能游戏工具箱，此工具的大部分功能都是需要您下载安装 Steam 才能使用。

Release Download
[Release Version](https://github.com/BeyondDimension/SteamTools/releases/latest)
[GitHub license](LICENSE)
[GitHub Star](https://github.com/BeyondDimension/SteamTools/stargazers)
[GitHub Fork](https://github.com/BeyondDimension/SteamTools/network/members)
GitHub Repo size
[GitHub Repo Languages](https://github.com/BeyondDimension/SteamTools/search?l=c%23)
[NET 6.0](https://docs.microsoft.com/zh-cn/dotnet/core/whats-new/dotnet-6)
[C# 10.0](https://docs.microsoft.com/zh-cn/dotnet/csharp/whats-new/csharp-10)

[Desktop UI](https://github.com/AvaloniaUI/Avalonia)
[Mobile GUI](https://github.com/xamarin/Xamarin.Forms)
[Official WebSite](https://github.com/ant-design/ant-design)
[BackManage WebSite](https://github.com/ant-design-blazor/ant-design-blazor)

[Build Status](https://actions-badge.atrox.dev/BeyondDimension/SteamTools/goto?ref=develop)
[GitHub Star](https://github.com/BeyondDimension/SteamTools)
[Gitee Star](https://gitee.com/rmbgame/SteamTools)

[爱发电](https://afdian.net/@rmbgame)
[Kofi](https://ko-fi.com/rmbgame)
[Patreon](https://www.patreon.com/rmbgame)
[Bilibili](https://space.bilibili.com/797215)
[QQ群](https://jq.qq.com/?_wv=1027&k=3JKPt4xC)

  
  


## 🚀 下载渠道

- [GitHub Releases](https://github.com/BeyondDimension/SteamTools/releases)
- [Gitee Releases](https://gitee.com/rmbgame/SteamTools/releases)
- [Official WebSite](https://steampp.net)
- [Microsoft Store](https://www.microsoft.com/store/apps/9MTCFHS560NG)
- [AUR](https://aur.archlinux.org/packages/watt-toolkit-bin)(官方 Release 构建)
- [AUR dev](https://aur.archlinux.org/packages/watt-toolkit-git)(拉取最新源代码从本地构建，不保证可用性，构建也许会出现失败问题)

## ✨ 功能

1. 网络加速    
  - ~~使用 [Titanium-Web-Proxy](https://github.com/justcoding121/Titanium-Web-Proxy) 开源项目进行本地反代来支持更快的访问游戏网站。~~
   使用 [YARP.ReverseProxy](https://github.com/microsoft/reverse-proxy) 开源项目进行本地反代来支持更快的访问游戏网站。
2. 脚本配置   
  通过加速服务拦截网络请求将一些 JS 脚本注入在网页中，提供类似网页插件的功能。
3. 账号切换   
  一键切换已在当前 PC 上登录过的 Steam 账号，与管理家庭共享库排序及禁用等功能。
4. 库存管理   
  让您直接管理 Steam 游戏库存，可以编辑游戏名称和[自定义封面](https://www.steamgriddb.com/)，也能解锁以及反解锁 Steam 游戏成就。
   监控 Steam 游戏下载进度实现 Steam 游戏下载完成定时关机功能。
   模拟运行 Steam 游戏，让您不用安装和下载对应的游戏也能挂游玩时间和 Steam 卡片
   自助管理 Steam 游戏云存档，随时删除和上传自定义的存档文件至 Steam 云
5. 本地令牌    
  让您的手机令牌统一保存在电脑中，目前仅支持 Steam 令牌，后续会开发支持更多的令牌种类与云同步令牌。
6. 自动挂卡    
  集成 [ArchiSteamFarm](https://github.com/JustArchiNET/ArchiSteamFarm) 在应用内提供 挂机掉落 Steam 集换式卡牌 等功能。
7. 游戏工具 
  强制游戏窗口使用无边框窗口化、更多功能待开发。





## 🖥 系统要求

### Windows


| OS                                                           | Version              | Architectures | Lifecycle                                                                                           |
| ------------------------------------------------------------ | -------------------- | ------------- | --------------------------------------------------------------------------------------------------- |
| [Windows Client](https://www.microsoft.com/windows/)         | 7 SP1(), 8.1()       | x64           | [Windows](https://support.microsoft.com/help/13853/windows-lifecycle-fact-sheet)                    |
| [Windows 10 Client](https://www.microsoft.com/windows/)      | Version 1607+()      | x64           | [Windows](https://support.microsoft.com/help/13853/windows-lifecycle-fact-sheet)                    |
| [Windows 11](https://www.microsoft.com/windows/)             | Version 22000+       | x64,          | [Windows](https://support.microsoft.com/help/13853/windows-lifecycle-fact-sheet)                    |
| [Windows Server](https://docs.microsoft.com/windows-server/) | 2008 R2 SP1(), 2012+ | x64           | [Windows Server](https://docs.microsoft.com/windows-server/get-started/windows-server-release-info) |


 Windows 7 SP1 必须安装 [扩展安全更新 (ESU)](https://docs.microsoft.com/troubleshoot/windows-client/windows-7-eos-faq/windows-7-extended-security-updates-faq) 且将在不再支持 **2022/11** 后发布的版本。  
 Windows 8.1 将在不再支持 **2022/11** 后发布的版本。  
 Windows Server 2008 R2 SP1 必须安装 [扩展安全更新 (ESU)](https://docs.microsoft.com/zh-cn/lifecycle/faq/extended-security-updates) 且将在不再支持 **2022/11** 后发布的版本。  
 Microsoft Store(Desktop Bridge) Version 1809+  

### Linux


| OS                                                                                                  | Version              | Architectures | Lifecycle                                                           |
| --------------------------------------------------------------------------------------------------- | -------------------- | ------------- | ------------------------------------------------------------------- |
| [Alpine Linux](https://alpinelinux.org/)                                                            | 3.13+                | x64, Arm64    | [Alpine](https://wiki.alpinelinux.org/wiki/Alpine_Linux:Releases)   |
| [CentOS](https://www.centos.org/)                                                                   | 7+                   | x64           | [CentOS](https://wiki.centos.org/FAQ/General)                       |
| [Debian](https://www.debian.org/)                                                                   | 10+                  | x64, Arm64    | [Debian](https://wiki.debian.org/DebianReleases)                    |
| [Fedora](https://getfedora.org/)                                                                    | 33+                  | x64           | [Fedora](https://fedoraproject.org/wiki/End_of_life)                |
| [openSUSE](https://opensuse.org/)                                                                   | 15+                  | x64           | [OpenSUSE](https://en.opensuse.org/Lifetime)                        |
| [Red Hat Enterprise Linux](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux) | 7+                   | x64, Arm64    | [Red Hat](https://access.redhat.com/support/policy/updates/errata/) |
| [SUSE Enterprise Linux (SLES)](https://www.suse.com/products/server/)                               | 12 SP2+              | x64           | [SUSE](https://www.suse.com/lifecycle/)                             |
| [Ubuntu](https://ubuntu.com/)                                                                       | 16.04, 18.04, 20.04+ | x64, Arm64    | [Ubuntu](https://wiki.ubuntu.com/Releases)                          |
| [Deepin / UOS](https://www.deepin.org/)                                                             | 20+                  | x64           | [Deepin](https://www.deepin.org/release-notes)                      |
| [Arch Linux](https://archlinux.org/)                                                                |                      | x64，Arm64     |                                                                     |


### macOS


| OS                                       | Version | Architectures |
| ---------------------------------------- | ------- | ------------- |
| [macOS](https://support.apple.com/macos) | 10.15+  | x64, Arm64    |


### Android


| OS                                            | Version      | Architectures                                                                                                                                                                                                                         |
| --------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Android](https://support.google.com/android) | 5.0(API 21)+ | [x64](https://developer.android.google.cn/ndk/guides/abis?hl=zh_cn#86-64), [Arm64](https://developer.android.google.cn/ndk/guides/abis?hl=zh_cn#arm64-v8a), [Arm32](https://developer.android.google.cn/ndk/guides/abis?hl=zh_cn#v7a) |


### ~~iOS / iPadOS~~


| OS                                   | Version | Architectures     |
| ------------------------------------ | ------- | ----------------- |
| [iOS](https://support.apple.com/ios) | 10.0+   | x64, Arm32, Arm64 |


## ⛔ 不受支持的操作系统

- Windows 8
  - [由于微软官方对该产品的支持已结束](https://docs.microsoft.com/zh-cn/lifecycle/products/windows-8)，故本程序无法在此操作系统上运行，[建议升级到 Windows 8.1](https://support.microsoft.com/zh-cn/windows/%E4%BB%8E-windows-8-%E6%9B%B4%E6%96%B0%E5%88%B0-windows-8-1-17fc54a7-a465-6b5a-c1a0-34140afd0669)
- 无桌面 GUI 的 Windows Server / Linux 版本
- Xbox or Windows Mobile / Phone

## 🌏 路线图

查看这个 [milestones](https://github.com/BeyondDimension/SteamTools/milestones) 来了解我们下一步的开发计划，并随时提出问题。

## ⌨️ 开发环境

[Visual Studio 2022](https://visualstudio.microsoft.com/zh-hans/vs/)  
[JetBrains Rider](https://www.jetbrains.com/rider/)  
~~[Visual Studio 2022 for Mac](https://visualstudio.microsoft.com/zh-hans/vs/mac/)~~  
~~[Visual Studio Code](https://code.visualstudio.com/)~~

- 系统要求
  - [Windows 10 版本 2004 或更高版本：家庭版、专业版、教育版和企业版（不支持 LTSC 和 Windows 10 S，在较早的操作系统上可能不受支持）](https://docs.microsoft.com/zh-cn/visualstudio/releases/2019/system-requirements)
  - [macOS 10.14 Mojave 或更高版本](https://docs.microsoft.com/zh-cn/visualstudio/productinfo/vs2019-system-requirements-mac)
- 工作负荷
  - Web 和云
    - ASP.NET 和 Web 开发
  - 桌面应用和移动应用
    - 使用 .NET 的移动开发 / .NET Multi-platform App UI 开发
    - .NET 桌面开发
    - 通用 Windows 平台开发
- 单个组件
  - GitHub Extension for Visual Studio(可选)
  - Windows 10 SDK (10.0.19041.0)
- [Visual Studio Marketplace](https://marketplace.visualstudio.com/)
  - [Avalonia for Visual Studio(可选)](https://marketplace.visualstudio.com/items?itemName=AvaloniaTeam.AvaloniaforVisualStudio)
  - [NUnit VS Templates(可选)](https://marketplace.visualstudio.com/items?itemName=NUnitDevelopers.NUnitTemplatesforVisualStudio)

[OpenJDK 11](https://docs.microsoft.com/zh-cn/java/openjdk/download#openjdk-11)  
[Android Studio 2021.1.1 或更高版本](https://developer.android.google.cn/studio/)  
[Xcode 13 或更高版本](https://developer.apple.com/xcode/)

## 🏗️ [项目结构](./src/README.md)

详见 [./src/README.md](./src/README.md)  





## 📄 感谢以下开源项目

- [Newtonsoft.Json](https://github.com/JamesNK/Newtonsoft.Json)
- [MetroRadiance](https://github.com/Grabacr07/MetroRadiance)
- [MetroTrilithon](https://github.com/Grabacr07/MetroTrilithon)
- [Livet](https://github.com/runceel/Livet)
- [StatefulModel](https://github.com/ugaya40/StatefulModel)
- [Hardcodet.NotifyIcon](https://github.com/HavenDV/Hardcodet.NotifyIcon.Wpf.NetCore)
- [System.Reactive](https://github.com/dotnet/reactive)
- [Titanium-Web-Proxy](https://github.com/justcoding121/Titanium-Web-Proxy)
- [YARP](https://github.com/microsoft/reverse-proxy)
- [FastGithub](https://github.com/dotnetcore/FastGithub)
- [Portable.BouncyCastle](https://github.com/novotnyllc/bc-csharp)
- [Ninject](https://github.com/ninject/Ninject)
- [log4net](https://github.com/apache/logging-log4net)
- [SteamAchievementManager](https://github.com/gibbed/SteamAchievementManager)
- [ArchiSteamFarm](https://github.com/JustArchiNET/ArchiSteamFarm)
- [Steam4NET](https://github.com/SteamRE/Steam4NET)
- [WinAuth](https://github.com/winauth/winauth)
- [SteamDesktopAuthenticator](https://github.com/Jessecar96/SteamDesktopAuthenticator)
- [Gameloop.Vdf](https://github.com/shravan2x/Gameloop.Vdf)
- [DnsClient.NET](https://github.com/MichaCo/DnsClient.NET)
- [Costura.Fody](https://github.com/Fody/Costura)
- [MessagePack-CSharp](https://github.com/neuecc/MessagePack-CSharp)
- [CSharpVitamins.ShortGuid](https://github.com/AigioL/CSharpVitamins.ShortGuid)
- [Nito.Comparers](https://github.com/StephenCleary/Comparers)
- [Nito.Disposables](https://github.com/StephenCleary/Disposables)
- [Crc32.NET](https://github.com/force-net/Crc32.NET)
- [gfoidl.Base64](https://github.com/gfoidl/Base64)
- [sqlite-net-pcl](https://github.com/praeclarum/sqlite-net)
- [AutoMapper](https://github.com/AutoMapper/AutoMapper)
- [Polly](https://github.com/App-vNext/Polly)
- [TaskScheduler](https://github.com/dahall/taskscheduler)
- [SharpZipLib](https://github.com/icsharpcode/SharpZipLib)
- [SevenZipSharp](https://github.com/squid-box/SevenZipSharp)
- [ZstdNet](https://github.com/skbkontur/ZstdNet)
- [Depressurizer](https://github.com/Depressurizer/Depressurizer)
- [NLog](https://github.com/nlog/NLog)
- [NUnit](https://github.com/nunit/nunit)
- [ReactiveUI](https://github.com/reactiveui/reactiveui)
- [MessageBox.Avalonia](https://github.com/AvaloniaUtils/MessageBox.Avalonia)
- [AvaloniaUI](https://github.com/AvaloniaUI/Avalonia)
- [AvaloniaGif](https://github.com/jmacato/AvaloniaGif)
- [Avalonia XAML Behaviors](https://github.com/wieslawsoltes/AvaloniaBehaviors)
- [FluentAvalonia](https://github.com/amwx/FluentAvalonia)
- [APNG.NET](https://github.com/jz5/APNG.NET)
- [Moq](https://github.com/moq/moq4)
- [NPOI](https://github.com/nissl-lab/npoi)
- [Fleck](https://github.com/statianzo/Fleck)
- [Swashbuckle.AspNetCore](https://github.com/domaindrivendev/Swashbuckle.AspNetCore)
- [AspNet.Security.OpenId.Providers](https://github.com/aspnet-contrib/AspNet.Security.OpenId.Providers)
- [AspNet.Security.OAuth.Providers](https://github.com/aspnet-contrib/AspNet.Security.OAuth.Providers)
- [ZXing.Net](https://github.com/micjahn/ZXing.Net)
- [QRCoder](https://github.com/codebude/QRCoder)
- [QR Code Generator for .NET](https://github.com/manuelbl/QrCodeGenerator)
- [TinyPinyin](https://github.com/promeG/TinyPinyin)
- [TinyPinyin.Net](https://github.com/hueifeng/TinyPinyin.Net)
- [Packaging utilities for .NET Core](https://github.com/qmfrederik/dotnet-packaging)
- [React](https://github.com/facebook/react)
- [Ant Design](https://github.com/ant-design/ant-design)
- [Ant Design Blazor](https://github.com/ant-design-blazor/ant-design-blazor)
- [Toast messages for Xamarin.iOS](https://github.com/andrius-k/Toast)
- [ImageCirclePlugin](https://github.com/jamesmontemagno/ImageCirclePlugin)
- [Visual Studio App Center SDK for .NET](https://github.com/microsoft/appcenter-sdk-dotnet)
- [AppCenter-XMac](https://github.com/nor0x/AppCenter-XMac)
- [MSBuild.Sdk.Extras](https://github.com/novotnyllc/MSBuildSdkExtras)
- [Xamarin.Essentials](https://github.com/xamarin/essentials)
- [Xamarin.Forms](https://github.com/xamarin/Xamarin.Forms)
- [Open Source Components for Xamarin](https://github.com/xamarin/XamarinComponents)
- [Google Play Services / Firebase / ML Kit for Xamarin.Android](https://github.com/xamarin/GooglePlayServicesComponents)
- [Picasso](https://github.com/square/picasso)
- [OkHttp](https://github.com/square/okhttp)
- [Material Components for Android](https://github.com/material-components/material-components-android)
- [AndroidX for Xamarin.Android](https://github.com/xamarin/AndroidX)
- [Android Jetpack](https://github.com/androidx/androidx)
- [ConstraintLayout](https://github.com/androidx/constraintlayout)
- [Entity Framework Core](https://github.com/dotnet/efcore)
- [ASP.NET Core](https://github.com/dotnet/aspnetcore)
- [Windows Forms](https://github.com/dotnet/winforms)
- [Windows Presentation Foundation (WPF)](https://github.com/dotnet/wpf)
- [C#/WinRT](https://github.com/microsoft/CsWinRT)
- [command-line-api](https://github.com/dotnet/command-line-api)
- [.NET Runtime](https://github.com/dotnet/runtime)
- [Fluent UI System Icons](https://github.com/microsoft/fluentui-system-icons)
- [Material design icons](https://github.com/google/material-design-icons)

