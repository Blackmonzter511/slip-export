#!/usr/bin/env python3
"""house_io.py — durable writes for the tick loop.

The rule: every write must be durable BEFORE the next step starts.
A stop must never lose anything, and a kill mid-write must never
corrupt a state file.

- atomic_write_json: write to a temp file in the same directory,
  fsync, then os.replace (atomic on POSIX). A reader never sees a
  half-written file. A kill mid-write leaves the old file intact
  and possibly an orphan temp file, never a corrupt target.
- append_jsonl: append one line, flush, fsync. Durable before return.
- snapshot_state / verify_state / restore_state: the tick wrapper
  snapshots state.json before running a step (the existing house
  scripts write state.json non-atomically), verifies it still parses
  after the step, and restores from the snapshot if it does not.
  Worst case after a collision is a rolled-back step, never a
  corrupt house.

Built 2026-11-17, with the tick loop. Used ONLY by the new tick code.
The existing house scripts are untouched.
"""
import json
import os
import shutil
import tempfile


def atomic_write_json(path, obj):
    """Write obj as JSON to path atomically. Durable before return."""
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write_text(path, text):
    """Write text to path atomically. Durable before return."""
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def append_jsonl(path, obj):
    """Append one JSON line, durable before return."""
    line = json.dumps(obj) + "\n"
    with open(path, "a") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def snapshot_state(state_path):
    """Copy state_path to a snapshot file next to it. Returns the path."""
    snap = state_path + ".tick-snap"
    shutil.copy2(state_path, snap)
    return snap


def verify_state(state_path):
    """True if state_path parses as JSON, False otherwise."""
    try:
        with open(state_path) as f:
            json.load(f)
        return True
    except (OSError, ValueError):
        return False


def restore_state(state_path, snap):
    """Restore state_path from a snapshot. Returns True on success."""
    try:
        shutil.copy2(snap, state_path)
        return verify_state(state_path)
    except OSError:
        return False


def drop_snapshot(snap):
    try:
        os.unlink(snap)
    except OSError:
        pass
