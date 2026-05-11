from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .switcher import (
    SteamSwitchError,
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

        self.mode_var = tk.StringVar(value="express")
        self.status_var = tk.StringVar(value="Ready")

        self._build_widgets()
        self._poll_events()
        self._run_async(self._load_users)

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(frame)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(top, text="Express", variable=self.mode_var, value="express").pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(top, text="Offline", variable=self.mode_var, value="offline").pack(side=tk.LEFT, padx=8)

        button_bar = ttk.Frame(frame)
        button_bar.pack(fill=tk.X, pady=(10, 6))

        self.btn_refresh = ttk.Button(button_bar, text="Refresh List", command=self.on_refresh)
        self.btn_refresh.pack(side=tk.LEFT)

        self.btn_login_new = ttk.Button(button_bar, text="Login New", command=self.on_login_new)
        self.btn_login_new.pack(side=tk.LEFT, padx=8)

        self.btn_select = ttk.Button(button_bar, text="Select Login", command=self.on_select)
        self.btn_select.pack(side=tk.LEFT, padx=8)

        cols = ("account", "persona", "sid", "recent")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        self.tree.heading("account", text="AccountName")
        self.tree.heading("persona", text="PersonaName")
        self.tree.heading("sid", text="SteamId64")
        self.tree.heading("recent", text="MostRecent")
        self.tree.column("account", width=170)
        self.tree.column("persona", width=210)
        self.tree.column("sid", width=240)
        self.tree.column("recent", width=90, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        status = ttk.Label(frame, textvariable=self.status_var, anchor=tk.W)
        status.pack(fill=tk.X, pady=(8, 0))

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        self.btn_refresh.configure(state=state)
        self.btn_login_new.configure(state=state)
        self.btn_select.configure(state=state)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _load_users(self) -> None:
        users = list_users()
        self._events.put(("users", users))

    def _selected_account(self) -> str:
        selected = self.tree.selection()
        if not selected:
            raise SteamSwitchError("Please select one account first.")
        values = self.tree.item(selected[0], "values")
        account = str(values[0]).strip() if values else ""
        if not account:
            raise SteamSwitchError("Selected row has empty account name.")
        return account

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
        self._run_async(self._op_login_new, self.mode_var.get())

    def on_select(self) -> None:
        try:
            account = self._selected_account()
        except SteamSwitchError as exc:
            messagebox.showerror("Select Login", str(exc))
            return
        self._set_status(f"Switching to {account}...")
        self._run_async(self._op_select, account, self.mode_var.get())

    def _replace_users(self, users) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        for user in users:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    user.account_name,
                    user.persona_name,
                    user.steam_id64,
                    "Yes" if user.most_recent else "No",
                ),
            )

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
