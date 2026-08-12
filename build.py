#!/usr/bin/env python3
"""
Regenerate the landing page's embedded data and headline figures from the CSVs.

WHY THIS EXISTS: index.html hard-codes a snapshot of the data so the page is a
single self-contained file with no server and no fetch. That is the right
tradeoff for a citable artifact - and it means the page silently goes stale the
moment a CSV changes. It happened within an hour of the page being built.

Three jobs:

  1. EMBED  the rows the page renders, as JSON, for the table and the chart.
     Only the fields the page actually displays are embedded. The full 61
     columns live in the CSV, which the page links. Embedding everything meant
     truncating long free-text fields mid-word, which put damaged data in the
     page source for no benefit.

  2. PRERENDER the headline figures into the markup. The JS recomputes them at
     load as a consistency check, but a crawler, an archive snapshot or a reader
     with JS disabled must still see real numbers. A dataset whose headline is
     blank in the Wayback Machine is not citable.

  3. ASSERT the figures written by hand in the findings prose against the CSV,
     and refuse to build if any has drifted. Prose needs judgment and cannot be
     generated, but it can be checked.

RUN THIS AFTER EVERY EDIT TO EITHER CSV, THEN COMMIT BOTH.

    python3 build.py            # rewrite embedded data + figures, report drift
    python3 build.py --check    # exit 1 if the page is stale; nothing written
"""
import csv, json, re, sys, datetime, statistics

TRACKER = "rule-16-1-tracker.csv"
INVOCATIONS = "party-invocations.csv"
PAGE = "index.html"
CODED = ("TEXT_AVAILABLE", "TEXT_ORDER_ON_DOCKET")

# Only what the page renders. Everything else is in the CSV, which the page links.
KEEP = ["mdl_no", "caption", "court", "judge", "jpml_transfer_date", "source_status",
        "cites_rule", "rule_role", "report_form", "days_transfer_to_conference",
        "a_conference_date", "courtlistener_url"]
IKEEP = ["invocation_id", "mdl_no", "case_name", "doc_title", "ecf", "date_filed",
         "pages", "joint_or_unilateral", "doc_kind", "cites_rule_16_1",
         "cites_committee_note"]

WORDS = {0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
         7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve",
         13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen",
         17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty"}


def rows():
    out = []
    for r in sorted(csv.DictReader(open(TRACKER)), key=lambda x: int(x["mdl_no"])):
        d = {k: r.get(k, "") for k in KEEP}
        d["caption"] = d["caption"].split("(master docket entry")[0].strip()
        out.append(d)
    return out


def invocations():
    return [{k: r.get(k, "") for k in IKEEP} for r in csv.DictReader(open(INVOCATIONS))]


def full_rows():
    """All columns, for the prose assertions."""
    return list(csv.DictReader(open(TRACKER)))


EFFECTIVE = datetime.date(2025, 12, 1)


def months_since_effective(today=None):
    d = today or datetime.date.today()
    m = (d.year - EFFECTIVE.year) * 12 + (d.month - EFFECTIVE.month)
    return m - (1 if d.day < EFFECTIVE.day else 0)


def stats(data):
    coded = [r for r in data if r["source_status"] in CODED]
    yes = [r for r in coded if r["cites_rule"] == "YES"]
    iv = [int(r["days_transfer_to_conference"]) for r in coded
          if r["days_transfer_to_conference"]]
    no_date = [r["mdl_no"] for r in coded if not r["days_transfer_to_conference"]]
    return {
        "universe": len(data),
        "coded": len(coded),
        "cite": len(yes),
        "nocite": len(coded) - len(yes),
        "pct": round(100 * len(yes) / len(coded)) if coded else 0,
        "intervals": len(iv),
        "min_days": min(iv) if iv else 0,
        "max_days": max(iv) if iv else 0,
        "no_date": no_date,
        "age_months": months_since_effective(),
        "no_order": sum(1 for r in data if r["source_status"] == "NO_ORDER_YET"),
        "unread": sum(1 for r in data if r["source_status"] not in CODED + ("NO_ORDER_YET",)),
    }


# ---------------------------------------------------------------- prose guard

THIN = ("3162", "3163", "3166", "3171", "3174", "3175")   # pin cites without quoted language

TOPICS = ["b2a_timing", "b2a_structure", "b2a_selection_procedure", "b2a_periodic_review",
          "b2a_responsibilities", "b2a_communication", "b2a_nonleadership_limits",
          "b2a_compensation", "b2b_vacate_modify", "b2c_conference_schedule",
          "b2d_direct_filing", "b2e_related_actions", "b3a_consolidated_pleadings",
          "b3b_factual_basis_exchange", "b3c_discovery", "b3d_pretrial_motions",
          "b3e_settlement_facilitation", "b3f_magistrate_master", "b3g_principal_issues"]


def prose_claims(page):
    """Every hand-written figure in the findings, with what the CSV says it should be.

    Prose cannot be generated - it carries judgment - but it can be asserted.
    Each entry is (label, literal that must appear in the page, computed value).
    """
    full = full_rows()
    coded = [r for r in full if r["source_status"] in CODED]
    yes = [r for r in coded if r["cites_rule"] == "YES"]
    no = [r for r in coded if r["cites_rule"] != "YES"]
    s = stats(rows())

    def topics_hit(group):
        return round(sum(sum(1 for t in TOPICS if r[t] == "YES") for r in group) / len(group))

    def n(col, val="YES", group=coded):
        return sum(1 for r in group if r[col] == val)

    mcl_noncite = sum(1 for r in no if "MCL" in r["rule_vocabulary"])

    def median_topics(group):
        return int(statistics.median([sum(1 for t in TOPICS if r[t] == "YES") for r in group]))

    def spread(group):
        v = [sum(1 for t in TOPICS if r[t] == "YES") for r in group]
        return min(v), max(v)

    ylo, yhi = spread(yes)
    nlo, nhi = spread(no)

    return [
        ("finding 1: citing / total",
         f"{len(yes)} of the {s['coded']} readable orders cite Rule 16.1 by name; "
         f"{len(no)} do not", None),
        ("finding 1: all coded orders order a report",
         f"all {s['coded']} call for a report", None),
        ("finding 1: median topics, citing vs non-citing",
         f"a median of {median_topics(yes)} of the {len(TOPICS)} items tracked here "
         f"against {median_topics(no)} for the", None),
        ("finding 1: spread of both groups",
         f"spread widely, {ylo} to {yhi} and {nlo} to {nhi},", None),
        ("finding 1: non-citing orders designating the MCL",
         f"{sum(1 for r in no if 'MCL' in r['rule_vocabulary'])} non-citing orders designate", None),
        ("finding 2: leadership",
         f"every order addresses, {n('b2a_leadership')} of {s['coded']}", None),
        ("finding 2: least-addressed",
         f"resolution, {n('b2d_direct_filing')} of {s['coded']} each", None),
        ("finding 3: TPLF null",
         f"litigation funding, {n('b4_tplf_disclosure')} of {s['coded']}", None),
        ("finding 4: interval range",
         f"runs from {s['min_days']} days to {s['max_days']}", None),
        ("findings footnote: column count",
         f"{len(TOPICS)} columns cover the Rule's 18 listed items", None),
        ("method: coverage",
         f"Coverage is <strong>{s['coded']} of {s['universe']}</strong>", None),
        ("limitations: thin tier",
         f"{len(THIN)} rows ({', '.join(THIN)}) give paragraph pointers", None),
        ("limitations: quoted tier",
         f"the other {s['coded'] - len(THIN)} quote it directly", None),
        ("limitations: thin rows among citing orders",
         f"{sum(1 for r in yes if r['mdl_no'] in THIN)} of the {len(yes)} citing orders sit "
         f"among them", None),
        ("limitations: chambers-routed reports",
         f"{n('report_channel', 'CHAMBERS_EMAIL')} of the {s['coded']} courts direct", None),
    ]


def _flat(s):
    """Collapse whitespace so that line wrapping in the HTML is not treated as drift."""
    return re.sub(r"\s+", " ", s)


def check_prose(page):
    flat = _flat(page)
    return [(label, literal) for label, literal, _ in prose_claims(page)
            if _flat(literal) not in flat]


# --------------------------------------------------------------------- render

def set_inner(page, el_id, html):
    """Replace the inner HTML of the element carrying this id.

    Written by hand rather than with a regex because the replacement HTML itself
    contains tags: a lazy `(.*?)(</)` pattern stops at the FIRST closing tag inside
    the element, so re-running the build appends a stray `</span>` to the citation
    tile every time. That is not idempotent, which silently corrupts the markup and
    makes --check report a freshly built page as stale. Walk the tag depth instead.
    """
    m = re.search(rf'<(\w+)(?=[^>]*\bid="{re.escape(el_id)}")[^>]*>', page)
    if not m:
        return page
    tag = m.group(1)
    start = m.end()
    depth, i = 1, start
    token = re.compile(rf'<(/?){tag}\b', re.I)
    while depth and (t := token.search(page, i)):
        depth += -1 if t.group(1) else 1
        i = t.end()
        if depth == 0:
            close = t.start()
            return page[:start] + html + page[close:]
    return page


def prerender(page, s):
    """Write the computed figures into the markup so they survive without JS."""
    puts = []

    def put(el_id, html):
        puts.append((el_id, html))
        return None

    subs = [
        put("t-univ", str(s["universe"])),
        put("t-coded", str(s["coded"])),
        put("t-coded-s", f"{WORDS[s['no_order']].lower()} "
                         f"{'has' if s['no_order'] == 1 else 'have'} no qualifying order"),
        put("t-cite", f'{s["cite"]} <span style="font-size:20px;'
                      f'color:var(--text-secondary)">/ {s["coded"]}</span>'),
        put("t-cite-s", f"{s['pct']}% of coded orders"),
        put("t-blk", str(s["unread"])),
        put("t-blk-s", f"{s['unread']} of {s['universe']}. See limitations."),
        put("pct-inline", f"{s['pct']}%"),
        put("n-intervals", str(s["intervals"])),
        put("age-months", str(s["age_months"])),
        put("age-months2", str(s["age_months"])),
        put("chart-n", f"n = {s['intervals']} of the {s['coded']} coded orders. "
                       + " and ".join("MDL " + m for m in s["no_date"])
                       + " set no conference date in the order. No interval is recorded "
                         "for them, and they are excluded here rather than counted as zero."),
    ]
    for el_id, html in puts:
        page = set_inner(page, el_id, html)
    return page


def main():
    check = "--check" in sys.argv
    data, inv = rows(), invocations()
    page = open(PAGE).read()

    m = re.search(r"const DATA=(\[.*?\]),\s*INV=(\[.*?\]);", page, re.S)
    if not m:
        sys.exit("could not find the embedded data block in " + PAGE)

    s = stats(data)
    stale = (json.loads(m.group(1)) != data or json.loads(m.group(2)) != inv
             or prerender(page, s) != page)
    drifted = check_prose(page)

    print(f"universe {s['universe']} · coded {s['coded']} · cite {s['cite']} · "
          f"no-cite {s['nocite']} ({s['pct']}%) · intervals {s['intervals']} "
          f"[{s['min_days']}-{s['max_days']}d] · no order yet {s['no_order']} · "
          f"not yet readable {s['unread']} "
          f"({round(100 * s['unread'] / s['universe'])}%)")

    if drifted:
        print("\nPROSE DRIFT - these hand-written figures no longer match the CSV:")
        for label, literal in drifted:
            print(f"  · {label}\n      expected the page to contain: {literal!r}")
        print("\nFix the wording in index.html, then re-run. The findings are written by "
              "hand on purpose; this check exists so they cannot quietly go stale.")
        sys.exit(1)

    if check:
        print("PAGE IS STALE - run build.py" if stale else "page matches the CSVs")
        sys.exit(1 if stale else 0)

    page = re.sub(r"const DATA=\[.*?\],\s*INV=\[.*?\];",
                  lambda _: "const DATA=" + json.dumps(data, separators=(",", ":")) +
                            ", INV=" + json.dumps(inv, separators=(",", ":")) + ";",
                  page, flags=re.S)
    page = prerender(page, s)
    page = re.sub(r'(id="upd">)[^<]*(</strong>)',
                  r"\g<1>" + datetime.date.today().strftime("%d %B %Y") + r"\g<2>", page)
    open(PAGE, "w").write(page)
    print("rebuilt " + PAGE + (" (data changed)" if stale else " (no data change)")
          + " · prose figures verified against the CSV")

    print("\nREMINDER - these numbers appear in the submission too. If any changed, "
          "recompute the letter before sending; it states thirteen figures drawn from "
          "this CSV.")


if __name__ == "__main__":
    main()
