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
import csv, os, re, sys
from collections import Counter, defaultdict

FILE = "subject-treatment.csv"
REPORTS = "report-treatment.csv"
INVOCATIONS = "party-invocations.csv"
SUBJECTS = 20
BOOL = {"TRUE", "FALSE", ""}
RBOOL = {"TRUE", "FALSE", "NOT_CHECKED", "NOT_READABLE", ""}


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


def report_errors():
    """The report layer, and the one constraint that ties it to the order layer.

    `report-treatment.csv` asks of each Rule 16.1 subject, for each 16.1(b)(1) report: did the
    report answer it, was that answer responsive to something the order directed, and did the
    report go beyond what the order asked. The third column is where the interesting question
    lives, because a report that answers more than the order asked is evidence the Rule is
    doing work the judge did not do.

    The join constraint is the reason this file exists rather than more prose in
    `party-invocations.csv`. `responsive_to_order=TRUE` asserts something about the ORDER,
    namely that it directed the parties on that subject, and the order layer already records
    exactly that in `party_direction`. Two tables that can disagree about the same fact will
    eventually disagree, so this checks them against each other. It is the only cross-layer
    constraint in the project and it is cheap.
    """
    if not os.path.exists(REPORTS):
        return []
    out, seen = [], set()
    direction = {}
    for r in csv.DictReader(open(FILE)):
        if r["party_direction"].strip().upper() == "TRUE":
            direction[(r["mdl_no"], r["subject_id"])] = True
    known = {r["invocation_id"] for r in csv.DictReader(open(INVOCATIONS))
             if "16.1(b)(1) REPORT" in (r.get("doc_kind") or "")} \
        if os.path.exists(INVOCATIONS) else set()

    per_report = Counter()
    for i, r in enumerate(csv.DictReader(open(REPORTS)), start=2):
        inv, sid = r["invocation_id"], r["subject_id"]
        where = f"line {i}  {inv} {sid}"
        per_report[inv] += 1
        if (inv, sid) in seen:
            out.append((where, "duplicate report-subject row"))
        seen.add((inv, sid))
        if known and inv not in known:
            out.append((where, f"{inv} is not a 16.1(b)(1) REPORT in {INVOCATIONS}"))

        vals = {f: r[f].strip().upper()
                for f in ("answered", "responsive_to_order", "beyond_order")}
        for f, v in vals.items():
            if v not in RBOOL:
                out.append((where, f"{f} is {r[f]!r}; must be TRUE, FALSE, NOT_CHECKED, "
                                   f"NOT_READABLE or blank"))
        if r["readable"].strip().upper() == "NO":
            if any(v != "NOT_READABLE" for v in vals.values()):
                out.append((where, "readable=NO, so every judgment must be NOT_READABLE; "
                                   "a document nobody has read cannot answer anything"))
            continue
        if any(v in ("", "NOT_CHECKED") for v in vals.values()):
            continue

        T = lambda f: vals[f] == "TRUE"
        if T("responsive_to_order") and not T("answered"):
            out.append((where, "responsive_to_order=TRUE but answered=FALSE"))
        if T("beyond_order") and not T("answered"):
            out.append((where, "beyond_order=TRUE but answered=FALSE"))
        if T("responsive_to_order") and not direction.get((r["mdl_no"], sid)):
            out.append((where, f"responsive_to_order=TRUE, but the order layer records no "
                               f"party_direction for MDL {r['mdl_no']} {sid}. One of the two "
                               f"tables is wrong; they cannot both be right."))
        if T("answered") and not r["quote"].strip():
            out.append((where, "answered=TRUE requires a verbatim quote"))

    for inv, n in per_report.items():
        if n != SUBJECTS:
            out.append((f"{inv}", f"has {n} subject rows; every report needs exactly "
                                  f"{SUBJECTS}, so a missing subject is visible as absence "
                                  f"rather than as a smaller denominator"))
    return out


CODEBOOK = "subject-treatment-codebook.md"


def codebook_subjects():
    """The twenty subjects as the codebook defines them, parsed from its own table.

    The codebook is the frozen definition of what a subject IS. Both CSVs carry a
    `subject_id` and the report layer also carries a `subject_definition`, which until
    31 August 2026 was typed by hand: ten of the twenty were blank and the ten that were
    filled in did not match the codebook's wording. A definition column that disagrees
    with the codebook is worse than an empty one, because a coder reads the row rather
    than the codebook and codes to the wrong question.

    Returns {subject_id: "(cite) subject"} in the codebook's order.
    """
    if not os.path.exists(CODEBOOK):
        return {}
    book = open(CODEBOOK, encoding="utf-8").read()
    rows = re.findall(r"^\| `(\w+)` \| (\([^|]+?)\s*\| ([^|]+?) \|$", book, re.M)
    return {sid: f"{cite.strip()} {subj.strip()}" for sid, cite, subj in rows}


def registry_errors():
    """Both CSVs must use the codebook's subject registry, exactly.

    Neither file's subject list had ever been checked against the codebook. Nothing stops a
    typo in a `subject_id` from creating a twenty-first subject that every count then divides
    by twenty, or a renamed subject in the codebook from leaving both CSVs describing a
    question that no longer exists. The check is three comparisons and it is the only thing
    in the project that reads the codebook as data rather than as prose.
    """
    want = codebook_subjects()
    if not want:
        return []
    out = []
    if len(want) != SUBJECTS:
        out.append((CODEBOOK, f"defines {len(want)} subjects; this validator and every "
                              f"denominator in the project assume {SUBJECTS}"))

    for path in (FILE, REPORTS):
        if not os.path.exists(path):
            continue
        ids = {r["subject_id"] for r in csv.DictReader(open(path))}
        for extra in sorted(ids - set(want)):
            out.append((path, f"subject_id {extra!r} is not in the codebook registry"))
        for missing in sorted(set(want) - ids):
            out.append((path, f"the codebook defines {missing!r} and no row uses it"))

    if os.path.exists(REPORTS):
        for i, r in enumerate(csv.DictReader(open(REPORTS)), start=2):
            w = want.get(r["subject_id"])
            if w is not None and r["subject_definition"].strip() != w:
                out.append((f"line {i}  {r['invocation_id']} {r['subject_id']}",
                            f"subject_definition disagrees with the codebook\n"
                            f"          codebook: {w!r}\n"
                            f"          row     : {r['subject_definition'].strip()!r}"))
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
    rerrs = report_errors()
    if os.path.exists(REPORTS):
        n = sum(1 for _ in csv.DictReader(open(REPORTS)))
        coded = sum(1 for r in csv.DictReader(open(REPORTS))
                    if r["answered"].strip().upper() in ("TRUE", "FALSE"))
        print(f"{REPORTS}: {n} rows, {coded} coded")
    errs = errs + rerrs + registry_errors()
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
