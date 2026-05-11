from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

from .switcher import (
    SteamSwitchError,
    SteamUser,
    list_users,
    perform_login_new,
    perform_select_account,
)


class SteamSwitchGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Steam Switch")
        self.root.geometry("760x460")

        self._busy = False
        self._events: queue.Queue[tuple[str, object]] = queue.Queue()
        self._action_buttons: list[ttk.Button] = []
        self._note_controls: list[tk.Widget] = []
        self._users: list[SteamUser] = []
        self._notes_file = Path(__file__).resolve().parent / "account_notes.json"
        self._notes = self._load_notes()

        self.status_var = tk.StringVar(value="Ready")

        self._build_widgets()
        self._poll_events()
        self._run_async(self._load_users)

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(frame)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Steam Accounts").pack(side=tk.LEFT)

        button_bar = ttk.Frame(frame)
        button_bar.pack(fill=tk.X, pady=(10, 6))

        self.btn_refresh = ttk.Button(button_bar, text="Refresh List", command=self.on_refresh)
        self.btn_refresh.pack(side=tk.LEFT)

        self.btn_login_new = ttk.Button(button_bar, text="Login New", command=self.on_login_new)
        self.btn_login_new.pack(side=tk.LEFT, padx=8)

        account_host = ttk.Frame(frame)
        account_host.pack(fill=tk.BOTH, expand=True)
        self.account_canvas = tk.Canvas(account_host, highlightthickness=0)
        self.account_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.account_scroll = ttk.Scrollbar(account_host, orient=tk.VERTICAL, command=self.account_canvas.yview)
        self.account_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.account_canvas.configure(yscrollcommand=self.account_scroll.set)
        self.account_rows = ttk.Frame(self.account_canvas)
        self.account_canvas_window = self.account_canvas.create_window((0, 0), window=self.account_rows, anchor="nw")
        self.account_rows.bind(
            "<Configure>",
            lambda _evt: self.account_canvas.configure(scrollregion=self.account_canvas.bbox("all")),
        )
        self.account_canvas.bind(
            "<Configure>",
            lambda evt: self.account_canvas.itemconfigure(self.account_canvas_window, width=evt.width),
        )

        status = ttk.Label(frame, textvariable=self.status_var, anchor=tk.W)
        status.pack(fill=tk.X, pady=(8, 0))

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        self.btn_refresh.configure(state=state)
        self.btn_login_new.configure(state=state)
        for btn in self._action_buttons:
            btn.configure(state=state)
        for widget in self._note_controls:
            widget.configure(state=state)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _load_notes(self) -> dict[str, str]:
        if not self._notes_file.exists():
            return {}
        try:
            raw = json.loads(self._notes_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
        if not isinstance(raw, dict):
            return {}
        notes: dict[str, str] = {}
        for k, v in raw.items():
            if isinstance(k, str) and isinstance(v, str):
                notes[k] = v
        return notes

    def _save_notes(self) -> None:
        self._notes_file.write_text(
            json.dumps(self._notes, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_users(self) -> None:
        users = list_users()
        self._events.put(("users", users))

    def _run_async(self, fn, *args) -> None:
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

    def _save_note_for_account(self, account: str, note_var: tk.StringVar) -> None:
        note = note_var.get().strip()
        if note:
            self._notes[account] = note
        else:
            self._notes.pop(account, None)
        self._save_notes()
        self._set_status(f"Saved note for {account}")

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 1] + "…"

    def _replace_users(self, users: list[SteamUser]) -> None:
        self._users = users
        self._action_buttons.clear()
        self._note_controls.clear()
        for child in self.account_rows.winfo_children():
            child.destroy()

        # Column headers + fixed grid make all rows aligned.
        headers = ("Account", "Persona", "Note", "Actions")
        for col, text in enumerate(headers):
            ttk.Label(self.account_rows, text=text).grid(row=0, column=col, sticky="w", padx=6, pady=(2, 4))
        ttk.Separator(self.account_rows, orient=tk.HORIZONTAL).grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=4,
            pady=(0, 4),
        )
        self.account_rows.grid_columnconfigure(0, weight=1, minsize=150)
        self.account_rows.grid_columnconfigure(1, weight=1, minsize=140)
        self.account_rows.grid_columnconfigure(2, weight=0, minsize=90)
        self.account_rows.grid_columnconfigure(3, weight=0, minsize=280)

        if not users:
            ttk.Label(self.account_rows, text="No remembered accounts.").grid(
                row=2, column=0, columnspan=4, sticky="w", padx=6, pady=8
            )
            return

        for idx, user in enumerate(users, start=2):
            recent = " *" if user.most_recent else ""
            account_text = self._truncate(user.account_name, 16) + recent
            ttk.Label(self.account_rows, text=account_text).grid(
                row=idx, column=0, sticky="w", padx=6, pady=3
            )
            ttk.Label(self.account_rows, text=user.persona_name).grid(
                row=idx, column=1, sticky="w", padx=6, pady=3
            )

            note_var = tk.StringVar(value=self._notes.get(user.account_name, ""))
            note_entry = ttk.Entry(self.account_rows, textvariable=note_var, width=8)
            note_entry.grid(row=idx, column=2, sticky="w", padx=6, pady=3)
            self._note_controls.append(note_entry)

            actions = ttk.Frame(self.account_rows)
            actions.grid(row=idx, column=3, sticky="w", padx=6, pady=3)

            btn_express = ttk.Button(
                actions,
                text="Login Express",
                command=lambda account=user.account_name: self._on_account_login(account, "express"),
            )
            btn_express.pack(side=tk.LEFT)
            self._action_buttons.append(btn_express)

            btn_offline = ttk.Button(
                actions,
                text="Login Offline",
                command=lambda account=user.account_name: self._on_account_login(account, "offline"),
            )
            btn_offline.pack(side=tk.LEFT, padx=(8, 0))
            self._action_buttons.append(btn_offline)

            note_btn = ttk.Button(
                actions,
                text="Save Note",
                command=lambda account=user.account_name, var=note_var: self._save_note_for_account(account, var),
            )
            note_btn.pack(side=tk.LEFT, padx=(8, 0))
            self._note_controls.append(note_btn)

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
                self._replace_users(payload)
                continue
            if evt == "err":
                self._set_busy(False)
                self._set_status("Failed")
                messagebox.showerror("Steam Switch", str(payload))
                continue
            if evt == "ok":
                self._set_busy(False)
                self._set_status("Done")
        self.root.after(100, self._poll_events)


def main() -> int:
    root = tk.Tk()
    SteamSwitchGui(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
