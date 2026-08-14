#!/usr/bin/env python3
"""
Validate subject-treatment.csv against the codebook's logical constraints.

Run this after every coding session, before committing. It enforces the
constraints that hold BY CONSTRUCTION, so a violation is a coding error rather
than a finding:

    party_direction  ->  express  ->  reached
    court_resolution ->  express  ->  reached

and the evidence requirements:

    express          ->  pin_cite present
    direction or resolution -> quote present

It does not judge coding decisions. It catches rows that cannot be true.

    python3 validate_treatment.py            # report; exit 1 on any error
    python3 validate_treatment.py --progress # also show how much is coded
"""
import csv, sys
from collections import Counter, defaultdict

FILE = "subject-treatment.csv"
SUBJECTS = 20
BOOL = {"TRUE", "FALSE", ""}


def load():
    return list(csv.DictReader(open(FILE)))


def errors(rows):
    out = []
    seen = set()
    for i, r in enumerate(rows, start=2):          # +2: header is line 1
        key = (r["mdl_no"], r["order_id"], r["subject_id"])
        where = f"line {i}  MDL {r['mdl_no']} {r['subject_id']}"

        if key in seen:
            out.append((where, "duplicate subject-order row"))
        seen.add(key)

        vals = {f: r[f].strip().upper() for f in
                ("reached", "express", "party_direction", "court_resolution")}
        for f, v in vals.items():
            if v not in BOOL:
                out.append((where, f"{f} is {r[f]!r}; must be TRUE, FALSE or blank"))

        if any(v == "" for v in vals.values()):     # not yet coded; skip logic
            continue

        T = lambda f: vals[f] == "TRUE"
        if T("express") and not T("reached"):
            out.append((where, "express=TRUE but reached=FALSE"))
        if T("party_direction") and not T("express"):
            out.append((where, "party_direction=TRUE but express=FALSE"))
        if T("court_resolution") and not T("express"):
            out.append((where, "court_resolution=TRUE but express=FALSE"))

        if T("express") and not r["pin_cite"].strip():
            out.append((where, "express=TRUE requires a pin_cite"))
        if (T("party_direction") or T("court_resolution")) and not r["quote"].strip():
            out.append((where, "direction or resolution requires a verbatim quote"))
        # "1" and "2" are the two coding passes. The third value records a cell that was
        # coded in pass 1 under codebook v1.0 and amended under v1.1 after adjudication,
        # which is provenance a reader needs and not a fourth pass.
        if r["pass"].strip() not in ("1", "2", "1 (v1.0), amended v1.1"):
            out.append((where, f"pass is {r['pass']!r}; must be 1, 2, "
                               f"or '1 (v1.0), amended v1.1'"))
    return out


def progress(rows):
    by = defaultdict(lambda: [0, 0])
    for r in rows:
        p = by[(r["pass"], r["mdl_no"])]
        p[1] += 1
        if r["reached"].strip():
            p[0] += 1
    print("\ncoded / total, by pass and MDL:")
    for (ps, mdl), (done, tot) in sorted(by.items()):
        bar = "#" * round(20 * done / tot) + "." * (20 - round(20 * done / tot))
        print(f"  pass {ps}  MDL {mdl}  {bar} {done:>2}/{tot}")
    tot = len(rows)
    done = sum(1 for r in rows if r["reached"].strip())
    print(f"\n  overall {done}/{tot} cells coded")

    # completeness of the evidence trail, which is the point of the long format
    ex = [r for r in rows if r["express"].strip().upper() == "TRUE"]
    if ex:
        withq = sum(1 for r in ex if r["quote"].strip())
        print(f"  of {len(ex)} express subjects, {withq} carry a verbatim quote "
              f"({round(100*withq/len(ex))}%)")


def main():
    rows = load()
    errs = errors(rows)
    print(f"{FILE}: {len(rows)} rows")
    if errs:
        print(f"\n{len(errs)} constraint violation(s):")
        for where, msg in errs[:40]:
            print(f"  {where}\n      {msg}")
        if len(errs) > 40:
            print(f"  ... and {len(errs)-40} more")
    else:
        print("all logical constraints satisfied")
    if "--progress" in sys.argv:
        progress(rows)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
