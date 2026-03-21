#!/usr/bin/env python3
"""
Liquid Fleet 3.0 Installer

Installs the fleet workspace into an existing OpenClaw directory.
Merges agent configuration into the target openclaw.json while
inheriting the target's global model settings.

Usage:
    python install.py                     # default: ~/.openclaw
    python install.py /path/to/openclaw   # custom target
    python install.py --dry-run           # preview without writing
"""

import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent

FLEET_SOURCE = SCRIPT_DIR / "fleet"
WORKSPACE_SOURCES = [
    "workspace-main",
    "workspace-pilot-general",
    "workspace-pilot-research",
    "workspace-pilot-build",
    "workspace-worker-drive",
    "workspace-worker-guard",
    "workspace-worker-sense",
]
FLEET_CONFIG_SOURCE = SCRIPT_DIR / "openclaw.json"

DEFAULT_TARGET = Path.home() / ".openclaw"


# ── JSON Merge ─────────────────────────────────────────────────────

def deep_merge(base: dict, overlay: dict) -> dict:
    """Recursively merge overlay into base. Overlay wins on conflicts."""
    result = deepcopy(base)
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def resolve_model(target_config: dict) -> dict | None:
    """Extract global model from target openclaw.json.

    Lookup order:
      1. agents.defaults.model  (agent-level default)
      2. model                  (top-level global)
    Returns None if neither exists.
    """
    agents_model = (
        target_config
        .get("agents", {})
        .get("defaults", {})
        .get("model")
    )
    if agents_model:
        return deepcopy(agents_model)

    global_model = target_config.get("model")
    if global_model:
        return deepcopy(global_model)

    return None


def prepare_agents_config(fleet_config: dict, inherited_model: dict | None) -> dict:
    """Build the agents block for merging.

    - Strips our hardcoded model from agents.defaults
    - Injects the inherited model (or omits if None)
    """
    agents = deepcopy(fleet_config.get("agents", {}))
    defaults = agents.get("defaults", {})

    # Remove our placeholder model
    defaults.pop("model", None)

    # Inherit from target
    if inherited_model:
        defaults["model"] = inherited_model

    agents["defaults"] = defaults

    return agents


def merge_openclaw_json(target_path: Path, fleet_config: dict) -> dict:
    """Merge fleet config into existing target openclaw.json."""
    if target_path.exists():
        with open(target_path) as f:
            target_config = json.load(f)
    else:
        target_config = {}

    inherited_model = resolve_model(target_config)
    agents_block = prepare_agents_config(fleet_config, inherited_model)

    # Merge agent list: append fleet agents, skip duplicates by id
    existing_agents = target_config.get("agents", {}).get("list", [])
    existing_ids = {a["id"] for a in existing_agents}
    fleet_agents = agents_block.pop("list", [])

    merged_list = []
    fleet_ids = {a["id"] for a in fleet_agents}

    # Fleet agents replace existing ones with same id.
    # Strip default:true from surviving non-fleet agents to ensure
    # Chief Mate (main) is the sole entry point.
    for agent in existing_agents:
        if agent["id"] not in fleet_ids:
            agent = deepcopy(agent)
            agent.pop("default", None)
            merged_list.append(agent)

    merged_list.extend(fleet_agents)

    # Build overlay
    overlay = {}

    # Merge agents.defaults (subagents, sandbox, model)
    overlay["agents"] = deep_merge(
        target_config.get("agents", {}),
        agents_block,
    )
    overlay["agents"]["list"] = merged_list

    # Merge bindings
    if "bindings" in fleet_config:
        overlay["bindings"] = deep_merge(
            target_config.get("bindings", {}),
            fleet_config["bindings"],
        )

    # Merge fleet metadata
    if "fleet" in fleet_config:
        overlay["fleet"] = deep_merge(
            target_config.get("fleet", {}),
            fleet_config["fleet"],
        )

    return deep_merge(target_config, overlay)


# ── File Operations ────────────────────────────────────────────────

def copy_tree(src: Path, dst: Path, dry_run: bool = False):
    """Copy directory tree, creating parents as needed."""
    if not src.exists():
        return

    for item in sorted(src.rglob("*")):
        if item.name == ".DS_Store":
            continue

        relative = item.relative_to(src)
        target = dst / relative

        if item.is_dir():
            if not dry_run:
                target.mkdir(parents=True, exist_ok=True)
            print(f"  mkdir  {target}")
        else:
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
            print(f"  copy   {target}")


def install(target_dir: Path, dry_run: bool = False):
    """Run the full installation."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Installing Liquid Fleet 3.0")
    print(f"  Source: {SCRIPT_DIR}")
    print(f"  Target: {target_dir}\n")

    if not target_dir.exists():
        if dry_run:
            print(f"  Would create {target_dir}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"  Created {target_dir}")

    # ── 1. Copy workspaces ─────────────────────────────────────────
    print("── Workspaces ──")
    for ws_name in WORKSPACE_SOURCES:
        src = SCRIPT_DIR / ws_name
        dst = target_dir / ws_name
        copy_tree(src, dst, dry_run)

    # ── 2. Copy fleet directory ────────────────────────────────────
    print("\n── Fleet ──")
    copy_tree(FLEET_SOURCE, target_dir / "fleet", dry_run)

    # ── 3. Merge openclaw.json ─────────────────────────────────────
    print("\n── Configuration ──")
    target_json_path = target_dir / "openclaw.json"

    with open(FLEET_CONFIG_SOURCE) as f:
        fleet_config = json.load(f)

    merged = merge_openclaw_json(target_json_path, fleet_config)

    # Report model inheritance
    if target_json_path.exists():
        with open(target_json_path) as f:
            inherited_model = resolve_model(json.load(f))
    else:
        inherited_model = None
    if inherited_model:
        print(f"  Model inherited from target: {json.dumps(inherited_model)}")
    else:
        print("  No existing model found in target — agents.defaults.model omitted")

    if dry_run:
        print(f"\n  Would write {target_json_path}")
        print(f"  Merged config preview:\n{json.dumps(merged, indent=2)}")
    else:
        with open(target_json_path, "w") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Wrote {target_json_path}")

    # ── Summary ────────────────────────────────────────────────────
    agent_ids = [a["id"] for a in merged.get("agents", {}).get("list", [])]
    print(f"\n── Done ──")
    print(f"  Agents installed: {', '.join(agent_ids)}")
    print(f"  Default agent:    main (Chief Mate)")
    print(f"  Fleet registry:   {target_dir / 'fleet' / 'registry'}")
    print(f"  Fleet memory:     {target_dir / 'fleet' / 'memory'}")
    print(f"  Task templates:   {target_dir / 'fleet' / 'tasks' / '.template'}")

    if not dry_run:
        print(f"\n  Fleet is ready. Start OpenClaw and talk to the Chief Mate.")


# ── CLI ────────────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry-run"]

    target = Path(args[0]) if args else DEFAULT_TARGET
    target = target.resolve()

    install(target, dry_run)


if __name__ == "__main__":
    main()
