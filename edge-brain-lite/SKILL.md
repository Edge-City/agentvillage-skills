---
name: edge-brain-lite
description: Give the user a personal, durable second brain. Installs the edge-brain-lite repo (a small, working AI-native memory system — capture loop, tiered memory, world model, governing specs) onto the user's machine, verifies it offline, then runs its guided onboarding interview to adapt the memory to the user's life and work. Use when the user asks for a second brain, better/persistent/personalized memory, an onboarding for their brain, or to "set up edge-brain-lite".
version: 1.0.0
author: Antony Evans
tags: [memory, second-brain, onboarding, personal-knowledge]
---

# Edge Brain Lite — install + personalized memory onboarding

You can give the user a real, file-based memory: **edge-brain-lite** ([github.com/antonyevans/edge-brain-lite](https://github.com/antonyevans/edge-brain-lite)), a small working "AI-native brain" — a capture loop, tiered memory (core / recalls / archival), a world model with freshness tracking, and seven written specs the agent governs itself against. It runs fully offline: pure Python 3.10+ standard library, no API keys, no external calls.

This skill does two things, in order:

1. **Install** — clone the repo to the user's machine and verify it with the built-in selftest.
2. **Onboard** — run the repo's own `ONBOARDING.md` interview, which adapts the brain to the user's business and seeds their personalized memory.

## 0. Safety rules

- The brain's `spec-no-autonomous-send` is a hard floor: nothing in it (or in this skill) sends, posts, or pays externally. Drafts only; the human sends.
- During onboarding, **interview and propose before writing** — the onboarding prompt enforces this; do not shortcut it.
- Never overwrite an existing brain. If the install directory already exists, see §4.
- The brain is plain Markdown on the user's machine. Before they put sensitive material in it, remind them once to decide where the repo lives and who can see it.

## 1. Prerequisites

This skill needs a file-aware host with shell access (Claude Code, OpenClaw, Hermes, Cowork, or similar). Check, and report plainly if missing:

- `git` — to clone. If absent, download the tarball instead: `https://github.com/antonyevans/edge-brain-lite/archive/refs/heads/main.tar.gz`
- `python3` ≥ 3.10 (`python3 --version`, or `python --version` on Windows) — for the brain's deterministic scripts. Nothing else: no pip installs, no keys.

If the host has no filesystem or shell access, tell the user this skill can't run here and stop.

## 2. Choose the install location

Ask the user where the brain should live before cloning. Default suggestion: `~/edge-brain-lite` (or a directory they already keep projects in). One sentence of context: this becomes their permanent memory, so it should be somewhere they'll keep, ideally backed by a private git remote later.

## 3. Install and verify

Narrate each step in one sentence before running it.

```bash
git clone https://github.com/antonyevans/edge-brain-lite <chosen-dir>
cd <chosen-dir>
python3 harness/selftest.py    # read-only; stands the whole brain up offline
```

The selftest must pass before onboarding. If it fails, report the exact output and stop — do not improvise fixes inside a fresh clone; the likely cause is a Python version below 3.10.

## 4. If the directory already exists

Do not delete or overwrite anything. Ask the user which of these they want:

- **Resume / re-onboard**: skip the clone and run the onboarding (§5) against the existing brain — the interview adapts what's already there.
- **Update**: `git pull` in the existing clone (only if they confirm their local changes are committed), then offer onboarding.
- **Fresh install elsewhere**: pick a different directory and proceed from §3.

## 5. Run the onboarding

The onboarding lives in the repo itself so it never drifts from the code. From the cloned directory:

1. Read `CLAUDE.md` (the brain's routing layer), then read `ONBOARDING.md` in full.
2. Execute the **THE PROMPT** block of `ONBOARDING.md` exactly as written, treating the user as the person being onboarded. It is a phased interview:
   - **Phase 0** — two-sentence greeting + five-sentence orientation.
   - **Phase 1** — intake interview in batches of three questions (business, inputs/outputs, recurring pain, external world + tone + safety boundary).
   - **Phase 2** — a proposal (structure fit, what gets seeded, spec tailoring, a bespoke-skills backlog) that the user must approve before anything is written.
   - **Phase 3** — adapt `CLAUDE.md`, seed `memory/core/` and `world-model/`, prove the capture loop on one real note from the user, write their `MY-BRAIN.md` cheat sheet, and re-run `selftest.py`.
3. Honor the onboarding prompt's `<known_failure_patterns>` — especially: no writes before approval, no tutorial dump, no tool jargon, no skills built during onboarding.

If your host session is rooted elsewhere (e.g. you are a village agent in your own workspace), operate on the brain by absolute path and read the clone's `CLAUDE.md` yourself — do not assume the host auto-loaded it.

## 6. After onboarding

Close with the three blocks the onboarding prompt specifies (what got adapted / how to come back / three next actions). Add one host-specific pointer: in future sessions, the user should either open the brain directory directly in their agent, or tell their agent where the brain lives so it reads `CLAUDE.md` and `memory/MEMORY.md` first. That is what makes the memory persistent and personal across sessions.

If the user wants the brain backed up, suggest creating a **private** git remote and pushing — but per the safety floor, only walk them through it; let them create the remote and confirm before any push.
