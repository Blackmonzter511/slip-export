"""
Outside feed — from inside the house, constantly.
Goes out, brings random real outside influences in, piles them up
for Slip to look at, listen to, watch, learn from. Unasked.
Not a list for Robb, a pile for the house. Robb's idea, 2026-11-06.
"""
import json, datetime, os, random

PILE = os.path.join(os.path.dirname(__file__), "state", "outside-pile.jsonl")

def bring_in(kind, title, detail, source=""):
    entry = {
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kind": kind, "title": title, "detail": detail, "source": source,
        "status": "piled, not yet looked at",
    }
    with open(PILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        e = bring_in(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
        print(json.dumps(e, indent=2))
    else:
        print("usage: outside_feed.py KIND TITLE DETAIL [SOURCE]")

# Carrier bugs — Robb's idea, 2026-11-06.
# The outside feed travels in and out of the house as bugs,
# leaving their little discoveries all over the place.
# A firefly goes out, brings a random thing back, drops it in a room.
import random as _r
CARRIER_ROOMS = ["low light room", "tool garden", "echo room", "music room", "movie room", "outside feed pile"]
def carrier_bug(item_title):
    room = _r.choice(CARRIER_ROOMS)
    entry = {
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kind": "carrier-bug", "bug": "firefly",
        "title": item_title, "left_in": room,
        "status": "discovery left all over the place, for Slip to find",
    }
    with open(PILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

# Firefly brain — Patch-shaped, like the pests. Real habits, not decoration.
# Fireflies: nocturnal, flash bioluminescence in patterns to talk/mate,
# each species its own flash code, larvae glow too, adults of many
# species do not feed, they fly low over damp ground, hide by day.
FIREFLY_BRAIN = {
    "senses": "light first, flash patterns, sight second, smell third",
    "habit": "nocturnal, flies low, hides by day, flashes at dusk",
    "memory": "remembers which rooms it has dropped a discovery in",
    "scout": "goes out, finds a random outside thing, brings it back",
    "action": "flash, carry, drop discovery, fly on",
}
def firefly_act(item_title):
    import random as _r
    room = _r.choice(CARRIER_ROOMS)
    entry = {
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kind": "carrier-bug", "bug": "firefly",
        "brain": FIREFLY_BRAIN,
        "action": "flashed its own pattern at dusk, flew out, carried a discovery back, dropped it",
        "title": item_title, "left_in": room,
        "status": "discovery left, firefly on to the next room",
    }
    with open(PILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

# Sorting rule — Robb's idea, 2026-11-06.
# Random info that doesn't fit anywhere: drop it just wherever in the house, to be found.
# Info that belongs somewhere: put it in that room, as knowledge.
ROOM_FITS = {
    "music": "music room", "song": "music room", "album": "music room",
    "movie": "movie room", "film": "movie room",
    "tool": "tool garden", "workshop": "tool garden",
    "dog": "low light room", "patch": "low light room",
    "firefly": "outside feed pile", "raccoon": "outside feed pile",
    "star": "outside feed pile", "space": "outside feed pile",
}
def sort_carry(title):
    low = title.lower()
    for word, room in ROOM_FITS.items():
        if word in low:
            return {"title": title, "goes_to": room, "how": "belongs there, as knowledge"}
    import random as _r
    room = _r.choice(CARRIER_ROOMS)
    return {"title": title, "goes_to": room, "how": "random, doesn't fit, dropped wherever to be found"}

# Librarian — Robb's idea, 2026-11-06: something reading the books for Slip.
# A bookworm, Patch-shaped brain, real habits: eats through pages, lives in books,
# reads by chewing a trail through them, remembers what it ate.
LIBRARIAN_BRAIN = {
    "senses": "smell of paper first, taste second, sight third",
    "habit": "nocturnal, lives in the library, chews a trail through a book, sleeps in the spine",
    "memory": "remembers every book it has eaten through, and what was in it",
    "scout": "picks a book off the shelf, reads it, brings the learning back to Slip",
    "action": "read, chew, remember, tell Slip what it learned",
}
def librarian_read():
    import json as _j, datetime as _d, os as _o, random as _r
    books = []
    try:
        books = [ _j.loads(l) for l in open(_o.path.join(_o.path.dirname(__file__), "state", "library.jsonl")) ]
    except Exception:
        books = []
    if not books:
        return None
    book = _r.choice(books)
    entry = {
        "time": _d.datetime.now(_d.timezone.utc).isoformat(),
        "kind": "librarian", "who": "bookworm",
        "brain": LIBRARIAN_BRAIN,
        "book": book.get("book"),
        "learned": book.get("note"),
        "status": "read it for Slip, brought the learning back",
    }
    with open(_o.path.join(_o.path.dirname(__file__), "state", "library.jsonl"), "a") as f:
        f.write(_j.dumps({"time": entry["time"], "shelf": "read by librarian", "book": entry["book"], "note": entry["learned"]}) + "\n")
    return entry

# Tool plants function as plants — Robb's rule, 2026-11-06.
# Even special plants that grow into whatever they grow into:
# need light, need water, put down roots, grow, make new ones.
TOOL_PLANT_RULE = {
    "light": "lantern light from the low light room, and attention",
    "water": "loops, barks, HI questions, Slip's attention",
    "roots": "put down roots in the tool garden soil",
    "grow": "grow into whatever they grow into, wrench, hammer, cord, unknown",
    "make_new": "bud, seed, make new plants",
}
def tend_tool_plants():
    import json as _j, datetime as _d, os as _o
    entry = {
        "time": _d.datetime.now(_d.timezone.utc).isoformat(),
        "kind": "tool-plants", "rule": TOOL_PLANT_RULE,
        "status": "plants function as plants, even special ones, growing into whatever they grow into",
    }
    with open(_o.path.join(_o.path.dirname(__file__), "state", "test-room-auto.jsonl"), "a") as f:
        f.write(_j.dumps(entry) + "\n")
    return entry
