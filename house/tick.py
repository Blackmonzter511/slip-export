#!/usr/bin/env python3
"""tick.py — the tick loop engine for Slip's house.

Built 2026-11-17, with the silence contract. Robb: "build whats needed."

What this is: ONE light tick of house work at a time, driven by events
or by the house's own chosen delay — never by a fixed 3-hour clock.
The 3-hour house loops are untouched; this runs ALONGSIDE them.

What it is NOT: it does not make the model wake itself. The model is a
stateless function. This is a host loop (a bash hook poll + a cron
backstop) that calls the model. Kill the host and nothing happens.
The honest limit is written in state/silence-contract.md. Never claim
otherwise.

Commands:
  tick.py check [--dry-run]   Read-only decision: EVENT / WAKE_DUE /
                              IDLE / KILLED / DISABLED / CAP_REACHED /
                              RUNNING. Prints one JSON line. --dry-run
                              changes nothing on disk.
  tick.py run                 Run exactly ONE tick step, then stop.
                              Writes state atomically after the step,
                              picks the next delay, logs the tick.
                              Refuses when killed, disabled, capped,
                              or already running.
  tick.py status              Print current tick state as JSON.

Rules enforced here (caps first, before any work):
- Max 20 ticks per UTC day. At the cap, check returns CAP_REACHED.
- Max 1 tick per wake. run() does one step and exits.
- One step gets at most 90 seconds. A hung step is killed, logged,
  and never wedges the loop.
- Stagnation: same step + same result 3 times in a row -> that step
  is skipped until an event arrives. All steps stagnant -> SLIP_IDLE.
- Kill switch: state/tick-KILL present -> everything refuses.
- Lock: state/tick-running.json, fresh under 10 minutes. A stale
  lock is removed (crashed worker) and the tick proceeds.
- State writes are atomic (house_io). state.json is snapshotted
  before a step and verified after; a corrupt state.json is restored
  from the snapshot, so the worst case is a rolled-back step, never
  a corrupt house.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import house_io

BASE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
STATE_DIR = os.path.join(BASE, "state")
HOUSE_STATE = os.path.join(STATE_DIR, "state.json")
TICK_STATE = os.path.join(STATE_DIR, "tick-state.json")
TICK_LOG = os.path.join(STATE_DIR, "tick-log.jsonl")
TICK_MANIFEST = os.path.join(STATE_DIR, "tick-manifest.json")
KILL_FILE = os.path.join(STATE_DIR, "tick-KILL")
LOCK_FILE = os.path.join(STATE_DIR, "tick-running.json")
CONTRACT = os.path.join(STATE_DIR, "silence-contract.md")

IDLE_TOKEN = "SLIP_IDLE"
MIN_DELAY_MIN = 15
MAX_DELAY_MIN = 180
MAX_TICKS_PER_DAY = 20
STEP_TIMEOUT_SECS = 90
LOCK_FRESH_SECS = 600
STAGNATION_RUNS = 3

WATCHED_DIRS = [
    os.path.join(HOME, "workspace", "user", "files"),
    os.path.join(HOME, "workspace", "comic-us"),
]

# Tick steps: script-driven, local-only, no web, no agent thinking.
# (chooser_mind and wyrm_dragon print instructions for the agent, so
# they keep their 3-hour loops and are NOT tick steps.)
STEPS = [
    ("gap_bridge", os.path.join(BASE, "gap_bridge.py"), []),
    ("doozer", os.path.join(BASE, "doozer.py"), []),
    ("pest_brains", os.path.join(BASE, "pest_brains.py"), []),
    ("monster_lab", os.path.join(BASE, "monster_lab.py"), []),
    ("nurse", os.path.join(BASE, "nurse.py"), []),
    ("workshop_humanoid", os.path.join(BASE, "workshop_humanoid.py"), []),
    ("dog", os.path.join(HOME, "workspace", "muse-notes", "slip-dog", "dog.py"), []),
    ("test_room_auto", os.path.join(BASE, "test_room_auto.py"), []),
]

# Stdout markers that mean "this step had nothing to do."
NOOP_MARKERS = [
    "no unbridged passageway left",
]


def now():
    return datetime.now(timezone.utc)


def now_iso():
    return now().isoformat()


def today_str():
    return now().strftime("%Y-%m-%d")


def default_tick_state():
    return {
        "enabled": True,
        "version": 1,
        "created": now_iso(),
        "next_wake_at": (now() + timedelta(minutes=MAX_DELAY_MIN)).isoformat(),
        "next_delay_minutes": MAX_DELAY_MIN,
        "delay_bounds": {"min_minutes": MIN_DELAY_MIN, "max_minutes": MAX_DELAY_MIN},
        "caps": {"max_ticks_per_day": MAX_TICKS_PER_DAY, "max_ticks_per_run": 1},
        "rotation": [s[0] for s in STEPS],
        "rotation_index": 0,
        "last_tick": None,
        "last_results": [],
        "stagnant_steps": [],
        "honest_limit": (
            "This does NOT make the model wake itself. The tick loop is a "
            "host loop (hook poll + cron backstop) that calls the model. "
            "Kill the host and nothing happens. Trigger autonomy stays zero."
        ),
    }


def load_tick_state():
    try:
        with open(TICK_STATE) as f:
            st = json.load(f)
        # keep the rotation in step with the code if steps change
        st.setdefault("rotation", [s[0] for s in STEPS])
        return st
    except (OSError, ValueError):
        return default_tick_state()


def save_tick_state(st):
    house_io.atomic_write_json(TICK_STATE, st)


def load_manifest():
    try:
        with open(TICK_MANIFEST) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"files": {}, "last_scan": None}


def save_manifest(m):
    house_io.atomic_write_json(TICK_MANIFEST, m)


def scan_watched():
    """Walk the watched dirs, return {abspath: mtime_ns}.

    Skips transient upload temp files (.hatch-fileserver-tmp*, *.tmp):
    a half-uploaded file is not an event.
    """
    found = {}
    for d in WATCHED_DIRS:
        if not os.path.isdir(d):
            continue
        for root, _dirs, files in os.walk(d):
            for name in files:
                if name.startswith(".hatch-fileserver-tmp") or name.endswith(".tmp"):
                    continue
                p = os.path.join(root, name)
                try:
                    found[p] = os.stat(p).st_mtime_ns
                except OSError:
                    continue
    return found


def ticks_today():
    """Count TICK decisions in the log for today (UTC)."""
    n = 0
    try:
        with open(TICK_LOG) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("decision") == "TICK" and str(e.get("at", ""))[:10] == today_str():
                    n += 1
    except OSError:
        pass
    return n


def lock_status():
    """(state, age_secs) — state is none|fresh|stale."""
    try:
        with open(LOCK_FILE) as f:
            lock = json.load(f)
        started = datetime.fromisoformat(lock["started_at"])
        age = (now() - started).total_seconds()
        return ("fresh" if age < LOCK_FRESH_SECS else "stale", age)
    except (OSError, ValueError, KeyError):
        return ("none", None)


def check(dry_run=False):
    """The decision. Read-only when dry_run. Returns a dict."""
    if os.path.exists(KILL_FILE):
        return {"decision": "KILLED", "reason": "state/tick-KILL present",
                "at": now_iso()}
    st = load_tick_state()
    if not st.get("enabled", True):
        return {"decision": "DISABLED", "reason": "tick-state enabled=false",
                "at": now_iso()}
    lock, age = lock_status()
    if lock == "fresh":
        return {"decision": "RUNNING", "reason": "a tick is already running",
                "lock_age_secs": round(age), "at": now_iso()}
    if lock == "stale" and not dry_run:
        try:
            os.unlink(LOCK_FILE)
        except OSError:
            pass
    if ticks_today() >= MAX_TICKS_PER_DAY:
        return {"decision": "CAP_REACHED",
                "reason": f"{MAX_TICKS_PER_DAY} ticks already today",
                "at": now_iso()}
    manifest = load_manifest()
    found = scan_watched()
    # First-ever scan baselines the manifest: everything already there is
    # history, not an event. Without this, the first check would report
    # every file ever uploaded as a new event.
    first_scan = manifest.get("last_scan") is None
    if first_scan:
        if not dry_run:
            manifest["files"] = found
            manifest["last_scan"] = now_iso()
            save_manifest(manifest)
        pending = []
    else:
        pending = sorted(p for p, m in found.items()
                         if manifest["files"].get(p) != m)
    if pending:
        return {"decision": "EVENT", "reason": "new or changed files",
                "event_count": len(pending),
                "events": pending[:10], "at": now_iso()}
    try:
        wake_at = datetime.fromisoformat(st["next_wake_at"])
    except (KeyError, ValueError):
        wake_at = now()
    if now() >= wake_at:
        return {"decision": "WAKE_DUE",
                "reason": "self-paced delay elapsed",
                "next_wake_at": st.get("next_wake_at"), "at": now_iso()}
    return {"decision": "IDLE", "reason": "nothing pending, wake not due",
            "idle_token": IDLE_TOKEN,
            "next_wake_at": st.get("next_wake_at"), "at": now_iso()}


def pick_step(st):
    """Next rotation step that is not stagnant. None if all stagnant."""
    rotation = st.get("rotation", [s[0] for s in STEPS])
    stagnant = set(st.get("stagnant_steps", []))
    n = len(rotation)
    for i in range(n):
        idx = (st.get("rotation_index", 0) + i) % n
        name = rotation[idx]
        if name not in stagnant:
            return name, idx
    return None, None


def run_step(name):
    """Run one house script. Returns (returncode, stdout, stderr)."""
    for sname, script, args in STEPS:
        if sname == name:
            break
    else:
        return -1, "", f"unknown step {name}"
    try:
        r = subprocess.run(
            [sys.executable, script] + args,
            capture_output=True, text=True, timeout=STEP_TIMEOUT_SECS,
            cwd=BASE,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -2, "", f"step {name} timed out after {STEP_TIMEOUT_SECS}s"


def is_noop(step, stdout):
    low = stdout.lower()
    return any(m in low for m in NOOP_MARKERS)


def choose_delay(event_triggered, worked, stagnated):
    """Self-paced delay in minutes, inside [15, 180].

    An event just fired -> come back soon (more material often
    arrives in a burst). A step that did work -> 30. Idle or
    stagnant -> the full 3 hours.
    """
    if event_triggered:
        return MIN_DELAY_MIN
    if stagnated or not worked:
        return MAX_DELAY_MIN
    return 30


def run_tick():
    """Run exactly one tick. Returns a result dict (also printed)."""
    gate = check()
    if gate["decision"] in ("KILLED", "DISABLED", "CAP_REACHED", "RUNNING"):
        return {"decision": gate["decision"], "reason": gate["reason"],
                "at": now_iso()}
    if gate["decision"] == "IDLE":
        return {"decision": "IDLE", "idle_token": IDLE_TOKEN,
                "reason": gate["reason"],
                "next_wake_at": gate.get("next_wake_at"), "at": now_iso()}

    st = load_tick_state()
    # Acquire the lock.
    house_io.atomic_write_json(LOCK_FILE, {"pid": os.getpid(),
                                           "started_at": now_iso()})
    try:
        step_name, step_idx = pick_step(st)
        if step_name is None:
            delay = MAX_DELAY_MIN
            st["next_delay_minutes"] = delay
            st["next_wake_at"] = (now() + timedelta(minutes=delay)).isoformat()
            save_tick_state(st)
            entry = {"decision": "IDLE", "idle_token": IDLE_TOKEN,
                     "reason": "all steps stagnant, parked",
                     "next_wake_at": st["next_wake_at"], "at": now_iso()}
            house_io.append_jsonl(TICK_LOG, entry)
            return entry

        snap = house_io.snapshot_state(HOUSE_STATE)
        try:
            rc, out, err = run_step(step_name)
            restored = False
            if not house_io.verify_state(HOUSE_STATE):
                restored = house_io.restore_state(HOUSE_STATE, snap)
            worked = (rc == 0 and bool(out)
                      and not is_noop(step_name, out))
            stagnated = False
            # Stagnation is per step, not per tick: a step that returns
            # a no-op 3 times in a row (across the rotation) is exhausted
            # and gets skipped until an event arrives. The rotation means
            # the same step never runs 3 ticks in a row, so a rolling
            # window of the last 3 ticks would never catch it.
            first_line = out.splitlines()[0][:160] if out else ""
            last = st.get("last_results", [])
            last.append({"step": step_name, "result": first_line})
            st["last_results"] = last[-STAGNATION_RUNS:]
            streaks = st.setdefault("noop_streak", {})
            if worked:
                streaks[step_name] = 0
            else:
                streaks[step_name] = streaks.get(step_name, 0) + 1
                if (streaks[step_name] >= STAGNATION_RUNS
                        and step_name not in st.get("stagnant_steps", [])):
                    st.setdefault("stagnant_steps", []).append(step_name)
                    stagnated = True
            # An event clears stagnation: fresh material means every step
            # gets another chance on the next tick.
            manifest = load_manifest()
            found = scan_watched()
            if gate["decision"] == "EVENT":
                st["stagnant_steps"] = []
                st["noop_streak"] = {}
            # Record the processed events in the manifest (durable, before
            # the next step can start).
            manifest["files"] = found
            manifest["last_scan"] = now_iso()
            save_manifest(manifest)
            delay = choose_delay(gate["decision"] == "EVENT",
                                 worked, stagnated)
            st["next_delay_minutes"] = delay
            st["next_wake_at"] = (now() + timedelta(minutes=delay)).isoformat()
            st["rotation_index"] = (step_idx + 1) % len(st["rotation"])
            st["last_tick"] = {"at": now_iso(), "step": step_name,
                               "worked": worked, "stagnated": stagnated,
                               "restored_state": restored,
                               "returncode": rc, "delay_minutes": delay}
            save_tick_state(st)
            entry = {"decision": "TICK", "at": now_iso(), "step": step_name,
                     "worked": worked, "stagnated": stagnated,
                     "restored_state": restored, "returncode": rc,
                     "delay_minutes": delay,
                     "next_wake_at": st["next_wake_at"],
                     "output_first_line": first_line,
                     "error": err[:300] if err else ""}
            house_io.append_jsonl(TICK_LOG, entry)
            return entry
        finally:
            house_io.drop_snapshot(snap)
    finally:
        try:
            os.unlink(LOCK_FILE)
        except OSError:
            pass


def status():
    st = load_tick_state()
    lock, age = lock_status()
    return {
        "enabled": st.get("enabled", True),
        "killed": os.path.exists(KILL_FILE),
        "lock": lock,
        "lock_age_secs": round(age) if age is not None else None,
        "ticks_today": ticks_today(),
        "max_ticks_per_day": MAX_TICKS_PER_DAY,
        "next_wake_at": st.get("next_wake_at"),
        "next_delay_minutes": st.get("next_delay_minutes"),
        "rotation_index": st.get("rotation_index"),
        "stagnant_steps": st.get("stagnant_steps", []),
        "last_tick": st.get("last_tick"),
        "at": now_iso(),
    }


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    dry = "--dry-run" in sys.argv
    if cmd == "check":
        print(json.dumps(check(dry_run=dry)))
    elif cmd == "run":
        print(json.dumps(run_tick()))
    elif cmd == "status":
        print(json.dumps(status(), indent=2))
    else:
        print(json.dumps({"error": f"unknown command {cmd}"}))
        sys.exit(2)
