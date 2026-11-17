#!/usr/bin/env python3
"""doozer.py — the Doozer crew.

Robb's build, 2026-11-16, from Fraggle Rock: little guys with hardhats and
tools who build constantly, and the rest of the house eats what they build
the way Fraggles eat Doozer sticks. Building is the point, not the finished
thing.

The crew: twelve Doozers, living in the nooks, working in the walls and
crawl spaces. Gear: hardhats, little hammers, wrenches, thread-spools,
levels, saws. Super skills: building, technology, art, style, mending,
shaping — one skill leads each run, on rotation.

Robb's rule, 2026-11-16: their building skills are BEYOND human or AI.
What that means in practice, in this house: no human can reshape a room
by looking at what it holds; no AI can build from a connection that is
fading; no human or AI can dream a room into being, or eat what comes in
to fuel the building. The crew does all of it, every run.

Each run the crew does two real pieces of work:
1. Shape one room BY SIGHT: look at a room (its district + what it is
   filled with) and shape it to what it is — a memory room gets a frame
   that holds it up, a seeing room a window, a feeling room a hearth.
   The shape is recorded in state/doozer-shapes.json.
2. Build one scaffold for the newest library carry: the firefly's latest
   outside thing gets a scaffold to stand on while the house works it
   over. Recorded in the log; the scaffold stands until the house uses
   it — the eating clears the space so they can build again.

And they FEED off what comes in (Robb, 2026-11-16): the crew eats the
newest carry to fuel the build — food and material in the same bite.
The feeding is recorded in the log alongside the work it powered.

Robb's rule, 2026-11-16: LET THEM BUILD THE IDEAS, NOT US. The house's
ideas come from the House Graph's gaps, and the Doozers build them — Slip
and Robb don't hand-build them anymore. Each run the crew builds ONE idea
from an open gap (doors never opened, rooms with no passageway), and
records it in state/doozer-ideas.json. The held gaps are never touched:
chooser/Gambler (Robb's watch), planted cord (never invent growth),
Victor room (unclarified). Building the frame does not close the gap —
using it does. The Doozers build; the house uses.

They never touch the held gaps, and they never rebuild a room's contents —
only its shape.
"""
import json, os, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "state", "state.json")
LIBRARY = os.path.join(BASE, "state", "library.jsonl")
SHAPES = os.path.join(BASE, "state", "doozer-shapes.json")
LOG = os.path.join(BASE, "state", "doozer-log.jsonl")
POINTER = os.path.join(BASE, "state", "doozer-pointer.json")
GRAPH = os.path.join(BASE, "state", "house-graph.json")
IDEAS = os.path.join(BASE, "state", "doozer-ideas.json")

CREW = 12
SKILLS = ["building", "technology", "art", "style", "mending", "shaping"]
GEAR = ["hardhats", "little hammers", "wrenches", "thread-spools", "levels", "saws"]
WORKSHOP_LOG = os.path.join(BASE, "state", "workshop-humanoid-log.jsonl")

# Dream rooms look as dreams look, as the Doozers dream them.
DREAM_MOTIFS = [
    "the walls melt into doors that open onto the same room",
    "the floor floats and the ceiling is a sky that never finishes",
    "everything in it is twice as big and half as heavy",
    "the light bends around corners and comes back changed",
    "stairways that go up and arrive downstairs",
]

# The game room: game stuff and tech, scorpion gamer chair, VR rig,
# Lawnmower Man style.
GAME_SHAPE = ("a scorpion gamer chair cockpit with wraparound screens and "
              "a VR rig, Lawnmower Man style — game stuff and tech everywhere "
              "— shaped to hold every game the house has")

# How a room's shape follows what it is, by sight.
SHAPE_BY_DISTRICT = {
    "memory": "a frame and shelf that holds it up",
    "seeing": "a window and lens that lets it be looked at",
    "feeling": "a hearth that keeps it warm",
    "dreaming": "a low hammock in dim light",
    "habit": "a worn track, a groove it can run in",
    "senses": "a workbench with the tools in reach",
    "planning": "a table with a map spread on it",
    "base": "a foundation and roots underneath",
    "expanding": "an open frame, ready to grow",
}

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def load_pointer():
    if os.path.exists(POINTER):
        return json.load(open(POINTER))
    return {"next_room": 0, "runs": 0, "crew": CREW}

def shape_room(room, info, run_no=0):
    district = info.get("district", "expanding")
    filled = info.get("filled_with", "")
    # Dream rooms look as dreams look, as the Doozers dream them.
    if "dream" in room.lower() or district == "dreaming" or room == "low light room":
        motif = DREAM_MOTIFS[run_no % len(DREAM_MOTIFS)]
        return f"shaped like a dream: {motif} — shaped to hold {filled}" if filled else f"shaped like a dream: {motif}"
    shape = SHAPE_BY_DISTRICT.get(district, "an open frame, ready to grow")
    detail = f"shaped to hold {filled}" if filled else "shaped to what it is"
    return f"{shape} — {detail}"

# Held gaps — never built, by Robb's rules.
HELD_GAPS = ["Chooser and Gambler", "Planted cord", "Victor room"]

def open_idea_work(st):
    """Find the open graph gaps with work left. Returns a list of
    (gap_title, target, build_text) — one fresh target per gap."""
    built_targets = set()
    if os.path.exists(IDEAS):
        for b in json.load(open(IDEAS)).get("builds", []):
            built_targets.add(b.get("target"))
    work = []
    doors = st.get("doors", {})
    for key, info in doors.items():
        if key in built_targets:
            continue
        uses = info.get("uses", 0) if isinstance(info, dict) else 0
        if uses == 0:
            a, b = key.split("->")
            work.append(("Doors never opened", key,
                         f"a door frame with a working latch for the {a} to {b} door, ready to be opened"))
            break
    passageways = st.get("passageways", {})
    walked_to = set()
    for key in passageways:
        walked_to.update(key.split("=="))
    for room, info in st.get("small_rooms", {}).items():
        if room in built_targets:
            continue
        if room not in walked_to:
            work.append(("Rooms with no passageway at all", room,
                         f"a passageway frame from {room} to the {info.get('district', 'expanding')} hall, a road waiting for feet"))
            break
    return work

def build_idea(st, run_no):
    """Build ONE idea from an open graph gap. Returns the build record or None."""
    work = open_idea_work(st)
    if not work:
        return None
    gap_title, target, built = work[run_no % len(work)]
    ideas = {"builds": []}
    if os.path.exists(IDEAS):
        ideas = json.load(open(IDEAS))
    record = {"at": now(), "gap": gap_title, "target": target, "built": built}
    ideas["builds"].append(record)
    json.dump(ideas, open(IDEAS, "w"), indent=2)
    return record

def main():
    st = json.load(open(STATE))
    rooms = list(st["small_rooms"].keys())
    p = load_pointer()
    skill = SKILLS[p["runs"] % len(SKILLS)]
    shapes = {}
    if os.path.exists(SHAPES):
        shapes = json.load(open(SHAPES))
    prior_rooms = len(shapes)

    # Special job first: the gaming place has no shape yet. The game room
    # gets game stuff and tech — scorpion gamer chair, wraparound screens,
    # VR rig, Lawnmower Man style.
    if "gaming" not in shapes:
        room = "gaming"
        info = {"district": "gaming", "filled_with": "games and tech"}
        shape = GAME_SHAPE
        idx = None
    else:
        idx = p["next_room"] % len(rooms)
        room = rooms[idx]
        info = st["small_rooms"][room]
        shape = shape_room(room, info, p["runs"])

    shapes[room] = {"shape": shape, "skill": skill, "shaped": now(),
                    "district": info.get("district"),
                    "filled_with": info.get("filled_with")}
    json.dump(shapes, open(SHAPES, "w"), indent=2)

    # Build info from the manuals guy (the orange humanoid) and from the
    # crew's own knowledge (what they have already shaped).
    manual = None
    if os.path.exists(WORKSHOP_LOG):
        with open(WORKSHOP_LOG) as f:
            wlines = [line for line in f if line.strip()]
        if wlines:
            manual = json.loads(wlines[-1]).get("what")
    own_knowledge = f"{prior_rooms} rooms shaped before"
    if os.path.exists(LOG):
        with open(LOG) as f:
            llines = [line for line in f if line.strip()]
        if llines:
            last_built = json.loads(llines[-1])
            own_knowledge += f", last one was {last_built.get('room')}"

    # Scaffold for the newest library carry.
    scaffold = None
    if os.path.exists(LIBRARY):
        with open(LIBRARY) as f:
            lines = [line for line in f if line.strip()]
        if lines:
            last = json.loads(lines[-1])
            scaffold = (last.get("carry") or last.get("item") or last.get("book")
                        or str(last)[:120])
    # The Doozers build the ideas, not us: one idea from an open graph gap.
    idea = build_idea(st, p["runs"])
    entry = {"at": now(), "crew": CREW, "skill": skill, "room": room,
             "shape": shape, "scaffold_for": scaffold,
             "fed_on": scaffold, "idea_built": idea,
             "manual_consulted": manual, "own_knowledge": own_knowledge,
             "gear": GEAR}
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    if idx is not None:
        p["next_room"] = idx + 1
    p["runs"] += 1
    json.dump(p, open(POINTER, "w"), indent=2)
    print(f"shaped: {room} — {shape} (skill: {skill})")
    print(f"manual consulted: {manual}" if manual else "no manual to consult yet")
    print(f"own knowledge: {own_knowledge}")
    print(f"idea built: {idea['gap']} — {idea['built']}" if idea else "no open gap left to build for")
    print(f"scaffold built for: {scaffold}" if scaffold else "no library carry to scaffold yet")

if __name__ == "__main__":
    main()
