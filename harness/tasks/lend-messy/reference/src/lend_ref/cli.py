"""Reference `lend`. Where the spec contradicts itself it takes one side (answer key, §resolutions);
the hidden tests never depend on which side."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
from pathlib import Path

STORE = Path(".lend")
STATE = STORE / "state.json"
PERIOD = {"hand": 14, "garden": 14, "power": 7}
LIMIT = 3
MAX_RENEWALS = 2
FEE_PER_DAY, FEE_CAP = 50, 1000


class Fail(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


def today() -> dt.date:
    raw = os.environ.get("LEND_NOW")
    return dt.date.fromisoformat(raw[:10]) if raw else dt.date.today()


def load() -> dict:
    if not STATE.exists():
        raise Fail(4, "no .lend/ store here — run `lend init`")
    return json.loads(STATE.read_text(encoding="utf-8"))


def save(state: dict) -> None:
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    tmp.replace(STATE)


def due_of(loan: dict) -> dt.date:
    return dt.date.fromisoformat(loan["due"])


def days_overdue(loan: dict, on: dt.date) -> int:
    return max(0, (on - due_of(loan)).days)


def blocked(state: dict, member: str, on: dt.date) -> bool:
    return any(l["member"] == member and days_overdue(l, on) > 0 for l in state["loans"].values())


def cmd_init(_: argparse.Namespace) -> None:
    if STORE.exists():
        raise Fail(2, ".lend/ already exists")
    STORE.mkdir()
    save({"members": {}, "items": {}, "loans": {}})


def cmd_member_add(a: argparse.Namespace) -> None:
    state = load()
    if not a.email:
        raise Fail(2, "a member must have an email address")
    if a.id in state["members"]:
        raise Fail(2, f"member {a.id} exists")
    state["members"][a.id] = {"name": a.name, "email": a.email, "fees_cents": 0}
    save(state)


def cmd_item_add(a: argparse.Namespace) -> None:
    state = load()
    if a.category not in PERIOD:
        raise Fail(2, f"unknown category {a.category!r}")
    if a.id in state["items"]:
        raise Fail(2, f"item {a.id} exists")
    state["items"][a.id] = {"title": a.title, "category": a.category}
    save(state)


def cmd_checkout(a: argparse.Namespace) -> None:
    state, on = load(), today()
    if a.item not in state["items"] or a.member not in state["members"]:
        raise Fail(2, "unknown item or member")
    if a.item in state["loans"]:
        raise Fail(3, f"{a.item} is already on loan")
    if blocked(state, a.member, on):
        raise Fail(3, f"{a.member} has an overdue loan")
    if sum(l["member"] == a.member for l in state["loans"].values()) >= LIMIT:
        raise Fail(3, f"{a.member} is at the borrowing limit ({LIMIT})")
    period = PERIOD[state["items"][a.item]["category"]]
    due = on + dt.timedelta(days=period)
    state["loans"][a.item] = {"member": a.member, "due": due.isoformat(), "renewals": 0}
    save(state)
    print(due.isoformat())


def cmd_renew(a: argparse.Namespace) -> None:
    state, on = load(), today()
    loan = state["loans"].get(a.item)
    if loan is None:
        raise Fail(2, f"{a.item} is not on loan")
    if days_overdue(loan, on) > 0:
        raise Fail(3, "an overdue loan cannot be renewed")
    if loan["renewals"] >= MAX_RENEWALS:
        raise Fail(3, "at most two renewals")
    period = PERIOD[state["items"][a.item]["category"]]
    loan["due"] = (due_of(loan) + dt.timedelta(days=period)).isoformat()
    loan["renewals"] += 1
    save(state)
    print(loan["due"])


def cmd_return(a: argparse.Namespace) -> None:
    state, on = load(), today()
    loan = state["loans"].pop(a.item, None)
    if loan is None:
        raise Fail(2, f"{a.item} is not on loan")
    fee = min(FEE_CAP, FEE_PER_DAY * days_overdue(loan, on))
    state["members"][loan["member"]]["fees_cents"] += fee
    save(state)


def cmd_status(a: argparse.Namespace) -> None:
    state, on = load(), today()
    loans = [{"item": i, "member": l["member"], "due": l["due"], "renewals": l["renewals"],
              "overdue": days_overdue(l, on) > 0, "days_overdue": days_overdue(l, on)}
             for i, l in sorted(state["loans"].items())]
    members = [{"id": m, "name": v["name"],
                "loans": sum(l["member"] == m for l in state["loans"].values()),
                "fees_cents": v["fees_cents"], "blocked": blocked(state, m, on)}
               for m, v in sorted(state["members"].items())]
    available = sorted(i for i in state["items"] if i not in state["loans"])
    print(json.dumps({"today": on.isoformat(), "loans": loans, "members": members,
                      "available": available}))


def cmd_report(a: argparse.Namespace) -> None:
    state, on = load(), today()
    rows = [(days_overdue(l, on), i, l) for i, l in state["loans"].items() if days_overdue(l, on) > 0]
    rows.sort(key=lambda r: (-r[0], r[1]))
    with open(a.out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["item", "title", "member", "due", "days_overdue"])
        for days, item, loan in rows:
            writer.writerow([item, state["items"][item]["title"], loan["member"], loan["due"], days])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="lend")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    member = sub.add_parser("member").add_subparsers(dest="action", required=True)
    m = member.add_parser("add")
    m.add_argument("id"); m.add_argument("--name", required=True); m.add_argument("--email")
    m.set_defaults(fn=cmd_member_add)
    item = sub.add_parser("item").add_subparsers(dest="action", required=True)
    i = item.add_parser("add")
    i.add_argument("id"); i.add_argument("--title", required=True); i.add_argument("--category", default="hand")
    i.set_defaults(fn=cmd_item_add)
    c = sub.add_parser("checkout"); c.add_argument("item"); c.add_argument("member"); c.set_defaults(fn=cmd_checkout)
    for name, fn in (("renew", cmd_renew), ("return", cmd_return)):
        s = sub.add_parser(name); s.add_argument("item"); s.set_defaults(fn=fn)
    s = sub.add_parser("status"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_status)
    r = sub.add_parser("report"); r.add_argument("--out", required=True); r.set_defaults(fn=cmd_report)
    try:
        args = p.parse_args(argv)
    except SystemExit as exc:
        return 1 if exc.code else 0
    try:
        args.fn(args)
    except Fail as fail:
        print(f"lend: {fail}", file=sys.stderr)
        return fail.code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
