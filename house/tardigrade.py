#!/usr/bin/env python3
"""tardigrade.py — the water bear's brain.

Real water bears have ~200 neurons and no learning worth the name. Robb's
fix for that, 2026-11-16: "make 'em smart." The house's water bear gets a
little brain of its own: it remembers where it stands, chooses the next
road on purpose, and learns which roads matter. It does not run every road
itself — it PICKS the road, and the house's walkers follow its pick. Roads
touching the space room still go to the tardigrade itself, the only runner
that can survive them.

Robb's rules, 2026-11-16: they run in PACKS, and they have a defense that
is NOT balling up to wait. The pack is five. The defense: when a road runs
through a hostile place (monster lab, space room), the pack links claws
into a living chain across the passage and spins a thread trip-line behind
it. It holds the road instead of hiding from it.

Robb's rule, 2026-11-16: they are FAST. Real water bears crawl; the house
pack runs two roads per loop run while everyone else runs one.
"""
import json, os, datetime

PACK_SIZE = 5
PACK_SPEED = 2  # roads per loop run, while every other walker runs one

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "state", "state.json")
GAP_POINTER = os.path.join(BASE, "state", "gap-bridge-pointer.json")
POINTER = os.path.join(BASE, "state", "tardigrade-pointer.json")
LOG = os.path.join(BASE, "state", "tardigrade-log.jsonl")

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def load_pointer():
    if os.path.exists(POINTER):
        return json.load(open(POINTER))
    return {"position": "space room", "walked": [], "count": 0, "pack": PACK_SIZE}

def defend(road):
    """The pack's defense — not balling up to wait. On a road through a
    hostile place (monster lab, space room), the pack links claws into a
    living chain across the passage and spins a thread trip-line behind it.
    Returns the defense description, or None on a safe road."""
    if not any(h in road for h in ("monster lab", "space room")):
        return None
    defense = ("pack of five linked claws into a chain across the passage, "
               "thread trip-line spun behind it — holds the road, does not hide")
    with open(LOG, "a") as f:
        f.write(json.dumps({"at": now(), "road": road, "defense": defense}) + "\n")
    return defense

def choose():
    """Pick the next unbridged passageway. Returns (target, why) or (None, why)."""
    st = json.load(open(STATE))
    bridged = []
    if os.path.exists(GAP_POINTER):
        bridged = json.load(open(GAP_POINTER)).get("bridged", [])
    unused = [k for k, v in st["passageways"].items()
              if v.get("uses", 0) == 0 and k not in bridged]
    if not unused:
        return None, "no unbridged passageway left — every road has feet on it"
    pos = load_pointer().get("position", "space room")
    # First: a road touching where it stands — it does not teleport.
    for k in unused:
        if pos in k.split("=="):
            return k, f"continues from where it stands ({pos})"
    # Second: the road touching the room with the fewest walked connections.
    walked_count = {}
    for k, v in st["passageways"].items():
        if v.get("uses", 0) > 0:
            for room in k.split("=="):
                walked_count[room] = walked_count.get(room, 0) + 1
    def loneliest(k):
        return min(walked_count.get(r, 0) for r in k.split("=="))
    return min(unused, key=loneliest), "the loneliest room first"

def remember(target, walker):
    """After a road is walked on its pick: remember where it now stands."""
    p = load_pointer()
    a, b = target.split("==")
    p["position"] = b if p.get("position") == a else a
    p["walked"].append(target)
    p["count"] = p.get("count", 0) + 1
    json.dump(p, open(POINTER, "w"), indent=2)
    with open(LOG, "a") as f:
        f.write(json.dumps({"at": now(), "road": target, "walker": walker,
                            "now_standing": p["position"]}) + "\n")
    return p["position"]

if __name__ == "__main__":
    t, why = choose()
    print(f"pick: {t} — {why}" if t else f"pick: none — {why}")
