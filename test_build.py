#!/usr/bin/env python3
"""
Prove that build.py's guards actually fire.

This repository's recurring failure, logged seven times in AUDIT.md, is a check that exists,
runs, reports success, and is not aimed at the thing that broke. Every guard in build.py was
written in response to one of those, and until now not one of them had ever been shown to
fail on purpose. A guard nobody has watched break is a guard nobody has tested.

The method is corruption injection. Copy the repository, break exactly one thing, run
`build.py --check` as a subprocess, and require it to exit non-zero AND to name the thing that
was broken. Naming matters as much as failing: a guard that dies with the wrong message sends
the next person to debug the wrong file, which is how the quota failure cost three runs.

    python3 test_build.py

Each case restores the file it touched, and the suite finishes by proving the untouched
repository still builds clean, so a test that corrupts and forgets cannot make the next case
pass for the wrong reason.
"""
import csv, os, re, shutil, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(tempfile.gettempdir(), "r161-build-test")


def build(args=("--check",)):
    r = subprocess.run([sys.executable, "build.py", *args], cwd=TMP,
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


def read(f):
    return open(os.path.join(TMP, f), encoding="utf-8").read()


def write(f, s):
    open(os.path.join(TMP, f), "w", encoding="utf-8").write(s)


def rows_of(f):
    with open(os.path.join(TMP, f), encoding="utf-8") as fh:
        r = list(csv.DictReader(fh))
    return r, list(r[0].keys())


def write_rows(f, rows, cols):
    cols = [c for c in cols if c is not None]
    with open(os.path.join(TMP, f), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows([{k: v for k, v in r.items() if k is not None} for r in rows])


RESULTS = []


def case(label, guard, mutate, must_say):
    """Break one thing, require the build to notice and to say which thing."""
    backups = {}
    try:
        touched = mutate(backups)
        code, out = build()
        fired = code != 0
        named = any(w.lower() in out.lower() for w in must_say)
        ok = fired and named
        RESULTS.append(ok)
        flag = "PASS" if ok else "FAIL"
        why = "" if ok else ("  <- did not fail at all" if not fired else
                             f"  <- failed without naming {must_say}")
        print(f"  {flag}  {guard:26} {label}{why}")
        if not ok:
            print("        " + " / ".join(out.strip().splitlines()[-3:])[:220])
    finally:
        for f, s in backups.items():
            write(f, s)
    return


def snap(backups, *files):
    for f in files:
        backups[f] = read(f)


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    shutil.copytree(REPO, TMP, ignore=shutil.ignore_patterns("__pycache__", ".git", ".github"))
    code, out = build()
    print(f"baseline: exit {code}  {out.strip().splitlines()[-1] if out.strip() else ''}\n")
    if code != 0:
        print("the untouched repository does not build; nothing below would mean anything")
        sys.exit(1)

    # ---- assert_rectangular, the shifted row -------------------------------------------
    # The published tracker does not round-trip through DictWriter, and rewriting the dataset
    # to test a guard would be its own kind of damage, so it is mutated as text.
    def unquoted_comma(b):
        snap(b, "rule-16-1-tracker.csv")
        s = read("rule-16-1-tracker.csv")
        # exactly the edit that broke MDL 3180 on 23 August: a comma inside an unquoted field
        write("rule-16-1-tracker.csv", s.replace(",TEXT_AVAILABLE,", ",TEXT, AVAILABLE,", 1))
    case("an unquoted comma splits one field into two", "assert_rectangular", unquoted_comma,
         ["ragged", "fields"])

    def short_row(b):
        snap(b, "subject-treatment.csv")
        lines = read("subject-treatment.csv").split("\n")
        lines[1] = ",".join(lines[1].split(",")[:-2])
        write("subject-treatment.csv", "\n".join(lines))
    case("a row two fields short", "assert_rectangular", short_row, ["ragged", "fields"])

    # ---- assert_links, the twelve dead links -------------------------------------------
    def strip_slug(b):
        snap(b, "rule-16-1-tracker.csv")
        s = read("rule-16-1-tracker.csv")
        m = re.search(r"https://www\.courtlistener\.com/docket/(\d+)/[^,\"\n]+/", s)
        write("rule-16-1-tracker.csv",
              s[:m.start()] + f"https://www.courtlistener.com/docket/{m.group(1)}/" + s[m.end():])
    case("a bare /docket/<id>/ with no slug", "assert_links", strip_slug,
         ["courtlistener_url", "404"])

    def no_trailing_slash(b):
        snap(b, "rule-16-1-tracker.csv")
        s = read("rule-16-1-tracker.csv")
        m = re.search(r"https://www\.courtlistener\.com/docket/\d+/[^,\"\n]+/", s)
        write("rule-16-1-tracker.csv", s[:m.end()-1] + s[m.end():])
    case("a docket URL with no trailing slash", "assert_links", no_trailing_slash,
         ["courtlistener_url"])

    # ---- assert_subject_columns ---------------------------------------------------------
    def flip_subject(b):
        snap(b, "subject-treatment.csv")
        rows, cols = rows_of("subject-treatment.csv")
        for r in rows:
            if r["reached"].strip().upper() == "TRUE":
                r["reached"] = "FALSE"
                r["express"] = r["party_direction"] = r["court_resolution"] = "FALSE"
                break
        write_rows("subject-treatment.csv", rows, cols)
    case("a reached cell flipped under the order layer", "assert_subject_columns",
         flip_subject, ["subject column drift"])

    # ---- assert_search_arithmetic -------------------------------------------------------
    def bad_status(b):
        snap(b, "rule-16-1-searches.csv")
        rows, cols = rows_of("rule-16-1-searches.csv")
        rows[0]["status"] = "CURENT"
        write_rows("rule-16-1-searches.csv", rows, cols)
    case("a typo in the status vocabulary", "assert_search_arithmetic", bad_status,
         ["unknown status"])

    def bad_source(b):
        snap(b, "rule-16-1-searches.csv")
        rows, cols = rows_of("rule-16-1-searches.csv")
        rows[0]["triage_source"] = "ROBOT"
        write_rows("rule-16-1-searches.csv", rows, cols)
    case("a triage_source outside the vocabulary", "assert_search_arithmetic", bad_source,
         ["triage_source"])

    def unbalanced(b):
        snap(b, "rule-16-1-searches.csv")
        rows, cols = rows_of("rule-16-1-searches.csv")
        for r in rows:
            if r["status"] == "CURRENT" and int(r["new_documents"]) > 0:
                r["hits_noise_rule_16"] = str(int(r["hits_noise_rule_16"]) + 1)
                break
        write_rows("rule-16-1-searches.csv", rows, cols)
    case("a hit counted in two categories", "assert_search_arithmetic", unbalanced,
         ["sum", "categor"])

    def duplicate_nonzero(b):
        snap(b, "rule-16-1-searches.csv")
        rows, cols = rows_of("rule-16-1-searches.csv")
        for r in rows:
            if r["status"] == "CURRENT" and int(r["new_documents"]) == 0:
                r["hits_noise_rule_16"] = "3"
                break
        write_rows("rule-16-1-searches.csv", rows, cols)
    case("a duplicate form given triage counts", "assert_search_arithmetic",
         duplicate_nonzero, ["duplicate form"])

    # ---- assert_citation_version --------------------------------------------------------
    def stale_cite(b):
        snap(b, "index.html")
        s = read("index.html")
        write("index.html", s.replace("(v1.1, August 2026)", "(v1.0, August 2026)", 1))
    case("one of three citation versions reverted", "assert_citation_version", stale_cite,
         ["citation version"])

    def stale_cff(b):
        snap(b, "CITATION.cff")
        s = read("CITATION.cff")
        write("CITATION.cff", s.replace('version: "1.1"', 'version: "1.2"'))
    case("CITATION.cff moved and nothing else did", "assert_citation_version", stale_cff,
         ["citation version"])

    # ---- check_readme -------------------------------------------------------------------
    def readme_headline(b):
        snap(b, "README.md")
        s = read("README.md")
        write("README.md", s.replace("8 of 15 MDLs with a readable", "9 of 15 MDLs with a readable", 1))
    case("the README headline corrupted", "check_readme", readme_headline,
         ["readme headline", "prose drift"])

    def readme_cells(b):
        snap(b, "README.md")
        s = read("README.md")
        write("README.md", s.replace("**300 of 300 cells**", "**299 of 300 cells**", 1))
    case("the README cell count corrupted", "check_readme", readme_cells,
         ["readme cell count", "prose drift"])

    def dataset_shape(b):
        """A column added to the tracker must break all five statements of its shape.

        The page says "61 variables" in the header badge, the JSON-LD description, the JSON-LD
        download entry, the download prose and the download link. All five were hand-written
        and unguarded until 31 August 2026; `audit_numbers.py` found them by listing every
        numeral on the page that nothing asserts.
        """
        snap(b, "rule-16-1-tracker.csv")
        rows, cols = rows_of("rule-16-1-tracker.csv")
        cols = [c for c in cols if c] + ["scratch"]
        for r in rows:
            r["scratch"] = ""
        write_rows("rule-16-1-tracker.csv", rows, cols)
    case("a column added to the tracker without updating the page", "check_prose",
         dataset_shape, ["shape: header badge"])

    def version_badge(b):
        """The version badge is prerendered, so a hand edit must read as stale.

        It said v1.0-draft for nineteen days while CITATION.cff said 1.1 and the citation box
        said v1.1, and assert_citation_version could not see it: that guard matches the
        parenthesised "(v1.1, August 2026)" form and the badge carries a bare version. The fix
        was to prerender it, which means the guard that now protects it is the stale check.
        """
        snap(b, "index.html")
        s = read("index.html")
        assert '<span class="pill" id="ver">v' in s, "the version badge moved; fix the test"
        write("index.html", re.sub(r'(id="ver">)v[\d.]+(<)', r"\g<1>v0.9\g<2>", s, count=1))
    case("the version badge edited by hand", "the embedded data block", version_badge,
         ["stale"])

    # ---- check_prose --------------------------------------------------------------------
    # The literal these two cases corrupt is the page's headline finding. It is written out
    # in full rather than matched with a loose pattern: the first version of this case used
    # r"(\d+) of (\d+) readable orders cite", which never matched because the sentence reads
    # "8 of THE 15 readable orders cite", and so the case reported a guard failure that was
    # really a test failure. A corruption test that does not corrupt anything is the same
    # mistake this whole suite exists to catch, one level up.
    FINDING1 = "8 of the 15 readable orders cite Rule 16.1 by name; 7 do not"
    WRONG1 = "9 of the 15 readable orders cite Rule 16.1 by name; 6 do not"

    def page_prose(b):
        snap(b, "index.html")
        s = read("index.html")
        assert s.count(FINDING1) == 1, "the asserted literal moved; fix the test, not the guard"
        write("index.html", s.replace(FINDING1, WRONG1, 1))
    case("the only copy of a finding contradicts the CSV", "check_prose", page_prose,
         ["prose drift"])

    def page_prose_duplicate(b):
        """A wrong copy of a claim sitting beside a correct copy.

        This is the case check_prose structurally cannot see, because it asks whether the
        right string is PRESENT and the right string is present. check_readme was rewritten
        in August for this exact shape and its docstring says so; the page's own guard was
        left with the shape the README's guard had abandoned. Running this case against
        build.py as it stood on 31 August 2026 exited 0 and printed "page matches the CSVs".
        """
        snap(b, "index.html")
        s = read("index.html")
        i = s.index(FINDING1) + len(FINDING1)
        write("index.html", s[:i] + " " + WRONG1 + s[i:])
    case("a wrong copy of a finding beside a correct copy", "check_contradictions",
         page_prose_duplicate, ["prose contradiction"])

    # ---- the data block ------------------------------------------------------------------
    def stale_block(b):
        snap(b, "rule-16-1-tracker.csv")
        rows, cols = rows_of("rule-16-1-tracker.csv")
        rows[0]["judge"] = rows[0]["judge"] + " Jr."
        write_rows("rule-16-1-tracker.csv", rows, cols)
    case("a CSV edited without rebuilding the page", "the embedded data block", stale_block,
         ["stale"])

    # ---- and the repository must still be clean ------------------------------------------
    code, out = build()
    ok = code == 0
    RESULTS.append(ok)
    print(f"\n  {'PASS' if ok else 'FAIL'}  every case restored what it broke; "
          f"the repository still builds clean")

    print(f"\n  {sum(RESULTS)}/{len(RESULTS)} passed\n")
    return all(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
