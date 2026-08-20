#!/usr/bin/env python3
"""
Autonomous watch for the Rule 16.1 tracker. Runs on GitHub Actions. No human involved.

NORMAL MODE (weekly)
  1. Reruns the seven naming forms and diffs the document IDs against the last run.
  2. Checks Guardrail 11's positive control inside that sweep and refuses to record a
     measurement if the control is absent.
  3. Triages any new document by rule, and by a model only where no rule decides and only
     where the model can quote the document verbatim. See triage.py.
  4. Updates rule-16-1-searches.csv, but ONLY if the classifier has been validated against
     the hand triage first, and only ever moving hits between categories that the new
     documents' own text supports. Anything undecided is counted `hits_unverified`, which is
     a real column that already sums into the arithmetic, and an issue is opened for it.
  5. Checks the dockets of MDLs marked NO_ORDER_YET.
  6. Runs validate_treatment.py and build.py as gates, and commits only if both pass.

BACKFILL MODE (--backfill, run once by hand from the Actions tab)
  Classifies the whole existing corpus and compares the result against the triage a human
  did by reading the documents. Until that comparison passes, normal mode will not touch
  rule-16-1-searches.csv at all. A classifier that has never been scored against the person
  it replaces is not evidence of anything, and this is the only corpus in existence where
  both answers are available.

WHAT IT STILL WILL NOT DO
  Code an order. Whether a provision fires `court_resolution` is judgment, and two trained
  coders split on it twenty-two times out of three hundred. Triage is a different kind of
  question: the document's own first line names the case it is in. The watch detects that a
  new order exists, opens an issue, and stops.

Secrets: COURTLISTENER_TOKEN (required). ANTHROPIC_API_KEY or OPENAI_API_KEY (optional; the
model tier is skipped without one and everything it would have decided stays unverified).
"""
import csv, io, json, os, subprocess, sys, time, datetime
import urllib.request, urllib.error, urllib.parse
import triage

API      = "https://www.courtlistener.com/api/rest/v4/"
TOKEN    = os.environ.get("COURTLISTENER_TOKEN", "")
CUTOFF   = "2025-12-01"
SEARCHES = "rule-16-1-searches.csv"
STATE    = "maintenance/watch-state.json"
LOG      = "maintenance/watch-log.csv"
LEDGER   = "maintenance/triage-ledger.csv"
VALID    = "maintenance/triage-validation.json"
ISSUE    = "maintenance/.watch-issue.md"

CONTROL_DOC  = 472850310
CONTROL_FORM = "spelled_out"

FORMS = [
    ("abbrev",           '"Fed. R. Civ. P. 16.1"'),
    ("spelled_out",      '"Federal Rule of Civil Procedure 16.1"'),
    ("frcp_acronym",     '"FRCP 16.1"'),
    ("frcp_periods",     '"F.R.C.P. 16.1"'),
    ("report_phrase",    '"Rule 16.1 Report"'),
    ("abbrev_no_spaces", '"Fed.R.Civ.P. 16.1"'),
    ("long_form",        '"Rule 16.1 of the Federal Rules of Civil Procedure"'),
]

NO_ORDER_YET = {"3176": 73170267}

CATS = {"post_effective_mdl": "hits_in_post_effective_mdl",
        "pre_effective_mdl":  "hits_in_pre_effective_mdl",
        "non_mdl":            "hits_non_mdl",
        "noise":              "hits_noise_rule_16",
        "unverified":         "hits_unverified"}

# CourtListener's documented limits for an authenticated user, all three applying at once:
# 5 per minute, 50 per hour, 125 per day. The first version of this file paced on the minute
# limit alone, at 13 seconds a request, which is 277 an hour. A backfill of 101 documents
# sailed past the hourly cap eleven minutes in and every request after that was refused. It
# did not crash: each failure was caught and skipped, so the run would have finished with
# half a ledger and reported a PASS, because a comparison that only checks whether the
# classifier OVER-counts a category passes trivially when most documents are missing from it.
# A silent underfill that validates itself is the exact failure this project keeps finding.
# Paced to a FRACTION of the documented caps, not to the caps themselves. The second live
# backfill obeyed 5/60, 50/3600 and 125/86400 by its own accounting and CourtListener still
# answered 429. For two runs that was read as evidence the published numbers were wrong. It
# was not. On 20 August 2026 the server said plainly what it was doing:
#
#     Rate limit exceeded: 125/day. Expected available in 54227 seconds.
#
# The documented limits are exactly what is metered. What was wrong was the assumption that a
# process begins its day with the full 125. The allowance belongs to the ACCOUNT, not to the
# run. The weekly watch, every backfill attempt, and every interactive CourtListener call made
# anywhere else all draw on one daily pool, and that pool refills one slot at a time on a
# rolling 24-hour window rather than resetting at midnight. A fresh process cannot see how
# much of it is already gone, and no endpoint will tell it. So this limiter's own arithmetic
# can be perfectly correct and still meet a 429 on request one.
#
# That makes the right answer to a 429 the opposite of retrying harder or pacing slower.
# Pacing slower does not create quota. It only means fewer documents get read before the job
# is killed. The run stops, keeps what it has, and says how much is left. See QuotaExhausted.
LIMITS = ((5, 60), (50, 3600), (125, 86400))
SAFETY = [0.8]           # multiplier on every cap; tightened only on a 429 with no Retry-After
# Stop reading with time to spare against the job's 350-minute timeout, so the run ends by
# writing what it has rather than by being killed holding it.
BUDGET_SECONDS = int(os.environ.get("BACKFILL_BUDGET_SECONDS", 300 * 60))
_hist  = []
THROTTLE = None          # set to a float in tests to bypass the limiter
DEADLINE = [None]        # absolute time this run must stop by; None disables the check


class QuotaExhausted(Exception):
    """The day's allowance is spent and the reset is further away than this run can wait.

    Raised instead of sleeping. CourtListener answers a 429 with a Retry-After that has been
    observed at fifteen hours, which is longer than any job in this repo is allowed to live.
    Sleeping on it means being killed by the timeout while still holding everything that was
    read. Raising it means the caller writes the ledger and reports honestly how far it got.
    """

    def __init__(self, seconds):
        self.seconds = int(seconds)
        super().__init__(f"daily quota spent; a slot frees in {self.seconds}s")


# ---------------------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------------------

def _throttle():
    """Block until a request can be made without breaching any of the three limits."""
    if THROTTLE is not None:
        time.sleep(THROTTLE)
        return
    while True:
        now = time.time()
        _hist[:] = [t for t in _hist if now - t < LIMITS[-1][1]]
        waits = []
        for n, window in LIMITS:
            cap = max(1, int(n * SAFETY[0]))
            recent = [t for t in _hist if now - t < window]
            if len(recent) >= cap:
                waits.append(window - (now - recent[-cap]) + 0.5)
        if not waits:
            _hist.append(now)
            return
        nap = min(max(waits), 300)
        print(f"  rate limit: waiting {nap:.0f}s ({len(_hist)} requests so far)", flush=True)
        time.sleep(nap)


def _open(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Token {TOKEN}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def get(path, params=None, url=None):
    """One request, throttled, with one retry on 429."""
    target = url or (API + path + "?" + urllib.parse.urlencode(params or {}))
    for attempt in range(1, 6):
        _throttle()
        try:
            return _open(target)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            # Honour the server's own instruction when it gives one. Blind 600 and 1200
            # second sleeps burned half the second backfill's time budget on documents it
            # then failed anyway.
            hdr = (e.headers.get("Retry-After") if e.headers else None) or ""
            told = hdr.strip().isdigit()
            nap = int(hdr) if told else min(60 * 2 ** (attempt - 1), 300)
            # A Retry-After longer than this run has left is not something to wait out. The
            # day's allowance is gone, and no amount of patience inside this process brings it
            # back before the job is killed.
            if DEADLINE[0] is not None and time.time() + nap > DEADLINE[0]:
                raise QuotaExhausted(nap)
            if told:
                print(f"  429; the server asks for {nap}s and this run can afford to wait",
                      flush=True)
            else:
                # No instruction from the server, so the limiter's own model may really be
                # wrong. This is the only case where tightening the pacing is a real answer.
                SAFETY[0] = max(0.25, SAFETY[0] * 0.75)
                print(f"  429 with no Retry-After (attempt {attempt}); pacing down to "
                      f"{SAFETY[0]:.0%} of the documented caps, waiting {nap}s", flush=True)
            time.sleep(nap)
    raise RuntimeError(f"429 after 5 attempts at {SAFETY[0]:.0%} of the documented caps")


def sweep(q, meta):
    """One naming form, all pages, returning its set of RECAP document ids.

    entry_date_filed_after, never filed_after. The second restricts by the CASE filing date,
    so it silently deletes every document in a case filed before the cutoff. It once produced
    a published null that was false and that no run of the same method could have refuted.

    Each result object is kept in `meta` because it carries the clerk's docket entry text,
    which the RECAP index searches alongside the document text. A hit on a document with no
    text layer was matched on that entry, and the entry is then the only evidence there is.
    """
    params = {"q": q, "type": "rd", "entry_date_filed_after": CUTOFF,
              "order_by": "score desc", "page_size": 100}
    ids, page = set(), None
    while True:
        d = get("search/", params) if page is None else get(None, url=page)
        for x in d.get("results", []):
            ids.add(x["id"])
            meta.setdefault(x["id"], x)
        page = d.get("next")
        if not page:
            return ids


def fetch_document(doc_id, meta):
    """The document itself, merged with what the search result already told us.

    plain_text and sha1 come from the document endpoint. `description`, the clerk's entry,
    comes from the search result: it is a property of the docket entry, not of the document,
    and the document endpoint's own `description` field is usually empty.
    """
    d = get(f"recap-documents/{doc_id}/",
            {"fields": "id,sha1,is_available,is_sealed,page_count,plain_text"})
    m = meta.get(doc_id, {})
    d["description"] = m.get("description") or d.get("description") or ""
    d["docket_id"] = m.get("docket_id")
    d["absolute_url"] = m.get("absolute_url")
    d["entry_date_filed"] = m.get("entry_date_filed")
    return d


def latest_entry(docket_id):
    d = get("docket-entries/", {"docket": docket_id, "order_by": "-entry_number",
                                "page_size": 1, "fields": "entry_number,date_filed"})
    res = d.get("results") or []
    return (res[0].get("entry_number") or 0, res[0].get("date_filed") or "") if res else (0, "")


# ---------------------------------------------------------------------------------------
# ledger
# ---------------------------------------------------------------------------------------

# `docket_id` is recorded even though no published figure uses it. It is the field the
# strongest locating rule reads, and storing it means a later change to the rules can be
# re-scored against the documents already read, using only the seven sweep requests rather
# than re-fetching a hundred documents. A ledger that keeps the evidence a rule consumed is
# a ledger you can re-run a rule against.
LEDGER_COLS = ["document_id", "first_seen", "forms", "category", "method", "rule",
               "mdl_no", "docket_id", "rules_version", "no_text_layer", "escalate",
               "evidence"]


def read_ledger():
    if not os.path.exists(LEDGER):
        return {}
    return {int(r["document_id"]): r for r in csv.DictReader(open(LEDGER))}


def write_ledger(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=LEDGER_COLS)
    w.writeheader()
    for k in sorted(rows, key=int):
        w.writerow({c: rows[k].get(c, "") for c in LEDGER_COLS})
    open(LEDGER, "w", newline="").write(buf.getvalue())


def classify_one(doc_id, forms, meta, reg, by_sha1, today, dockets=None, learned=None):
    # Try the search result first. It costs nothing, it is already in hand, and for a document
    # that names the Rule on a docket we recognise it is sufficient. Only what it declines
    # is worth a request.
    hit = meta.get(doc_id, {})
    v = triage.classify_from_search(hit, reg, dockets, learned)
    doc = hit if v else fetch_document(doc_id, meta)
    if not v:
        v = triage.classify(doc, reg, by_sha1, dockets, learned)
    if v["category"] == "unverified" and v.get("escalate"):
        m = triage.ask_model(doc, reg)
        if m and m["category"] != "unverified":
            v = {**v, **m, "rule": v["rule"] + "+MODEL"}
        elif m:
            v = {**v, "method": m["method"], "escalate": m["escalate"] or v["escalate"]}
    row = {"document_id": doc_id, "first_seen": today, "forms": " ".join(sorted(forms)),
           "category": v["category"], "method": v.get("method", "RULE"), "rule": v["rule"],
           "mdl_no": v.get("mdl_no", ""), "docket_id": doc.get("docket_id") or "",
           "rules_version": triage.RULES_VERSION,
           "no_text_layer": "YES" if v["no_text_layer"] else "",
           "escalate": v.get("escalate", ""), "evidence": v.get("evidence", "")}
    if doc.get("sha1") and v["category"] != "unverified":
        by_sha1[doc["sha1"]] = {"document_id": doc_id, "category": v["category"],
                                "mdl_no": v.get("mdl_no", "")}
    return row


# ---------------------------------------------------------------------------------------
# search log
# ---------------------------------------------------------------------------------------

def read_searches():
    rows = list(csv.DictReader(open(SEARCHES)))
    return rows, list(rows[0].keys())


def current_rows(rows):
    return {r["query_form"]: r for r in rows if r["status"] == "CURRENT"}


def validated():
    """Has the classifier been scored against the hand triage, and did it pass?"""
    if not os.path.exists(VALID):
        return False, "the classifier has never been scored against the hand triage; run the workflow once with backfill=true"
    v = json.load(open(VALID))
    return bool(v.get("passed")), v.get("summary", "")


# ---------------------------------------------------------------------------------------
# backfill
# ---------------------------------------------------------------------------------------

def backfill_complete():
    """Has a previous run already read every document under the current rules?

    Answered from the validation file alone, so a scheduled resume on a corpus that is
    already finished costs nothing at all. Keyed on the rules version for the same reason the
    ledger is: a file written by an older classifier is not an answer about this one.
    """
    try:
        v = json.load(open(VALID))
    except Exception:
        return False
    return bool(v.get("complete")) and v.get("rules_version") == triage.RULES_VERSION


def backfill(today, reg, dockets=None, learned=None):
    """Classify the existing corpus and score it against the triage a human did by reading.

    THE TEST IS ONE-SIDED AND THAT IS STATED ON PURPOSE. The hand triage exists only as
    per-form totals, not per document, so the comparison cannot confirm that any individual
    call matches. What it CAN do is catch a call that is definitely wrong: if the classifier
    puts more documents in a category than the human's total for that category, at least one
    of them is misfiled. So this proves disagreement and merely bounds agreement, and the
    number it reports is the number of documents the classifier was willing to decide, not
    the number it got right.
    """
    meta, now_forms = {}, {}
    # Set before the first request, not before the reading loop: the seven sweeps are requests
    # too, and a run that has no quota left will meet the 429 there.
    DEADLINE[0] = time.time() + BUDGET_SECONDS
    try:
        for form, q in FORMS:
            now_forms[form] = sweep(q, meta)
    except QuotaExhausted as e:
        return "PAUSED", (f"the day's CourtListener allowance was already spent before the "
                          f"sweep finished, so the universe was never established. A slot "
                          f"frees in {e.seconds}s ({e.seconds / 3600:.1f} hours). Nothing was "
                          f"measured, nothing was scored and nothing was lost.")
    if CONTROL_DOC not in now_forms.get(CONTROL_FORM, set()):
        return None, "positive control absent; refusing to score anything"

    union = sorted(set().union(*now_forms.values()))
    ledger, by_sha1, failed = read_ledger(), {}, {}
    # Anything decided by an older set of rules is read again, not trusted.
    todo = [d for d in union
            if ledger.get(d, {}).get("rules_version") != triage.RULES_VERSION]
    print(f"backfill: {len(union)} documents, {len(todo)} still to read", flush=True)
    # A backfill can take longer than the quota allows in one day, and the account's daily
    # allowance is shared with whatever else ran. So it works to a wall-clock budget, writes
    # the ledger as it goes, and stops cleanly with an honest partial result rather than being
    # killed by the job timeout with everything still in memory. A partial run fails the
    # validation, which is correct: re-running resumes from the ledger.
    paused = None
    for i, doc_id in enumerate(union, 1):
        if ledger.get(doc_id, {}).get("rules_version") == triage.RULES_VERSION:
            continue
        if time.time() > DEADLINE[0]:
            print(f"  budget spent with {len([d for d in union if d not in ledger])} "
                  f"documents unread; stopping cleanly. Re-run to resume.", flush=True)
            break
        forms = [f for f in now_forms if doc_id in now_forms[f]]
        try:
            ledger[doc_id] = classify_one(doc_id, forms, meta, reg, by_sha1, today,
                                          dockets, learned)
        except QuotaExhausted as e:
            # Must be caught above the generic handler below. Recorded as a failure it would
            # be retried once per remaining document, each one raising the same thing, and the
            # run would end with a hundred identical entries and no explanation.
            paused = e.seconds
            print(f"  {i}/{len(union)} stopped at the day's quota; a slot frees in "
                  f"{e.seconds}s ({e.seconds / 3600:.1f} hours). Everything read so far is "
                  f"kept and the next run resumes from it.", flush=True)
            break
        except Exception as e:
            failed[doc_id] = f"{type(e).__name__}: {e}"
            print(f"  {i}/{len(union)} {doc_id} FAILED {failed[doc_id]}", flush=True)
            write_ledger(ledger)     # keep what has been read; a later run resumes from it
            continue
        if i % 10 == 0 or ledger[doc_id]["category"] == "unverified":
            print(f"  {i}/{len(union)} {doc_id} -> {ledger[doc_id]['category']} "
                  f"({ledger[doc_id]['rule']})", flush=True)
        if i % 10 == 0:
            write_ledger(ledger)     # nothing read should be lost to a timeout
    write_ledger(ledger)

    rows, _ = read_searches()
    cur = current_rows(rows)
    overs, decided, total = [], 0, 0
    per_form_report = {}
    for form, _ in FORMS:
        r = cur.get(form)
        if not r or int(r["new_documents"]) == 0:
            continue                       # duplicate form: its row is all zeroes by design
        counts = {c: 0 for c in CATS}
        for doc_id in now_forms[form]:
            if doc_id in ledger:
                counts[ledger[doc_id]["category"]] += 1
        total += len(now_forms[form])
        decided += sum(v for c, v in counts.items() if c != "unverified")
        per_form_report[form] = {"computed": counts,
                                 "recorded": {c: int(r[col]) for c, col in CATS.items()}}
        for c, col in CATS.items():
            if c == "unverified":
                continue
            if counts[c] > int(r[col]):
                overs.append(f"{form}/{c}: classifier {counts[c]}, hand triage {int(r[col])}")

    # A missing document is not a neutral absence. The overrun test only asks whether the
    # classifier put MORE documents in a category than the hand triage did, so every document
    # it never managed to read makes the test easier to pass. A partial ledger that reports
    # PASS is worse than an outright failure, because it turns automatic triage on.
    missing = [d for d in union
               if ledger.get(d, {}).get("rules_version") != triage.RULES_VERSION]
    passed = not overs and not missing
    summary = (f"{decided} of {total} form-hits decided by rule or verified quote; "
               + ("no category exceeded the hand triage's totals"
                  if not overs else f"{len(overs)} category overruns")
               + (f"; {len(missing)} of {len(union)} documents were never read, so the "
                  f"comparison is not valid" if missing else ""))
    if paused and missing:
        summary += (f". The run stopped because the account's daily allowance ran out, not "
                    f"because anything is wrong with it; a slot frees in {paused}s "
                    f"({paused / 3600:.1f} hours) and the next run picks up where this one "
                    f"left off")
    json.dump({"date": today, "passed": passed, "summary": summary, "overruns": overs,
               "per_form": per_form_report, "documents": len(ledger),
               "expected_documents": len(union), "complete": not missing,
               "rules_version": triage.RULES_VERSION, "paused_seconds": paused,
               "missing": missing[:50], "failures": failed},
              open(VALID, "w"), indent=1, sort_keys=True)
    if paused and missing:
        print("PAUSED: " + summary, flush=True)
        return "PAUSED", summary
    print(("PASSED: " if passed else "FAILED: ") + summary, flush=True)
    for o in overs:
        print("  overrun " + o, flush=True)
    if missing:
        print(f"  missing {len(missing)}: {missing[:10]}{' ...' if len(missing) > 10 else ''}",
              flush=True)
    return passed, summary


# ---------------------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------------------

def main(argv):
    if not TOKEN:
        sys.exit("COURTLISTENER_TOKEN is not set")
    today = datetime.date.today().isoformat()
    reg = triage.load_registry()
    dockets, learned = triage.load_dockets(), {}

    if "--backfill" in argv or "--backfill-resume" in argv:
        # The resume is scheduled daily until it finishes, because the corpus needs more
        # requests than one day's allowance reliably has left in it. Once the ledger is whole
        # the schedule keeps firing and this returns before touching the network.
        if "--backfill-resume" in argv and backfill_complete():
            print(f"backfill already complete under rules {triage.RULES_VERSION}; "
                  f"no requests made", flush=True)
            return 0
        passed, summary = backfill(today, reg, dockets, learned)
        if passed == "PAUSED":
            # Not a failure. No issue, no attention flag: the next run continues it. Reported
            # so that a pause lasting weeks is visible in the log rather than looking quiet.
            write_log(today, "BACKFILL_PAUSED", 0, [], [], [], "", "", summary)
            emit(False, f"Rule 16.1 triage backfill {today}: paused, out of quota for today")
            return 0
        if passed is None:
            write_log(today, "CONTROL_FAILED", 0, [], [], [], "", "", summary)
            emit(True, f"Rule 16.1 backfill {today}: positive control failed")
            return 1
        write_log(today, "BACKFILL", 0, [], [], [], "", "", summary)
        if not passed:
            open(ISSUE, "w").write(backfill_issue(today, summary))
        emit(not passed, f"Rule 16.1 triage backfill {today}: "
                         + ("passed" if passed else "FAILED"))
        return 0

    state = json.load(open(STATE)) if os.path.exists(STATE) else {"forms": {}, "dockets": {}}
    old_forms   = {k: set(v) for k, v in state.get("forms", {}).items()}
    old_dockets = state.get("dockets", {})

    DEADLINE[0] = time.time() + BUDGET_SECONDS
    now_forms, meta, errors, quota = {}, {}, [], None
    for form, q in FORMS:
        try:
            now_forms[form] = sweep(q, meta)
        except QuotaExhausted as e:
            quota = e.seconds
            break
        except Exception as e:
            errors.append(f"{form}: {type(e).__name__}: {e}")

    # Checked before the positive control, and this ordering is the whole point of the branch.
    # A sweep cut short by quota leaves now_forms incomplete, the control document missing, and
    # the run one line away from announcing that the search method is broken. It is not broken.
    # It never ran. Guardrail 11 answers "is the query still finding what it should", which is
    # a question about a query that was actually sent.
    if quota is not None:
        write_log(today, "QUOTA_EXHAUSTED", 0, [], [], [], "", "",
                  f"the account's daily CourtListener allowance was spent before this week's "
                  f"sweep could finish; a slot frees in {quota}s ({quota / 3600:.1f} hours). "
                  f"No measurement was recorded, the positive control was NOT evaluated, and "
                  f"the state file is left as it was. This is not a finding about the record "
                  f"or about the search. Something else drew on the same daily pool.")
        open(ISSUE, "w").write(quota_issue(today, quota))
        emit(True, f"Rule 16.1 watch {today}: out of CourtListener quota, no sweep run")
        return 1
    ok = not errors

    control_ok = CONTROL_DOC in now_forms.get(CONTROL_FORM, set())
    if ok and not control_ok:
        write_log(today, "CONTROL_FAILED", 0, [], [], [], "", "",
                  f"positive control absent: document {CONTROL_DOC} was not returned by the "
                  f"{CONTROL_FORM} form. The sweep is broken, not the record. No measurement "
                  f"recorded and the state file is left as it was.")
        open(ISSUE, "w").write(control_issue(today))
        emit(True, f"Rule 16.1 watch: positive control failed ({today})")
        return 1

    union_now = set().union(*now_forms.values()) if now_forms else set()
    union_old = set().union(*old_forms.values()) if old_forms else set()
    new  = sorted(union_now - union_old) if old_forms else []
    gone = sorted(union_old - union_now) if old_forms else []
    per_form = {f: len(now_forms.get(f, ())) for f, _ in FORMS}

    # ---- triage the new documents ----------------------------------------------------
    ledger = read_ledger()
    by_sha1 = {r["evidence"].split()[-1].strip("()"): {"document_id": r["document_id"],
                                                       "category": r["category"],
                                                       "mdl_no": r["mdl_no"]}
               for r in ledger.values() if r["rule"] == "R1"}
    triaged = {}
    for doc_id in new:
        if ledger.get(doc_id, {}).get("rules_version") == triage.RULES_VERSION:
            # Already read under the CURRENT rules in a run that was not allowed to fold it
            # into the counts. Its verdict stands; re-fetching would reach the same answer.
            triaged[doc_id] = ledger[doc_id]
            continue
        forms = [f for f in now_forms if doc_id in now_forms[f]]
        try:
            triaged[doc_id] = classify_one(doc_id, forms, meta, reg, by_sha1, today,
                                           dockets, learned)
        except Exception as e:
            errors.append(f"document {doc_id}: {type(e).__name__}: {e}")
    if triaged:
        ledger.update(triaged)
        write_ledger(ledger)

    # ---- update the search log, if the classifier has earned the right ----------------
    can, why = validated()
    log_updated, blocked = [], ""
    snapshots = {p: open(p, newline="").read() for p in (SEARCHES, "index.html")}
    if triaged and ok and not gone:
        if can:
            log_updated = update_searches(now_forms, old_forms, triaged, today)
        else:
            blocked = why
    elif triaged and gone:
        blocked = ("documents disappeared from the sweep this week, so no count was changed. "
                   "A shrinking corpus is not a triage problem.")

    # ---- dockets with no qualifying order --------------------------------------------
    docket_moves = []
    for mdl, did in NO_ORDER_YET.items():
        try:
            n, d = latest_entry(did)
        except Exception as e:
            errors.append(f"docket {mdl}: {type(e).__name__}: {e}")
            continue
        prior = old_dockets.get(mdl)
        was = prior.get("entry_number", 0) if isinstance(prior, dict) else 0
        state.setdefault("dockets", {})[mdl] = {"docket_id": did, "entry_number": n,
                                                "date_filed": d}
        if was and n > was:
            docket_moves.append(f"MDL {mdl}: docket entries {was} -> {n} (latest {d})")

    val_ok,   val_msg   = gate(["python3", "validate_treatment.py"])
    build_ok, build_msg = gate(["python3", "build.py"] + ([] if log_updated else ["--check"]))
    if log_updated and not (val_ok and build_ok):
        # Restored from bytes read before the update, not with `git checkout`. A revert that
        # depends on the working tree being a clean git checkout is a revert that quietly does
        # nothing when it is not, and the run would then commit a change a gate had rejected.
        for path, before in snapshots.items():
            open(path, "w", newline="").write(before)
        log_updated, blocked = [], (f"a gate failed after the update, so the change was "
                                    f"rolled back: {build_msg or val_msg}")

    undecided = [d for d, r in triaged.items() if r["category"] == "unverified"]
    orders    = [d for d, r in triaged.items()
                 if r["category"] == "post_effective_mdl" and _looks_like_order(meta.get(d, {}))]
    attention = bool(undecided or orders or docket_moves or errors or gone or blocked) \
        or not val_ok or not build_ok
    status = ("ERRORS" if errors else
              "NEW_DOCUMENTS" if new or docket_moves else
              "GATE_FAILED" if not (val_ok and build_ok) else
              "NO_CHANGE")

    note = "; ".join(filter(None, [
        "" if val_ok else f"validate_treatment FAILED: {val_msg}",
        "" if build_ok else f"build FAILED: {build_msg}",
        f"triaged {len(triaged)} new: " + _tally(triaged) if triaged else "",
        f"search log updated for {', '.join(log_updated)}" if log_updated else "",
        (f"search log NOT updated ({len(triaged)} document(s) held pending and still counted "
         f"as new next week): {blocked}") if blocked else "",
        "; ".join(docket_moves), "; ".join(errors),
        "baseline established, no prior state to diff against" if not old_forms else "",
    ])) or "no new documents in any naming form; both gates passed"

    write_log(today, status, len(union_now), new, gone,
              [f"{f}={per_form[f]}" for f, _ in FORMS],
              "PASS" if val_ok else "FAIL", "PASS" if build_ok else "FAIL", note)

    # A document is written into the state file only once it has been ACCOUNTED FOR, meaning
    # its category is reflected in the search log. A document that was seen and triaged but
    # could not be folded in, because the classifier is not yet validated or because the
    # corpus shrank, stays out of the state and therefore reads as new again next week. The
    # state file records what has been counted, not what has been looked at. Without this a
    # document seen during a blocked week would be silently skipped forever, and the next row
    # written would carry a `hits` total its own category columns could not sum to.
    unaccounted = set() if log_updated else set(triaged)
    if ok:
        state["forms"] = {f: sorted(set(ids) - unaccounted) for f, ids in now_forms.items()}
    state["pending"] = sorted(unaccounted)
    state["generated"] = today
    state["control"] = {"document": CONTROL_DOC, "form": CONTROL_FORM, "passed": control_ok}
    json.dump(state, open(STATE, "w"), indent=1, sort_keys=True)

    print(f"{status}: union {len(union_now)}, new {len(new)}, dropped {len(gone)}")
    if attention:
        open(ISSUE, "w").write(issue_body(today, status, new, gone, per_form, docket_moves,
                                          val_ok, val_msg, build_ok, build_msg, errors,
                                          meta, triaged, log_updated, blocked, orders))
    emit(attention, f"Rule 16.1 watch {today}: {status.lower().replace('_', ' ')}")
    return 0


def _tally(triaged):
    c = {}
    for r in triaged.values():
        c[r["category"]] = c.get(r["category"], 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(c.items()))


def _looks_like_order(m):
    blob = ((m.get("short_description") or "") + " " + (m.get("description") or "")).upper()
    return "ORDER" in blob


def update_searches(now_forms, old_forms, triaged, today):
    """Add each new document to its forms' counts. Supersede, never edit.

    Counts are carried forward and added to, not recomputed: the existing CURRENT rows hold a
    triage that a person did by reading, and there is no per-document record of it to rebuild
    from. So the new row is the old row plus this week's documents, and the provenance column
    says which of the two produced it.
    """
    rows, hdr = read_searches()
    if "triage_source" not in hdr:
        hdr = hdr[:hdr.index("status")] + ["triage_source"] + hdr[hdr.index("status"):]
        for r in rows:
            r.setdefault("triage_source", "HUMAN")
    cur, changed, new_rows = current_rows(rows), [], []
    for form, _ in FORMS:
        r = cur.get(form)
        if not r:
            continue
        added = [d for d in triaged if d in now_forms[form] and d not in old_forms.get(form, ())]
        if not added:
            continue
        dup = int(r["new_documents"]) == 0 and int(r["hits"]) > 0
        row = dict(r)
        row["run_date"] = today
        row["hits"] = len(now_forms[form])
        row["status"] = "CURRENT"
        row["triage_source"] = "HUMAN" if dup else (
            "MIXED" if r.get("triage_source", "HUMAN") == "HUMAN" else "MACHINE")
        if dup:
            # A duplicate form carries its true hits and zeroes everywhere else, or the union
            # arithmetic double counts. build.py enforces this; do not "fix" it here.
            row["new_documents"] = 0
            for col in CATS.values():
                row[col] = 0
            row["notes"] = (f"Automated run {today}. Still returns exactly the same documents "
                            f"as the abbrev form. Recorded so no future run wastes a call.")
        else:
            fresh = [d for d in added if _is_fresh(d, form, now_forms)]
            row["new_documents"] = int(r["new_documents"]) + len(fresh)
            for c, col in CATS.items():
                row[col] = int(r[col]) + sum(1 for d in added if triaged[d]["category"] == c)
            row["hits_no_text_layer"] = int(r["hits_no_text_layer"]) + sum(
                1 for d in added if triaged[d]["no_text_layer"] == "YES")
            row["notes"] = (
                f"Automated run {today}, machine triage. {len(added)} document(s) added to the "
                f"superseded run of {r['run_date']}: "
                + "; ".join(f"{d} -> {triaged[d]['category']} ({triaged[d]['method']} "
                            f"{triaged[d]['rule']})" for d in added)
                + f". Per-document evidence in {LEDGER}. Prior counts carried forward unchanged.")
        new_rows.append(row)
        r["status"] = "SUPERSEDED"
        r["notes"] = f"Superseded by the automated run of {today}. " + r["notes"]
        changed.append(form)

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=hdr)
    w.writeheader()
    for r in rows + new_rows:
        w.writerow({c: r.get(c, "") for c in hdr})
    open(SEARCHES, "w", newline="").write(buf.getvalue())
    return changed


def _is_fresh(doc_id, form, now_forms):
    """A document counts as new for the first form in sweep order that returned it."""
    for f, _ in FORMS:
        if doc_id in now_forms.get(f, ()):
            return f == form
    return False


def gate(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    tail = (p.stdout + p.stderr).strip().splitlines()
    return p.returncode == 0, (tail[-1] if tail else "")


# ---------------------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------------------

def clip(s, n):
    s = " ".join((s or "").split())
    return s[:n] + ("…" if len(s) > n else "")


def quota_issue(today, seconds):
    return (
        f"# The weekly sweep did not run on {today}\n\n"
        f"CourtListener refused the request with `Rate limit exceeded: 125/day`. A slot frees "
        f"in {seconds} seconds ({seconds / 3600:.1f} hours).\n\n"
        f"**Nothing here is a finding about the data or about the search.** No measurement was "
        f"recorded, the Guardrail 11 positive control was not evaluated, and the state file is "
        f"unchanged, so next week's diff still compares against the last sweep that actually "
        f"happened.\n\n"
        f"The 125 a day belongs to the account, not to this job. Every other thing that talks "
        f"to CourtListener under the same token draws on the same pool, and it refills one slot "
        f"at a time over a rolling 24 hours rather than resetting at midnight. So the question "
        f"worth asking is what else spent it: an interactive session, a backfill resume that "
        f"was expected to skip Monday, or a second workflow.\n\n"
        f"No action is needed for the record itself. Re-run this workflow by hand once the "
        f"window has cleared if you want the week measured rather than skipped.\n")


def control_issue(today):
    return (f"# Positive control failed on {today}\n\n"
            f"The {CONTROL_FORM} form did not return RECAP document {CONTROL_DOC}, Pretrial "
            f"Order No. 28 in MDL 3108.\n\nUnder Guardrail 11 this means the search method "
            f"stopped working, not that the corpus changed. Nothing was written to the state "
            f"file or the search log, so the next run compares against the same baseline as "
            f"this one.\n\nCheck whether the query still parses, whether "
            f"`entry_date_filed_after` is still an accepted parameter, and whether the "
            f"document is still in RECAP.\n")


def backfill_issue(today, summary):
    v = json.load(open(VALID))
    b = [f"# Triage backfill failed on {today}\n", summary + "\n",
         "**Automatic triage stays off** until this passes.\n"]
    if v.get("missing"):
        b.append(f"## {len(v['missing'])} of {v.get('expected_documents')} documents were "
                 f"never read\n")
        b.append("The comparison is not valid until every document has been classified. The "
                 "overrun test only asks whether the classifier put MORE documents in a "
                 "category than the hand triage did, so an unread document makes it easier to "
                 "pass. A run that stops early must fail, not report a smaller success.\n")
        for d, why in list(v.get("failures", {}).items())[:20]:
            b.append(f"- {d}: {why}")
        b.append("\nThe ledger keeps what was read, so re-running the backfill resumes rather "
                 "than starting over.\n")
    if v.get("overruns"):
        b.append("## Overruns\n")
        b.append("The classifier put more documents in a category than the hand triage's own "
                 "total for that category, so at least one of those calls is wrong.\n")
        b += [f"- {o}" for o in v.get("overruns", [])]
    b.append("\n## Per form\n\n| form | category | classifier | hand triage |\n|---|---|--:|--:|")
    for form, d in v.get("per_form", {}).items():
        for c in d["computed"]:
            if d["computed"][c] or d["recorded"][c]:
                b.append(f"| {form} | {c} | {d['computed'][c]} | {d['recorded'][c]} |")
    b.append(f"\nPer-document reasoning is in `{LEDGER}`: every row carries the rule that fired "
             f"and the string it fired on, so a wrong call can be traced to the rule that made "
             f"it rather than argued about in the abstract.\n")
    return "\n".join(b)


def issue_body(today, status, new, gone, per_form, docket_moves, val_ok, val_msg,
               build_ok, build_msg, errors, meta, triaged, log_updated, blocked, orders):
    b = [f"# Rule 16.1 watch, {today}\n", f"Status: **{status}**\n"]
    if log_updated:
        b.append(f"`rule-16-1-searches.csv` was updated automatically for: "
                 f"{', '.join(log_updated)}. Those rows carry `triage_source` other than "
                 f"HUMAN and cite the ledger. Prior counts were carried forward, not "
                 f"recomputed.\n")
        b.append("**Two published findings quantify over the whole corpus and cannot be "
                 "rechecked by counting.** Finding 3a says that across all returned documents "
                 "exactly one names the Rule two different ways, and the local-rule collision "
                 "finding rests on which districts generate 16.1 references. `build.py` "
                 "verifies the numbers in those sentences and cannot verify the word "
                 "\"exactly.\" Read the new documents against both before treating this week "
                 "as settled.\n")
    if blocked:
        b.append(f"**The search log was not changed.** {blocked}\n")
    if triaged:
        b.append("## Triage of the new documents\n")
        b.append("| document | category | how | rule | no text layer |\n|---|---|---|---|---|")
        for d, r in triaged.items():
            b.append(f"| [{d}](https://www.courtlistener.com{meta.get(d, {}).get('absolute_url', '')}) "
                     f"| {r['category']} | {r['method']} | {r['rule']} | {r['no_text_layer'] or ''} |")
        b.append("")
        undecided = {d: r for d, r in triaged.items() if r["category"] == "unverified"}
        if undecided:
            b.append(f"### {len(undecided)} document(s) nothing could decide\n")
            b.append("These are counted `hits_unverified`, which is a real category that sums "
                     "into the arithmetic, so no figure on the page is wrong while they sit "
                     "there. They are the only part of this week that needs a person.\n")
            for d, r in undecided.items():
                m = meta.get(d, {})
                b.append(f"**{d}** — {r['escalate']}")
                b.append(f"- {m.get('entry_date_filed', '?')} · docket {m.get('docket_id', '?')} "
                         f"· entry {m.get('document_number', '?')} · text available: "
                         f"{m.get('is_available', '?')}")
                b.append(f"- clerk's entry: {clip(m.get('description'), 500) or '(none)'}")
                b.append(f"- matching text: {clip(m.get('snippet'), 700) or '(none)'}\n")
    if orders:
        b.append("## Possibly a new order to code\n")
        for d in orders:
            m = meta.get(d, {})
            b.append(f"- [{d}](https://www.courtlistener.com{m.get('absolute_url', '')}) "
                     f"in MDL {triaged[d]['mdl_no'] or '?'}: {clip(m.get('description'), 300)}")
        b.append("\nTriage put these in a post-effective MDL and the clerk's entry calls them "
                 "orders. **Nothing was coded.** Coding is done against codebook v1.1 using "
                 "`maintenance/chatgpt-standing-prompt.md` and merged by hand.\n")
    if gone:
        b.append(f"## {len(gone)} document(s) the sweep no longer returns\n")
        b.append("A drop is not normally possible in a growing corpus. Check for a sealed or "
                 "stricken filing, or a change in how the index tokenises the query. No count "
                 "was changed this week because of it.\n")
        b += [f"- RECAP {i}" for i in gone] + [""]
    if docket_moves:
        b.append("## Movement on a docket with no qualifying order\n")
        b += [f"- {m}" for m in docket_moves]
        b.append("\nMDL 3176 is the dataset's only true negative. The naming sweep cannot see an "
                 "order that does not name the Rule, so this docket is watched directly. New "
                 "entries do not mean a qualifying order was entered; read them.\n")
    if not val_ok:
        b.append(f"## validate_treatment.py failed\n\n```\n{val_msg}\n```\n")
    if not build_ok:
        b.append(f"## build.py failed\n\n```\n{build_msg}\n```\n")
    if errors:
        b.append("## Request errors\n")
        b += [f"- {e}" for e in errors]
        b.append("\nA form that errored is recorded as an error, never as a form with no hits. "
                 "The state file keeps its previous ID set for that form.\n")
    b.append(f"\n---\nPer-form hits: {', '.join(f'{k}={v}' for k, v in per_form.items())}. "
             f"History in `{LOG}`, per-document triage in `{LEDGER}`.")
    return "\n".join(b)


def write_log(today, status, union, new, gone, per_form, val, build, note):
    hdr = ["run_date", "status", "union_hits", "per_form", "new_document_ids",
           "dropped_document_ids", "validate", "build_check", "note"]
    exists = os.path.exists(LOG)
    with open(LOG, "a", newline="") as fh:
        w = csv.writer(fh)
        if not exists:
            w.writerow(hdr)
        w.writerow([today, status, union, " ".join(per_form), " ".join(map(str, new)),
                    " ".join(map(str, gone)), val, build, note])


def emit(attention, title):
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"attention={'true' if attention else 'false'}\n")
            fh.write(f"title={title}\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
