steam_switch extracted core code (raw copy, no compile guarantee)

Structure
- Core switching logic remains under steam_switch/src/...
- UI-related files are stripped out to steam_switch/others/ui/

Core chain (non-UI)
1) Service contracts / user state
- src/ST.Client/Services/ISteamService.cs
- src/ST.Client/Services/IPlatformService.cs
- src/ST.Client/Services/Mvvm/SteamConnectService.cs
- src/ST.Client/Models/Steam/SteamUser.cs

2) Switching implementation
- src/ST.Client.Desktop.Windows/Services/Implementation/SteamServiceImpl.cs
- src/ST.Client.Desktop.Windows/Services/Implementation/WindowsPlatformServiceImpl.cs
- src/ST.Client.Desktop.Mac/Services/Implementation/MacPlatformServiceImpl.cs
- src/ST.Client.Desktop.Linux/Services/Implementation/LinuxPlatformServiceImpl.cs

3) Entrypoints and registration
- src/Startup.cs
- src/ST.Client.CommandLine/CommandLineHost.cs

4) Related settings
- src/ST.Client/Settings/SteamAccountSettings.cs
- src/ST.Client/Settings/SteamSettings.cs

UI moved to others/ui
- SteamAccountPage.axaml
- SteamAccountPage.axaml.cs
- SteamAccountPageViewModel.cs

Notes
- Files are copied as-is from repository tree.
- No compile/syntax guarantee by design.
