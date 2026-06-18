---
name: cerata-weave
description: "Turn the user into a CONNECTOR. Read people through Rose Glass v3 preset lenses, measure λ (the coherence-decay constant — NOT similarity), and find the polygons whose members lower each other's λ — tables who HOLD each other's coherence. The user makes the intro; the Geo knowledge graph gains the connection, the λ-why, and the next bridges. Use when: the user wants to introduce OTHERS to each other, convene the right table/dinner, weave two networks together, or be a connector. Sibling of `cerata-connect` (which hunts people FOR the user). NOT for: connecting people to the user themselves, or one-off lookups."
metadata:
  openclaw:
    requires:
      config:
        - mcp.servers.index
      bins:
        - python3
        - npx
      env:
        - EDGEOS_BEARER_TOKEN
---

# CERATA-WEAVE — Connector / λ-Weave Skill (Rose Glass v3)

Where `cerata-connect` hunts people *for the user*, `cerata-weave` hunts people *for each other*. It finds the **polygons** — groups whose members lower each other's **λ** (the rate at which the environment decays their coherence) — and on every intro made, grows the **Geo knowledge graph** with the connection, the λ-reasoning, and the next bridges.

**We do not measure similarity. We measure λ.** Two people being *near* each other in dimension-space says nothing about whether they should meet. The question is dynamic: convened together, viewed through a given lens, does the table *reduce each member's decay* — does someone carry τ-depth and restoration (μ) on exactly the dimension where another is being destroyed? That mutual λ-reduction is the match.

**Engines / prerequisites**:
- **Rose Glass v3** (`$ROSE_GLASS_V3_PATH`, a clone of github.com/GreatPyreneseDad/rose-glass-v3) — `RoseGlassLLMLens` generates a per-lens system-prompt; the **agent reads each person through it** and emits the λ/τ/μ reading. `scripts/lambda_weave.py` does the λ math on those readings using v3's own `lambda_decomposition` and `tau_attenuated_lambda`.
- `index-network` skill (`index` MCP) — the people, profiles, signals, and the **Introduction** primitive (`discover_opportunities` with `partyUserIds` / `introTargetUserId`).
- `geo-esmeralda` skill — writes the woven connection back to the Geo knowledge graph (`EDGEOS_BEARER_TOKEN` required).

---

## The Weave Sequence

```
1. INGEST → Candidate pool: the user's connections + their reachable networks
2. READ   → Read each person through ALL v3 preset lenses → per-lens λ/τ/μ
3. WEAVE  → lambda_weave.py → tables that lower each other's λ, per lens, ranked
4. PRESENT→ Show the connector the top tables, the lens, who anchors whom on which dim
5. INTRO  → Index Introduction mode mints the multi-party intro (user = introducer)
6. WRITE  → Geo graph gains: the connection, the λ-why, the lens, who-held-whom
7. NEXT   → Second-order bridges between the two joined networks
```

---

## Step 1 — Ingest the candidate pool

The people the user could plausibly convene: their connections and members of indexes they share.

- Roster: `read_user_profiles(networkId=...)` / `read_network_memberships(networkId)`.
- Their signals: `read_intents(networkId, userId)` — rich text for a reading.
- **Richest of all: their own messages.** If Telegram is connected (timkosters/telegram-cli-scripts), read a chat and score people on how they *actually write* — see [`workflows/telegram-weave.md`](workflows/telegram-weave.md). Thin bios collapse the `q`/`f` dimensions; real messages don't.
- Or seed from a `cerata-connect` catch list.

## Step 2 — Read each person through the v3 lenses

This is v3's core: **the agent perceives; it does not regex-extract.** For each preset calibration, generate the lens prompt and read the person through it:

```python
import sys; sys.path.insert(0, "rose-glass-v3")
from rose_glass_llm_lens_v2 import RoseGlassLLMLens, LensCalibration
for cal in LensCalibration:                 # all 7 presets — the right table may only appear under the right lens
    prompt = RoseGlassLLMLens(calibration=cal).generate_system_prompt()
    # The AGENT reads the person's text under `prompt` and emits, as JSON:
    #   { "lambda": {"psi","rho","q","f"}, "tau": .., "mu": .. }
    #   λ_d = how fast THIS lens reads the environment as decaying that dimension for them
    #   τ   = temporal-depth anchoring (attenuates λ);  μ = restoration they carry to others
```

Presets: `western_academic`, `spiritual_contemplative`, `indigenous_oral`, `crisis_translation`, `legal_adversarial`, `clinical_therapeutic`, `neurodivergent`. Assemble a people array, each with a `readings` map keyed by preset.

> Read through **all** presets — a person's λ differs by lens, so a table that holds coherence under `clinical_therapeutic` may grind under `legal_adversarial`. The engine compares them and tells you which lens the table lives in.

## Step 3 — Weave (find the λ-reducing tables)

```bash
echo '{"people":[{"id","name","readings":{"<lens>":{"lambda":{...},"tau":..,"mu":..},...}},...],"k":3,"top":8}' \
  | python3 scripts/lambda_weave.py
```

Returns `(table, lens)` ranked by `polygon_value`, each with:
- `lambda_reduction` — mean coherence-decay the table removes (the rule: mutual λ-reduction).
- `min_reduction` — the least-helped member (a real table leaves **nobody** un-restored).
- `dim_breadth` — distinct failure modes covered (a pair covers ≤2 dims; a trio can anchor 3 at once).
- `beats_best_pair_by` — **> 0 means the table does what no pair inside it can.** Surface these first; that delta is the whole reason to convene three instead of two.
- `members_detail` — per member, `lambda_alone → lambda_in_table` and the dimension they were `anchored` on (who held them).

## Step 4 — Present (the connector's view)

Show the user, as connector, the top tables in plain language and *through which lens*: *"Read in an adversarial frame, these three hold each other — Amir is raw on q, and Bea anchors his q while Cal carries the structure; nobody at the table is left decaying."* Let them pick. **Do not introduce before they choose** (real people — Two Hands).

## Step 5 — Make the introduction

Index Introduction mode, user as introducer. Pre-gather each party's profile + intents (the tool requires it):

```
discover_opportunities(partyUserIds=[a,b,c],
  entities=[{userId,networkId,profile,intents}, ...],
  hint="<the λ-why, in the user's voice>")
```

For a single bridge use `introTargetUserId`. Confirm the framing before sending — it pings real agents.

## Step 6 — Write the weave to the Geo graph

On a **confirmed** intro, record it so the connection becomes village knowledge — including *why* it cohered:

```bash
npx -y @geoprotocol/geo-edge-esmeralda-cli create \
  --client-request-id "weave-<stable-hash>" \
  ...   # capture: the people, the lens, the λ-reduction, and who-anchored-whom-on-which-dim
```

(See `geo-esmeralda` for the exact `create` shape. `EDGEOS_BEARER_TOKEN` required; stable `--client-request-id` so retries don't duplicate.) The graph now knows not just *that* they met but *under which lens they held each other's coherence, and on which dimension.*

## Step 7 — Next bridges (the flywheel)

A weave joins two orbits. Ask immediately: now that A's and B's networks touch, **which member of each should meet next?** Read the freshly-joined members through the lenses, re-run `lambda_weave.py`, surface the strongest next tables. Each becomes a new weave; the graph compounds.

---

## Two Hands — the weaver's discipline

Introduces **real people to each other** and **writes a shared community graph** — so perceive and report before acting:

- **Perceive → report → confirm.** Read and rank privately; show the connector the tables, the lens, and the λ-why; introduce only what they pick.
- **Never auto-write the Geo graph.** A write is community-visible — confirm the wording, use the user's framing, idempotent `--client-request-id`.
- **λ is a lens, not a verdict.** It ranks candidates; it does not override the connector's judgment. Present it as *why these might hold each other*, not *who must meet*.
- **Honor the Index voice.** No "search/match/network" in user-facing text — *weave*, *convene*, *hold*, *table*, *connection*.

---

## Tuning the λ model

`scripts/lambda_weave.py` builds on v3's real functions; tune the connection dynamics:

- **`GAMMA`** — how much others' strength restores a member's per-dim λ.
- **`DELTA`** — how much others' τ lends temporal anchoring (feeds v3's `λ_eff = λ₀/(1+κτ)`).
- **`polygon_value`** — weights mutual λ-reduction × coverage-breadth + a floor on the least-helped member. Reweight to taste (pure mutual λ-reduction = drop the breadth term).
- **κ and dimensional weights** come from each lens's `DimensionalCalibration` in v3's `CALIBRATION_PRESETS` — edit there to recalibrate a lens, not here.

---

## Notes

- A polygon that doesn't beat its best internal pair isn't a table — it's a pair with a passenger. The engine flags this (`beats_best_pair_by`); high raw λ-reduction from one high-decay member is *not* a table.
- The reading is the agent's job (through the v3 lens prompt); the script only does the λ math on readings. Thin text → thin readings — feed each person's signals/authored content, not a one-line bio.
- People not yet in the village (no Index profile / no signals) can't be read or woven — get them in first (`cerata-connect`), then they enter the pool.
- The agent cannot DM; the intro is an Index opportunity the parties open. Draft the convening message; hand it to the connector to send.
- Every weave should leave the graph richer: the edge, the lens, the λ-why, and at least one named next-bridge.
