#!/usr/bin/env python3
"""
How an order invokes Rule 16.1, against how much it directs the parties.

    python3 invocation_analysis.py

This recomputes, from the CSVs alone, the numbers in the 31 August 2026 working note. It is
here so the note can be checked rather than believed, and so the numbers move when the data
does. It writes nothing and is not part of the build.

THE CLAIM. Split the coded orders by `rule_role`, which records HOW an order invokes the Rule
rather than whether it cites it. Orders that set the Rule's topics out in their own words
(AGENDA, TRANSCRIPTION, RESIDUAL) direct the parties on 15 or more of the 19 subjects on the
site's scale. Orders that incorporate the Rule by reference, and orders that never mention it,
direct on 13 or fewer. The two groups do not overlap.

THE CAVEAT, WHICH IS NOT SMALL. The codebook holds that blanket incorporation alone does not
satisfy `express`, because a reader must consult the Rule to learn what was incorporated, and
`party_direction` requires `express`. So the two incorporation orders are held near zero BY
CONSTRUCTION. They reach all nineteen subjects and express two. An order saying "address each
of the matters listed in Rule 16.1" and an order naming those matters impose similar
obligations on the parties; this measure scores them 1 and 19.

That makes the honest reading narrower than the headline: `party_direction` measures how an
order says it, not what the parties must do. The finding is real and the mechanism is the
instrument's, and both halves have to be reported together.
"""
import csv, math, sys, statistics

TRACKER = "rule-16-1-tracker.csv"
CELLS = "subject-treatment.csv"
SETS_OUT = {"AGENDA", "TRANSCRIPTION", "RESIDUAL"}
ROLE_WORDS = {"AGENDA": "sets the topics as a conference agenda",
              "TRANSCRIPTION": "reproduces the Rule's topics",
              "RESIDUAL": "sets its own topics, Rule cited residually",
              "INCORPORATION": "incorporates the Rule by reference",
              "NOT_INVOKED": "never mentions the Rule"}


def fisher(a, b, c, d):
    """Two-sided Fisher exact on [[a, b], [c, d]].

    Written out rather than imported because this repository has no dependencies on purpose:
    a maintenance script that stops running when a library moves is not maintenance.
    """
    def p(w, x, y, z):
        return (math.comb(w + x, w) * math.comb(y + z, y)) / math.comb(w + x + y + z, w + y)
    obs, tot, n = p(a, b, c, d), 0.0, a + b + c + d
    for i in range(0, min(a + b, a + c) + 1):
        j, k, l = a + b - i, a + c - i, n - (a + b) - (a + c) + i
        if j < 0 or k < 0 or l < 0:
            continue
        q = p(i, j, k, l)
        if q <= obs * (1 + 1e-9):
            tot += q
    return tot


def load():
    trk = {r["mdl_no"]: r for r in csv.DictReader(open(TRACKER))}
    rows = list(csv.DictReader(open(CELLS)))
    subjects = sorted({r["subject_id"] for r in rows})
    scale19 = [s for s in subjects if s != "b2a_leadership"]   # the site's own scale
    cell = {(r["mdl_no"], r["subject_id"]): r for r in rows}
    mdls = sorted({r["mdl_no"] for r in rows}, key=int)
    def n(m, col):
        return sum(1 for s in scale19 if cell[(m, s)][col].strip().upper() == "TRUE")
    return trk, mdls, n, len(scale19)


def main():
    trk, mdls, n, scale = load()
    print(f"{len(mdls)} coded orders, on the site's {scale}-subject scale\n")
    print(f"{'MDL':6}{'court':<12}{'how it invokes the Rule':<44}"
          f"{'reach':>6}{'expr':>6}{'dir':>5}{'res':>5}")
    for m in sorted(mdls, key=lambda x: (-n(x, "party_direction"), x)):
        role = trk[m]["rule_role"]
        print(f"{m:6}{trk[m]['court']:<12}{ROLE_WORDS.get(role, role):<44}"
              f"{n(m,'reached'):>6}{n(m,'express'):>6}"
              f"{n(m,'party_direction'):>5}{n(m,'court_resolution'):>5}")

    sets = [m for m in mdls if trk[m]["rule_role"] in SETS_OUT]
    other = [m for m in mdls if m not in sets]
    sv = sorted(n(m, "party_direction") for m in sets)
    ov = sorted(n(m, "party_direction") for m in other)
    print(f"\nsets out the topics   n={len(sv)}  {sv}  median {statistics.median(sv):g}")
    print(f"incorporates/silent   n={len(ov)}  {ov}  median {statistics.median(ov):g}")
    print(f"lowest in the first group {min(sv)}; highest in the second {max(ov)}  -> "
          f"{'no overlap' if min(sv) > max(ov) else 'OVERLAPPING'}")

    for thr in (15, scale):
        a = sum(1 for m in sets if n(m, "party_direction") >= thr)
        c = sum(1 for m in other if n(m, "party_direction") >= thr)
        print(f"\ndirects on >= {thr}: sets-out {a}/{len(sets)}, other {c}/{len(other)}, "
              f"Fisher p = {fisher(a, len(sets)-a, c, len(other)-c):.5f}")

    cy = [m for m in mdls if trk[m]["cites_rule"] == "YES"]
    cn = [m for m in mdls if m not in cy]
    a = sum(1 for m in cy if n(m, "party_direction") >= 15)
    c = sum(1 for m in cn if n(m, "party_direction") >= 15)
    print(f"\nfor contrast, the split the site already uses, cites vs not, >= 15: "
          f"{a}/{len(cy)} against {c}/{len(cn)}, "
          f"Fisher p = {fisher(a, len(cy)-a, c, len(cn)-c):.5f}")
    print("  the two incorporation orders cite the Rule and sit at the bottom, which is why "
          "invocation style separates the set better than citation does.")

    # R4 governs party_direction in MDLs 3163 and 3185, and those cells cannot be checked
    # against their own quotes. Both sit in the lower group, so drop them and look again.
    keep_s = [m for m in sets if m not in ("3163", "3185")]
    keep_o = [m for m in other if m not in ("3163", "3185")]
    a = sum(1 for m in keep_s if n(m, "party_direction") >= 15)
    c = sum(1 for m in keep_o if n(m, "party_direction") >= 15)
    print(f"\ndropping MDLs 3163 and 3185, whose party_direction rests on codebook rule R4: "
          f"{a}/{len(keep_s)} against {c}/{len(keep_o)}, "
          f"Fisher p = {fisher(a, len(keep_s)-a, c, len(keep_o)-c):.5f}")

    # The sharper result is not that one split wins. It is that the two splits explain
    # different columns, and each explains its own completely.
    print("\nwhich split explains which column:")
    print(f"  {'column':18}{'by citation':<34}{'by invocation style'}")
    for col in ("reached", "express", "party_direction", "court_resolution"):
        def sep(g1, g2):
            v1, v2 = sorted(n(m, col) for m in g1), sorted(n(m, col) for m in g2)
            return "SEPARATED" if min(v1) > max(v2) else "no"
        print(f"  {col:18}{sep(cy, cn):<34}{sep(sets, other)}")
    print("  Citing the Rule tells you whether an order REACHES every subject. How it invokes")
    print("  the Rule tells you whether it DIRECTS the parties on them. The two incorporation")
    print("  orders are the wedge: they reach 19 like every other citing order and direct on")
    print("  1 and 2, below seven of the nine orders in their own group.")

    print(f"\nn is {len(mdls)}. Three of the upper group share a form order, so the six are "
          f"not six independent draftings.")


if __name__ == "__main__":
    main()
