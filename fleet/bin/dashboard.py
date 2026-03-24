#!/usr/bin/env python3
"""
Jia Mu's Hall — Fleet Status Dashboard

Reads fleet state from files. No LLM, no network. Always accurate.

Usage:
    python fleet/bin/dashboard.py            # summary view
    python fleet/bin/dashboard.py --full     # full detail per active task
    python fleet/bin/dashboard.py T-001      # single task deep-dive
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
FLEET_DIR  = Path(__file__).resolve().parent.parent
REGISTRY   = FLEET_DIR / "registry" / "tasks.json"
TASKS_DIR  = FLEET_DIR / "tasks"

# ---------------------------------------------------------------------------
# ANSI colors
R   = "\033[0m"
B   = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GRN = "\033[32m"
YEL = "\033[33m"
CYN = "\033[36m"

STATE_STYLE = {
    "NEW":          CYN,
    "RUNNING":      GRN,
    "WAITING_USER": YEL + B,
    "BLOCKED":      RED + B,
    "SYNTHESIZING": CYN,
    "DONE":         DIM,
    "FAILED":       RED,
    "ARCHIVED":     DIM,
}

W = 68  # line width


# ---------------------------------------------------------------------------
# Primitives

def hr(ch="─", color=""):
    return f"{color}{ch * W}{R}"


def load_registry() -> dict:
    if not REGISTRY.exists():
        return {"tasks": [], "lastTaskId": 0}
    with open(REGISTRY) as f:
        return json.load(f)


def load_status(task_id: str) -> dict:
    p = TASKS_DIR / task_id / "STATUS.json"
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def load_file(task_id: str, name: str) -> str:
    p = TASKS_DIR / task_id / name
    return p.read_text() if p.exists() else ""


def state_tag(state: str) -> str:
    color = STATE_STYLE.get(state, "")
    return f"{color}[{state}]{R}"


def display_text(value: str | None, default: str = "—") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def status_blocker(status: dict) -> str:
    blockers = status.get("blockers", [])
    if blockers:
        return str(blockers[0]).strip()
    if status.get("waitingOnJiaMu") or status.get("waitingOnCaptain"):
        return "waiting on Jia Mu"
    return "none"


# ---------------------------------------------------------------------------
# Formatters

def fmt_task_brief(task: dict, status: dict) -> str:
    tid   = task.get("taskId", "?")
    state = task.get("state", "?")
    title = display_text(task.get("title"), "Untitled")
    pilot = display_text(task.get("pilotAgent") or task.get("pilot"))
    goal = display_text(status.get("currentGoal"), title)
    next_a = display_text(status.get("nextAction"), "none")
    blockers = display_text(status_blocker(status), "none")
    updated = display_text(task.get("updatedAt") or status.get("updatedAt"))

    lines = [f"  {B}## Task {tid}: {title}{R}"]
    lines.append(f"     State:    {state_tag(state)}")
    lines.append(f"     Pilot:    {pilot}")
    lines.append(f"     Goal:     {goal}")
    lines.append(f"     Next:     {next_a}")
    lines.append(f"     Blockers: {blockers}")
    lines.append(f"     Updated:  {updated}")
    return "\n".join(lines)


def fmt_task_full(task: dict, status: dict) -> str:
    brief = fmt_task_brief(task, status)
    tid   = task.get("taskId", "?")

    extras = []

    sailors = status.get("workerResults", [])
    if sailors:
        ww = ", ".join(
            f"{w.get('agentId','?')}({w.get('status','?')})" for w in sailors
        )
        extras.append(f"     Sailors:  {ww}")

    last = status.get("lastConclusion", "")
    if last:
        extras.append(f"     Last:     {last[:80]}")

    decisions = load_file(tid, "DECISIONS.md")
    if decisions:
        last_decision = [l for l in decisions.strip().splitlines() if l.strip()]
        if last_decision:
            extras.append(f"     Decision: {last_decision[-1][:70]}")

    return brief + ("\n" + "\n".join(extras) if extras else "")


# ---------------------------------------------------------------------------
# Views

def view_single(task_id: str, tasks: list):
    task = next((t for t in tasks if t["taskId"] == task_id.upper()), None)
    if not task:
        print(f"\n  Task {task_id} not found.\n")
        return

    status   = load_status(task_id.upper())
    task_md  = load_file(task_id.upper(), "TASK.md")
    handoff  = load_file(task_id.upper(), "HANDOFF.md")
    plan     = load_file(task_id.upper(), "PLAN.md")

    print(f"\n{hr('═', B)}")
    print(f"  {B}TASK DETAIL: {task_id.upper()}{R}")
    print(hr("═", B))
    print(fmt_task_full(task, status))

    if task_md:
        print(f"\n{hr('─', DIM)}  {DIM}TASK.md (excerpt){R}")
        print(DIM + "\n".join(task_md.splitlines()[:20]) + R)

    if handoff:
        print(f"\n{hr('─', DIM)}  {DIM}HANDOFF.md (recovery snapshot){R}")
        print(DIM + "\n".join(handoff.splitlines()[:30]) + R)

    print()


def view_summary(tasks: list, full: bool):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    active_states  = {"NEW", "RUNNING", "WAITING_USER", "BLOCKED", "SYNTHESIZING"}
    active   = [t for t in tasks if t.get("state") in active_states]
    waiting  = [t for t in active if t.get("state") == "WAITING_USER"]
    blocked  = [t for t in active if t.get("state") == "BLOCKED"]
    running  = [t for t in active if t.get("state") not in {"WAITING_USER", "BLOCKED"}]
    done     = [t for t in tasks  if t.get("state") in {"DONE", "FAILED"}]

    pilot_ids = {t.get("pilotAgent") for t in active if t.get("pilotAgent")}

    # ── Header ────────────────────────────────────────────────
    print(f"\n{hr('═', B)}")
    print(f"  {B}LIQUID FLEET — JIA MU'S HALL{R}"
          f"{'':>20}{DIM}{now}{R}")
    print(hr("═", B))
    print(f"  Active Pilots:  {len(pilot_ids)} / 3   "
          f"Active Tasks: {len(active)}   "
          f"Completed: {len(done)}   "
          f"Total: {len(tasks)}")

    fmt = fmt_task_full if full else fmt_task_brief

    # ── Waiting on Jia Mu ─────────────────────────────────────
    if waiting:
        print(f"\n{hr('─', YEL + B)}")
        print(f"  {YEL}{B}WAITING ON YOU  ({len(waiting)}){R}")
        print(hr("─", YEL + B))
        for t in waiting:
            print(fmt(t, load_status(t["taskId"])))
            print()

    # ── Running ───────────────────────────────────────────────
    if running:
        print(f"\n{hr('─', GRN)}")
        print(f"  {B}IN PROGRESS  ({len(running)}){R}")
        print(hr("─", GRN))
        for t in running:
            print(fmt(t, load_status(t["taskId"])))
            print()

    # ── Blocked ───────────────────────────────────────────────
    if blocked:
        print(f"\n{hr('─', RED)}")
        print(f"  {RED}{B}BLOCKED  ({len(blocked)}){R}")
        print(hr("─", RED))
        for t in blocked:
            print(fmt_task_brief(t, load_status(t["taskId"])))
            print()

    if not active:
        print(f"\n  {DIM}No active tasks. Tell Wang Xifeng to start one.{R}")

    # ── Operations Panel ─────────────────────────────────────
    print(hr("─", DIM))
    print(f"  {B}OPERATIONS PANEL{R}  {DIM}— fixed command reference{R}")
    print(hr("─", DIM))
    print(f"  {B}View Commands{R}")
    print(f"  {DIM}{'Refresh dashboard':<22}{R}  python fleet/bin/dashboard.py")
    print(f"  {DIM}{'Task detail':<22}{R}  python fleet/bin/dashboard.py T-001")
    print(f"  {DIM}{'Full detail view':<22}{R}  python fleet/bin/dashboard.py --full")
    print()
    print(f"  {B}Task Commands{R}")
    print(f"  {DIM}{'Start new task':<22}{R}  \"new task: <what you want done>\"")
    print(f"  {DIM}{'Switch focus':<22}{R}  \"switch to T-001\"")
    print(f"  {DIM}{'Continue task':<22}{R}  \"continue T-001: <your reply>\"")
    print(f"  {DIM}{'Pause task':<22}{R}  \"pause T-001\"")
    print(f"  {DIM}{'End task':<22}{R}  \"end T-001\"")
    print(f"  {DIM}{'Status report':<22}{R}  \"report all tasks\"")
    print(f"  {DIM}{'Show blockers':<22}{R}  \"show blocked tasks\"")
    print(hr("─", DIM))
    print()


# ---------------------------------------------------------------------------

def main():
    args    = sys.argv[1:]
    full    = "--full" in args
    args    = [a for a in args if a != "--full"]
    target  = args[0] if args else None

    registry = load_registry()
    tasks    = registry.get("tasks", [])

    if target:
        view_single(target, tasks)
    else:
        view_summary(tasks, full)


if __name__ == "__main__":
    main()
