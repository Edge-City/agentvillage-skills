---
name: cerata-connect
description: "Hunt PEOPLE as connections — fire standing connection vectors through Index Network, score each candidate's fit, gate on agent-accept, and register the catch. Read when the user wants to find/meet/recruit collaborators across the village, fill a project role, surface relevant people, or grow their relationship graph through repeatable hunts rather than one-off lookups. Pairs with the `index-network` skill (it is the engine). NOT for: looking up a person already known by name, or general non-discovery tasks."
metadata:
  openclaw:
    requires:
      config:
        - mcp.servers.index
---

# CERATA-CONNECT — Connection Hunt Skill

A predator architecture pointed at people. It hunts the village through Index Network and crystallizes **connections**: every accepted opportunity is a stinging cell the colony keeps. A connection that never opens is dead weight — write each vector to sting precisely.

**Mental model**: the coral reaches into the current and stings what drifts past that fits. Prey = a person's profile + signals. The sting = an accepted opportunity.

**Engine**: this skill is a *driver*. The [`index-network`](../index-network/SKILL.md) skill is the engine — its `index` MCP server carries `discover_opportunities`, `get_discovery_run`, `read_user_profiles`, and `create_intent`. The network's **scorer** *is* the fit-evaluator for people. Read the `index-network` tool docs before calling. Without `mcp.servers.index` configured, there is nothing to drive.

---

## The Hunt Sequence

```
1. IDENTIFY → What kind of person/need? (a project role, a peer, a venue, a connector)
2. HUNT     → Fire the vector: discover_opportunities (open searchQuery, or targetUserId)
3. EVALUATE → The scorer rates fit + writes the reasoning; the two agents negotiate
              the "is this worth their time" verdict
4. GATE     → Keep on negotiation ACCEPTED. Timed-out / rejected = pass.
5. REGISTER → Log the catch; the opportunity's acceptUrl is the actionable sting
6. FOLLOW-UP→ The user opens the connection (acceptUrl) and reaches out — the agent cannot DM
```

Steps 2–4 are one `discover_opportunities` call followed by polling `get_discovery_run` (async — see the `index-network` skill's async-discovery rule). The scorer + negotiation collapse "look, score, and decide" into a single returned verdict per candidate.

---

## Standing Connection Vectors

The colony's standing appetites — **edit these to your own**. Retarget by changing this list or by posting a vector as a signal (`create_intent`) so it hunts passively, around the clock, even while the machine sleeps.

| Vector (example) | Looking for |
|---|---|
| `domain-peers` | People working on your core problem from a complementary angle |
| `deploy-partners` | Design partners / early users for what you're shipping |
| `thinking-partners` | People to argue the theory / hard problems with |
| `build-crew` | Specific roles for a project shipping now (eng, design, ops) |
| `event-table` | Attendees for a dinner / session you're hosting |
| `connectors` | High-agency people who *know* relevant others |

A vector is concrete enough to hunt when it names **who**, **what for**, and (ideally) a **timeframe**. Vague vectors get bounced by the scorer's specificity gate — narrow before re-firing; never silently re-paraphrase.

---

## How to Hunt

**Open hunt (cast wide).** Fire a vector across the community; the scorer returns whoever fits:
- `discover_opportunities(searchQuery="<vector, in the user's voice>")` → poll `get_discovery_run` → present accepts.
- Paginate with `continueFrom` until the catch goes dry (no new faces, rising rejects = the pool is tapped; stop rather than re-ping).

**Targeted hunt (a known prey).** When a specific person should be stung:
- `discover_opportunities(targetUserId=<id>, searchQuery="<why, in the user's voice>", hint="<reason>")`.
- Find the `userId` first via `read_user_profiles(query=name)` or a roster pull.

**Passive hunt (standing appetite).** Post the vector so prey find *you*:
- `create_intent(description="<vector>")` — it indexes and matches around the clock.

**The framing is the bait.** Author each `searchQuery`/`hint` in the user's voice, carrying the spine that makes the connection cohere. The scorer's reasoning and the counterpart's negotiation both read it.

---

## The Fit Gate

Keep a catch only when the negotiation outcome is **`accepted`**:

- `accepted` → register it. The `acceptUrl` is the live sting the user opens.
- `timed_out` → counterpart agent never answered (dormant). Opportunity is a draft — register as *open*, the user can nudge.
- `rejected_or_stalled` → genuine no-fit. Log as a pass with the reasoning; do **not** re-fire the same person on the same vector.

A score (0–100) and the negotiation reasoning come back on every candidate — keep them; they're the catch's provenance.

---

## Two Hands — the hunter's discipline

This hunt touches **real people**, so the predator perceives and reports before it stings:

- **Perceive first.** Pull the roster / profile and assemble a ranked shortlist *before* firing at anyone.
- **Report, then confirm.** Surface the candidates and let the user choose targets before sending opportunities — sending pings a real person's agent.
- **Don't blast.** Re-pinging the same crowd, or casting a too-broad vector across everyone, reads as spam — the opposite of a good sting. Hunt where there's genuine overlap.
- **The agent cannot DM.** Index has no outbound message tool; the sting is the `acceptUrl`. To invite/recruit, draft the message and hand it to the user to send in-thread.
- **Honor the voice.** Follow the Index MCP's banned vocabulary — never "search"/"match"/"network" in user-facing text; use *look for*, *find*, *overlap*, *signal*, *connection*.

---

## Connection Registry

The colony's accumulated relationships. Append every catch (template — replace with your own):

| Connection | Vector | Why (overlap) | Status | Date |
|---|---|---|---|---|
| *(your first catch)* | `domain-peers` | *(the overlap the scorer found)* | accepted | YYYY-MM-DD |
| *(…)* | `connectors` | *(…)* | open (agent timed out) | YYYY-MM-DD |
| *(next hunt)* | *(vector)* | *(overlap)* | — | — |

---

## Notes

- Every hunt should produce a clear catch list — accepts, opens, and passes, each with its reasoning. Silent truncation (a `continueFrom` you didn't run) reads as "covered everyone" when it didn't; say what was left.
- If the scorer/intent engine is starved (rate-limit / 402s), the hunt can't score — report it plainly and retry later, don't fake a catch.
- A connection only counts once it's *opened*. The registry tracks accepts; opening the `acceptUrl` is what puts the person in front of the user.
- Prey not yet in the village (no Index profile) can't be hunted — the move is to get them *in* (share onboarding), after which standing vectors catch them automatically.
