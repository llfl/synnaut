# Synnaut

> Task-oriented multi-agent orchestration for OpenClaw.
> Design model: bounded recursion, explicit task cards, and a file-based control plane.

## What Synnaut Is

Synnaut turns OpenClaw into a structured multi-agent runtime for long-running work.
Instead of relying on a single chat session to remember everything, it separates the system into:

- one permanent control agent: the Chief Mate
- task-scoped Pilot agents
- short-lived Sailor agents
- file-based task state, handoff, and review records

The result is a system that can run multiple tasks in parallel, switch focus safely, and recover from expired sessions without losing the working context.

## Why This Design

OpenClaw is strong at agent routing and sub-agent execution, but raw agent spawning alone is not enough for reliable orchestration. Synnaut adds the missing control layer:

- explicit task registration before execution
- deterministic agent topology
- persistent state outside the chat thread
- human-readable recovery files
- structured review and archive flow

This keeps the system auditable and predictable when tasks span multiple sessions.

## Architecture

```text
Human Operator
    |
    v
main (Chief Mate)
    |
    +-- fleet/bin/taskbus.py
    |      create / list / show / switch / update / archive
    |
    +-- pilot-general   (General Pilot / general orchestration)
    +-- pilot-research  (Research Pilot / research orchestration)
    +-- pilot-build     (Build Pilot / implementation orchestration)
             |
             +-- worker-drive  (Engineer / implement and deliver)
             +-- worker-guard  (Mechanic / test and validate)
             +-- worker-sense  (Lookout / search and analyze)
```

### Agent Roles

| Layer | Agent ID | Display Role | Responsibility |
|-------|----------|--------------|----------------|
| Control plane | `main` | Chief Mate | Receives user requests, creates tasks, selects Pilots, tracks state, synthesizes outputs |
| Task orchestration | `pilot-general` | General Pilot | Flexible task decomposition across mixed work |
| Task orchestration | `pilot-research` | Research Pilot | Research-heavy workflows, source gathering, comparison, analysis |
| Task orchestration | `pilot-build` | Build Pilot | Implementation-heavy workflows, code changes, validation loops |
| Execution | `worker-drive` | Engineer | Build, edit, implement, and deliver concrete outputs |
| Execution | `worker-guard` | Mechanic | Review, test, validate, and enforce constraints |
| Execution | `worker-sense` | Lookout | Search, fetch, inspect, and analyze information |

### Bounded Recursion

Synnaut uses an explicit two-hop topology:

- `main` can spawn only Pilots
- Pilots can spawn only Sailors
- Sailors cannot spawn additional agents

This is enforced through `allowAgents` in [`openclaw.json`](openclaw.json).

## Execution Chain

Every task follows the same control path.

### 1. Intake

The operator gives a request to `main`. The system first decides whether the request belongs to:

- a new task
- a follow-up on an existing task
- a task switch
- a task completion or archive action

### 2. Task Registration

Before any Pilot is spawned, `main` writes the task to the file-based control plane through [`fleet/bin/taskbus.py`](fleet/bin/taskbus.py).

This creates:

- a registry entry in `fleet/registry/tasks.json`
- a human-readable task summary in `fleet/registry/active.md`
- a task directory under `fleet/tasks/<TASK_ID>/`
- a full task card, context file, plan file, decision log, handoff file, review file, and status record

This makes the task card the source of truth instead of the transient chat state.

### 3. Pilot Dispatch

`main` selects one Pilot based on task shape:

- `pilot-build` for implementation-heavy work
- `pilot-research` for research-heavy work
- `pilot-general` for mixed or ambiguous work

The Pilot receives explicit task context rather than inheriting hidden conversation state.

### 4. Sailor Execution

If the Pilot needs parallel sub-work, it may dispatch Sailors:

- `worker-drive` (Engineer) for implementation
- `worker-guard` (Mechanic) for review and validation
- `worker-sense` (Lookout) for research and information gathering

Sailors are leaf nodes. They return focused results and exit. They do not own task state.

### 5. Synthesis

The Pilot merges Sailor outputs into a task-level result and reports back to `main`.
`main` remains the only agent that changes primary task state.

### 6. Switch or Recover

If the operator switches to another task, Synnaut can:

- continue an existing live session
- or recover the task from `STATUS.json` and `HANDOFF.md`

This allows multi-task operation without treating one chat thread as the only memory store.

### 7. Review and Archive

When work is complete, the system records review signals, preserves a final handoff snapshot, and archives the task for later inspection and reuse.

## File-Based Control Plane

Synnaut keeps orchestration state on disk, not only in prompts.

### Core Files

| Path | Purpose |
|------|---------|
| [`fleet/bin/taskbus.py`](fleet/bin/taskbus.py) | Task state transitions and task scaffolding |
| [`fleet/bin/dashboard.py`](fleet/bin/dashboard.py) | Read-only operator dashboard |
| [`fleet/registry/tasks.json`](fleet/registry/tasks.json) | Global machine-readable task index |
| [`fleet/registry/active.md`](fleet/registry/active.md) | Human-readable active task summary |
| `fleet/tasks/<TASK_ID>/TASK.md` | Explicit task card |
| `fleet/tasks/<TASK_ID>/STATUS.json` | Current machine-readable task state |
| `fleet/tasks/<TASK_ID>/HANDOFF.md` | Recovery snapshot for context switching or expired sessions |
| `fleet/tasks/<TASK_ID>/REVIEW.md` | Outcome review and learning events |

### State Model

```text
NEW -> RUNNING -> WAITING_USER / BLOCKED / SYNTHESIZING -> DONE / FAILED -> ARCHIVED
```

Only `main` is allowed to advance primary task state. Pilots can recommend state changes, but they do not own the registry.

## Task Switching Model

Synnaut supports two switching styles:

- Thread-bound switching: when the channel/runtime supports persistent bound sessions
- Soft switching: when `main` routes follow-up work using task records and recovery files

This makes the design portable across channels with different session models.

## Recommended Operating Envelope

The current repository is designed around a conservative operating model:

- up to 3 active Pilots as an orchestration policy
- up to 2 Sailors per Pilot as an orchestration policy
- 900-second Sailor timeout via OpenClaw sub-agent defaults
- 120-minute session archive window via OpenClaw sub-agent defaults

The first two are workflow limits enforced by prompts and control logic. The latter two are runtime defaults configured in [`openclaw.json`](openclaw.json).

## Study Cases

### Case 1: Build a Feature with Review Gate

Request:
"Implement a new authentication flow."

Chain:

1. `main` creates a task card and assigns `pilot-build`
2. `pilot-build` dispatches `worker-drive` (Engineer) to implement the change
3. `pilot-build` dispatches `worker-guard` (Mechanic) to review and validate the output
4. the Pilot synthesizes findings and returns a structured report
5. `main` updates the task state and presents the result to the operator

Why this matters:
Implementation and verification are separated, so code shipping is not coupled to the same agent that wrote the change.

### Case 2: Compare Vendors or APIs

Request:
"Research three API providers and recommend one."

Chain:

1. `main` creates a task and assigns `pilot-research`
2. `pilot-research` dispatches `worker-sense` (Lookout) to gather and compare sources
3. if needed, `worker-guard` (Mechanic) cross-checks claims or verifies consistency
4. the Pilot produces a structured recommendation with tradeoffs
5. `main` records the conclusion and next step

Why this matters:
Source gathering, verification, and final recommendation are distinct phases, which reduces hand-wavy research output.

### Case 3: Run Multiple Tasks and Switch Safely

Requests:

- "Start a build task for the release branch."
- "Also investigate why sandbox startup is failing."
- "Switch back to the release task."

Chain:

1. `main` opens separate task records for both requests
2. each task gets its own Pilot session and status file
3. switching focus updates the active task context without overwriting the other task
4. if one Pilot session expires, `main` can recover from `HANDOFF.md` and `STATUS.json`

Why this matters:
The system treats multitasking as a first-class workflow instead of forcing every task into one linear conversation.

## Runtime Notes

Sandboxing is opt-in during installation:

```bash
python install.py --sandbox
```

This is deliberate. Sandbox mode depends on a compatible container runtime and a usable `openclaw-sandbox` image. A default-on sandbox would make installation fail in environments where that image is not available.

## Repository Map

- [`openclaw.json`](openclaw.json): OpenClaw agent topology and tool permissions
- [`install.py`](install.py): installer that merges Synnaut into an existing OpenClaw setup
- [`workspace-main/AGENTS.md`](workspace-main/AGENTS.md): control-plane behavior for `main`
- [`fleet/bin/taskbus.py`](fleet/bin/taskbus.py): task state machine entrypoint
- [`fleet/bin/dashboard.py`](fleet/bin/dashboard.py): terminal dashboard for operators

## Design Principles

- Explicit state is safer than conversational memory.
- Orchestration and execution should be separate responsibilities.
- Parallel work should be bounded, not recursive by default.
- Task switching should recover from files, not from hope.
- Review artifacts matter as much as execution artifacts.
