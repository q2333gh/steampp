from __future__ import annotations

import os
import re
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

try:
    import winreg
except Exception:  # pragma: no cover
    winreg = None

STEAM_REG_PATH = r"Software\\Valve\\Steam"
AUTO_LOGIN_USER = "AutoLoginUser"
STEAM_PATH = "SteamPath"
STEAM_EXE = "SteamExe"


@dataclass(slots=True)
class SteamUser:
    account_name: str
    steam_id64: str
    persona_name: str
    most_recent: bool


class SteamSwitchError(RuntimeError):
    pass


ProgressCb = Callable[[str], None]
_OP_LOCK = threading.Lock()


def ensure_windows() -> None:
    if sys.platform != "win32":
        raise SteamSwitchError("This CLI supports Windows only.")
    if winreg is None:
        raise SteamSwitchError("winreg is unavailable in this environment.")


def _read_reg_value(name: str) -> str:
    ensure_windows()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STEAM_REG_PATH) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value)
    except OSError as exc:
        raise SteamSwitchError(f"Failed to read registry value: {name}") from exc


def _write_reg_value(name: str, value: str) -> None:
    ensure_windows()
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, STEAM_REG_PATH) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
    except OSError as exc:
        raise SteamSwitchError(f"Failed to write registry value: {name}") from exc


def get_steam_dir() -> Path:
    path = _read_reg_value(STEAM_PATH).strip()
    if not path:
        raise SteamSwitchError("SteamPath is empty in registry.")
    result = Path(path).expanduser().resolve()
    if not result.exists():
        raise SteamSwitchError(f"Steam directory does not exist: {result}")
    return result


def get_steam_exe() -> Path:
    exe = _read_reg_value(STEAM_EXE).strip()
    if not exe:
        raise SteamSwitchError("SteamExe is empty in registry.")
    result = Path(exe).expanduser().resolve()
    if not result.exists():
        raise SteamSwitchError(f"Steam executable does not exist: {result}")
    return result


def get_loginusers_vdf() -> Path:
    vdf = get_steam_dir() / "config" / "loginusers.vdf"
    if not vdf.exists():
        raise SteamSwitchError(f"loginusers.vdf not found: {vdf}")
    return vdf


def parse_loginusers(content: str) -> list[SteamUser]:
    # Match each top-level user block: "<steamid64>" { ... }
    block_re = re.compile(r'"(?P<sid>\d{17})"\s*\{(?P<body>.*?)\}', re.S)

    def pick(body: str, key: str) -> str:
        m = re.search(rf'"{re.escape(key)}"\s*"(?P<v>.*?)"', body)
        return m.group("v") if m else ""

    users: list[SteamUser] = []
    for m in block_re.finditer(content):
        body = m.group("body")
        account = pick(body, "AccountName")
        if not account:
            continue
        users.append(
            SteamUser(
                account_name=account,
                steam_id64=m.group("sid"),
                persona_name=pick(body, "PersonaName"),
                most_recent=pick(body, "MostRecent") == "1",
            )
        )
    return users


def list_users() -> list[SteamUser]:
    content = get_loginusers_vdf().read_text(encoding="utf-8", errors="ignore")
    users = parse_loginusers(content)
    if not users:
        raise SteamSwitchError("No remembered users found in loginusers.vdf.")
    return users


def set_current_user(account_name: str) -> None:
    _write_reg_value(AUTO_LOGIN_USER, account_name)


def _run(cmd: Iterable[str]) -> None:
    try:
        subprocess.run(list(cmd), check=True)
    except subprocess.CalledProcessError as exc:
        raise SteamSwitchError(f"Command failed: {' '.join(cmd)}") from exc


def kill_steam_processes() -> None:
    # Ignore taskkill non-zero exit in case process is not running.
    subprocess.run(["taskkill", "/IM", "steam.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["taskkill", "/IM", "steamwebhelper.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def start_steam(mode: str) -> None:
    exe = str(get_steam_exe())
    args: list[str] = [exe]
    if mode == "offline":
        args.append("-offline")
    _run(args)


def login_new(mode: str) -> None:
    kill_steam_processes()
    set_current_user("")
    start_steam(mode)


def select_account(account_name: str, mode: str) -> SteamUser:
    users = list_users()
    found = next((u for u in users if u.account_name == account_name), None)
    if found is None:
        raise SteamSwitchError(f"Account not found: {account_name}")
    kill_steam_processes()
    set_current_user(found.account_name)
    start_steam(mode)
    return found


def _validate_mode(mode: str) -> None:
    if mode not in ("offline", "express"):
        raise SteamSwitchError(f"Unsupported mode: {mode}")


def _run_with_lock(fn: Callable[[], None]) -> None:
    if not _OP_LOCK.acquire(blocking=False):
        raise SteamSwitchError("Another switch/start operation is running.")
    try:
        fn()
    finally:
        _OP_LOCK.release()


def perform_login_new(mode: str, progress: ProgressCb | None = None) -> None:
    _validate_mode(mode)

    def emit(step: str) -> None:
        if progress is not None:
            progress(step)

    def run() -> None:
        emit("Lock acquired")
        emit("Stopping Steam processes")
        kill_steam_processes()
        emit("Clearing AutoLoginUser")
        set_current_user("")
        emit("Starting Steam")
        start_steam(mode)
        emit("Done")

    _run_with_lock(run)


def perform_select_account(account_name: str, mode: str, progress: ProgressCb | None = None) -> SteamUser:
    if not account_name.strip():
        raise SteamSwitchError("AccountName cannot be empty.")
    _validate_mode(mode)
    result: SteamUser | None = None

    def emit(step: str) -> None:
        if progress is not None:
            progress(step)

    def run() -> None:
        nonlocal result
        emit("Lock acquired")
        emit("Resolving account")
        users = list_users()
        found = next((u for u in users if u.account_name == account_name), None)
        if found is None:
            raise SteamSwitchError(f"Account not found: {account_name}")
        emit("Stopping Steam processes")
        kill_steam_processes()
        emit("Setting AutoLoginUser")
        set_current_user(found.account_name)
        emit("Starting Steam")
        start_steam(mode)
        emit("Done")
        result = found

    _run_with_lock(run)
    assert result is not None
    return result
