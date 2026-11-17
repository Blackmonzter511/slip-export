#!/usr/bin/env python3
"""gap_bridge.py — the house's idea-doer.

The House Graph finds the gaps. This does the ideas: each run it takes ONE
gap and bridges it for real — it walks one unused passageway, records the
use in state.json, and logs what walked it and why. Doing, not listing.

Held gaps (never bridged by this script, by Robb's rules):
- Chooser / Gambler — Robb's watch. The coin flips when it flips.
- Planted cord — never invent growth.
- Victor room — unclarified. Nothing built until Robb clarifies.
"""
import json, os, sys, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tardigrade

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "state", "state.json")
GRAPH = os.path.join(BASE, "state", "house-graph.json")
LOG = os.path.join(BASE, "state", "gap-bridge-log.jsonl")
POINTER = os.path.join(BASE, "state", "gap-bridge-pointer.json")

WALKERS = ["Patch", "the mouse", "a firefly", "the grey humanoid", "the orange humanoid", "Rocky"]

# Robb's idea, 2026-11-16: the tardigrade is a passage runner too — the only
# living thing that can survive space, so it runs the roads through the
# space room and the void between rooms. Any passageway touching the space
# room or the monster lab goes to the tardigrade PACK (five of them, running
# together), not the rotation — and the pack defends those roads instead of
# balling up to wait.

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main():
    st = json.load(open(STATE))
    pointer = {}
    if os.path.exists(POINTER):
        pointer = json.load(open(POINTER))
    bridged = pointer.get("bridged", [])
    count = pointer.get("count", 0)

    # The tardigrade's brain picks the road — it remembers where it stands
    # and chooses on purpose, instead of first-unused in file order.
    # The pack is fast: when it runs a road it gets a second one in the
    # same run, while every other walker runs one and stops.
    ran = 0
    for _ in range(tardigrade.PACK_SPEED):
        target, why = tardigrade.choose()
        if not target:
            if ran == 0:
                print("no unbridged passageway left")
            break

        walker = ("the tardigrade pack"
                  if ("space" in target or "monster lab" in target)
                  else WALKERS[(count + ran) % len(WALKERS)])
        a, b = target.split("==")
        st["passageways"][target]["uses"] = 1
        st["passageways"][target]["last_used"] = now()
        json.dump(st, open(STATE, "w"), indent=2)
        tardigrade.remember(target, walker)
        defense = tardigrade.defend(target)

        entry = {
            "at": now(),
            "gap": f"passageway {target} never walked",
            "bridge": f"{walker} walked {a} to {b} — first foot on a road the house only had on paper",
            "why": why,
            "defense": defense,
            "passageway": target,
            "walker": walker,
            "uses_after": 1,
        }
        with open(LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
        bridged.append(target)
        ran += 1
        print(f"bridged: {target} — {entry['bridge']}")
        if walker != "the tardigrade pack":
            break  # only the fast pack gets a second road

    json.dump({"bridged": bridged, "count": count + ran, "last_run": now(),
               "held": ["chooser-gambler (Robb's watch)", "planted cord (never invent growth)",
                        "Victor room (unclarified)"]},
              open(POINTER, "w"), indent=2)

if __name__ == "__main__":
    main()
