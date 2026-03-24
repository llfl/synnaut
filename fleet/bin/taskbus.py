#!/usr/bin/env python3
"""
Liquid Fleet 3.0 — Task Bus

CLI tool for the Chief Mate to manage the task registry.
Operates on the canonical fleet/ directory under the OpenClaw config root.
This fleet/ directory is shared runtime state, not a workspace-local folder.

Usage:
    python taskbus.py create  "Build auth module" --pilot pilot-build --priority high
    python taskbus.py list    [--state RUNNING] [--blocked]
    python taskbus.py show    T-001
    python taskbus.py switch  T-001
    python taskbus.py update  T-001 --state RUNNING --session-id abc123
    python taskbus.py archive T-001
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────

FLEET_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = FLEET_DIR / "registry" / "tasks.json"
ACTIVE_PATH = FLEET_DIR / "registry" / "active.md"
TASKS_DIR = FLEET_DIR / "tasks"
TEMPLATE_DIR = TASKS_DIR / ".template"

VALID_STATES = [
    "NEW", "RUNNING", "WAITING_USER", "BLOCKED",
    "SYNTHESIZING", "DONE", "FAILED", "ARCHIVED",
]

VALID_PILOTS = [
    "pilot-general", "pilot-research", "pilot-build",
]


# ── Registry I/O ──────────────────────────────────────────────────

def load_registry() -> dict:
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return {"meta": {"version": "1.0", "lastTaskId": 0, "prefix": "T"}, "tasks": []}


def save_registry(reg: dict):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write("\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def task_id(num: int, prefix: str = "T") -> str:
    return f"{prefix}-{num:03d}"


# ── Status I/O ────────────────────────────────────────────────────

def load_status(tid: str) -> dict:
    path = TASKS_DIR / tid / "STATUS.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_status(tid: str, status: dict):
    path = TASKS_DIR / tid / "STATUS.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ── Active Summary ────────────────────────────────────────────────

def refresh_active(reg: dict):
    active = [t for t in reg["tasks"] if t["state"] not in ("DONE", "FAILED", "ARCHIVED")]
    waiting = [t for t in active if t["state"] == "WAITING_USER"]
    blocked = [t for t in active if t["state"] == "BLOCKED"]
    running = [t for t in active if t["state"] not in ("WAITING_USER", "BLOCKED")]
    lines = ["# Active Tasks\n"]
    lines.append(f"Active: {len(active)}")
    lines.append(f"Running: {len(running)}")
    lines.append(f"Waiting: {len(waiting)}")
    lines.append(f"Blocked: {len(blocked)}")
    lines.append("")
    if not active:
        lines.append("No active tasks.\n")
    else:
        for t in active:
            status = load_status(t["taskId"])
            goal = status.get("currentGoal") or t.get("title") or "—"
            next_action = status.get("nextAction") or "none"
            blockers = status.get("blockers", [])
            blocker_text = blockers[0] if blockers else ("waiting on Captain" if status.get("waitingOnCaptain") else "none")
            lines.append(f"## Task {t['taskId']}: {t.get('title', 'Untitled')}")
            lines.append(f"State: {t.get('state', '—')}")
            lines.append(f"Pilot: {t.get('pilot', '—')}")
            lines.append(f"Goal: {goal}")
            lines.append(f"Next: {next_action}")
            lines.append(f"Blockers: {blocker_text}")
            lines.append(f"Updated: {t.get('updatedAt', '—')}")
            lines.append("")
        lines.append("")
    ACTIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ACTIVE_PATH, "w") as f:
        f.write("\n".join(lines))


# ── Task Card Fields ──────────────────────────────────────────────

TASK_CARD_DEFAULTS = {
    "goal": "",
    "scope_in": "",
    "scope_out": "",
    "deadline": "No explicit deadline",
    "context": "",
    "output_format": "Structured report (Goal/Findings/Risks/Options/Decision/Next Step)",
    "sailors": "yes",
    "max_sailors": "2",
    "worker_tags": "worker-drive / worker-guard / worker-sense",
    "report_granularity": "brief",
    "decision_style": "autonomous",
    "captain_notes": "",
}


# ── Scaffold Task Dir ─────────────────────────────────────────────

def scaffold_task(tid: str, title: str, pilot: str, priority: str,
                  card: dict | None = None):
    task_dir = TASKS_DIR / tid
    if task_dir.exists():
        print(f"  ERROR: {task_dir} already exists")
        sys.exit(1)

    task_dir.mkdir(parents=True)
    ts = now_iso()
    card = card or {}

    # Build replacement map: template placeholders → actual values
    goal = card.get("goal") or title
    context = card.get("context", "") or "(none provided)"

    replacements = {
        "{TASK_ID}": tid,
        "{TIMESTAMP}": ts,
        "{PILOT_ID}": pilot,
        "{PRIORITY}": priority,
        "{Task objective in one sentence}": goal,
        "{what to do}": card.get("scope_in", "") or "(to be defined by Pilot)",
        "{what NOT to do}": card.get("scope_out", "") or "(to be defined by Pilot)",
        "{When is this task considered overdue? Time-based or condition-based.}":
            card.get("deadline", TASK_CARD_DEFAULTS["deadline"]),
        "{Known information, references, constraints}": context,
        "{criterion 1}": goal,
        "{criterion 2}": "Pilot confirms acceptance criteria met",
        "{Expected deliverable format}":
            card.get("output_format", TASK_CARD_DEFAULTS["output_format"]),
        "{yes / no}": card.get("sailors", TASK_CARD_DEFAULTS["sailors"]),
        "{number}": card.get("max_sailors", TASK_CARD_DEFAULTS["max_sailors"]),
        "{#动力与开拓 / #结构与风控 / #感知与策略}":
            card.get("worker_tags", TASK_CARD_DEFAULTS["worker_tags"]),
        "{brief / detailed / on-demand}":
            card.get("report_granularity", TASK_CARD_DEFAULTS["report_granularity"]),
        "{autonomous / confirm-first / present-options}":
            card.get("decision_style", TASK_CARD_DEFAULTS["decision_style"]),
        "{any style preferences from captain-preferences.md}":
            card.get("captain_notes", "") or "(see captain-preferences.md)",
        "{Context provided in the Task Card}": context,
        "{Information collected during execution}": "(pending)",
        "(initialized from Task Card)": goal,
    }

    for tmpl in sorted(TEMPLATE_DIR.iterdir()):
        if tmpl.name == ".DS_Store":
            continue
        dst = task_dir / tmpl.name
        if tmpl.suffix == ".json":
            with open(tmpl) as f:
                data = json.load(f)
            data["taskId"] = tid
            data["title"] = title
            data["pilot"] = pilot
            data["pilotAgent"] = pilot
            data["state"] = "NEW"
            data["createdAt"] = ts
            data["updatedAt"] = ts
            data["currentGoal"] = card.get("goal") or title
            with open(dst, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
        else:
            content = tmpl.read_text()
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            dst.write_text(content)


# ── Commands ──────────────────────────────────────────────────────

def cmd_create(args):
    if len(args) < 1:
        print("Usage: taskbus.py create <title> [--pilot X] [--priority X] [--goal X] [--scope-in X] [--scope-out X] [--deadline X] [--context X] [--output-format X] [--sailors yes|no] [--max-sailors N] [--worker-tags X] [--report-granularity X] [--decision-style X] [--captain-notes X]")
        sys.exit(1)

    title = args[0]
    pilot = "pilot-general"
    priority = "medium"
    card = {}

    i = 1
    while i < len(args):
        key = args[i]
        val = args[i + 1] if i + 1 < len(args) else None
        if key == "--pilot" and val:
            pilot = val
            i += 2
        elif key == "--priority" and val:
            priority = val
            i += 2
        elif key == "--goal" and val:
            card["goal"] = val
            i += 2
        elif key == "--scope-in" and val:
            card["scope_in"] = val
            i += 2
        elif key == "--scope-out" and val:
            card["scope_out"] = val
            i += 2
        elif key == "--deadline" and val:
            card["deadline"] = val
            i += 2
        elif key == "--context" and val:
            card["context"] = val
            i += 2
        elif key == "--output-format" and val:
            card["output_format"] = val
            i += 2
        elif key == "--sailors" and val:
            card["sailors"] = val
            i += 2
        elif key == "--max-sailors" and val:
            card["max_sailors"] = val
            i += 2
        elif key == "--worker-tags" and val:
            card["worker_tags"] = val
            i += 2
        elif key == "--report-granularity" and val:
            card["report_granularity"] = val
            i += 2
        elif key == "--decision-style" and val:
            card["decision_style"] = val
            i += 2
        elif key == "--captain-notes" and val:
            card["captain_notes"] = val
            i += 2
        else:
            i += 1

    if pilot not in VALID_PILOTS:
        print(f"  ERROR: unknown pilot '{pilot}'. Valid: {', '.join(VALID_PILOTS)}")
        sys.exit(1)

    reg = load_registry()
    num = reg["meta"]["lastTaskId"] + 1
    reg["meta"]["lastTaskId"] = num
    tid = task_id(num, reg["meta"]["prefix"])

    entry = {
        "taskId": tid,
        "title": title,
        "state": "NEW",
        "pilot": pilot,
        "priority": priority,
        "sessionId": None,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    reg["tasks"].append(entry)

    scaffold_task(tid, title, pilot, priority, card)
    save_registry(reg)
    refresh_active(reg)

    print(f"  Created {tid}: {title}")
    print(f"  Pilot:    {pilot}")
    print(f"  Priority: {priority}")
    print(f"  Files:    {TASKS_DIR / tid}/")


def cmd_list(args):
    reg = load_registry()
    tasks = reg["tasks"]

    # Filters
    state_filter = None
    blocked_only = False
    i = 0
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            state_filter = args[i + 1].upper()
            i += 2
        elif args[i] == "--blocked":
            blocked_only = True
            i += 1
        else:
            i += 1

    if state_filter:
        tasks = [t for t in tasks if t["state"] == state_filter]
    if blocked_only:
        tasks = [t for t in tasks if t["state"] == "BLOCKED"]

    if not tasks:
        print("  No tasks found.")
        return

    print(f"  {'ID':<8} {'State':<14} {'Pilot':<16} {'Title'}")
    print(f"  {'─'*8} {'─'*14} {'─'*16} {'─'*30}")
    for t in tasks:
        print(f"  {t['taskId']:<8} {t['state']:<14} {t.get('pilot', '—'):<16} {t['title']}")


def cmd_show(args):
    if not args:
        print("Usage: taskbus.py show <task-id>")
        sys.exit(1)

    tid = args[0].upper()
    reg = load_registry()
    entry = next((t for t in reg["tasks"] if t["taskId"] == tid), None)

    if not entry:
        print(f"  ERROR: task {tid} not found")
        sys.exit(1)

    status = load_status(tid)

    print(f"  Task:       {entry['taskId']}")
    print(f"  Title:      {entry['title']}")
    print(f"  State:      {entry['state']}")
    print(f"  Pilot:      {entry.get('pilot', '—')}")
    print(f"  Priority:   {entry.get('priority', '—')}")
    print(f"  Session:    {entry.get('sessionId') or '—'}")
    print(f"  Created:    {entry.get('createdAt', '—')}")
    print(f"  Updated:    {entry.get('updatedAt', '—')}")

    if status.get("currentGoal"):
        print(f"  Goal:       {status['currentGoal']}")
    if status.get("nextAction"):
        print(f"  Next:       {status['nextAction']}")
    if status.get("blockers"):
        print(f"  Blockers:   {', '.join(status['blockers'])}")
    if status.get("threadId"):
        print(f"  Thread:     {status['threadId']}")
    print(f"  Focus:      {status.get('focusMode', 'soft')}")


def cmd_switch(args):
    if not args:
        print("Usage: taskbus.py switch <task-id>")
        sys.exit(1)

    tid = args[0].upper()
    reg = load_registry()
    entry = next((t for t in reg["tasks"] if t["taskId"] == tid), None)

    if not entry:
        print(f"  ERROR: task {tid} not found")
        sys.exit(1)

    if entry["state"] in ("DONE", "FAILED", "ARCHIVED"):
        print(f"  ERROR: task {tid} is {entry['state']} — cannot switch to it")
        sys.exit(1)

    status = load_status(tid)

    # Record switch event
    switch_entry = {"timestamp": now_iso(), "action": "focus"}
    history = status.get("switchHistory", [])
    history.append(switch_entry)
    status["switchHistory"] = history
    save_status(tid, status)

    print(f"  Switched to {tid}: {entry['title']}")
    print(f"  State:      {entry['state']}")
    print(f"  Session:    {entry.get('sessionId') or '—'}")
    if status.get("currentGoal"):
        print(f"  Goal:       {status['currentGoal']}")
    if status.get("nextAction"):
        print(f"  Next:       {status['nextAction']}")
    if status.get("waitingOnCaptain"):
        print(f"  ⚠ Waiting on Captain input")

    # Check if session is alive (placeholder — real check depends on OpenClaw API)
    if not entry.get("sessionId"):
        handoff = TASKS_DIR / tid / "HANDOFF.md"
        if handoff.exists():
            print(f"  Session expired — HANDOFF.md available for recovery")
        else:
            print(f"  Session expired — no handoff data")


def cmd_update(args):
    if not args:
        print("Usage: taskbus.py update <task-id> [--state X] [--session-id X] [--thread-id X] [--goal X] [--next X] [--blocker X]")
        sys.exit(1)

    tid = args[0].upper()
    reg = load_registry()
    entry = next((t for t in reg["tasks"] if t["taskId"] == tid), None)

    if not entry:
        print(f"  ERROR: task {tid} not found")
        sys.exit(1)

    status = load_status(tid)
    ts = now_iso()

    i = 1
    while i < len(args):
        key, val = args[i], args[i + 1] if i + 1 < len(args) else None
        if key == "--state" and val:
            val = val.upper()
            if val not in VALID_STATES:
                print(f"  ERROR: invalid state '{val}'. Valid: {', '.join(VALID_STATES)}")
                sys.exit(1)
            entry["state"] = val
            status["state"] = val
            i += 2
        elif key == "--session-id" and val:
            entry["sessionId"] = val
            status["sessionId"] = val
            i += 2
        elif key == "--thread-id" and val:
            status["threadId"] = val
            status["focusMode"] = "thread"
            i += 2
        elif key == "--goal" and val:
            status["currentGoal"] = val
            i += 2
        elif key == "--next" and val:
            status["nextAction"] = val
            i += 2
        elif key == "--blocker" and val:
            status.setdefault("blockers", []).append(val)
            i += 2
        elif key == "--waiting":
            status["waitingOnCaptain"] = True
            i += 1
        elif key == "--no-waiting":
            status["waitingOnCaptain"] = False
            i += 1
        else:
            i += 1

    entry["updatedAt"] = ts
    status["updatedAt"] = ts

    save_status(tid, status)
    save_registry(reg)
    refresh_active(reg)

    print(f"  Updated {tid}: state={entry['state']}")


def cmd_archive(args):
    if not args:
        print("Usage: taskbus.py archive <task-id>")
        sys.exit(1)

    tid = args[0].upper()
    reg = load_registry()
    entry = next((t for t in reg["tasks"] if t["taskId"] == tid), None)

    if not entry:
        print(f"  ERROR: task {tid} not found")
        sys.exit(1)

    entry["state"] = "ARCHIVED"
    entry["updatedAt"] = now_iso()

    status = load_status(tid)
    status["state"] = "ARCHIVED"
    status["updatedAt"] = now_iso()

    save_status(tid, status)
    save_registry(reg)
    refresh_active(reg)

    print(f"  Archived {tid}: {entry['title']}")


# ── CLI Router ────────────────────────────────────────────────────

COMMANDS = {
    "create": cmd_create,
    "list": cmd_list,
    "show": cmd_show,
    "switch": cmd_switch,
    "update": cmd_update,
    "archive": cmd_archive,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage: taskbus.py <command> [args]")
        print(f"Commands: {', '.join(COMMANDS)}")
        sys.exit(1)

    COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
