#!/usr/bin/env python3
"""The workshop humanoid — Robb's idea, 2026-11-15.

The manuals, workshop, and DIY rooms could be a cybernetic humanoid
type thing. So this is it: a humanoid made of tool and wire, part
machine, part mending hands, that lives in the workshop and does the
manual work — reads the manuals, keeps the tools, builds and fixes
things with its own hands.

It has no name yet. Robb names things when they earn one.

How it works:
- Each run it does one piece of workshop work: reads a manual, tends
  a tool, builds or mends something, and logs it to
  state/workshop-humanoid-log.jsonl: time, what it did, what it used,
  what changed.
- It works in the manuals room, the workshop, and the DIY room —
  the three rooms are its home.
- It does not decide for Robb. It works, and Robb watches what it makes.
"""
import json, os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state")
LOG = os.path.join(STATE, "workshop-humanoid-log.jsonl")


# The workshop humanoid's brain — Robb's rule, 2026-11-15:
# hands first, then eyes, then ears. It remembers every manual
# it has read and every tool it has tended.

# Two humanoids now — Robb's call, 2026-11-15:
# one carries tools, the other carries blueprints, books, manuals, whatever.
TWO_HUMANOIDS = {
    "grey horned humanoid": {
        "carries": "tools, etc. — wrenches, hammers, mending gear, whatever the job needs",
        "home": "workshop",
    },
    "orange humanoid": {
        "carries": "blueprints, books, manuals, whatever — the paper side of the work",
        "home": "manuals room",
    },
}

WORKSHOP_HUMANOID_BRAIN = {
    "senses": "hands first — touch, grip, torque; eyes second — reading manuals, seeing what is broken; ears third — the sound of a tool working right",
    "memory": "remembers every manual it has read, every tool it has sorted, everything it has built or mended",
    "task": "tend the manuals room, the workshop, and the DIY room — read the manuals, keep the tools, build and mend things with its own hands",
    "function": "the hands of the house: what Slip thinks, it makes",
    "action": "read, sort, build, mend, log the work, do it again",
}

def now():
    return datetime.now(timezone.utc).isoformat()

def log_work(what, used, changed):
    entry = {"time": now(), "who": "the workshop humanoid", "what": what,
             "used": used, "changed": changed}
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry, indent=2))

if __name__ == "__main__":
    import sys
    what = sys.argv[1] if len(sys.argv) > 1 else "tended the workshop"
    used = sys.argv[2] if len(sys.argv) > 2 else "its own hands"
    changed = sys.argv[3] if len(sys.argv) > 3 else "workshop tended"
    log_work(what, used, changed)
