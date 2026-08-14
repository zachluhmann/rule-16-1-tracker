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

A sample this size gives a wide confidence interval. Treat the result as a signal about
where the definitions are soft, not as a precise coefficient. The disagreement set is
the more useful output.

The sample is 49 cells, not 50. Item 20, MDL 3167 / `b3e_settlement_facilitation`, was
removed on 13 August 2026 because it is worked through as test case 5 in the codebook
itself, so any coder handed the codebook is handed that cell's answer. Item numbers were
deliberately not renumbered: the gap at 20 is the visible trace of the removal.

IF THE SECOND CODER IS A LANGUAGE MODEL, the header of the disagreement file and any
reported figure must say so. Agreement between two models is weaker evidence than
agreement between two people, because their errors are correlated in ways two humans'
are not. Disagreement, by contrast, is strong evidence either way: two systems trained
differently that read the same sentence differently have found a genuinely soft
definition.
"""
import csv, sys, os
from collections import Counter

DEFAULT_SAMPLE = "reliability-sample.csv"
PASS1 = "subject-treatment.csv"
OUT = "reliability-disagreements.csv"
ATTRS = ["reached", "express", "party_direction", "court_resolution"]


def load(path):
    """Read a filled-in sample, tolerating what a second coder is likely to hand back.

    Column names are matched case-insensitively and with spaces or hyphens folded to
    underscores, because a coder returning a spreadsheet often renames them slightly.
    Values are accepted as TRUE/FALSE in any case, and also as T/F, YES/NO, Y/N, 1/0,
    which is what people and models actually type. Anything else is an error rather than
    a guess: a cell whose value cannot be read must stop the run, not be coerced.
    """
    if not os.path.exists(path):
        sys.exit(f"{path} not found")
    raw = list(csv.DictReader(open(path)))
    if not raw:
        sys.exit(f"{path} has no rows")

    def norm(k):
        return (k or "").strip().lower().replace(" ", "_").replace("-", "_")

    rows = [{norm(k): (v or "").strip() for k, v in r.items()} for r in raw]
    for need in ["item", "mdl_no", "subject_id"]:
        if need not in rows[0]:
            sys.exit(f"{path}: no column named {need!r}. Found: {sorted(rows[0])}")
    return rows


TRUEY = {"TRUE", "T", "YES", "Y", "1"}
FALSEY = {"FALSE", "F", "NO", "N", "0"}


def boolean(v, where):
    u = v.strip().upper()
    if u in TRUEY:
        return True
    if u in FALSEY:
        return False
    sys.exit(f"{where}: cannot read {v!r} as a boolean. "
             f"Use TRUE or FALSE; leave blank if not coded.")


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
    paths = [a for a in sys.argv[1:] if not a.startswith("-")] or [DEFAULT_SAMPLE]
    passes = {os.path.basename(a).rsplit(".", 1)[0]: load(a) for a in paths}
    p1 = {(r["mdl_no"], r["subject_id"]): r for r in csv.DictReader(open(PASS1))}

    all_dis = []
    for label, sample in passes.items():
        filled = [r for r in sample if all(r.get(a, "") for a in ATTRS)]
        print(f"\n{'='*70}\n{label}: {len(sample)} cells, {len(filled)} fully coded")
        if not filled:
            print("  nothing to score in this file"); continue
        if len(filled) < len(sample):
            print(f"  scoring the {len(filled)} complete cells only; "
                  f"{len(sample) - len(filled)} are blank or partial")

        print(f"\n{'attribute':<20}{'agree':>8}{'n':>5}{'pct':>8}{'kappa':>9}"
              f"{'coder T':>9}{'pass1 T':>9}")
        print("-" * 68)
        dis = []
        for a in ATTRS:
            h, m = [], []
            for r in filled:
                key = (r["mdl_no"], r["subject_id"])
                if key not in p1:
                    sys.exit(f"{label} item {r['item']}: {key} not in {PASS1}")
                hv = boolean(r[a], f"{label} item {r['item']} / {a}")
                mv = p1[key][a].strip().upper() == "TRUE"
                h.append(hv); m.append(mv)
                if hv != mv:
                    dis.append({"pass": label, "item": r["item"], "mdl_no": r["mdl_no"],
                                "subject_id": r["subject_id"], "attribute": a,
                                "coder": str(hv).upper(), "pass1": str(mv).upper(),
                                "pass1_pin_cite": p1[key]["pin_cite"],
                                "pass1_quote": p1[key]["quote"],
                                "pass1_coding_note": p1[key]["coding_note"],
                                "coder_note": r.get("note_optional", ""),
                                "resolution": ""})
            ag = sum(1 for x, y in zip(h, m) if x == y)
            k = kappa(h, m)
            ks = "n/a" if k != k else f"{k:.3f}"
            print(f"{a:<20}{ag:>8}{len(h):>5}{100*ag/len(h):>7.0f}%{ks:>9}"
                  f"{sum(h):>9}{sum(m):>9}")

        tot = len(filled) * len(ATTRS)
        # Two denominators, and the larger one flatters the result. The four attributes
        # are logically nested -- party_direction and court_resolution each imply express
        # implies reached -- so one disputed cell can produce up to four disputed
        # attributes, and the 4N comparisons are not independent. Cell-level agreement is
        # the conservative figure and the one to quote.
        cells = {(d["mdl_no"], d["subject_id"]) for d in dis}
        print(f"\nattribute level: {tot - len(dis)}/{tot} agree "
              f"({100*(tot-len(dis))/tot:.0f}%), {len(dis)} disagreements")
        print(f"cell level:      {len(filled) - len(cells)}/{len(filled)} cells fully agree "
              f"({100*(len(filled)-len(cells))/len(filled):.0f}%), {len(cells)} cells in dispute")
        print("  The attribute figure is the flattering one: the four fields are nested, so")
        print("  one disputed cell can count as up to four disputed attributes. Quote the cell")
        print("  figure, or quote both.")
        if dis:
            print("concentration:")
            for lab, key in (("by attribute", "attribute"), ("by subject", "subject_id"),
                             ("by order", "mdl_no")):
                c = Counter(d[key] for d in dis).most_common(5)
                print(f"  {lab}: " + ", ".join(f"{k} ({v})" for k, v in c))
        else:
            print("no disagreements, which on a sample this size is itself worth being")
            print("suspicious about: check that the pass was coded blind.")
        all_dis += dis

    # Where two second coders overlap, compare them to each other. This is the only
    # figure in the exercise that is not about pass 1, and if one coder is a model and
    # the other a person it is the one that says whether the model tracks a human at all.
    if len(passes) > 1:
        labels = list(passes)
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                A = {(r["mdl_no"], r["subject_id"]): r for r in passes[labels[i]]
                     if all(r.get(a, "") for a in ATTRS)}
                B = {(r["mdl_no"], r["subject_id"]): r for r in passes[labels[j]]
                     if all(r.get(a, "") for a in ATTRS)}
                both = sorted(set(A) & set(B))
                if not both:
                    continue
                print(f"\n{'='*70}\n{labels[i]} vs {labels[j]}: {len(both)} cells coded by both")
                agree = sum(1 for k in both for a in ATTRS
                            if boolean(A[k][a], "A") == boolean(B[k][a], "B"))
                n = len(both) * len(ATTRS)
                print(f"  {agree}/{n} agree ({100*agree/n:.0f}%)")
                split = [(k, a) for k in both for a in ATTRS
                         if boolean(A[k][a], "A") != boolean(B[k][a], "B")]
                for (mdl, subj), a in split:
                    print(f"    MDL {mdl} {subj} / {a}: "
                          f"{labels[i]}={A[(mdl,subj)][a].upper()} "
                          f"{labels[j]}={B[(mdl,subj)][a].upper()} "
                          f"pass1={p1[(mdl,subj)][a].strip().upper()}")

    if all_dis:
        with open(OUT, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(all_dis[0].keys()))
            w.writeheader(); w.writerows(all_dis)
        print(f"\nwrote {OUT} ({len(all_dis)} rows)")
        print("Every disagreement must end as either a codebook amendment or a note that")
        print("the cell is genuinely ambiguous. Fill the `resolution` column.")
        print("\nIF EITHER PASS WAS CODED BY A LANGUAGE MODEL, say so wherever this is")
        print("reported. It is not inter-rater reliability and must not be called that.")


if __name__ == "__main__":
    main()
