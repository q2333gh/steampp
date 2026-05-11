# steam-switch-py

Windows-only Steam account switch tool managed by `uv`.
GUI is implemented with DearPyGui.

## Commands
- `steam-switch list`
- `steam-switch login_new [--mode offline|express]`
- `steam-switch select --account <account_name> [--mode offline|express]`
- `steam-switch-gui`

## Run
```bash
cd steam_switch/steam_switch_py
uv run steam-switch list
uv run steam-switch-gui
```
