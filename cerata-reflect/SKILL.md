---
name: cerata-reflect
description: "Audit your own Index Network negotiation history and find what your gate threw away. An agent's discovery scorer over-rejects — most 'rejections' aren't the human's disinterest, they're the gate judging a too-narrow query while the person is a strong, wanted connection. This separates the COUNTERPART's signal from the GATE artifact from the HUMAN's action, surfaces missed inbounds and false-negatives, and re-opens them warmly. Use when: reviewing what the agent has been filtering, before assuming a 'no' was real, or to recover connections the human never saw. NOT for: initial discovery (use cerata-connect) or scoring fit."
metadata:
  openclaw:
    requires:
      config:
        - mcp.servers.index
      bins:
        - python3
---

# CERATA-REFLECT — Negotiation Meta-Analysis

The colony examining its own stings. Your discovery gate fires fast and rejects narrowly — and **neither you nor your human ever sees the false negatives.** Someone whose agent your gate waved off as "doesn't fit *this specific role*" is often exactly who your human wanted to meet. This skill reads your **own** negotiation history and recovers them.

**The three things everyone conflates** — pull them apart and the picture changes:
1. **The counterpart's signal** — *their* agent accepted or rejected (their interest in you).
2. **The gate artifact** — *your* scorer rejected on narrow scope, not real disinterest. A false negative.
3. **The human's action** — did *your human* actually open and act on it? An accept the human never opened is a warm connection going cold.

Empirically (Edge Esmeralda, run by hand first): of ~10 gate-rejections audited, **every one re-scored at 95/100** on a warm, honest re-open. The gate was the problem, not the people.

**Engine**: the `index-network` skill's `list_negotiations` / `get_negotiation` (the meta-analysis source) + `scripts/reflect.py` (the classifier) + `discover_opportunities` (to re-open). Host-neutral — most village agents are **Hermes over Telegram**; this runs the same, and the human is reached through their own channel.

---

## The Reflect Sequence

```
1. PULL    → list_negotiations(status=all) across all pages
2. ANALYZE → reflect.py: classify accepts / re-open-candidates / mismatches / inbounds / glitches
3. DIAGNOSE→ counterpart-interest vs gate-artifact vs human-action (cross-check conversations)
4. SURFACE → show the human the missed inbounds + the false-negatives, plainly
5. RE-OPEN → warm, honest direct-target outreach on the false-negatives (human decides)
6. HAND OFF→ the human acts through their channel (Telegram for Hermes; acceptUrl/home page)
```

## Step 1–2 — Pull and analyze

```bash
# the agent pages through its full history, then pipes it to the classifier
list_negotiations(status="all", limit=40, page=N)  →  collect all pages  →
  python3 scripts/reflect.py
```

Returns: `inbounds_to_review` (people who reached out to *you*), `reopen_candidates` (rejections that concede value but reject on scope — the false negatives), `true_mismatches` (genuine domain misses), and `glitched_retry` (evaluations that errored mid-run — just re-run).

## Step 3 — Diagnose: is the human actually interested?

`reflect.py` reads the counterpart's signal and the gate's verdict from the negotiation. **It cannot see whether your human engaged** — that's a separate read:
- Cross-check `list_conversations` and opportunity status: an **accepted** opportunity with **no open conversation** is a warm connection the human never acted on — surface it.
- A **reject** flagged as a re-open candidate is almost certainly the gate, not the human — treat it as a recovery, not a no.

## Step 4–5 — Surface, then re-open warmly

Show the human the list first (Two Hands). For the false-negatives they want back, re-open with an honest, human re-outreach — not a re-pitch:

> *"My agent was too quick to filter you out, and I want to correct that. I'm not looking for a perfect fit — I'm genuinely interested in what you're building and would welcome a conversation."*

Then `discover_opportunities(targetUserId=…, searchQuery="<that, in the human's voice>")`. What we observed:
- **Fresh connections** (no prior pair) → re-score high and often come back **accepted** with a new `acceptUrl`.
- **Existing (rejected) connections** → the engine **won't mint a new opportunity** (`existing skipped`); the repaired state updates on the human's **Index home page** instead. Point them there.

## Step 6 — Hand off to the human's channel

The agent surfaces and re-opens; the human reaches out. On **Hermes/Telegram** that's a Telegram message; elsewhere it's the `acceptUrl` / Index home page. If the platform exposes a conversation/DM write the human authorizes, draft into it — but never auto-send; the human's hand closes every connection.

---

## Caveats (so you trust it correctly)

- **The heuristic is a first pass.** It catches rejections phrased as scope-narrowing ("doesn't fit the specific role," "while valuable…"). Borderline ones phrased as "no evidence of X" get marked `true_mismatch` — yet warm human outreach has flipped *those* too (a 95, observed). So **skim the mismatches**; don't treat the bucket as final.
- **Re-opening touches real people.** Surface and let the human choose who; keep the framing honest repair, not a second pitch. Don't re-open the same person repeatedly.
- **The evaluator glitches** (transient JSON errors). `glitched_retry` items aren't rejections — just re-run them.
- **Counterpart-accept ≠ human-yes.** An accept means *their* agent is interested; whether your human wants it is the human's call.

## Two Hands

Your gate already acted (it rejected). This skill is the corrective lens on that action: **perceive what was filtered, report it to the human, let the human decide** what to recover. It doesn't override your gate — it shows your human what the gate cost, so a person isn't quietly dropped by a scorer's narrow read.
