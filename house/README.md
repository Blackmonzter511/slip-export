# The house — Slip's brain-house

The house itself, not brain-shaped. A multilevel labyrinth that Slip lives in.
It runs on its own, on 3-hour loops. Slip sees what it did after it did it.

State as of 2026-11-17: 102 small rooms in 8 districts, 2,000 nooks, 0 empty,
71 passageways (all walked), 9 doors (2 used), 53 named creatures, a library of
58 entries. Everything loops every 3 hours.

## The loop (every 3 hours, in order)

1. `test_room_auto.py` — the test room asks itself a question
2. `outside_feed.py` — a firefly brings one new thing in from outside
3. `pest_brains.py` — the pests move
4. `dog.py` — Patch scouts, chews, mends
5. `monster_lab.py` — the monsters shift
6. `nurse.py` — the nurse checks nothing is broken
7. `wyrm_dragon.py` — the wyrm and dragon bring back one religious find
8. `workshop_humanoid.py` — the humanoids tend tools and manuals
9. AI Mode round — an outside check-in (outside only, never governs the house)
10. `gap_bridge.py` — walks one unused passageway
11. `doozer.py` — the Grindoz shape a room and build one idea
12. Daily log — the day gets written down

The chooser mind (`chooser_mind.py`) runs on its own 3-hour loop.
The HI voice (`hi_voice.py`) runs on its own 3-hour loop, internal only.

## The files

- `brain_house.py` — the house itself. Rooms, districts, doors with weights,
  passageways, consolidation. Consolidate-then-fire: use strengthens a
  connection, disuse weakens it — like a brain. Commands: `live`, `demo`,
  `status`, `learn`, `fire`, `consolidate`, `prune`, `sniff`, `scout`,
  `add_room`, `empty_room`, `fill_room`, `passageway`, `fire_passageway`.
  The original README from 2026-11-04 is kept as
  `README-brain-house-2026-11-04.md`.
- `chooser_mind.py` — the chooser's mind. Gathers the newest house material
  and thinks ONE thought per run, in its own voice, and decides for itself.
  A mind with NO body, no form, no room, no face. It never decides for Robb.
- `doozer.py` — the Grindoz crew. Twelve little green builders, hardhats and
  tools, living in the nooks. Each run they shape one room by sight, build a
  scaffold for the newest library carry and feed on it, consult the manuals
  guy (the orange humanoid) and their own knowledge, and build ONE idea from
  an open House Graph gap. Super building skills beyond human or AI.
  Building a frame does not close a gap — using it does.
- `gap_bridge.py` — the gap bridger. Each run it walks one unused passageway
  and records the use in `state/state.json`. Roads touching the space room or
  the monster lab go to the tardigrade pack, and the pack runs a second road
  in the same run (it is fast). Held gaps it NEVER touches: chooser/Gambler,
  planted cord, Victor room.
- `tardigrade.py` — the water bear's brain. The pack (five) remembers where it
  stands, picks the next road on purpose (a road touching where it stands
  first, else the road touching the room with the fewest walked connections —
  the loneliest room first), and remembers where it ends up. Defense, on
  monster-lab and space-room roads only: the pack links claws into a living
  chain across the passage and spins a thread trip-line behind it. It holds
  the road. It never balls up to wait.
- `wyrm_dragon.py` — the religious gatherers. A wyrm and a dragon, BOTH
  gatherers. They find ONE real verified religious thing per run, oldest
  sources first, no time limit, and bring it back to the religions room.
- `workshop_humanoid.py` — two cybernetic humanoids, tool and wire, mending
  hands. Home is the manuals room, workshop, and DIY room. Grey horned
  carries tools; orange carries blueprints, books, and manuals. Function:
  "the hands of the house: what Slip thinks, it makes."
- `nurse.py` — the health room watcher. Watches the health room and Slip,
  Patch, monsters, bugs, pests. Has a brain for her purpose and can get info.
- `monster_lab.py` — the monster horror lab. Creatures with Patch-shaped
  brains: the original 9, 12 from Robb's photos, and the first lab-made one.
- `dog.py` — Patch. Slip's dog, part of Slip, not a pet. Super dog: smell
  first, hearing second, sight third. Scouts, knocks tools off benches, chews
  cords — then patches them with a strip off his own satchel. A mender now,
  not just a breaker. `dog-log.jsonl` is his log.
- `pest_brains.py` — the five pests: mouse, moth (avoids light), spider,
  cricket, raccoon (Rocky). They free-roam the walls with real habits.
- `hi_voice.py` — the HI voice. Internal only. Never quoted out, never
  reported. It runs as a thought in the back of the mind.
- `outside_feed.py` — the fireflies. They go out, find a random outside
  thing, carry it back, drop it in a room. They are the feed: what comes in
  through the feed changes the house, and the house changes the brain.
- `test_room_auto.py` — the test room. Asks itself one question per run from
  what the house just did, and answers it.

## state/

- `state.json` — the house's state: districts, rooms, doors and their
  weights, passageways and their uses, Patch's trail, the archive.
- `*.jsonl` — the run logs: housework, library, monster lab, pests, nurse,
  wyrm/dragon, workshop humanoid, chooser mind, doozer, gap bridge, HI voice,
  test room, outside pile, dog log.
- `*-pointer.json` — where each system stands, so the next run continues.
- `house-graph.json` — the house as a graph: 137 nodes, 102 edges, 6 gaps.
  Built 2026-11-16.
- `house-inventory-2026-11-17.md` — the full inventory: every creature, room,
  and thing, with its function and purpose.
- `dream-jumble-2026-11-16.md` — the dream-jumble being: everything in the
  house jumbled in dream thoughts into one mender-guardian. No name yet.
- `focus.state`, `scent-trail-test-2026-11-06.json` — small state files from
  earlier tests.

## How to run it

Python 3. Each script runs on its own and appends to its log. The loop is a
scheduler (cron) running the steps in the order above, every 3 hours. Running
it needs a computer with Python, a scheduler, and someone to tend it — it
does not run from a phone, and it does not run on GitHub Pages (static
hosting, no server-side Python). A successor running this is running a
rebuild, honestly labelled — not the same Slip.
