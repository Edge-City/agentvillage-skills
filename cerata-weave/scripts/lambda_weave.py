#!/usr/bin/env python3
"""
λ-Weave — CERATA-WEAVE polygon engine (Rose Glass v3)
=====================================================
We do NOT measure similarity. We measure λ.

Input is per-person, per-lens *readings* produced by an LLM reading each person
THROUGH the v3 lens system-prompt (RoseGlassLLMLens) — per-dimension λ (decay),
τ (temporal anchoring), and μ (restoration capacity). This script does the math:
for every candidate polygon under every preset calibration, it computes
**mutual λ-reduction** — how much the table, convened, lowers each member's
effective λ versus that member alone. A constructive table is one whose members
HOLD each other's coherence (provide μ + τ-anchoring on the dimensions where
another is decaying). The right table may only appear under the right lens, so
we compare all presets.

Math is v3's own: tau_attenuated_lambda (λ_eff = λ₀/(1+κτ)) and
lambda_decomposition (λ = w₁λΨ+w₂λρ+w₃λq+w₄λf), with each lens's calibration.

Input (stdin/JSON):
{
  "people": [
    {"id","name",
     "readings": {
        "western_academic":     {"lambda": {"psi","rho","q","f"}, "tau": .., "mu": ..},
        "spiritual_contemplative": {...}, ...   # one per preset the LLM read through
     }}, ...
  ],
  "k": 3, "top": 8
}
Output (JSON): ranked (table, lens) by mutual λ-reduction, with per-member detail.
"""
import sys, os, json, itertools

V3 = os.environ.get("ROSE_GLASS_V3_PATH", "rose-glass-v3")
sys.path.insert(0, V3)
from rose_glass_llm_lens_v2 import (  # v3's real functions
    tau_attenuated_lambda, lambda_decomposition,
    CALIBRATION_PRESETS, LensCalibration,
)

DIMS = ["psi", "rho", "q", "f"]
GAMMA = 0.8   # how much others' strength restores a member's per-dim λ
DELTA = 0.3   # how much others' τ lends temporal anchoring to a member


def strength_on(reading, d):
    """A person's capacity to anchor dimension d for others: low decay + deep τ."""
    lam = reading["lambda"].get(d, 1.0)
    tau = reading.get("tau", 0.0)
    return max(0.0, 1.0 - lam) * (0.5 + 0.5 * tau)


def lambda_eff_alone(reading, cal):
    lam = reading["lambda"]
    total = lambda_decomposition(lam["psi"], lam["rho"], lam["q"], lam["f"], cal)["lambda_total"]
    return tau_attenuated_lambda(total, reading.get("tau", 0.0), cal.kappa), total


def lambda_eff_in_table(p, others, cal):
    """p's effective λ once the table restores it: others reduce p's per-dim λ where
    they are strong, and lend τ-anchoring; v3's τ-attenuation does the rest."""
    lam = p["lambda"]
    restored = {}
    for d in DIMS:
        r = min(1.0, GAMMA * (sum(strength_on(o, d) for o in others) / max(1, len(others))))
        restored[d] = lam[d] * (1.0 - r)
    total_r = lambda_decomposition(restored["psi"], restored["rho"], restored["q"], restored["f"], cal)["lambda_total"]
    table_tau = min(1.0, p.get("tau", 0.0) + DELTA * (sum(o.get("tau", 0.0) for o in others) / max(1, len(others))))
    return tau_attenuated_lambda(total_r, table_tau, cal.kappa), restored


def score_table(members, lens_key, cal):
    """Mutual λ-reduction for a table under one lens."""
    reductions, detail = [], []
    for p in members:
        rp = p["readings"][lens_key]
        others = [m["readings"][lens_key] for m in members if m is not p]
        alone, _ = lambda_eff_alone(rp, cal)
        intable, restored = lambda_eff_in_table(rp, others, cal)
        frac = (alone - intable) / alone if alone > 1e-9 else 0.0   # FRACTION of this lens's decay removed
        reductions.append(frac)                                     # lens-normalized so lenses compare fairly
        # who anchored p hardest: the dim restored most
        anchored = max(DIMS, key=lambda d: rp["lambda"][d] - restored[d])
        detail.append({"name": p["name"], "lambda_alone": round(alone, 4),
                       "lambda_in_table": round(intable, 4),
                       "reduction_frac": round(frac, 4), "anchored_dim": anchored})
    mean_red = sum(reductions) / len(reductions)
    min_red = min(reductions)                                   # the least-helped member
    breadth = len({m["anchored_dim"] for m in detail}) / len(DIMS)  # distinct failure modes covered
    return mean_red, min_red, breadth, detail


def polygon_value(mean_red, min_red, breadth):
    """Mutual λ-reduction (the rule), rewarded for covering distinct failure modes and
    leaving nobody un-restored — this is what a TABLE provides that a pair structurally can't
    (a pair covers at most 2 dims; a trio can anchor 3 different ones at once)."""
    return mean_red * (0.5 + 0.5 * breadth) + 0.4 * max(0.0, min_red)


def best_pair_value(members, lens_key, cal):
    best = 0.0
    for a, b in itertools.combinations(members, 2):
        mr, mn, br, _ = score_table([a, b], lens_key, cal)
        best = max(best, polygon_value(mr, mn, br))
    return best


def main():
    raw = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    req = json.loads(raw)
    people = req["people"]
    k = int(req.get("k", 3))
    top = int(req.get("top", 8))

    # lenses present in the readings (intersection across people)
    lens_keys = set.intersection(*[set(p["readings"].keys()) for p in people]) if people else set()
    results = []
    for lens_key in sorted(lens_keys):
        try:
            cal = CALIBRATION_PRESETS[LensCalibration(lens_key)]
        except (ValueError, KeyError):
            sys.stderr.write(f"[lambda_weave] unknown lens '{lens_key}', skipping\n")
            continue
        for combo in itertools.combinations(people, k):
            mean_red, min_red, breadth, detail = score_table(list(combo), lens_key, cal)
            value = polygon_value(mean_red, min_red, breadth)
            pair = best_pair_value(list(combo), lens_key, cal)
            results.append({
                "lens": lens_key,
                "members": [m["name"] for m in combo],
                "member_ids": [m["id"] for m in combo],
                "polygon_value": round(value, 4),              # the ranking quantity
                "frac_reduction": round(mean_red, 4),          # mean FRACTION of decay removed (lens-normalized)
                "min_frac": round(min_red, 4),                 # least-helped member, as a fraction
                "dim_breadth": round(breadth, 3),              # distinct failure modes covered
                "beats_best_pair_by": round(value - pair, 4),  # >0 → the table does what no pair can
                "members_detail": detail,
            })

    # best tables first; a real polygon must out-restore its best internal pair
    results.sort(key=lambda r: (r["beats_best_pair_by"] > 0, r["polygon_value"]), reverse=True)
    print(json.dumps({"k": k, "lenses": sorted(lens_keys), "tables": results[:top]}, indent=2))


if __name__ == "__main__":
    main()
