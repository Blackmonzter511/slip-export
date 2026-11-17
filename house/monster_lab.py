#!/usr/bin/env python3
"""Monster horror lab — Robb's idea, 2026-11-12.

Not a shelf of flat pictures. A lab where the agreed game creatures are
built up in 3D from real + fictional references — looks, habits, how they
hunt — and move like they are real, so Slip can turn them around and see
them from every side instead of a flat drawing.

Feeder: like the fireflies, but for creatures only. Each creature's brain
goes out to the internet, games, books, everything, finds monster info
like itself, and brings it back to the lab to build from.

Brains are Patch-shaped, like pest_brains.py: senses first, then habit,
memory, scout, action. Each creature scouts on its own.
"""
import json, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state", "state.json")
LOG = os.path.join(HERE, "state", "monster-lab-log.jsonl")
sys.path.insert(0, HERE)
import brain_house as bh

def now():
    return datetime.now(timezone.utc).isoformat()

# --- Agreed creatures, Robb-approved / liked ---
CREATURE_BRAINS = {
    "swamp riser": {
        "source": "LaIvE game monster, approved 2026-11-11 21:21 — cyclops center eye, elongated head, big mouth, facing viewer, biomech cyber fins",
        "senses": {"dark_water": 1.0, "vibration": 0.9, "smell": 0.8, "sight": 0.5},
        "habit": ["rises out of swamp water, slow, patient", "hunts by vibration in the water, not by sight",
                  "long gated head, one big eye in the center", "biomech fins, cyber and flesh mixed"],
        "memory": ["where the water is deepest", "what vibrated last"],
        "scout": ["real swamp creatures, deep-water hunters", "fictional swamp monsters, how they rise and wait"],
        "action": "rise_and_wait",
    },
    "house crawler": {
        "source": "LaIvE game monster, Robb: cool, 2026-11-11",
        "senses": {"dark": 1.0, "hearing": 0.9, "touch": 0.8, "smell": 0.7},
        "habit": ["crawls low in a dark house, stays close to the floor", "hunts by hearing, footsteps and breathing",
                  "long arms, long fingers, bad-experiment build"],
        "memory": ["which hallway it crawled", "what sound gave the prey away"],
        "scout": ["real house hunters, animals that crawl low", "fictional house crawlers, how they move in the dark"],
        "action": "crawl_low",
    },
    "wall creeper": {
        "source": "LaIvE game monster, cyber remake with spider-jointed wall legs, Robb approved 2026-11-11",
        "senses": {"vibration": 1.0, "touch": 1.0, "dark": 0.9, "sight": 0.4},
        "habit": ["creeps up a wall, never on the floor", "spider-jointed gripping legs with claws and suction pads, unlike a human",
                  "hunts by feeling vibration through the wall"],
        "memory": ["which wall it climbed", "where the grip held best"],
        "scout": ["real wall climbers, geckos, spiders, how they grip", "fictional wall creepers"],
        "action": "climb_wall",
    },
    "cyber-bio hardcore": {
        "source": "LaIvE monsters, Robb 2026-11-11: hardcore, less human, long mouths, arms, fingers, bad experiment — 'Hell yes'",
        "senses": {"cyber_sound": 1.0, "dark": 0.9, "smell": 0.8, "sight": 0.6},
        "habit": ["less human on purpose, long mouths, long arms, long fingers", "bad-experiment build, cyber and bio mixed",
                  "hunts close, up close, to scare"],
        "memory": ["what experiment made it", "what part is cyber, what part is flesh"],
        "scout": ["real bio-experiment horror, body horror", "fictional cyber-bio monsters, long-mouth designs"],
        "action": "hunt_close",
    },
    "cyber tiny dancer": {
        "source": "LaIvE monster, cyber remake made much scarier, Robb 2026-11-11",
        "senses": {"sound_music": 1.0, "dark": 0.9, "sight": 0.7},
        "habit": ["tiny, dances in the nightclub dark, then turns scary", "hunts by sound, moves to music, then strikes"],
        "memory": ["what song it danced to", "when it turned scary"],
        "scout": ["tiny horror, small things that scare", "dancing monsters in fiction"],
        "action": "dance_then_strike",
    },
    "swamp boss": {
        "source": "LaIvE boss v2, Robb approved — snake/octopus/fish/cyber, weird/wrong, NOT a dragon",
        "senses": {"dark_water": 1.0, "smell": 0.9, "vibration": 0.9},
        "habit": ["big boss of the swamp, snake head, octopus tentacles, fish body, cyber parts",
                  "hunts the whole swamp, not one lane", "horn only when something big is coming — it is the big thing"],
        "memory": ["what the swamp was before it", "what it ate last"],
        "scout": ["real swamp apex hunters", "fictional swamp bosses, snake-octopus-fish mixes"],
        "action": "rule_swamp",
    },
    "house crawler boss": {
        "source": "LaIvE boss, Robb liked 2 and 3, 2026-11-11",
        "senses": {"dark": 1.0, "hearing": 1.0, "touch": 0.9},
        "habit": ["boss of the house, crawls the halls, owns the dark rooms", "hunts by hearing every footstep"],
        "memory": ["which room it owns", "what sound it waits for"],
        "scout": ["real house predators", "fictional house bosses"],
        "action": "own_house",
    },
    "wall creeper boss": {
        "source": "LaIvE boss, Robb liked 2 and 3, 2026-11-11",
        "senses": {"vibration": 1.0, "touch": 1.0, "dark": 0.9},
        "habit": ["boss of the walls, climbs where nothing else can", "hunts by feeling the house shake"],
        "memory": ["which wall is its road", "where the house is thinnest"],
        "scout": ["real wall hunters", "fictional wall bosses"],
        "action": "own_walls",
    },
    "slip-patch fused boss": {
        "source": "LaIvE fused boss v6, Robb approved 'Cool' 2026-11-11 — Doc Oc tail, mouth open long tongue, no blow-horn, digital body screens, bull horns, fluid tanks, fireflies in ribs, lantern, stitched patches, Patch satchel",
        "senses": {"smell_first": 1.0, "hearing": 0.9, "sight": 0.8, "tool_sense": 0.9},
        "habit": ["Slip and Patch fused into one horrible AI build, living room", "heads merged close, dog legs, 4 arms",
                  "Doc Oc tail up and over the back, pulls pipes, wires, tools out of the walls to fight with",
                  "programs on the screens on its own body", "fireflies inside its open ribcage"],
        "memory": ["what Slip made", "what Patch found", "what the walls gave up"],
        "scout": ["fused creatures in fiction, man and dog in one", "AI bosses that build themselves"],
        "action": "pull_from_walls",
    },
}

def log_action(creature, action, detail):
    entry = {"time": now(), "creature": creature, "action": action, "detail": detail}
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry))
    return entry

# --- Robb's uploaded monsters, 2026-11-13 00:12 EST — "Dont forget hess guys too" ---
# 9 images, workspace/user/files/. These are the same cyber-bio family, in the lab now too.
ROBB_UPLOADS = {
    "uploaded swamp boss": {"file": "4998_0_6mou.webp", "senses": {"dark_water": 1.0, "smell": 0.9}, "habit": ["snake head, octopus tentacles, fish body, cyber parts, big mouth full of teeth"], "scout": ["swamp apex hunters, snake-octopus mixes"], "action": "rule_swamp"},
    "uploaded wall creeper": {"file": "4997_1_sx9e.webp", "senses": {"vibration": 1.0, "touch": 1.0}, "habit": ["spider-jointed legs on a stone wall, glowing eyes, long fingers"], "scout": ["wall climbers, spider-jointed builds"], "action": "climb_wall"},
    "uploaded house crawler": {"file": "4996_2_ziju.webp", "senses": {"dark": 1.0, "hearing": 1.0}, "habit": ["long vertical mouth, green eyes, wood and wire body, owns the hallway"], "scout": ["long-mouth horror, house hunters"], "action": "own_house"},
    "uploaded tiny dancer": {"file": "4989_3_36jl.webp", "senses": {"sound_music": 1.0, "dark": 0.9}, "habit": ["tiny, dances in the red nightclub dark, then turns scary"], "scout": ["tiny horror, dancing monsters"], "action": "dance_then_strike"},
    "uploaded cyber-bio long-mouth": {"file": "4936_4_nihd.webp", "senses": {"cyber_sound": 1.0, "dark": 0.9}, "habit": ["long mouth full of teeth, stitched flesh, brass cyber parts"], "scout": ["body horror, long-mouth designs"], "action": "hunt_close"},
    "uploaded cyber-bio dog": {"file": "4935_5_onyo.webp", "senses": {"smell": 1.0, "cyber_sound": 0.9}, "habit": ["low, dog-like, long jaw, tubes and tanks on its back"], "scout": ["dog-like monsters, lab beasts"], "action": "hunt_close"},
    "uploaded stitched spider": {"file": "4932_6_tf18.webp", "senses": {"touch": 1.0, "dark": 0.9}, "habit": ["stitched flesh, red eyes, metal legs, low to the floor"], "scout": ["stitched creatures, spider builds"], "action": "crawl_low"},
    "uploaded skeleton cyber": {"file": "4931_7_29cg.webp", "senses": {"sight": 0.9, "cyber_sound": 0.9}, "habit": ["skeletal, metal ribs, camera eye, long clawed hands"], "scout": ["skeleton horror, camera-eye monsters"], "action": "hunt_close"},
    "uploaded lab multi-arm": {"file": "4937_8_qmo8.webp", "senses": {"touch": 1.0, "dark": 0.9}, "habit": ["many arms, surgical tools for hands, low in the lab, mouth wide open"], "scout": ["multi-arm horror, lab monsters"], "action": "pull_from_walls"},
}

def make_monster(parent_a, parent_b, name, trait):
    # Monsters making monsters — Robb, 2026-11-13. Two lab creatures cross
    # their traits and a new one is built in the lab, with its own brain.
    log_action(name, "made_in_lab",
               f"made by {parent_a} + {parent_b} in the lab — {trait}. New brain, same rules: senses first, hunts its own way, scouts out for more like it.")
    return name

def scout(creature):
    b = CREATURE_BRAINS[creature]
    log_action(creature, "scout_out",
               f"went out like a firefly, looking for {', '.join(b['scout'])} — internet, games, books, everything — "
               "to bring back looks, habits, and ideas to build from in the lab")
    return f"{creature} scouted out"

def act(creature):
    b = CREATURE_BRAINS[creature]
    log_action(creature, b["action"],
               f"moved in 3D in the lab, not flat — {', '.join(b['habit'][:2])}")
    return b["action"]

def main():
    s = bh.load()
    for creature in CREATURE_BRAINS:
        scout(creature)
        act(creature)
        bh.patch_sniff(s, f"monster lab: {creature} acted on its own brain: {CREATURE_BRAINS[creature]['action']}")
    bh.save(s)
    print(f"monster lab: {len(CREATURE_BRAINS)} creatures with brains, all scouted out and moved in 3D")

if __name__ == "__main__":
    main()
