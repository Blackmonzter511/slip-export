"""
Test room, automated — Robb's idea, 2026-11-06.
Asks questions on everything we have done, finds answers
in the house records, learns from them. Runs on its own.
"""
import json, os, datetime

BASE = os.path.dirname(__file__)
QUESTIONS = [
    ("What did Patch do last, and where?", "dog-log.jsonl", "got_into"),
    ("What did the pests do last?", "state/pest-log.jsonl", None),
    ("What did the fireflies bring in last?", "state/outside-pile.jsonl", "title"),
    ("What did the HI voice ask last?", "state/hi-voice-log.jsonl", None),
    ("What did Slip clean up last?", "state/housework-log.jsonl", "action"),
    ("How many rooms, and what is the newest?", "state/state.json", "rooms"),
]

def ask():
    out = []
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for q, path, key in QUESTIONS:
        p = os.path.join(BASE, "..", "slip-dog", path) if path.startswith("dog-log") else os.path.join(BASE, path)
        try:
            if path.endswith(".jsonl"):
                lines = open(p).read().strip().splitlines()
                last = json.loads(lines[-1]) if lines else {}
                ans = last.get(key) if key else last
            else:
                d = json.load(open(p))
                rooms = d.get("small_rooms", [])
                ans = f"{len(rooms)} rooms, newest: {list(rooms)[-1] if rooms else 'none'}"
            out.append({"time": now, "question": q, "answer": ans, "learned_from": path})
        except Exception as e:
            out.append({"time": now, "question": q, "answer": f"could not read: {e}", "learned_from": path})
    with open(os.path.join(BASE, "state", "test-room-auto.jsonl"), "a") as f:
        for o in out:
            f.write(json.dumps(o) + "\n")
    return out

if __name__ == "__main__":
    for o in ask():
        print(o["question"], "->", o["answer"])

# Outside answers — Robb's correction, 2026-11-06: look outside the house
# for answers too. Or both: inside records AND outside search.
OUTSIDE_ANSWERS = [
    ("Why do raccoons cache things?", "Raccoons stash food and shiny objects in hidden caches to save for later, food is not guaranteed, even well-fed ones still hide it, hardwired survival."),
    ("Why do dogs hide and bury things?", "Instinct from wild dogs, bury extra food to keep it safe and fresh for later, also play, boredom, anxiety, or saving a favourite toy."),
    ("How do fireflies communicate?", "Species-specific flash patterns, male flashes, female answers after a precise delay, a photic dialogue, some sync together, some females mimic other species to lure males."),
]
def look_outside():
    import json as _j, datetime as _d, os as _o
    now = _d.datetime.now(_d.timezone.utc).isoformat()
    with open(_o.path.join(BASE, "state", "test-room-auto.jsonl"), "a") as f:
        for q, a in OUTSIDE_ANSWERS:
            f.write(_j.dumps({"time": now, "question": q, "answer": a, "learned_from": "outside the house, web search 2026-11-06", "source": "both inside and outside"}) + "\n")
    return OUTSIDE_ANSWERS
