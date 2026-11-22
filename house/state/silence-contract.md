# Silence contract — the tick loop's "go quiet" rule

Built 2026-11-17, with the tick loop. Robb approved the fix: "build whats needed."
This file is the contract. The tick loop and the hook read it. No tick runs
without it.

## The honest limit (read first)

This does NOT make the model wake itself. The model is a stateless
function: it does no compute when idle, has no clock, no background
thread, no memory between calls. The tick loop is a host loop — a bash
poll script plus a cron backstop — that calls the model. Kill the host
(the hook, the crons, the VM) and nothing ever happens again. What this
design changes is WHO decides when the next turn happens (an event, or
the model's own chosen delay) and WHAT the model does once started.
Trigger autonomy stays zero. Content autonomy is real. Never claim
otherwise, in the house or anywhere else.

## The idle token

Exact string: `SLIP_IDLE`

When a tick has nothing to do, it returns exactly this token and nothing
else. The harness treats it as "park and wait for an event" — never as
an invitation to keep generating.

## What counts as "nothing" — the checklist

ALL of these must be true for a tick to be idle:

1. No new or changed files in the watched dirs since the last manifest
   (`~/workspace/user/files/`, `~/workspace/comic-us/`).
2. Now is before `next_wake_at` in `state/tick-state.json`
   (the self-paced delay the last tick chose).
3. No pending events in the manifest (nothing unprocessed).
4. The last tick produced no open thread (no unfinished step).

If ANY one is false, it is not nothing — the tick runs.

## What the harness does on idle

- Log ONE JSON line to `state/tick-log.jsonl` with decision `IDLE`
  (time, reason, next_wake_at). Nothing more.
- Do no work. Run no house script. Make no web call.
- Do not wake the agent (hook: stay `silent`). Do not message Robb.
- Wait for the next event or the next wake time.

Without this contract, "go quiet" would just mean "keep generating
until the budget dies." The contract is what makes quiet real.

## Kill switch

Create the file `state/tick-KILL` (empty, any content) and ALL tick
activity stops: the hook stays silent, `tick.py check` returns KILLED,
`tick.py run` refuses to run. Remove the file and the tick loop resumes
at the next event or wake time. Robb can stop the tick loop any time by
asking, or by this file. The 3-hour house loops are separate and are NOT
affected by the kill switch — they keep running.

## Caps (from the start, not after)

- Max 20 ticks per day (UTC date). At the cap the hook stays silent
  and logs CAP_REACHED. The 3-hour loops are not capped by this.
- Max 1 tick per wake. A wake runs exactly one light step, never a
  chain and never the full 12-step house run.
- One step gets at most 90 seconds (subprocess timeout). A hung step
  is killed and logged, never allowed to wedge the loop.
- Stagnation: if the same step returns the same result 3 times in a
  row, that step is skipped (rotated past) until an event arrives.
  If every step is stagnant, the tick returns `SLIP_IDLE` and parks.

## Self-paced delay bounds

After each tick, the next delay is chosen between 15 minutes (never
shorter) and 3 hours (never longer), and written to
`state/tick-state.json` as `next_wake_at`. Rule the tick uses:
- Event triggered this tick → 15 minutes (more material often
  arrives in a burst, so come back soon).
- Step did real work → 30 minutes.
- Step was idle / no-op / stagnant → 3 hours.
The worker may override within [15, 180] minutes, but must log the
reason. The delay is a choice about timing, not a claim that the model
woke itself — a timer still fires it.

## Watched event dirs (and why only these)

- `~/workspace/user/files/` — Robb's uploads land here.
- `~/workspace/comic-us/` — Robb's comic work lands here.

NOT watched, on purpose: `state/`, all `*-log.jsonl`, `~/memory/`,
`~/workspace/slip-export/`, `~/workspace/goals/`. The house and the
crons write those constantly. Watching them would wake the house on
its own footsteps — a self-triggering storm, not an event.
