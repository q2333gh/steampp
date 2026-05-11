from __future__ import annotations

import json
import queue
import threading
import ctypes
from pathlib import Path
from typing import Any

import dearpygui.dearpygui as dpg

from .switcher import SteamUser, list_users, perform_login_new, perform_select_account


def _enable_windows_dpi_awareness() -> None:
    # Avoid blurry rendering on high-DPI displays.
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def _get_windows_dpi_scale() -> float:
    try:
        dpi = ctypes.windll.user32.GetDpiForSystem()
        if dpi and dpi > 0:
            return max(1.0, min(2.5, dpi / 96.0))
    except Exception:
        pass
    return 1.0


class SteamSwitchGui:
    def __init__(self) -> None:
        self._busy = False
        self._events: queue.Queue[tuple[str, object]] = queue.Queue()
        self._notes_file = Path(__file__).resolve().parent / "account_notes.json"
        self._notes = self._load_notes()
        self._users: list[SteamUser] = []
        self._interactive_items: list[int | str] = []
        self._note_input_tags: dict[str, str] = {}
        self._table_container_tag = "accounts_table_container"
        self._status_tag = "status_text"
        self._error_window_tag = "error_modal"
        self._font_default: int | str | None = None
        self._font_zh: int | str | None = None
        self._dpi_scale = 1.0

        self._build_ui()
        self._set_status("Loading account list...")
        self._run_async(self._load_users)

    def _build_ui(self) -> None:
        _enable_windows_dpi_awareness()
        self._dpi_scale = _get_windows_dpi_scale()
        dpg.create_context()
        self._setup_fonts()
        dpg.create_viewport(title="Steam Switch", width=self._s(1120), height=self._s(700))

        with dpg.window(label="Steam Switch", tag="main_window"):
            dpg.add_text("Steam Accounts")
            dpg.add_spacer(height=self._s(2))

            with dpg.group(horizontal=True):
                refresh_btn = dpg.add_button(label="Refresh List", callback=lambda: self.on_refresh())
                login_new_btn = dpg.add_button(label="Login New", callback=lambda: self.on_login_new())
                self._interactive_items.extend([refresh_btn, login_new_btn])

            dpg.add_spacer(height=self._s(6))
            dpg.add_child_window(tag=self._table_container_tag, autosize_x=True, height=self._s(560), border=True)
            dpg.add_spacer(height=self._s(4))
            dpg.add_text("Ready", tag=self._status_tag)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)

    def _setup_fonts(self) -> None:
        consolas_candidates = [
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/consolab.ttf",
        ]
        zh_candidates = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]

        font_size = max(16, int(round(16 * self._dpi_scale)))
        with dpg.font_registry():
            for path in consolas_candidates:
                if Path(path).exists():
                    with dpg.font(path, font_size) as font:
                        pass
                    self._font_default = font
                    break

            for path in zh_candidates:
                if Path(path).exists():
                    with dpg.font(path, font_size) as font:
                        pass
                    self._font_zh = font
                    break

        if self._font_default is not None:
            dpg.bind_font(self._font_default)

    def _load_notes(self) -> dict[str, str]:
        if not self._notes_file.exists():
            return {}
        try:
            raw = json.loads(self._notes_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
        if not isinstance(raw, dict):
            return {}
        return {k: v for k, v in raw.items() if isinstance(k, str) and isinstance(v, str)}

    def _save_notes(self) -> None:
        self._notes_file.write_text(json.dumps(self._notes, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 1] + "..."

    @staticmethod
    def _contains_cjk(text: str) -> bool:
        return any("\u4e00" <= ch <= "\u9fff" for ch in text)

    def _s(self, value: int) -> int:
        return max(1, int(round(value * self._dpi_scale)))

    def _set_status(self, text: str) -> None:
        dpg.set_value(self._status_tag, text)
        if self._contains_cjk(text) and self._font_zh is not None and dpg.does_item_exist(self._status_tag):
            dpg.bind_item_font(self._status_tag, self._font_zh)
        elif self._font_default is not None and dpg.does_item_exist(self._status_tag):
            dpg.bind_item_font(self._status_tag, self._font_default)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        for item in self._interactive_items:
            if dpg.does_item_exist(item):
                if busy:
                    dpg.disable_item(item)
                else:
                    dpg.enable_item(item)

    def _load_users(self) -> None:
        users = list_users()
        self._events.put(("users", users))

    def _run_async(self, fn, *args: Any) -> None:
        if self._busy:
            return
        self._set_busy(True)

        def worker() -> None:
            try:
                fn(*args)
                self._events.put(("ok", None))
            except Exception as exc:  # noqa: BLE001
                self._events.put(("err", exc))

        threading.Thread(target=worker, daemon=True).start()

    def _op_login_new(self, mode: str) -> None:
        perform_login_new(mode, progress=lambda step: self._events.put(("status", f"LoginNew: {step}")))

    def _op_select(self, account: str, mode: str) -> None:
        perform_select_account(account, mode, progress=lambda step: self._events.put(("status", f"Switch({account}): {step}")))

    def on_refresh(self) -> None:
        self._set_status("Refreshing account list...")
        self._run_async(self._load_users)

    def on_login_new(self) -> None:
        self._set_status("Starting login_new...")
        self._run_async(self._op_login_new, "express")

    def _on_account_login(self, account: str, mode: str) -> None:
        self._set_status(f"Switching to {account} ({mode})...")
        self._run_async(self._op_select, account, mode)

    def _save_note_for_account(self, account: str) -> None:
        input_tag = self._note_input_tags.get(account)
        if not input_tag or not dpg.does_item_exist(input_tag):
            return
        note = str(dpg.get_value(input_tag)).strip()
        if note:
            self._notes[account] = note
        else:
            self._notes.pop(account, None)
        self._save_notes()
        self._set_status(f"Saved note for {account}")

    def _normalize_note_text(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)

    def _on_note_changed(self, account: str, value: Any) -> None:
        note = self._normalize_note_text(value).strip()
        if note:
            self._notes[account] = note
        else:
            self._notes.pop(account, None)
        self._save_notes()
        self._set_status(f"Auto-saved note for {account}")

    def _show_error(self, message: str) -> None:
        if dpg.does_item_exist(self._error_window_tag):
            dpg.delete_item(self._error_window_tag)
        with dpg.window(
            label="Steam Switch Error",
            tag=self._error_window_tag,
            modal=True,
            no_close=True,
            no_resize=True,
            width=560,
            height=180,
        ):
            dpg.add_text(message, wrap=520)
            dpg.add_spacer(height=10)
            dpg.add_button(label="OK", width=100, callback=lambda: dpg.delete_item(self._error_window_tag))

    def _replace_users(self, users: list[SteamUser]) -> None:
        self._users = users
        self._note_input_tags.clear()
        self._interactive_items = [item for item in self._interactive_items if dpg.does_item_exist(item)]
        if dpg.does_item_exist(self._table_container_tag):
            dpg.delete_item(self._table_container_tag, children_only=True)
        if not users:
            empty_text = dpg.add_text("No remembered accounts.", parent=self._table_container_tag)
            if self._font_default is not None:
                dpg.bind_item_font(empty_text, self._font_default)
            return

        for user in users:
            card = dpg.add_child_window(
                parent=self._table_container_tag,
                autosize_x=True,
                height=self._s(76),
                border=True,
            )
            with dpg.table(
                parent=card,
                header_row=False,
                policy=dpg.mvTable_SizingFixedFit,
                resizable=False,
                borders_innerV=False,
                borders_outerV=False,
                borders_innerH=False,
                borders_outerH=False,
                no_host_extendX=False,
            ):
                dpg.add_table_column(init_width_or_weight=self._s(105))
                dpg.add_table_column(init_width_or_weight=self._s(250))
                dpg.add_table_column(init_width_or_weight=self._s(95))
                dpg.add_table_column(init_width_or_weight=self._s(370))

                with dpg.table_row():
                    dpg.add_text("Account:")
                    recent = " *" if user.most_recent else ""
                    account_item = dpg.add_text(f"{self._truncate(user.account_name, 16)}{recent}")
                    dpg.add_text("Persona:")
                    persona_item = dpg.add_text(user.persona_name)
                    if self._contains_cjk(user.account_name) and self._font_zh is not None:
                        dpg.bind_item_font(account_item, self._font_zh)
                    if self._contains_cjk(user.persona_name) and self._font_zh is not None:
                        dpg.bind_item_font(persona_item, self._font_zh)

                with dpg.table_row():
                    dpg.add_text("Note:")
                    note_tag = f"note::{user.account_name}"
                    self._note_input_tags[user.account_name] = note_tag
                    note_input = dpg.add_input_text(
                        tag=note_tag,
                        default_value=self._notes.get(user.account_name, ""),
                        width=self._s(96),
                        callback=lambda _s, app_data, account=user.account_name: self._on_note_changed(account, app_data),
                    )
                    if self._font_zh is not None:
                        dpg.bind_item_font(note_input, self._font_zh)
                    self._interactive_items.append(note_input)
                    dpg.add_text("Actions:")
                    with dpg.group(horizontal=True):
                        express_btn = dpg.add_button(
                            label="Login Express",
                            width=self._s(170),
                            callback=lambda _s, _a, account=user.account_name: self._on_account_login(account, "express"),
                        )
                        offline_btn = dpg.add_button(
                            label="Login Offline",
                            width=self._s(170),
                            callback=lambda _s, _a, account=user.account_name: self._on_account_login(account, "offline"),
                        )
                    self._interactive_items.extend([express_btn, offline_btn])

    def _poll_events(self) -> None:
        while True:
            try:
                evt, payload = self._events.get_nowait()
            except queue.Empty:
                break
            if evt == "status":
                self._set_status(str(payload))
                continue
            if evt == "users":
                self._replace_users(payload)  # type: ignore[arg-type]
                continue
            if evt == "err":
                self._set_busy(False)
                self._set_status("Failed")
                self._show_error(str(payload))
                continue
            if evt == "ok":
                self._set_busy(False)
                self._set_status("Done")

    def run(self) -> int:
        while dpg.is_dearpygui_running():
            self._poll_events()
            dpg.render_dearpygui_frame()
        dpg.destroy_context()
        return 0


def main() -> int:
    gui = SteamSwitchGui()
    return gui.run()


if __name__ == "__main__":
    raise SystemExit(main())
