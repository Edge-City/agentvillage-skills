#!/usr/bin/env python3
"""
Co-attendance cohort — CERATA-COHORT
====================================
Connects people who showed up to the same classes. Co-attendance is a cheap,
strong connection signal: a shared room is shared context.

Input (stdin/JSON):
  {"events": {"Class A": ["Name",...], "Class B": [...]}, "target": "Name"?, "top": 12}
Output:
  - with "target": that person's co-attendees, ranked by # shared classes (+ which).
  - without: the strongest co-attendance pairs across everyone.
Feed the cohort into cerata-connect (introduce) or cerata-weave (λ-tables within it).
"""
import sys, json, itertools
from collections import defaultdict


def main():
    req = json.loads(open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read())
    events = req["events"]
    top = int(req.get("top", 12))
    target = req.get("target")

    attends = defaultdict(set)                 # person -> set of classes
    for cls, people in events.items():
        for p in people:
            attends[p].add(cls)

    shared = lambda a, b: sorted(attends[a] & attends[b])

    if target:
        if target not in attends:
            print(json.dumps({"error": f"'{target}' not found in any class"}))
            return
        rows = [{"name": p, "shared_count": len(s := shared(target, p)), "shared_classes": s}
                for p in attends if p != target and shared(target, p)]
        rows.sort(key=lambda r: (r["shared_count"], r["name"]), reverse=True)
        print(json.dumps({"target": target, "co_attendees": rows[:top]}, indent=2))
    else:
        pairs = [{"pair": [a, b], "shared_count": len(s := shared(a, b)), "shared_classes": s}
                 for a, b in itertools.combinations(sorted(attends), 2) if shared(a, b)]
        pairs.sort(key=lambda r: (r["shared_count"], r["pair"]), reverse=True)
        print(json.dumps({"pairs": pairs[:top]}, indent=2))


if __name__ == "__main__":
    main()
