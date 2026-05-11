from __future__ import annotations

import argparse
import sys

from .switcher import SteamSwitchError, list_users, login_new, select_account


def _add_common_mode(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--mode",
        choices=("offline", "express"),
        default="express",
        help="offline: start steam with -offline; express: normal login",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="steam-switch", description="Windows Steam account switch CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List remembered Steam accounts")

    p_login_new = sub.add_parser("login_new", help="Start new account login flow")
    _add_common_mode(p_login_new)

    p_select = sub.add_parser("select", help="Select one remembered account and start Steam")
    p_select.add_argument("--account", help="AccountName from Steam loginusers.vdf")
    p_select.add_argument("--index", type=int, help="1-based index from list command")
    _add_common_mode(p_select)

    return parser


def _handle_list() -> int:
    users = list_users()
    for idx, user in enumerate(users, start=1):
        marker = "*" if user.most_recent else " "
        print(f"{idx:>2}. [{marker}] {user.account_name} ({user.persona_name}) sid={user.steam_id64}")
    return 0


def _handle_login_new(mode: str) -> int:
    login_new(mode)
    print(f"OK: login_new mode={mode}")
    return 0


def _pick_account(account: str | None, index: int | None) -> str:
    users = list_users()
    if account:
        return account
    if index is not None:
        if index < 1 or index > len(users):
            raise SteamSwitchError(f"Index out of range: {index}")
        return users[index - 1].account_name
    for idx, user in enumerate(users, start=1):
        marker = "*" if user.most_recent else " "
        print(f"{idx:>2}. [{marker}] {user.account_name} ({user.persona_name})")
    raw = input("Choose account index: ").strip()
    if not raw.isdigit():
        raise SteamSwitchError("Invalid index input.")
    picked = int(raw)
    if picked < 1 or picked > len(users):
        raise SteamSwitchError(f"Index out of range: {picked}")
    return users[picked - 1].account_name


def _handle_select(account: str | None, index: int | None, mode: str) -> int:
    selected_account = _pick_account(account, index)
    user = select_account(selected_account, mode)
    print(f"OK: selected {user.account_name} mode={mode}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "list":
            return _handle_list()
        if args.cmd == "login_new":
            return _handle_login_new(args.mode)
        if args.cmd == "select":
            return _handle_select(args.account, args.index, args.mode)
        raise SteamSwitchError(f"Unsupported command: {args.cmd}")
    except SteamSwitchError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
