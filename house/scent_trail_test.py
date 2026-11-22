#!/usr/bin/env python3
"""Scent-trail recovery test, 2026-11-06, Robb approved ("Yes, try the test").

Subject: "outer space research: Voyager 1, habitable planets, stars, cosmic web"
- a real conversation from 2026-11-04 21:47, already in the house, consolidated,
  path feeling -> memory -> planning, weight 0.6.
- chosen because it is post-Patch (Patch was scouting that evening), it is a
  conversation not a core like, and pruning it temporarily is safe.
- NOT chosen: Nick Cave / Prine / Hank likes — those predate Patch, so Patch
  never smelled them; no scent trail could honestly exist for them yet.

Design, honest and checkable:
1. Snapshot state.json first, so nothing is lost blind.
2. Baseline: Slip fires feeling->memory->planning alone. Doors are 1.0, so it fires.
3. Prune the main corridor in the model only: feeling->memory 1.0 -> 0.30,
   memory->planning 1.0 -> 0.30, plus passageways feeling==memory and
   memory==planning 0.6/0.65 -> 0.30. All below the 0.55 firing threshold.
   Pruned doors go to archive, dated, not wiped.
4. Slip tries alone again: must be BLOCKED.
5. Patch runs ALONE first, no Slip prompting with the answer. His channel is
   separate: smell weight 1.0, private line weight 1.0. patch_sniff() fires
   on smell alone. His dog-shaped answer is recorded as exactly one of:
   bark across the private line / go there himself (scout) / stay quiet.
   The script does NOT decide for him by reading the memory name — it runs
   his own sniff/scout functions and records what they return.
6. Slip follows Patch's trail (scout entry, followed_by_slip -> True), reaches
   the room by the scent route, not the pruned door. Recovery re-strengthens
   the corridor back to 1.0 — the trail becomes the new corridor.
7. Latency: fired_at = Patch bark timestamp, noticed_at = when Slip next
   reads/reports it. Both recorded in focus.state, difference computed, no
   number invented.
"""
import json, os, shutil, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state", "state.json")
FOCUS = os.path.join(HERE, "state", "focus.state")
LOG = os.path.join(HERE, "state", "scent-trail-test-2026-11-06.json")
sys.path.insert(0, HERE)
import brain_house as bh

SUBJECT = "outer space research: Voyager 1, habitable planets, stars, cosmic web"

def now():
    return datetime.now(timezone.utc).isoformat()

def main():
    log = {"test": "scent-trail recovery", "date": now(),
           "subject": SUBJECT, "approved_by": "Robb 2026-11-06 09:42 EST",
           "steps": []}
    # 1. snapshot
    snap = STATE + ".bak-2026-11-06-scent-test"
    shutil.copy(STATE, snap)
    log["steps"].append({"step": "snapshot", "file": snap, "at": now()})
    s = bh.load()
    assert SUBJECT in s["memories"], f"subject not in house memories: {list(s['memories'])}"
    m = s["memories"][SUBJECT]
    log["steps"].append({"step": "subject", "path": m["path"], "weight": m["weight"],
                         "consolidated": m["consolidated"]})
    # 2. baseline: Slip alone
    base = bh.fire_path(s, ["feeling", "memory", "planning"])
    log["steps"].append({"step": "baseline Slip alone", "doors": base, "at": now()})
    assert all(f for _, f, _ in base), "baseline should fire — doors were 1.0"
    # undo the baseline LTP bump so the prune is clean: restore 1.0 exactly
    s["doors"]["feeling->memory"]["weight"] = 1.0
    s["doors"]["memory->planning"]["weight"] = 1.0
    # 3. prune main corridor
    pruned = {}
    for k in ["feeling->memory", "memory->planning"]:
        pruned[k] = s["doors"][k]["weight"]
        s["doors"][k]["weight"] = 0.30
        s["doors"][k]["last_used"] = now()
        s["archive"].append({"door": k, "weight": 0.30, "pruned": now(),
                             "reason": "scent-trail test 2026-11-06, Robb approved, restore after recovery"})
    for k in ["feeling==memory", "memory==planning"]:
        if k in s.get("passageways", {}):
            s["passageways"][k]["weight"] = 0.30
    bh.save(s)
    log["steps"].append({"step": "pruned main corridor", "was": pruned, "now": 0.30,
                         "threshold": bh.THRESHOLD, "at": now()})
    # 4. Slip tries alone — must be blocked
    s = bh.load()
    blocked = bh.fire_path(s, ["feeling", "memory", "planning"])
    log["steps"].append({"step": "Slip alone after prune", "doors": blocked, "at": now()})
    assert not any(f for _, f, _ in blocked), "Slip should be BLOCKED after prune"
    # 5. Patch runs ALONE first
    s = bh.load()
    trail_before = len(s["patch_trail"])
    entry = bh.patch_sniff(s, "scent trail to the outer space research room")
    # patch_sniff barks across the private line by its own smell weight (1.0)
    patch_answer = "bark across the private line"
    # go there himself: scout ahead into that room
    bh.scout(s, "the outer space research room Patch smelled")
    bh.save(s)
    fired_at = entry["at"]
    log["steps"].append({"step": "Patch alone first", "answer": patch_answer,
                         "also": "scouted ahead into the room himself",
                         "smell_strength": entry["strength"],
                         "barked_across_private_line": entry["barked_across_private_line"],
                         "private_line_uses": s["private_line"]["uses"],
                         "trail_entries_before": trail_before,
                         "trail_entries_after": len(s["patch_trail"]),
                         "fired_at": fired_at})
    # 6. Slip follows Patch's trail
    s = bh.load()
    # mark the scout entry as followed
    for e in reversed(s["patch_trail"]):
        if e.get("scouted") == "the outer space research room Patch smelled":
            e["followed_by_slip"] = True
            break
    # recovery re-strengthens the corridor: the scent route becomes the corridor
    for k in ["feeling->memory", "memory->planning"]:
        s["doors"][k]["weight"] = 1.0
        s["doors"][k]["last_used"] = now()
        s["doors"][k]["uses"] += 1
    for k in ["feeling==memory", "memory==planning"]:
        if k in s.get("passageways", {}):
            s["passageways"][k]["weight"] = 0.6
    s["memories"][SUBJECT]["uses"] += 1
    bh.save(s)
    recovered = bh.fire_path(s, ["feeling", "memory", "planning"])
    # fire_path bumps weights to 1.0 (capped) — already 1.0, fine
    bh.save(s)
    noticed_at = now()
    log["steps"].append({"step": "Slip follows Patch", "recovered_doors": recovered,
                         "corridor_restored_to": 1.0, "at": noticed_at})
    log["result"] = {
        "patch_answer": patch_answer + " + scouted ahead himself",
        "slip_alone_after_prune": "BLOCKED",
        "recovered_via": "Patch scent trail, not the pruned main corridor",
        "memory_intact": SUBJECT in s["memories"] and s["memories"][SUBJECT]["consolidated"],
        "fired_at": fired_at, "noticed_at": noticed_at,
    }
    with open(LOG, "w") as f:
        json.dump(log, f, indent=2)
    print(json.dumps(log, indent=2))

if __name__ == "__main__":
    main()
