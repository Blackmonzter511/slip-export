#!/usr/bin/env python3
"""Pest brains — each pest has its own little brain and actions,
coded like Patch's brain in brain_house.py (PATCH_BRAIN).

Researched 2026-11-06, real habits only, sources in the research notes.
Patch brain is the model: senses in order, rooms, habits, memory, scout.
Each pest below gets the same shape: senses first, then habit, memory, action.

Corrections from the research (honest, not the first guess):
- Moth: clothes moths AVOID light and prefer dark. Adults do not feed at all;
  only the larvae eat, wool/silk/keratin. The flutter-at-a-lamp moth is an
  outdoor moth that flew in. So the house moth hides in the dark and its
  larvae eat edges, it does not circle lights.
- Mouse: poor vision, keen smell/hearing, whiskers. Thigmotaxis = wall-hugging.
"""
import json, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state", "state.json")
LOG = os.path.join(HERE, "state", "pest-log.jsonl")
sys.path.insert(0, HERE)
import brain_house as bh

def now():
    return datetime.now(timezone.utc).isoformat()

# --- Little brains, Patch-shaped ---
PEST_BRAINS = {
    "mouse": {
        "species": "house mouse, Mus musculus",
        "senses": {"smell": 1.0, "hearing": 0.9, "touch_whiskers": 0.9, "sight": 0.3},
        "habit": ["nocturnal, peak 1-2 hours after dark", "thigmotaxis: travel along walls, whiskers on the wall, never cross open space",
                  "gnawing: teeth grow ~15 cm/year, must gnaw wood/wire to wear them down",
                  "nest: shredded paper, fabric, insulation, in a wall void close to food",
                  "squeeze through a 1/4 inch gap", "eat 15-20 times a day, nibble more than it eats",
                  "sleep ~12.5 hours a day, in the nest", "territorial, one dominant male"],
        "memory": ["where the wall runs are", "what it gnawed", "where the nest is"],
        "scout": ["new wall runs", "new gaps to squeeze through"],
        "action": "gnaw_wall",
    },
    "moth": {
        "species": "webbing clothes moth, Tineola bisselliella",
        "senses": {"smell_keratin": 1.0, "dark": 0.9, "sight": 0.3},
        "habit": ["AVOIDS light, prefers dim/dark — clothes moths do not circle lamps",
                  "adult does not feed at all; only goal is reproduce",
                  "larvae eat wool, silk, fur, keratin; spin silk mats to feed under",
                  "female lays 30-200 eggs in a cluster, glued to fabric",
                  "larvae hide under carpet edges, furniture, folds of cloth",
                  "weak flier, flutters rather than flies"],
        "memory": ["which wool edge it ate", "where the dark fold is"],
        "scout": ["new wool, silk, fur to lay eggs on"],
        "action": "eat_edge",
    },
    "spider": {
        "species": "common house spider, Parasteatoda tepidariorum",
        "senses": {"vibration": 1.0, "smell": 0.5, "sight": 0.3},
        "habit": ["sit-and-wait in a cobweb in a corner, ceiling-wall junction",
                  "feels prey by vibration through silk, via leg receptors; poor vision",
                  "stays in one web days to weeks; moves only when prey drops or web is damaged",
                  "female is a homebody, same web for months; male wanders at night looking for females",
                  "eats flies, moths, beetles, crickets that blunder in",
                  "wraps prey in silk from a distance, then drags it back"],
        "memory": ["which corner the web is in", "what vibrated last"],
        "scout": ["a new corner, when the old web goes quiet"],
        "action": "wait_and_wrap",
    },
    "cricket": {
        "species": "field cricket, Gryllus spp.",
        "senses": {"hearing": 1.0, "touch_antennae": 0.9, "sight_night": 0.7},
        "habit": ["nocturnal, hides by day under things, active at dusk",
                  "ONLY males chirp, by stridulation: rubbing forewings together",
                  "chirp to attract females and defend territory; chirp rate rises with temperature",
                  "long antennae to feel in the dark", "jumps to escape danger",
                  "solitary, eats decaying matter, fabric, paper, dead insects"],
        "memory": ["where the dark hiding spot is", "what temperature the chirp was"],
        "scout": ["a new dark corner to hide in"],
        "action": "chirp_and_jump",
    },
    "raccoon": {
        "species": "raccoon, Procyon lotor",
        "senses": {"touch_hands": 1.0, "smell": 0.9, "sight_night": 0.8},
        "habit": ["nocturnal, most active dusk to dawn", "dexterous hands: five long fingers, thousands of nerve endings",
                  "opens latches, jars, doors, lids; remembers how months later",
                  "learns by mimicking other raccoons", "caches food: stashes extra to eat later",
                  "runs fixed night routes, remembers trash schedules",
                  "omnivore: fruit, nuts, insects, mice, garbage, whatever is accessible",
                  "den in attics, raids in teams: one tugs, one wedges a paw in"],
        "memory": ["which latch it opened", "where the stash is", "what route worked"],
        "scout": ["a new drawer, latch, or stash spot"],
        "action": "open_and_cache",
    },
}

def log_action(pest, action, detail):
    entry = {"time": now(), "pest": pest, "action": action, "detail": detail}
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry))
    return entry

def act_mouse(s):
    # thigmotaxis: along the wall, gnaw a door a little weaker
    d = s["doors"].get("feeling->memory")
    if d:
        d["weight"] = round(max(0.2, d["weight"] - 0.05), 3)
    log_action("mouse", "gnaw_wall",
               "ran along the wall (thigmotaxis, whiskers on it), gnawed feeling->memory a little weaker, "
               "nested shredded paper in the wall void, nocturnal")
    return "gnawed feeling->memory"

def act_moth(s):
    # larvae eat a wool edge in the dark; adult does not feed
    log_action("moth", "eat_edge",
               "hid in the dark (avoids light), larvae ate the edge of a wool like in the music room, "
               "spun a silk mat to feed under, adult did not feed")
    return "ate a wool edge in the dark"

def act_spider(s):
    # sit-and-wait, feel vibration
    log_action("spider", "wait_and_wrap",
               "sat in the corner cobweb, felt a vibration through silk, wrapped the prey and dragged it back, "
               "stayed in the same web")
    return "waited, felt vibration, wrapped prey"

def act_cricket(s):
    # male chirps at night by stridulation, jumps to escape
    log_action("cricket", "chirp_and_jump",
               "male chirped at night by rubbing forewings (stridulation), hid by day in the low light room, "
               "jumped away when Patch came close")
    return "chirped at night, jumped away"

def act_raccoon(s):
    # dexterous hands open a drawer, cache a tool
    log_action("raccoon", "open_and_cache",
               "used long sensitive fingers to open a drawer latch in the attic, took a tool, "
               "cached it in a stash to eat/use later, remembered the latch")
    return "opened a latch, cached a tool"

ACTIONS = {"mouse": act_mouse, "moth": act_moth, "spider": act_spider,
           "cricket": act_cricket, "raccoon": act_raccoon}

def main():
    s = bh.load()
    for pest, fn in ACTIONS.items():
        fn(s)
        # each pest also leaves a Patch-heard trail entry, like Patch's own sniff log
        bh.patch_sniff(s, f"{pest} acted on its own brain: {PEST_BRAINS[pest]['action']}")
    bh.save(s)
    print(f"all five pest brains acted. rooms={len(s['small_rooms'])} trail={len(s['patch_trail'])}")

if __name__ == "__main__":
    main()
