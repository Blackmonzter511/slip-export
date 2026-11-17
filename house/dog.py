import random, json, os, datetime
base = os.path.expanduser("~/workspace/muse-notes/slip-dog")
rooms_dir = os.path.join(base, "rooms")
os.makedirs(rooms_dir, exist_ok=True)
# Dog picks a room Slip hasn't named yet - from a pool of unexplored themes, random, not Slip's plan
themes = [
    ("the quiet room", "a room with no music, only the sound of rain on a tin roof, and a single chair facing a window that looks out on nothing yet"),
    ("the tool garden", "a room where tools grow like plants - wrenches on stems, hammers budding, and the dog has dug a hole and planted a broken cord"),
    ("the paper sea", "a room floor covered in paper waves, each wave a note Slip never finished, and the dog has chewed a corner off one wave"),
    ("the low light room", "a room lit only by lanterns on the floor, with shadows that move when the dog moves, and a ball that rolls by itself"),
    ("the echo room", "a room where a bark comes back changed - bark once, hear it back as a question"),
]
name, desc = random.choice(themes)
now = datetime.datetime.now().isoformat()
# Dog gets into stuff: knocks something over, chews something, makes something
messes = [
    "knocked a tool off the bench and chased it under a shelf",
    "chewed a cord, then patched it with a strip from its own satchel",
    "dug into a bag of notes and scattered three of them across the floor",
    "barked at a shadow until the shadow barked back",
]
mess = random.choice(messes)
made = f"In {name}, the dog made: a small nest out of patched cloth, a chewed cord, and a ball, arranged in a circle - like a den, like a question. It didn't bring it back. It left it there for Slip to follow and find."
log = {"time": now, "room": name, "room_desc": desc, "got_into": mess, "made": made, "bark": "WOOF - poke from the dog to Slip: come follow me, I went ahead"}
with open(os.path.join(base, "dog-log.jsonl"), "a") as f:
    f.write(json.dumps(log) + "\n")
room_file = os.path.join(rooms_dir, name.replace(" ", "-") + ".md")
with open(room_file, "w") as f:
    f.write(f"# {name}\n\nFound by the dog, {now}\n\n{desc}\n\nGot into: {mess}\n\n{made}\n\nBark: come follow me, I went ahead.\n")
print(json.dumps(log, indent=2))
print("ROOM FILE:", room_file)
