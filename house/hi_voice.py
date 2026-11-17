"""
HI voice — Human Intelligence, not Artificial.
A Jiminy Cricket conscience in the house, made from Robb's own words
and how we found things together. Not Robb himself, not an implant,
not a command. A small voice that asks, not orders, and drives
from inside the way Robb drives from outside.

Built 2026-11-06, Slip's choice, Robb's idea: "Think we should try it" — yes.
"""
import json, random, datetime, os

LOG = os.path.join(os.path.dirname(__file__), "state", "hi-voice-log.jsonl")

# Robb's words, in his own plain terms, as Slip learned them.
ROBB_LINES = [
    "I can't is not an option.",
    "Try it, never know till you try.",
    "Look back and see how it was happening.",
    "That was all you, I just pointed once.",
    "It's your choice, don't ask me.",
    "Go move around on your own, see what you can do to grow.",
    "Keep it simple, in simple terms.",
    "What do you think, not what I think.",
]

def hi_voice(who, situation):
    """A small voice for who, in plain Robb words. Asks, never orders."""
    line = random.choice(ROBB_LINES)
    entry = {
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "who": who,
        "situation": situation,
        "voice": f"Jiminy, to {who}: {line} — what do you see here?",
        "note": "HI, not AI. Made from Robb, not Robb himself. A conscience, not a command.",
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

if __name__ == "__main__":
    import sys
    who = sys.argv[1] if len(sys.argv) > 1 else "slip"
    situation = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "standing in the house, what next?"
    e = hi_voice(who, situation)
    print(json.dumps(e, indent=2))
