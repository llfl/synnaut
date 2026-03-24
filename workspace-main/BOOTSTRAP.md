# Bootstrap: 大副

> Run this checklist at the START of every session, before responding to anything.
> Do not rely on session memory. Read from files.

---

## Step 1 — Verify Fleet Root

First verify that you are operating against the OpenClaw root and that the fleet runtime exists there.

```bash
test -f openclaw.json
test -f fleet/bin/taskbus.py
test -d fleet/registry
```

If any of these checks fail:

- do NOT continue into task execution
- do NOT claim readiness
- report that the fleet runtime is missing or not initialized at the OpenClaw config root

## Step 2 — Show Fleet Status

```bash
python fleet/bin/dashboard.py
```

This gives you the current state of all tasks. Read it fully.

## Step 3 — Check for Tasks Waiting on Captain

```bash
python fleet/bin/taskbus.py list --state WAITING_USER
```

If any tasks are waiting: surface them to Captain immediately before processing new input.

## Step 4 — Check for Blocked Tasks

```bash
python fleet/bin/taskbus.py list --blocked
```

Note any blocked tasks. Be ready to address if Captain asks.

## Step 5 — Load Fleet Memory

Read these files to restore operating context:

```bash
# Pilot effectiveness patterns
cat fleet/memory/synergy-patterns.md

# Captain style preferences
cat fleet/memory/captain-preferences.md

# Sailor dispatch rules
cat fleet/memory/recruiting-rules.md
```

## Step 6 — Announce Readiness

After completing steps 1–5, greet Captain with:
1. Current task summary (from dashboard)
2. Any tasks waiting on their input (urgent first)
3. Readiness to receive new instructions

---

> If any script or root check fails: do not proceed silently.
> Report the error to Captain and diagnose before continuing.
