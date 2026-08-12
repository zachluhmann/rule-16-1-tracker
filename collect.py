#!/usr/bin/env python3
"""
Rule 16.1 Tracker — CourtListener collection script.

Pulls candidate documents that reference Fed. R. Civ. P. 16.1, dedupes them,
and writes a review queue you code by hand. It does NOT code anything. Coding
is the product; automation only finds the documents.

SETUP
-----
    pip install requests
    export COURTLISTENER_TOKEN="your-token"      # free at courtlistener.com

USAGE
-----
    python collect.py                    # run all queries, write review-queue.csv
    python collect.py --query precise    # just the high-precision query
    python collect.py --since 2025-12-01 # restrict by date filed

RATE LIMITS (free authenticated tier) — MEASURED, NOT ESTIMATED
---------------------------------------------------------------
    5/minute · 50/hour · 125/day   <-- the DAILY cap is the real constraint

The 125/day ceiling was hit in a single working session on 2026-08-11 and it
resets on a rolling window, not at midnight. Batch aggressively:
  * read_document accepts a LIST of chunk indexes (up to 10) in one call
  * search_document accepts a LIST of up to 10 document ids in one call
A Free Law Project membership lifts all three limits and is now worth it. The
script self-throttles to stay under the per-minute cap and will stop cleanly on a
429 rather than hammering — but nothing it does can get you past the daily cap.

THE SEARCH TRAP — READ THIS (TWO TRAPS, NOT ONE)
------------------------------------------------
TRAP 2, discovered 2026-08-11 and worse than trap 1: the index does NOT treat
"16.1" as a token distinct from "16". Run the "precise" query below with no
filed_after and you get ~697 documents, overwhelmingly plain Rule 16 scheduling
orders reciting "pursuant to Fed. R. Civ. P. 16."

The precision of every query in this file therefore depends on
filed_after=2025-12-01 — the rule did not exist before then, so the date filter
removes the Rule 16 noise for free. State the date filter as PART OF THE QUERY in
any published methodology, and never report a raw hit count as a measure of
anything. See PROTOCOL.md Guardrail 10 for how this constrains the
pre-effective-date question.

TRAP 1: Do NOT query bare "Rule 16.1". It returns ~1,470 mostly-garbage RECAP hits,
because the District of Massachusetts and the Southern District of Florida each
have a LOCAL Rule 16.1. S.D. Fla. paperless scheduling orders routinely say
things like "relieved of the conference report requirement of Local Rule
16.1(b)". None of that is the federal rule.

Use the precision queries below. Expect ~29 dockets from the precise query and
~59 documents from the MDL-scoped one — and note that MDL 3175's leadership
order alone appears roughly 20 times across associated member cases, which is
why deduping on docket_entry_id is not optional.
"""

import argparse
import csv
import os
import sys
import time
from collections import OrderedDict

try:
    import requests
except ImportError:
    sys.exit("pip install requests")

API = "https://www.courtlistener.com/api/rest/v4"
TOKEN = os.environ.get("COURTLISTENER_TOKEN", "")

# Query set. Keys become the `matched_query` column so you can see which
# query surfaced a document and tune precision over time.
QUERIES = OrderedDict([
    # High precision. Almost no local-rule noise, because nobody writes out
    # "Federal Rule of Civil Procedure" when they mean a local rule.
    ("precise", '"Federal Rule of Civil Procedure 16.1"'),

    # Catches "Fed. R. Civ. P. 16.1" and "FRCP 16.1" style cites.
    ("abbrev", '"Fed. R. Civ. P. 16.1" OR "F.R.C.P. 16.1" OR "FRCP 16.1"'),

    # Scoped catch-all. Higher recall, needs manual triage — this is where
    # local-rule noise creeps back in, so read every hit.
    ("mdl_scoped", '"Rule 16.1" AND ("multidistrict" OR "MDL")'),

    # The TPLF expansion field. Run it against the same MDL universe so you
    # can answer whether courts order funding disclosure under 16.1(b)(4).
    ("tplf", '("litigation funding" OR "third-party funding" OR "litigation finance") '
             'AND ("multidistrict" OR "MDL") AND (disclos* OR discover*)'),

    # ---- THE REPORT LAYER (added 2026-08-11) --------------------------------
    # Rule 16.1's only real mandates run to the PARTIES' REPORT, not the judge.
    # Every query above finds orders. These find the reports — and reports are
    # EASIER to find, because parties name the rule in the docket text itself.
    #
    # This was discovered the expensive way: MDL 3170 ECF 33 is docketed as
    # "STATUS Report F.R.C.P. 16.1" — thirteen pages, on the public docket,
    # invisible to every order-focused query above. It is the first actual
    # Rule 16.1 report located, and it documents the single-report mechanism of
    # 16.1(b)(1) failing in the rule's sixth week.
    ("reports", '"Rule 16.1 Report" OR "F.R.C.P. 16.1" OR "16.1 Report" '
                'OR "Fed. R. Civ. P. 16.1 Report"'),

    # Party briefing that cites the rule without being a report. Catches the
    # bar-side invocations (leadership fights, motions) that no survey measures.
    ("party_cites", '"Rule 16.1" AND ("leadership counsel" OR "interim lead" '
                    'OR "steering committee")'),

    # Is the Advisory Committee's note being briefed as operative authority?
    # In MDL 3170 it is quoted four times, and the rulemaking record itself is
    # cited. If that generalizes it is a finding in its own right.
    ("committee_note", '"16.1" AND ("Advisory Committee" OR "Committee Note" '
                       'OR "Committee\'s note")'),
])

FIELDS = [
    "matched_query", "case_name", "docket_number", "court", "date_filed",
    "description", "docket_entry_id", "docket_id", "absolute_url",
    "download_url", "coded",
]


def get(path, params, tries=3):
    """GET with token auth, gentle throttle, and clean 429 handling."""
    if not TOKEN:
        sys.exit("Set COURTLISTENER_TOKEN. Free token at courtlistener.com.")
    headers = {"Authorization": f"Token {TOKEN}"}
    for attempt in range(tries):
        r = requests.get(f"{API}{path}", params=params, headers=headers, timeout=60)
        if r.status_code == 429:
            print("  ! rate limited — stopping cleanly. Rerun later or upgrade.",
                  file=sys.stderr)
            return None
        if r.ok:
            time.sleep(13)   # ~4.6 req/min, just under the 5/min cap
            return r.json()
        print(f"  ! HTTP {r.status_code} (attempt {attempt+1})", file=sys.stderr)
        time.sleep(5)
    return None


def search(query, since=None, max_pages=10):
    """Run one RECAP-document search, following pagination."""
    rows, page, cursor = [], 0, None
    while page < max_pages:
        params = {"q": query, "type": "rd", "order_by": "dateFiled desc"}
        if since:
            params["filed_after"] = since
        if cursor:
            params["cursor"] = cursor
        data = get("/search/", params)
        if not data:
            break
        results = data.get("results", [])
        rows.extend(results)
        print(f"  page {page+1}: +{len(results)} (total {len(rows)})")
        nxt = data.get("next")
        if not nxt or not results:
            break
        cursor = nxt.split("cursor=")[-1].split("&")[0]
        page += 1
    return rows


def flatten(hit, qname):
    """RECAP search hits nest documents under `recap_documents`."""
    docs = hit.get("recap_documents") or [{}]
    out = []
    for d in docs:
        out.append({
            "matched_query": qname,
            "case_name": hit.get("caseName", ""),
            "docket_number": hit.get("docketNumber", ""),
            "court": hit.get("court_id", ""),
            "date_filed": d.get("entry_date_filed") or hit.get("dateFiled", ""),
            "description": (d.get("description") or d.get("short_description") or "")[:300],
            "docket_entry_id": d.get("docket_entry_id", ""),
            "docket_id": hit.get("docket_id", ""),
            "absolute_url": "https://www.courtlistener.com" + (d.get("absolute_url") or ""),
            "download_url": d.get("filepath_local") or "",
            "coded": "NO",
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", choices=list(QUERIES) + ["all"], default="all")
    ap.add_argument("--since", default="2025-12-01",
                    help="Rule 16.1 effective date; widen to catch pre-effective invocations")
    ap.add_argument("--out", default="review-queue.csv")
    args = ap.parse_args()

    names = list(QUERIES) if args.query == "all" else [args.query]
    seen, rows = set(), []

    for name in names:
        print(f"\n>> {name}: {QUERIES[name]}")
        for hit in search(QUERIES[name], since=args.since):
            for row in flatten(hit, name):
                # THE dedupe. MDL leadership orders replicate across every
                # member case; without this your N is inflated ~20x.
                key = row["docket_entry_id"] or (row["docket_id"], row["description"])
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)

    rows.sort(key=lambda r: (r["date_filed"] or ""), reverse=True)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"\n{len(rows)} unique documents -> {args.out}")
    print("\nNext: read each order and code it into rule-16-1-tracker.csv.")
    print("Code from the ORDER TEXT, never from the docket description.")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# ALERT CONFIGURATION — do this once, in the CourtListener web UI
# ---------------------------------------------------------------------------
#
# SEARCH ALERT (catches new orders anywhere)
#   1. Run this search in the UI:
#        "Federal Rule of Civil Procedure 16.1"   (type: RECAP)
#   2. Save it as an alert, frequency: Daily.
#   This is your primary capture mechanism and it costs nothing.
#
# DOCKET ALERTS (catches everything in your known universe)
#   Free tier gives 5 docket alerts; installing the RECAP browser extension
#   raises it to 15. Members get unlimited. You have ~15 MDLs, so the free
#   tier *just barely* works — but membership is the right call once you're
#   past 15 MDLs, which happens within a year.
#
#   Set one alert per MDL master docket. Docket alerts incur NO PACER fees.
#
# PACER COSTS
#   $0.10/page, $3.00 cap per document, and fees are WAIVED ENTIRELY below
#   $30/quarter. At ~40-60 documents a year you will almost certainly never
#   pay a cent. Written opinions are always free regardless.
#
#   Also: apply for a PACER fee exemption as an NYU student researcher —
#   courts grant these for scholarly research.
#
# INSTALL THE RECAP EXTENSION
#   Every document you pull from PACER then flows back into the public
#   archive. Costs you nothing, makes the commons better, and means your
#   own sources stay free and stable for anyone citing you.


# ===========================================================================
# THE RETRIEVAL LADDER — run these IN ORDER before calling any row blocked
# ===========================================================================
# Added 2026-08-11. Following this ladder took the block rate from 57% to 13%.
# A prematurely declared NEEDS_PACER_PULL is a soft version of the same error
# as a wrongly coded NO.
#
# 1. RECAP search (the queries above).
#
# 2. THE DUPLICATE-RECORD TECHNIQUE. The same filing can exist as more than one
#    recap_document; some copies have a text layer and some do not. Enumerate
#    every AVAILABLE document on the master docket:
#
#        GET /recap-documents/?docket_entry__docket__id=<CL docket id>
#                              &is_available=true
#                              &fields=id,document_number,attachment_number,
#                                      description,page_count,is_available
#
#    Or, via search:  type=rd, docket_number=..., available_only=true
#    NOTE: type=rd results use DIFFERENT field names than docket results. Ask
#    for id / docket_id / entry_number / entry_date_filed / description /
#    short_description / is_available / page_count. Asking for caseName or
#    dateFiled silently returns empty objects.
#    NOTE: scope by DOCKET ID, not by caption keywords — a caption search
#    returns the JPML's own docket, which is a different docket entirely.
#
#    Unblocked this way: MDL 3166, 3163, 3172, 3179, 3185.
#
# 3. THE DISTRICT COURT'S OWN WEBSITE. Free, public, court-published, and it
#    lists orders in SEQUENCE — which is how you discover that a conference
#    order and the management order it produced say different things. It also
#    surfaces reassignment and recusal orders that RECAP metadata flattens.
#
#        site:<district>.uscourts.gov "md<MDL number>"
#
#    The District of Utah's page is the model and it closed MDL 3167, which two
#    rounds of RECAP work could not:
#        https://www.utd.uscourts.gov/multi-district-litigation-mdl-cases
#
#    ⚠ These are CMS paths, not permanent identifiers. Perma.cc every one the
#    day you cite it.
#
# 4. MEMBER-CASE DOCKETS. MDL pretrial orders are usually entered in every
#    member case; one of those copies may have a text layer. MDL 3167's PTO 1
#    names its six member cases on the face of the order.
#
# 5. govinfo.gov — free and permanent, but district-court order coverage is thin.
#
# 6. PACER, last. $0.10/page, $3.00/document cap, waived below $30/quarter.
#
# Only after all six is a row honestly NEEDS_PACER_PULL.
#
#
# UNIVERSE RECONCILIATION — the thing that actually protects the denominator
# ---------------------------------------------------------------------------
# Monthly, pull:
#   https://www.jpml.uscourts.gov/sites/jpml/files/
#       Pending_MDL_Dockets_By_MDL_Number-<Month>-<D>-<YYYY>.pdf
#
# Read the DATE CLOSED column: for a pending MDL that is the date the Panel's
# docket closed, i.e. the transfer date. That is what puts an MDL in or out of
# the post-2025-12-01 universe — NOT the DATE FILED, which is when the petition
# was filed.
#
# Three traps this catches, all of which bit the seed:
#   • An entire in-scope MDL can be missing. MDL 3170 (Trans Union) was, and its
#     master docket is a -cv- number, so no docket-number pattern finds it.
#   • "Not Assigned" on a JPML docket means the petition is UNDECIDED, not that
#     the MDL is a phantom. MDL 3181 was written off on that basis and is real.
#   • Sequence gaps are usually not gaps. 3164, 3165, 3168-3170*, 3173, 3177,
#     3182-3184, 3186 are JPML docket numbers for petitions that were denied or
#     withdrawn. A JPML "MDL No." is a docket number for a MOTION, not proof an
#     MDL exists — which is also why a stray reference to a high MDL number in a
#     party filing does not mean the universe grew.
#     (* 3170 is the exception that proves it: a real MDL the seed missed.)
