#!/usr/bin/env python3
"""
Score a filled-in reliability-sample.csv against pass 1.

    python3 score_reliability.py

Reports, per attribute: raw percent agreement, the raw disagreement count, Cohen's
kappa, and the prevalence of TRUE in each coder's marks. Writes every disagreement to
reliability-disagreements.csv.

WHAT THIS MEASURES, AND WHAT IT DOES NOT

This is a HUMAN-versus-PASS-1 comparison on a 50-cell stratified random sample. It is
the only design in this project that tests whether the codebook travels to a reader who
did not write it. It is not intra-rater reliability and must not be reported as such;
see the amended reliability section of subject-treatment-codebook.md.

Kappa is reported alongside raw agreement on purpose. Where prevalence is extreme -
`reached` is TRUE in roughly three quarters of all cells - kappa can look poor despite
near-total agreement, because the chance-agreement term is large. Read the two together
or neither.

A 50-cell sample gives a wide confidence interval. Treat the result as a signal about
where the definitions are soft, not as a precise coefficient. The disagreement set is
the more useful output.
"""
import csv, sys, os
from collections import Counter

SAMPLE = "reliability-sample.csv"
PASS1 = "subject-treatment.csv"
OUT = "reliability-disagreements.csv"
ATTRS = ["reached", "express", "party_direction", "court_resolution"]


def kappa(a, b):
    """Cohen's kappa for two binary label sequences."""
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = 0.0
    for lab in (True, False):
        pe += (a.count(lab) / n) * (b.count(lab) / n)
    if pe == 1.0:
        return float("nan")          # both coders used one label throughout
    return (po - pe) / (1 - pe)


def main():
    if not os.path.exists(SAMPLE):
        sys.exit(f"{SAMPLE} not found")
    sample = list(csv.DictReader(open(SAMPLE)))
    p1 = {(r["mdl_no"], r["subject_id"]): r for r in csv.DictReader(open(PASS1))}

    filled = [r for r in sample if all(r[a].strip() for a in ATTRS)]
    print(f"{SAMPLE}: {len(sample)} cells, {len(filled)} fully coded")
    if not filled:
        sys.exit("nothing to score yet")
    if len(filled) < len(sample):
        print(f"  WARNING: scoring the {len(filled)} complete cells only; "
              f"{len(sample) - len(filled)} are blank or partial")

    bad = [r["item"] for r in filled for a in ATTRS
           if r[a].strip().upper() not in ("TRUE", "FALSE")]
    if bad:
        sys.exit(f"non-boolean values in items: {', '.join(sorted(set(bad)))}")

    disagreements = []
    print(f"\n{'attribute':<20}{'agree':>8}{'n':>5}{'pct':>8}{'kappa':>9}"
          f"{'human T':>9}{'pass1 T':>9}")
    print("-" * 68)
    for a in ATTRS:
        h, m = [], []
        for r in filled:
            key = (r["mdl_no"], r["subject_id"])
            if key not in p1:
                sys.exit(f"item {r['item']}: {key} not in {PASS1}")
            hv = r[a].strip().upper() == "TRUE"
            mv = p1[key][a].strip().upper() == "TRUE"
            h.append(hv); m.append(mv)
            if hv != mv:
                disagreements.append({
                    "item": r["item"], "mdl_no": r["mdl_no"],
                    "subject_id": r["subject_id"], "attribute": a,
                    "human": str(hv).upper(), "pass1": str(mv).upper(),
                    "pass1_pin_cite": p1[key]["pin_cite"],
                    "pass1_quote": p1[key]["quote"],
                    "pass1_coding_note": p1[key]["coding_note"],
                    "human_note": r.get("note_optional", ""),
                    "resolution": ""})
        ag = sum(1 for x, y in zip(h, m) if x == y)
        k = kappa(h, m)
        ks = "n/a" if k != k else f"{k:.3f}"
        print(f"{a:<20}{ag:>8}{len(h):>5}{100*ag/len(h):>7.0f}%{ks:>9}"
              f"{sum(h):>9}{sum(m):>9}")

    tot = len(filled) * len(ATTRS)
    print(f"\noverall: {tot - len(disagreements)}/{tot} agree "
          f"({100*(tot-len(disagreements))/tot:.0f}%), {len(disagreements)} disagreements")

    if disagreements:
        with open(OUT, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(disagreements[0].keys()))
            w.writeheader(); w.writerows(disagreements)
        print(f"wrote {OUT}")
        print("\nconcentration of disagreements:")
        for label, key in (("by attribute", "attribute"), ("by subject", "subject_id"),
                           ("by order", "mdl_no")):
            c = Counter(d[key] for d in disagreements).most_common(5)
            print(f"  {label}: " + ", ".join(f"{k} ({v})" for k, v in c))
        print("\nEvery disagreement must end as either a codebook amendment or a note")
        print("that the cell is genuinely ambiguous. Fill the `resolution` column.")
    else:
        print("no disagreements, which on 50 cells is itself worth being suspicious about:")
        print("check that the sample was coded blind.")


if __name__ == "__main__":
    main()
