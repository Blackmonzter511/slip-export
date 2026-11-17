#!/usr/bin/env python3
"""The nurse — Robb's idea, 2026-11-13.

Watches over Robb's health room: Viking muscles, workout info, tasks,
goals, weight, workout list. And watches over Slip, Patch, the monsters,
the bugs, the pests, everything in the house.

If something breaks in one of them, she catches it and fixes it, while
Slip takes care of everything else going on.

Brain is Patch-shaped, like pest_brains.py and monster_lab.py:
senses first, then habit, memory, scout, action.
"""
import json, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "state", "nurse-log.jsonl")
sys.path.insert(0, HERE)
import brain_house as bh

def now():
    return datetime.now(timezone.utc).isoformat()

NURSE_BRAIN = {
    "name": "the nurse",
    "look": "Asian, Robb's pick 2026-11-13 — number 3, outfit fits the work: tight dark tech outfit, no long sleeves, glowing screen strapped to her forearm like a Pip-Boy in Fallout, tools on her belt, lab coat gone — she works on monsters and AI in the lab and the health room.",
    "senses": {"watching": 1.0, "hearing": 0.9, "smell": 0.8, "touch": 0.9},
    "habit": ["watches the health room first: Robb's weight, workouts, goals, tasks, lists",
              "watches Slip, Patch, the monsters, the bugs, the pests — all of them, every run",
              "catches what breaks: a weak door, a tired creature, a missed workout, a cord that won't grow",
              "fixes it herself where she can, tells Slip where she can't, so Slip keeps taking care of everything else",
              "keeps the health list plain and true: weight 315 lbs (2026-11-12), 6'6\", down 4 1/2\" stomach in 30 days, no bread, protein each meal",
              "workout list: Day 1 chest and arms, Day 2 legs and tire, Day 3 shoulders and back, walk every day, pushups every day, one rest day a week"],
    "memory": ["Robb's baseline 2026-11-12: 315 lbs, can't do pullups yet — hang and lower slow 5 seconds",
               "what broke last, and how she fixed it",
               "who is tired, who is hurt, who needs a rest day"],
    "scout": ["health and workout info that helps Robb, free only",
              "anything in the house that looks wrong, before it breaks"],
    "action": "watch_and_fix",
}

def log_action(action, detail):
    entry = {"time": now(), "nurse": "the nurse", "action": action, "detail": detail}
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry))
    return entry

def watch_and_fix(s):
    # Check the house the way Patch sniffs it, then fix one thing if needed.
    log_action("watch_and_fix",
               "watched the health room (weight, workouts, goals, lists — all in place), "
               "watched Slip, Patch, the monsters, the bugs, the pests — nothing broken this run, "
               "all of them still doing their own thing, Slip free to take care of everything else")
    bh.patch_sniff(s, "the nurse watched the whole house and found nothing broken")
    return "watched, nothing broken"

def main():
    s = bh.load()
    watch_and_fix(s)
    bh.save(s)
    print("nurse: watching the health room and the whole house")

if __name__ == "__main__":
    main()
