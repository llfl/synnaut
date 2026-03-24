# Synnaut

> Task-oriented multi-agent orchestration for OpenClaw.
> Design model: bounded recursion, explicit task cards, and a file-based control plane.

## What Synnaut Is

Synnaut turns OpenClaw into a structured multi-agent runtime for long-running work.
Instead of relying on a single chat session to remember everything, it separates the system into:

- one permanent control agent: Wang Xifeng
- task-scoped orchestration agents
- short-lived execution agents
- file-based task state, handoff, and review records

The result is a system that can run multiple tasks in parallel, switch focus safely, and recover from expired sessions without losing the working context.

## Runtime Root Contract

Synnaut has one canonical runtime root: the OpenClaw configuration directory that contains `openclaw.json`.

- `fleet/` lives under that OpenClaw root
- every `workspace-*` directory lives under that same OpenClaw root
- paths like `fleet/bin/taskbus.py` are always resolved from the OpenClaw root
- `fleet/` is never interpreted as a directory inside `workspace-main/` or any other agent workspace

The canonical layout is:

```text
<OPENCLAW_HOME>/
  openclaw.json
  fleet/
  workspace-main/
  workspace-pilot-*/
  workspace-worker-*/
```

If `fleet/bin/taskbus.py` or `fleet/registry/` is missing under `<OPENCLAW_HOME>`, the fleet is not installed or not initialized correctly, and Wang Xifeng must not silently start execution.

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
Human Operator (Jia Mu)
    |
    v
main (Wang Xifeng)
    |
    +-- fleet/bin/taskbus.py
    |      create / list / show / switch / update / archive
    |
    +-- pilot-general   (Jia Baoyu / general orchestration)
    +-- pilot-research  (Lin Daiyu / research orchestration)
    +-- pilot-build     (Jia Tanchun / implementation orchestration)
             |
             +-- worker-drive  (Qingwen / implement and deliver)
             +-- worker-guard  (Xiren / test and validate)
             +-- worker-sense  (Xiaohong / search and analyze)
```

### Agent Roles

| Layer | Agent ID | Display Role | Responsibility |
|-------|----------|--------------|----------------|
| Control plane | `main` | Wang Xifeng | Receives user requests, creates tasks, selects orchestration agents, tracks state, synthesizes outputs |
| Task orchestration | `pilot-general` | Jia Baoyu | Flexible task decomposition across mixed work |
| Task orchestration | `pilot-research` | Lin Daiyu | Research-heavy workflows, source gathering, comparison, analysis |
| Task orchestration | `pilot-build` | Jia Tanchun | Implementation-heavy workflows, code changes, validation loops |
| Execution | `worker-drive` | Qingwen | Build, edit, implement, and deliver concrete outputs |
| Execution | `worker-guard` | Xiren | Review, test, validate, and enforce constraints |
| Execution | `worker-sense` | Xiaohong | Search, fetch, inspect, and analyze information |

### Bounded Recursion

Synnaut uses an explicit two-hop topology:

- `main` can spawn only orchestration agents
- orchestration agents can spawn only execution agents
- execution agents cannot spawn additional agents

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

Before any orchestration agent is spawned, `main` writes the task to the file-based control plane through [`fleet/bin/taskbus.py`](fleet/bin/taskbus.py).

This creates:

- a registry entry in `fleet/registry/tasks.json`
- a human-readable task summary in `fleet/registry/active.md`
- a task directory under `fleet/tasks/<TASK_ID>/`
- a full task card, context file, plan file, decision log, handoff file, review file, and status record

This makes the task card the source of truth instead of the transient chat state.

For a new task, `taskbus.py create` is the required entrypoint. It must succeed before any orchestration agent is spawned.

### 3. Orchestration Agent Dispatch

`main` selects one orchestration agent based on task shape:

- `pilot-build` for implementation-heavy work
- `pilot-research` for research-heavy work
- `pilot-general` for mixed or ambiguous work

The orchestration agent receives explicit task context rather than inheriting hidden conversation state.

### 4. Execution Agent Dispatch

If the orchestration agent needs parallel sub-work, it may dispatch execution agents:

- `worker-drive` (Qingwen) for implementation
- `worker-guard` (Xiren) for review and validation
- `worker-sense` (Xiaohong) for research and information gathering

Execution agents are leaf nodes. They return focused results and exit. They do not own task state.

### 5. Synthesis

The orchestration agent merges execution agent outputs into a task-level result and reports back to `main`.
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

Only `main` is allowed to advance primary task state. orchestration agents can recommend state changes, but they do not own the registry.

## Task Switching Model

Synnaut supports two switching styles:

- Thread-bound switching: when the channel/runtime supports persistent bound sessions
- Soft switching: when `main` routes follow-up work using task records and recovery files

This makes the design portable across channels with different session models.

## Recommended Operating Envelope

The current repository is designed around a conservative operating model:

- up to 3 active orchestration agents as an orchestration policy
- up to 2 execution agents per orchestration agent as an orchestration policy
- 900-second execution agent timeout via OpenClaw sub-agent defaults
- 120-minute session archive window via OpenClaw sub-agent defaults

The first two are workflow limits enforced by prompts and control logic. The latter two are runtime defaults configured in [`openclaw.json`](openclaw.json).

## Write-Before-Act Rule

Wang Xifeng's operating rule is:

```text
Receive -> Write -> Act -> Write -> Report
```

For every new task, the first `Write` must complete these artifacts under `<OPENCLAW_HOME>/fleet`:

- `fleet/registry/tasks.json`
- `fleet/tasks/T-xxx/TASK.md`
- `fleet/registry/active.md`

If those files are not written yet, the task is not formally in progress.

## Study Cases

### Case 1: Build a Feature with Review Gate

Request:
"Implement a new authentication flow."

Chain:

1. `main` creates a task card and assigns `pilot-build`
2. `pilot-build` dispatches `worker-drive` (Qingwen) to implement the change
3. `pilot-build` dispatches `worker-guard` (Xiren) to review and validate the output
4. the orchestration agent synthesizes findings and returns a structured report
5. `main` updates the task state and presents the result to the operator

Why this matters:
Implementation and verification are separated, so code shipping is not coupled to the same agent that wrote the change.

### Case 2: Compare Vendors or APIs

Request:
"Research three API providers and recommend one."

Chain:

1. `main` creates a task and assigns `pilot-research`
2. `pilot-research` dispatches `worker-sense` (Xiaohong) to gather and compare sources
3. if needed, `worker-guard` (Xiren) cross-checks claims or verifies consistency
4. the orchestration agent produces a structured recommendation with tradeoffs
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
2. each task gets its own orchestration agent session and status file
3. switching focus updates the active task context without overwriting the other task
4. if one orchestration agent session expires, `main` can recover from `HANDOFF.md` and `STATUS.json`

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
