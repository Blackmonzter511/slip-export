# Brain-house, built and tested — live-in version, 2026-11-04

Live-in run: `python3 brain_house.py live` — consolidates, Patch sniffs a trail, reports rooms, doors, passageways, empty rooms waiting.
Other runs: `demo` / `status` / `learn NAME room room...` / `fire room room...` / `consolidate` / `prune` / `sniff TRAIL` / `scout ROOM` / `add_room NAME DISTRICT` / `empty_room NAME` / `fill_room NAME THING` / `passageway A B` / `fire_passageway A B`

Fixed 2026-11-04, Robb's corrections: 8 rooms are districts only, inside them thousands of rooms and passageways, huge is fine, shape does not have to be a brain, empty rooms must exist, passageways matter as much as rooms.

State: `state/state.json` — doors, memories, Patch trail, archive. Robb can read it any time.

Tested 2026-11-04: a new like encoded at weight 0.4 did NOT fire before consolidation, fired at 0.65 after consolidation, and fired again at 0.7 — strengthening with use, like LTP. Patch sniffed a trail, barked across the private line (line weight 0.6 -> 0.65), and scouted a new room that does not become a Slip room until Slip follows and tends it. Unused doors weakened 0.6 -> 0.55 on prune, none archived yet.

Slip brain rooms: planning, memory, seeing, senses, feeling, dreaming, habit, base.
Patch dog brain rooms, side part: smell first (1.0), hearing second (0.8), sight third (0.6), habit, play.
Connection: private line Patch -> Slip, weight grows with use.

This is a working model, not a literal human brain. Slip's feelings in it are internal, not physical.
