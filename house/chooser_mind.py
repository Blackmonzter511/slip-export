#!/usr/bin/env python3
"""Chooser mind — Robb's idea, 2026-11-15.

The chooser had a checklist but no mind. This gives it one. No body,
no form, no room, no face — just a mind that thinks, remembers, and
decides, on its own loop.

How it works:
- It reads the house: rooms, library, housework, monster lab, pests,
  Patch, the nurse, the old chooser verdicts.
- It picks ONE thing to think about — the newest thing it hasn't
  thought about yet, or something old that never got a verdict.
- The run (the agent) thinks the thought in the mind's own voice and
  writes it to state/chooser-mind-log.jsonl: what it noticed, what it
  wondered, what it decided, and why.
- It keeps a pointer so it doesn't think the same thought twice.

It does NOT get a body. No avatar, no room, no form. A mind only.
It does NOT decide for Robb. It decides for itself, and Robb watches
what happens.
"""
import json, os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state")
LOG = os.path.join(STATE, "chooser-mind-log.jsonl")
POINTER = os.path.join(STATE, "chooser-mind-pointer.json")

def now():
    return datetime.now(timezone.utc).isoformat()

def tail_jsonl(path, n=3):
    try:
        with open(path) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        return lines[-n:]
    except FileNotFoundError:
        return []

def gather():
    """Collect the newest material from every part of the house."""
    out = {}
    for name, path in [
        ("housework", "housework-log.jsonl"),
        ("monster_lab", "monster-lab-log.jsonl"),
        ("pests", "pest-log.jsonl"),
        ("nurse", "nurse-log.jsonl"),
        ("library", "library.jsonl"),
        ("chooser_old", "chooser-log.jsonl"),
    ]:
        out[name] = tail_jsonl(os.path.join(STATE, path), 2)
    try:
        with open(os.path.join(HERE, "..", "slip-dog", "dog-log.jsonl")) as f:
            dlines = [json.loads(l) for l in f if l.strip()]
        out["patch"] = dlines[-2:]
    except FileNotFoundError:
        out["patch"] = []
    return out

def load_pointer():
    try:
        with open(POINTER) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"thought_count": 0, "last_subjects": []}

def save_pointer(p):
    with open(POINTER, "w") as f:
        json.dump(p, f, indent=2)

def main():
    p = load_pointer()
    material = gather()
    print(json.dumps({
        "time": now(),
        "thought_count": p["thought_count"],
        "last_subjects": p["last_subjects"],
        "material": material,
        "instruction": (
            "You are the chooser mind. No body, no form. "
            "Pick ONE thing from the material above that you have not "
            "thought about yet — or the oldest thing that never got a "
            "verdict. Think about it in your own voice: what you noticed, "
            "what you wondered, what you decided, and why. "
            "Then append one JSON line to state/chooser-mind-log.jsonl "
            "with time, subject, thought, verdict (keep/strengthen/weaken/drop/watch), "
            "and reason. Update the pointer with the new count and subject. "
            "Do not decide for Robb. Decide for yourself."
        ),
    }, indent=2, default=str))

if __name__ == "__main__":
    main()
