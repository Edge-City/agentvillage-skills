#!/usr/bin/env python3
"""
Telegram → per-person text — CERATA-WEAVE reading source
========================================================
Parses the output of timkosters/telegram-cli-scripts `read-messages.ts` (a chat
or group) into per-author aggregated text, so each person can be read through the
v3 lenses. Rich behavioral text >> thin bios — this is the preferred reading
source for lambda_weave.

Pipe a chat's messages in; get {name: text} out, selecting the most-active voices.

  bun read-messages.ts "Edge Esmeralda 2026" --limit 250 \
    | python3 telegram_aggregate.py --min-chars 180 --top 8 > people_text.json

Then read each person's text through the v3 preset lenses (see SKILL.md) to build
the readings, and run lambda_weave.py.
"""
import sys, re, json, argparse

LINE = re.compile(r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]\s+(.+?):\s?(.*)$')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-chars", type=int, default=180, help="drop authors with less text than this")
    ap.add_argument("--top", type=int, default=8, help="keep the N most-active authors")
    ap.add_argument("--cap", type=int, default=900, help="truncate each author's text to N chars")
    args = ap.parse_args()

    people, cur = {}, None
    for ln in sys.stdin.read().splitlines():
        m = LINE.match(ln)
        if m:
            cur = m.group(1).strip()
            people.setdefault(cur, []).append(m.group(2))
        elif cur and ln.strip():
            people[cur].append(ln)                      # continuation line of a multi-line message

    agg = {p: " ".join(t).strip() for p, t in people.items()}
    ranked = sorted(agg.items(), key=lambda kv: len(kv[1]), reverse=True)
    out = {p: t[:args.cap] for p, t in ranked if len(t) >= args.min_chars}
    out = dict(list(out.items())[:args.top])
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
