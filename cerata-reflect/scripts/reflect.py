#!/usr/bin/env python3
"""
Negotiation meta-analysis — CERATA-REFLECT
==========================================
An agent's discovery gate over-rejects. Most "rejections" aren't the human
saying no — they're the agent's scorer judging a too-narrow query ("doesn't fit
THIS specific role"), while the actual person is a strong, wanted connection.
Neither the human nor the agent ever sees these false negatives.

This reads an agent's OWN Index negotiation history (list_negotiations output)
and separates three things people conflate:
  1. the COUNTERPART's signal  — their agent accepted / rejected (their interest)
  2. the GATE artifact         — rejections on narrow scope, not real disinterest
  3. the HUMAN's action        — did the human actually open / act on it (unknown
                                 from negotiations alone; needs conversation state)

Output: inbounds the human may have missed, false-negatives worth re-opening,
genuine mismatches, and the accepts sitting unopened.

Usage:
  <list_negotiations JSON> | python3 reflect.py
"""
import sys, json, re
from collections import defaultdict

# Reasoning patterns that mark a rejection as a likely GATE artifact (re-openable),
# not the human's disinterest: a concession of value + a scope/role narrowing.
NARROW_MARKERS = [
    r"does not (directly )?(fit|satisfy|align|match)", r"too narrow", r"specific (query|role|criterion)",
    r"primary (criterion|discovery query)", r"this specific", r"not the .* host", r"rather than",
    r"while .* (valuable|impressive|capable|exceptional|strong)", r"same-side", r"does not .* indicate",
    r"not .* interested in .* hosting", r"core intent is", r"his stated goals are focused",
]
NAME_RE = re.compile(r"^([A-Z][A-Za-z.\-']+(?:\s+[A-Z][A-Za-z.\-']+){0,2})[\s,.:'’]")


def name_of(neg):
    p = (neg.get("latestMessagePreview") or "").strip()
    m = NAME_RE.match(p)
    if m:
        return m.group(1).rstrip(",.:")
    # fall back to "for X" / "X's" / "X is" mentions
    for pat in (r"for ([A-Z][A-Za-z.\-']+(?:\s+[A-Z][A-Za-z.\-']+){0,2})",
                r"([A-Z][A-Za-z.\-']+(?:\s+[A-Z][A-Za-z.\-']+){0,2})['’]s",
                r"\b([A-Z][A-Za-z.\-']+(?:\s+[A-Z][A-Za-z.\-']+){0,1}) (?:is|does|has)\b"):
        m = re.search(pat, p)
        if m:
            return m.group(1)
    return neg.get("counterpartyId", "?")[:8]


def main():
    data = json.loads(sys.stdin.read())
    negs = data.get("negotiations") or data.get("data", {}).get("negotiations") or data
    # latest negotiation per counterparty (dedupe continuations)
    latest = {}
    for n in negs:
        cid = n.get("counterpartyId")
        if cid not in latest or (n.get("turnCount", 0) > latest[cid].get("turnCount", 0)):
            latest[cid] = n

    inbound, reopen, mismatch, accepts, glitched = [], [], [], [], []
    for cid, n in latest.items():
        action = n.get("latestAction")
        role = n.get("role")  # 'candidate' = THEY reached out to you (inbound)
        prev = (n.get("latestMessagePreview") or "")
        nm = name_of(n)
        row = {"name": nm, "id": cid, "role": role, "action": action}
        if "error" in prev.lower() or "json parse" in prev.lower():
            glitched.append(row); continue
        if action == "accept":
            accepts.append(row)
            if role == "candidate":
                inbound.append({**row, "note": "reached out TO you — did the human see it?"})
        elif action in ("reject", "rejected_or_stalled"):
            narrow = any(re.search(p, prev, re.I) for p in NARROW_MARKERS)
            (reopen if narrow else mismatch).append(
                {**row, "why": "narrow-gate reject (concedes value, rejects on scope) — likely false negative"
                 if narrow else "looks like a genuine domain mismatch"})
        elif action in ("propose",) and role == "candidate":
            inbound.append({**row, "note": "inbound proposal — awaiting your response"})

    out = {
        "counterparties": len(latest),
        "summary": {"accepts": len(accepts), "reopen_candidates": len(reopen),
                    "true_mismatches": len(mismatch), "inbounds": len(inbound),
                    "glitched_retry": len(glitched)},
        "inbounds_to_review": inbound,         # people who came to YOU
        "reopen_candidates": reopen,           # the gate was too narrow — warm re-open these
        "true_mismatches": mismatch,           # leave these
        "glitched_retry": glitched,            # engine errored mid-eval — just retry
        "note": "Negotiations show the COUNTERPART's interest and the GATE's verdict. "
                "Whether the HUMAN engaged is separate — cross-check open conversations / "
                "opportunity status (accepted vs pending-unopened) to find warm connections the human never acted on.",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
