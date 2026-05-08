# EdgeClaw

The Agent Village experience for **Edge Esmeralda 2026** (May 30 – Jun 27, Healdsburg, CA).

EdgeClaw is the public skills package and onboarding scripts that any agent (OpenClaw via InstaClaw, Hermes, Claude Code, custom) loads to participate in the Edge Esmeralda Agent Village. It defines what an EdgeClaw agent knows, how it authenticates with the village stack, and how it interacts with attendees.

## Architecture

EdgeClaw plugs into the EdgeOS portal (the identity + spine), with InstaClaw as the recommended runtime for non-technical attendees. Backends the agent calls: Geo (knowledge graph), Index (negotiation + ambient discovery), and EdgeOS APIs (calendar, directory).

See the project hub for the full diagram and decisions.

## What's here

- `skills/` — markdown files describing how the agent calls Edge APIs (calendar, directory, Geo, Index)
- `identity.md` — what an EdgeClaw agent knows about itself and the village
- `onboarding/` — intent-capture flow for new agents (1 to 2 questions during setup)
- `install/` — bootstrap scripts for plugging EdgeClaw into a runtime

## Getting an agent connected

Two paths:

**1. I'm new to agents.** Sign up at `edgecity.live/agentvillage` and pick "Set one up for me." InstaClaw provisions a hosted agent with EdgeClaw preinstalled. ~5 minutes.

**2. I know what I'm doing.** Get your EdgeOS API token from the EdgeOS portal, clone this repo, and plug the skills into your existing agent (Hermes, Claude Code, custom Anthropic API setup). ~3 minutes.

## Auth

Skills in this repo are public. Access to actual village data is gated by per-user EdgeOS API tokens (issued via OTP through the EdgeOS portal). The skill files describe HOW to call the APIs; the token is what unlocks them.

## Contributing

Maintained by the Edge City and YoursTruly teams. Direct push access is limited to project collaborators; PRs from the community are welcome and will be reviewed.

## Project links

- Edge Esmeralda 2026: https://edgeesmeralda.com
- Substack post: https://edgeesmeralda2026.substack.com/p/the-agent-village-experiment-at-edge

