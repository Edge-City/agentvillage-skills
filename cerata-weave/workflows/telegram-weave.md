# Workflow — Weaving on Telegram message data

The λ-weave is only as good as the text it reads. Bios under-activate the `q` and
`f` dimensions and the readings collapse. **A person's own messages are the richest
reading source there is** — how they actually write reveals their dimensional
signature far better than a one-line profile. This workflow reads a Telegram chat,
scores each active voice through the v3 lenses, and finds the tables that hold each
other's coherence.

Data source: [timkosters/telegram-cli-scripts](https://github.com/timkosters/telegram-cli-scripts)
(read/draft Telegram from the CLI; `save-draft` only — never auto-sends). Auth is the
user's own Telegram account, one-time interactive (`bun auth.ts`).

## The pipeline

```
read-messages.ts  →  telegram_aggregate.py  →  read through v3 lenses  →  lambda_weave.py  →  tables
   (a chat)            ({name: text})           (agent emits λ/τ/μ)        (mutual λ-reduction)
```

### 1. Pull a chat and aggregate by author

```bash
cd <telegram-cli-scripts>
bun read-messages.ts "Edge Esmeralda 2026" --limit 250 \
  | python3 <cerata-weave>/scripts/telegram_aggregate.py --min-chars 180 --top 8 \
  > /tmp/people_text.json     # { "Name": "their aggregated messages", ... }
```

Pick a chat where people write *substance*, not just logistics — a topical group or a
1-on-1 thread reads sharper than the all-hands channel. Use `search-dialogs.ts` to
find a group/person, `list-recent.ts` to see what's active.

### 2. Read each person through the v3 lenses

For each person in `people_text.json`, the **agent reads their text** through each
preset calibration (`RoseGlassLLMLens`, see SKILL.md §2) and emits a reading:
`{ "lambda": {psi,rho,q,f}, "tau": .., "mu": .. }`. Build the `people[].readings`
map keyed by lens. This is the v3 perception step — the LLM does it; no regex.

### 3. Weave

```bash
python3 <cerata-weave>/scripts/lambda_weave.py < readings.json
```

Returns `(table, lens)` ranked by mutual λ-reduction + coverage-breadth — the groups
whose members lower each other's λ the most. Read the `held` line: each member, the
fraction of their decay the table removes, and the dimension they were anchored on.

### 4. Act

- **Convene / introduce** the top table via `index-network` Introduction mode, or draft
  the invite straight into Telegram with `save-draft.ts @username "..."` (the user sends).
- **Write the weave** to the Geo graph (SKILL.md §6): the connection, the lens, who held
  whom on which dimension.

## Example shape (anonymized)

Reading three real voices from a group chat produced, under the communal lens:

```
[indigenous_oral]  Researcher + Facilitator + Host   ← beats its best pair
   held:  Researcher 64% (on f)   Facilitator 63% (on Ψ)   Host 56% (on ρ)
```

A deep-domain researcher who is *new and socially fresh* gets folded in on `f` by two
community-weavers; in return he carries the rigor (`Ψ`) and wisdom (`ρ`) they're lighter
on. Each anchored on their weakest dimension — a table, not a pair. It surfaced under
the restoration lens, as a "hold each other" table should.

## Two Hands (this workflow especially)

- **Real messages are sensitive.** The λ readings are interpretive psychological reads of
  real people. They are for the user's private connector judgment — **do not commit,
  publish, or share per-person λ readings.** Anonymize any example that leaves the machine
  (as above).
- **Read, don't send.** `save-draft.ts` drafts only; the user reviews and sends. The weave
  surfaces tables; the user decides who to convene.
- **The model is a lens, not a verdict.** Present a table as *why these might hold each
  other*, never as *who must meet*.
