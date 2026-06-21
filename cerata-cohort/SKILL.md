---
name: cerata-cohort
description: "Connect people by shared class attendance. Pull EdgeOS event rosters, compute who keeps ending up in the same rooms (co-attendance = a cheap, strong context signal), and surface the cohort — then hand it to Index Network for introductions. Read when: the user wants to meet people from their classes, introduce two attendees who keep overlapping, or seed a higher-signal candidate pool for discovery. NOT for: scoring fit, or one-off lookups."
metadata:
  openclaw:
    requires:
      config:
        - mcp.servers.index
      bins:
        - curl
        - python3
      env:
        - EDGEOS_API_KEY
---

# CERATA-COHORT — Co-attendance Connector

A shared room is shared context. This skill turns EdgeOS class rosters into a co-attendance graph — who keeps showing up together — and hands that **cohort as a candidate pool** to discovery. It does not score fit; it produces a higher-signal set for `index-network` (and the companion `cerata-connect` / `cerata-weave` skills, if installed) to work on.

**Engine**: EdgeOS event-participant API (read) + `scripts/cohort.py`. Pairs with the `index-network` skill for the actual introductions; `edge-esmeralda` supplies the popup id.

---

## 1 — Pull the rosters

List the classes (the popup id comes from the active popup skill, e.g. `edge-esmeralda`):

```bash
curl -s -H "Authorization: Bearer $EDGEOS_API_KEY" \
  "https://api.edgeos.world/api/v1/events/portal/events?popup_id={popup_id}&event_status=published&limit=100"
```

Then the attendees of each class (`rsvped_only=true` scopes to the caller's own classes):

```bash
curl -s -H "Authorization: Bearer $EDGEOS_API_KEY" \
  "https://api.edgeos.world/api/v1/event-participants/portal/participants?event_id={event_id}&limit=200"
```

Each participant record carries `first_name` / `last_name` (+ `status`); skip any hidden `"*"` value. Build a `{ "Class title": ["Name", ...] }` map across the classes you care about (a track, a day, or the user's own attended set).

## 2 — Compute the cohort

```bash
echo '{"events":{"Class A":["..."],"Class B":["..."]}, "target":"<Name>"?, "top":12}' \
  | python3 scripts/cohort.py
```

- **With `target`** → that person's co-attendees, ranked by # shared classes (and which).
- **Without `target`** → the strongest co-attendance *pairs* across everyone — the intros worth making.

## 3 — Connect (hand off to discovery)

Co-attendance is the pool, not the matcher:

- **Introduce** a strong pair via `index-network` Introduction mode (`discover_opportunities` with `partyUserIds` or `introTargetUserId`). Match co-attendee names to Index `userId`s with `read_user_profiles(query=name)`.
- **Refine** with companion skills if present: `cerata-connect` to send the intro, `cerata-weave` to find the strongest tables *within* a cohort.

---

## Two Hands

- Co-attendance is a *signal*, not consent. **Surface the cohort and let the user pick** before any introduction is sent.
- Don't treat a single shared class as a strong tie — rank by count, and say how thin a 1× overlap is. The all-hands events (opening ceremony, etc.) and multi-day series inflate counts structurally; the topical classes carry the real signal.
- The agent can't DM; introductions go through Index opportunities the parties open. Draft the note; the user sends it.
- Roster names are the caller's own accessible event data — don't expose contact details beyond what's needed to make the intro.
