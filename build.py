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

_TENS = {20: "Twenty", 30: "Thirty", 40: "Forty", 50: "Fifty",
         60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninety"}


def _plural_districts(n):
    """"one district" / "two districts". Written out because the page said "two district"
    for one build: the count was computed and the noun was hard-coded next to it."""
    return f"{WORDS[n].lower()} district" + ("" if n == 1 else "s")


def word(n):
    """Spell out an integer below 100.

    WORDS stops at twenty because for a long time nothing on the page went higher. A
    corrected count went to twenty-nine and raised a KeyError, which is the good failure
    mode: the build refused rather than printing a bare numeral into a sentence that reads
    as spelled-out prose. This extends the range instead of silently falling back."""
    if n in WORDS:
        return WORDS[n]
    if n >= 100:
        raise ValueError(f"word() is for figures below one hundred, got {n}")
    tens, ones = divmod(n, 10)
    return _TENS[tens * 10] + ("-" + WORDS[ones].lower() if ones else "")


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


SUBJECTS = ["b2a_leadership", "b2a_timing", "b2a_structure", "b2a_selection_procedure",
            "b2a_periodic_review", "b2a_responsibilities", "b2a_communication",
            "b2a_nonleadership_limits", "b2a_compensation", "b2b_vacate_modify",
            "b2c_conference_schedule", "b2d_direct_filing", "b2e_related_actions",
            "b3a_consolidated_pleadings", "b3b_factual_basis_exchange", "b3c_discovery",
            "b3d_pretrial_motions", "b3e_settlement_facilitation", "b3f_magistrate_master",
            "b3g_principal_issues"]


SUBJECT_PROSE = {
    "b2a_leadership": "whether leadership counsel should be appointed",
    "b2a_selection_procedure": "the procedure for selecting them",
    "b2a_periodic_review": "periodic review of leadership appointments",
    "b2a_timing": "the timing of the appointments",
    "b2a_structure": "the structure of leadership counsel",
    "b2a_responsibilities": "their responsibilities and authority",
    "b2a_communication": "methods for communicating with the court",
    "b2a_nonleadership_limits": "limits on nonleadership counsel",
    "b2a_compensation": "compensating leadership counsel",
    "b2b_vacate_modify": "orders that should be vacated or modified",
    "b2c_conference_schedule": "a schedule for additional conferences",
    "b2d_direct_filing": "direct filing",
    "b2e_related_actions": "related actions elsewhere",
    "b3a_consolidated_pleadings": "consolidated pleadings",
    "b3b_factual_basis_exchange": "exchanging the factual bases of claims",
    "b3c_discovery": "discovery",
    "b3d_pretrial_motions": "likely pretrial motions",
    "b3e_settlement_facilitation": "measures to facilitate resolution",
    "b3f_magistrate_master": "referral to a magistrate judge or master",
    "b3g_principal_issues": "the principal factual and legal issues",
}


def subject_stats():
    """Figures computed from subject-treatment.csv, the canonical subject-level table.

    Findings 2 and 2b are asserted against this file rather than against the twenty
    subject columns in the order-level CSV. Those columns are a pre-existing coding that
    the subject-level pass supersedes; regenerating them is a later step, and until then
    the two sources disagree on 27 of 260 cells. Anything the page says about how many
    orders reach a subject must come from here, or it will be asserting the old numbers.
    """
    reached = {}
    for r in csv.DictReader(open("subject-treatment.csv")):
        if r["reached"].strip():
            reached.setdefault(r["mdl_no"], {})[r["subject_id"]] = \
                r["reached"].strip().upper() == "TRUE"
    n = len(reached)
    hits = {s: sum(1 for m in reached if reached[m][s]) for s in SUBJECTS}
    # Split by whether the order cites the Rule, so the page can state both coverage
    # measures. TOPICS-based figures elsewhere in this file still come from the
    # order-level columns; these come from the subject-level table, and the two disagree
    # until the order-level subject columns are regenerated. See AUDIT.md, 12 Aug 2026.
    cites = {r["mdl_no"]: r["cites_rule"] for r in full_rows()}
    scale19 = [x for x in SUBJECTS if x != "b2a_leadership"]   # the site's 19-column scale
    yes = [m for m in reached if cites.get(m) == "YES"]
    no = [m for m in reached if cites.get(m) != "YES"]

    def per(group, field):
        return sorted(sum(1 for x in scale19 if col[m][x][field]) for m in group)

    col = {}
    for r in csv.DictReader(open("subject-treatment.csv")):
        col.setdefault(r["mdl_no"], {})[r["subject_id"]] = {
            f: r[f].strip().upper() == "TRUE"
            for f in ("reached", "express", "party_direction", "court_resolution")}

    def med(v):
        return int(statistics.median(v))

    def rate(group):
        cells = sum(1 for m in group for x in SUBJECTS if col[m][x]["court_resolution"])
        return round(100 * cells / (len(SUBJECTS) * len(group)))

    return {
        "n": n,
        "hits": hits,
        "cite_med": med(per(yes, "reached")), "nocite_med": med(per(no, "reached")),
        "cite_lo": per(yes, "reached")[0], "cite_hi": per(yes, "reached")[-1],
        "nocite_lo": per(no, "reached")[0], "nocite_hi": per(no, "reached")[-1],
        "cite_exp_med": med(per(yes, "express")), "nocite_exp_med": med(per(no, "express")),
        "cite_exp_lo": per(yes, "express")[0],
        "cite_res_rate": rate(yes), "nocite_res_rate": rate(no),
        "universal": sorted(s for s in SUBJECTS if hits[s] == n),
        "least": min(hits.values()) if hits else 0,
        "least_ids": sorted(x for x in SUBJECTS if hits[x] == min(hits.values())),
        "direct_filing": hits.get("b2d_direct_filing", 0),
        "uncoded": [m for m in {r["mdl_no"] for r in csv.DictReader(open("subject-treatment.csv"))}
                    if m not in reached],
    }


def assert_subject_columns():
    """The twenty subject columns in the order-level CSV are derived output equal to
    `reached` in subject-treatment.csv. migrate_subject_columns.py writes them; this
    refuses to build if they have since drifted apart.

    The check is here rather than in the migration script because drift can be introduced
    by editing either file, and the build is the thing that runs every time.
    """
    want = {}
    for r in csv.DictReader(open("subject-treatment.csv")):
        if r["reached"].strip():
            want.setdefault(r["mdl_no"], {})[r["subject_id"]] = (
                "YES" if r["reached"].strip().upper() == "TRUE" else "NOT_ADDRESSED")
    bad = []
    for r in full_rows():
        if r["mdl_no"] not in want:
            continue
        for s in SUBJECTS:
            if r[s].strip() != want[r["mdl_no"]][s]:
                bad.append(f"MDL {r['mdl_no']} {s}: order-level {r[s].strip()!r}, "
                           f"derived {want[r['mdl_no']][s]!r}")
    if bad:
        print(f"\nSUBJECT COLUMN DRIFT - {len(bad)} cell(s) disagree with "
              f"subject-treatment.csv:")
        for b in bad[:20]:
            print("  · " + b)
        if len(bad) > 20:
            print(f"  ... and {len(bad) - 20} more")
        print("\nsubject-treatment.csv is canonical. Re-run migrate_subject_columns.py.")
        sys.exit(1)


def search_stats():
    """Counts over rule-16-1-searches.csv, the log of the uptake queries.

    Search results are not derivable from the other CSVs, so they get their own file
    rather than being typed into the page as bare numbers. This is what lets build.py
    assert the findings that rest on them.
    """
    all_rows = list(csv.DictReader(open("rule-16-1-searches.csv")))
    # Three kinds of row live in this file and only one of them is a live figure.
    #   CURRENT    the corrected sweep, run under entry_date_filed_after
    #   SUPERSEDED the original sweep, run under filed_after, which restricts by CASE
    #              filing date and so excluded every document in a case filed before the
    #              effective date. Kept because its per-form counts are the proof of the
    #              diagnosis, not because they are still true of the corpus.
    #   REFERENCE  measurements that are not naming forms and belong to no published count
    # Nothing on the page may be computed from anything but CURRENT.
    rows = [r for r in all_rows if r["status"] == "CURRENT"]
    superseded = [r for r in all_rows if r["status"] == "SUPERSEDED"]
    n = lambda k: sum(int(r[k]) for r in rows)
    # `hits` double-counts: two forms returned the same documents. `new_documents` is
    # the count of documents no earlier form had returned, so it sums to the true union.
    return {"forms": len(rows),
            "productive": sum(1 for r in rows if int(r["new_documents"]) > 0),
            "empty": sum(1 for r in rows if int(r["hits"]) == 0),
            "docs": n("new_documents"), "hits": n("hits"),
            "unverified": n("hits_unverified"),
            "mdl": n("hits_in_post_effective_mdl"),
            "pre_mdl": n("hits_in_pre_effective_mdl"),
            "nonmdl": n("hits_non_mdl"), "noise": n("hits_noise_rule_16"),
            # Orthogonal to the five triage categories, which partition the hits. This one
            # counts hits whose document has NO readable text, so the Rule's name was matched
            # in the clerk's docket entry rather than in the filing. Not part of the sum.
            "no_text": n("hits_no_text_layer"),
            "old_docs": sum(int(r["new_documents"]) for r in superseded),
            "added": n("new_documents") - sum(int(r["new_documents"]) for r in superseded)}


def assert_search_arithmetic():
    """Every hit in a distinct query form is in exactly one triage category.

    The five category columns must sum to `hits` for each CURRENT row that contributed new
    documents. A duplicate form -- one whose results another form already returned, like
    `abbrev_no_spaces` -- carries its true `hits` but zeroes in every category, so that the
    union arithmetic is not double counted. Those rows are checked to be all zero instead.

    This is why the file's category columns do not sum to the file's `hits` column and that
    is not a bug: the difference is exactly the duplicate rows' hits.
    """
    cats = ["hits_in_post_effective_mdl", "hits_in_pre_effective_mdl",
            "hits_non_mdl", "hits_noise_rule_16", "hits_unverified"]
    # Every published figure is computed from status == CURRENT. A typo in that column would
    # silently drop a row from every count and nothing else would notice, which is the same
    # class of failure as the date filter: a query that quietly stops seeing part of its
    # corpus. So the vocabulary is closed and the build refuses on anything outside it.
    KNOWN = {"CURRENT", "SUPERSEDED", "REFERENCE", "CONTROL"}
    for r in csv.DictReader(open("rule-16-1-searches.csv")):
        if r["status"] not in KNOWN:
            sys.exit(f"search row {r['query_form']}: unknown status {r['status']!r}; "
                     f"must be one of {sorted(KNOWN)}")
        if r["status"] != "CURRENT":
            continue
        got, hits = sum(int(r[c]) for c in cats), int(r["hits"])
        if int(r["new_documents"]) == 0:
            if got:
                sys.exit(f"search row {r['query_form']}: a duplicate form must carry zeroes "
                         f"in every triage column, found {got}")
        elif got != hits:
            sys.exit(f"search row {r['query_form']}: triage columns sum to {got}, "
                     f"hits is {hits}. Every hit belongs to exactly one category.")


def invocation_stats():
    """Counts over party-invocations.csv, for the findings about non-MDL invocations."""
    rows = list(csv.DictReader(open(INVOCATIONS)))
    nonmdl = [r for r in rows if r["mdl_no"] == "NON-MDL"]
    outside = [r for r in nonmdl if "OUTSIDE ITS SCOPE" in r["doc_kind"]]
    # A court citing the Rule in a case it does not govern and a lawyer doing the same
    # thing are different facts and the page counts them separately. Before INV-017 every
    # outside-scope record happened to be a court order, so one count served for both and
    # the finding said "orders." The first party-side instance made that silently wrong,
    # which is the same failure shape as the search filter: a count that was right only
    # because the world had not yet produced the case that distinguished it.
    orders = [r for r in outside if r["filer"].upper().startswith("COURT")
              or r["filer"].upper().startswith("THE COURT")]
    filings = [r for r in outside if r not in orders]
    courts = sorted({r["court"] for r in orders})
    dates = sorted(r["date_filed"] for r in orders)
    def pretty(d):
        return datetime.date.fromisoformat(d).strftime("%B %Y") if d else ""
    return {"n": len(rows), "nonmdl": len(nonmdl), "outside": len(orders),
            "outside_all": len(outside), "outside_filings": len(filings),
            "outside_courts": courts,
            "all_courts": sorted({r["court"] for r in outside}),
            "first": dates[0] if dates else "", "last": dates[-1] if dates else "",
            "span_first": pretty(dates[0] if dates else ""),
            "span_last": pretty(dates[-1] if dates else "")}


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
    ss = subject_stats()
    iv = invocation_stats()
    sq = search_stats()

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
        ("finding 1: median coverage, citing vs non-citing",
         f"a median of {ss['cite_med']} of the {len(TOPICS)} items tracked here "
         f"against {ss['nocite_med']} for the", None),
        ("finding 1: spread of both groups",
         f"spread, {ss['cite_lo']} to {ss['cite_hi']} and "
         f"{ss['nocite_lo']} to {ss['nocite_hi']},", None),
        ("finding 1b: the two measures and the resolution inversion",
         f"the medians are {ss['cite_exp_med']} and {ss['nocite_exp_med']}, and the citing "
         f"spread widens to {ss['cite_exp_lo']}", None),
        ("finding 1b: resolution rates",
         f"decide {ss['cite_res_rate']}% of the subjects they raise, against "
         f"{ss['nocite_res_rate']}%", None),
        ("finding 1: non-citing orders designating the MCL",
         f"{sum(1 for r in no if 'MCL' in r['rule_vocabulary'])} non-citing orders designate", None),
        # Both of these literals are anchored at BOTH ends on purpose. Anchored on one
        # side only, a shorter computed list stays a substring of the longer sentence on
        # the page and the check silently passes. Verified by mutation test 12 Aug 2026.
        ("finding 2: which subjects every order reaches",
         "every order: " + " and ".join(SUBJECT_PROSE[x] for x in ss["universal"])
         + f". Both stand at {ss['n']} of {ss['n']} orders read subject by subject", None),
        ("finding 2: least-addressed subjects and count",
         "The least-addressed items are "
         + " and ".join(SUBJECT_PROSE[x] for x in ss["least_ids"])
         + f", {ss['least']} of {ss['n']} each", None),
        ("finding 2b: direct filing",
         f"moves it to {ss['direct_filing']} of {ss['n']}", None),
        ("finding 3a: query forms",
         f"the same {WORDS[sq['forms']].lower()} forms return", None),
        ("finding 3a: unique document count",
         f"forms return {sq['docs']} documents rather than {sq['old_docs']}", None),
        ("finding 3a: how many the corrected filter added",
         f"an increase of {sq['added']}. One form went", None),
        ("finding 3a: how many forms were productive",
         f"{word(sq['productive'])} of the {WORDS[sq['forms']].lower()} forms returned "
         f"something no other form did", None),
        ("finding 3a: every addition has been read",
         f"All {sq['added']} additions have now been read", None),
        # The corrected counts appear in four sentences across three sections. Each is
        # anchored separately, because the failure this whole exercise exposed was a
        # number that was consistent everywhere it appeared and wrong in every place.
        ("finding 3a: one document, several names",
         f"Across {sq['docs']} documents exactly one names the Rule", None),
        ("limitations: how many the wrong filter hid",
         f"hid {sq['added']} documents and produced a published null", None),
        ("limitations: corrected sweep total",
         f"corrected sweep returns {sq['docs']} documents, all of which", None),
        # The triage totals are per HIT, not per document: a document returned by three forms
        # is triaged three times, which is why these sum to `hits` minus the duplicate form's
        # 41 and not to 101. The page therefore states them only about the 33 additions, where
        # the two coincide, and the guard is on that sentence.
        ("finding 3a: hits with no text layer",
         f"{word(sq['no_text'])} of the {sq['docs']} results have no readable text", None),
        ("finding 3a: what the additions turned out to be",
         "Thirteen contain no literal \"16.1\" anywhere", None),
        ("finding 3b: rule cited outside MDL practice",
         f"{WORDS[iv['outside']]} orders across", None),
        ("finding 3b: how many districts",
         f"orders across {WORDS[len(iv['outside_courts'])].lower()} districts", None),
        ("finding 3b: how many further districts on the party side",
         "party side, in " + _plural_districts(len(iv["all_courts"])
                                               - len(iv["outside_courts"])) + " more", None),
        ("finding 3b: the span of dates",
         f"between {iv['span_first']} and {iv['span_last']},", None),
        ("finding 3: TPLF null",
         f"litigation funding, {n('b4_tplf_disclosure')} of {s['coded']}", None),
        ("finding 4: interval range",
         f"runs from {s['min_days']} days to {s['max_days']}", None),
        # 61 appears in three places including the JSON-LD, and is derivable, so it is
        # asserted rather than trusted. Found unguarded by a numeral audit on 13 Aug 2026.
        ("meta pill: variable count",
         f"{len(full[0])} variables", None),
        ("JSON-LD: variable count",
         f"{len(full[0])} variables per MDL", None),
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


def _text(s):
    """The page with tags removed, so a figure sitting inside a <span> can be asserted as
    ordinary prose rather than as markup."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))


def check_prose(page):
    flat, text = _flat(page), _text(page)
    return [(label, literal) for label, literal, _ in prose_claims(page)
            if _flat(literal) not in flat and _flat(literal) not in text]


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
    SUB_STATS = subject_stats()
    INV_STATS = invocation_stats()
    SQ_STATS = search_stats()
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
        put("f3a-forms", WORDS[SQ_STATS["forms"]].lower()),
        put("f3a-hits", str(SQ_STATS["docs"])),
        put("f3a-old", str(SQ_STATS["old_docs"])),
        put("f3a-added", str(SQ_STATS["added"])),
        put("f3a-added2", str(SQ_STATS["added"])),
        put("f3a-hits2", str(SQ_STATS["docs"])),
        put("f3a-hits3", str(SQ_STATS["docs"])),
        put("f3a-notext", word(SQ_STATS["no_text"])),
        # Sentence-initial since the rewrite of 13 Aug 2026, so no .lower() here.
        put("f3a-prod", word(SQ_STATS["productive"])),
        put("f3a-forms2", WORDS[SQ_STATS["forms"]].lower()),
        put("f3a-unver", word(SQ_STATS["unverified"])),
        put("f3b-n", WORDS[INV_STATS["outside"]]),
        put("f3b-courts", WORDS[len(INV_STATS["outside_courts"])].lower() + " districts"),
        put("f3b-fc", _plural_districts(len(INV_STATS["all_courts"])
                                        - len(INV_STATS["outside_courts"]))),
        put("f3b-first", INV_STATS["span_first"]),
        put("f3b-last", INV_STATS["span_last"]),
        put("f1-cm", str(SUB_STATS["cite_med"])),
        put("f1-nm", str(SUB_STATS["nocite_med"])),
        put("f1-clo", str(SUB_STATS["cite_lo"])),
        put("f1-chi", str(SUB_STATS["cite_hi"])),
        put("f1-nlo", str(SUB_STATS["nocite_lo"])),
        put("f1-nhi", str(SUB_STATS["nocite_hi"])),
        put("f1b-cem", str(SUB_STATS["cite_exp_med"])),
        put("f1b-nem", str(SUB_STATS["nocite_exp_med"])),
        put("f1b-celo", str(SUB_STATS["cite_exp_lo"])),
        put("f1b-crr", str(SUB_STATS["cite_res_rate"])),
        put("f1b-nrr", str(SUB_STATS["nocite_res_rate"])),
        put("f2-universal", str(len(SUB_STATS["universal"]) and SUB_STATS["n"])),
        put("f2-den", str(SUB_STATS["n"])),
        put("f2-least", str(SUB_STATS["least"])),
        put("f2-den2", str(SUB_STATS["n"])),
        put("f2b-df", str(SUB_STATS["direct_filing"])),
        put("f2b-den", str(SUB_STATS["n"])),
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
    assert_subject_columns()
    assert_search_arithmetic()
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
