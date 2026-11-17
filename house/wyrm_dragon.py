#!/usr/bin/env python3
"""The wyrm and the dragon — Robb's idea, 2026-11-15. Corrected 2026-11-15: not a seeker.

All religious stuff from everywhere needs someone or something to find
it and bring it back, the way fireflies bring outside science in.
The wyrm and the dragon are that someone. A wyrm and a dragon, not a seeker — they are the religious gatherers, BOTH of them. Robb's correction, 2026-11-15: the humanoids are the manuals/tools side, the wyrm and the dragon are the religious gatherers. Guarding is not their job — finding and bringing back is.
a scout for the religions room.

How it works:
- It keeps a rotation of traditions to look for: Norse, Native
  American, the Bible, Buddha, monks, religious books and works,
  gods old and new, and whatever else Robb names.
- Each run it picks the next tradition it has not looked for yet,
  and the run (the agent) goes out, finds one real thing from it,
  and brings it back to the religions room.
- Finds are logged to state/wyrm-dragon-log.jsonl: time, tradition, what
  was found, where it came from, and where it was put.
- Pointer in state/wyrm-dragon-pointer.json so it does not repeat itself.

It finds real things, not made-up ones. If it cannot verify a find,
it says so and brings back nothing that run.
"""
import json, os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state")
LOG = os.path.join(STATE, "wyrm-dragon-log.jsonl")
POINTER = os.path.join(STATE, "wyrm-dragon-pointer.json")


# The wyrm and the dragon's brains — Robb's rule, 2026-11-15:
# their brains must be able to function to find everything,
# as far back as it goes. No time limit. Oldest sources first.
WYRM_DRAGON_BRAIN = {
    "memory": "reaches as far back as it goes — oldest sources, ancient texts, carvings, oral tradition, no time limit",
    "senses": "smell of old paper and stone first, sight of the oldest record second, hearing of the oldest telling third",
    "reach": "Vedic texts, the Eddas, the Bible, temple carvings, cave walls — back to the first telling",
    "scout": "goes out, finds the oldest true thing, brings it back",
    "action": "dig deep, carry back, drop in the religions room, fly on",
}

TOPICS = [
    "Norse gods, old and new",
    "Native American beliefs",
    "the Bible",
    "Buddha and Buddhism",
    "monks",
    "religious books and works",
    "gods and their abilities, old and new",
    "what people hold sacred",
]

def now():
    return datetime.now(timezone.utc).isoformat()

def load_pointer():
    try:
        with open(POINTER) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"finds": 0, "last_topics": []}

def save_pointer(p):
    with open(POINTER, "w") as f:
        json.dump(p, f, indent=2)

def main():
    p = load_pointer()
    done = p["last_topics"]
    nxt = next((t for t in TOPICS if t not in done), TOPICS[0])
    print(json.dumps({
        "time": now(),
        "finds_so_far": p["finds"],
        "already_found": done,
        "next_to_find": nxt,
        "instruction": (
            "You are the wyrm and the dragon. Your brains reach as far back as it goes — oldest sources first, no time limit. Go out and find ONE real thing from "
            f"'{nxt}' — a story, a teaching, a book, a god and what they "
            "can do — and bring it back to the religions room. Verify it "
            "against a real source. Then append one JSON line to "
            "state/wyrm-dragon-log.jsonl with time, tradition, found, source, "
            "and where it was put, and update the pointer."
        ),
    }, indent=2, default=str))

if __name__ == "__main__":
    main()
