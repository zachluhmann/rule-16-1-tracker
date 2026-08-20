#!/usr/bin/env python3
"""Offline tests for triage.py and watch.py. No network, no token, no GitHub.

Part 1 scores the rule tier against documents whose correct category is already recorded in
this repository, using text taken from the documents themselves. Part 2 runs the whole watch
against a stubbed API across six scenarios.

The property that matters more than any single assertion: the watch must not change a
published count unless it has been validated, and must never touch the coding files at all.
"""
import hashlib, io, json, os, re, shutil, subprocess, sys, urllib.parse, urllib.request

REPO = os.path.dirname(os.path.abspath(__file__))
TMP  = "/tmp/watch-test"
sys.path.insert(0, REPO)
import triage

# ---------------------------------------------------------------------------------------
# Part 1. The rule tier, against real documents.
#
# Each fixture's text is the part of the real filing that a reader would decide on: the ECF
# header stamp, the caption block, and the sentence naming the Rule. The expected category is
# the one recorded in rule-16-1-searches.csv or party-invocations.csv for that document.
# ---------------------------------------------------------------------------------------

FIXTURES = [
    dict(id=464150837, expect="post_effective_mdl", why="MDL 3170 report; also names MDL 3164 in passing",
         is_available=True, sha1="74b65a20a424def52a8f81a3972284ef08d7da2d", description="",
         plain_text="""     Case: 1:25-cv-10320 Document #: 33 Filed: 01/05/26 Page 1 of 13 PageID #:1247
IN THE UNITED STATES DISTRICT COURT FOR THE NORTHERN DISTRICT OF ILLINOIS
IN RE: TRANS UNION, LLC, CUSTOMER  )  Case No. 25 CV 10320
DATA SECURITY BREACH LITIGATION    )  MDL No. 3170
                                   )  Judge Robert W. Gettleman
                          FED. R. CIV. P. 16.1 REPORT
The Snelgrove Plaintiffs submit the following Report pursuant to Fed. R. Civ. P. 16.1 and the
Court's Case Management Order #2. CVN filed the first action and filed briefs in MDL 3164 as
well as MDL 3170, taking positions that the JPML ultimately adopted."""),

    dict(id=480741139, expect="noise", why="motion to compel; names Rule 16 but never 16.1",
         is_available=True, sha1="02fa9f00ac6865e8e1d464825cb4a27a00704251",
         description="Motion to Compel",
         plain_text="""Case 4:24-cv-01022-SDJ  Document 259 Filed 05/28/26  Page 1 of 12 PageID #: 4044
UNITED STATES DISTRICT COURT FOR THE EASTERN DISTRICT OF TEXAS
AMIDE BEVERAGE COMPANY, LLC v. AMAZON.COM, INC. C.A. No. 4:24-cv-1022-SDJ
PLAINTIFF'S MOTION TO COMPEL RULE 30(b)(6) DEPOSITIONS
F.R.C.P. 26 .... 4, 5
F.R.C.P. 16 .... 1, 2, 3, 5
The OGP provides: "Absent agreement of the parties, depositions of witnesses shall not be
taken until after the Initial Rule 16 management conference." """),

    dict(id=472850310, expect="pre_effective_mdl", why="MDL 3108, centralized June 2024; the Guardrail 11 control",
         is_available=True, sha1="aaaa000000000000000000000000000000000001",
         description="MDL Pretrial Order",
         plain_text="""     CASE 0:24-md-03108-DWF-DJF  Doc. 540  Filed 03/19/26  Page 1 of 1
UNITED STATES DISTRICT COURT DISTRICT OF MINNESOTA
In re: CHANGE HEALTHCARE, INC.  MDL No. 24-3108 (DWF/DJF)
CUSTOMER DATA SECURITY BREACH LITIGATION      PRETRIAL ORDER NO. 28
Pursuant to the Court's Pretrial Order No. 2 and consistent with Federal Rule of Civil
Procedure 16.1 aimed at providing case-management guidance in MDLs, the Court directs the
parties to place the following items on the agenda."""),

    dict(id=466008549, expect="noise", why="pro se opposition about the SOUTHERN DISTRICT OF FLORIDA's own local rule 16.1",
         is_available=True, sha1="aaaa000000000000000000000000000000000002", description="",
         plain_text="""Case 0:25-cv-62222-XXXX Document 41 Entered on FLSD Docket 03/02/26
OPPOSITION TO DEFENDANTS DTCC AND FINRA'S MOTION TO STAY THE REQUIREMENTS OF LOCAL RULE 16.1
Plaintiff opposes the motion to stay the requirements of Local Rule 16.1. Local Rule 16.1(b)
requires a scheduling conference. Nothing in Local Rule 16.1 permits the relief sought."""),

    dict(id=479971934, expect="non_mdl", why="ordinary 2021 civil case in D.N.D. citing the federal rule",
         is_available=True, sha1="aaaa000000000000000000000000000000000003",
         description="Motion for Scheduling Conference",
         plain_text="""Case 1:21-cv-00090-DMT-CRH  Document 214  Filed 06/02/26  Page 1 of 9
UNITED STATES DISTRICT COURT FOR THE DISTRICT OF NORTH DAKOTA
Tesoro High Plains Pipeline Company, LLC v. United States of America
Plaintiff respectfully requests a conference under Fed. R. Civ. P. 16.1(a) to address the
schedule for the remaining claims."""),

    dict(id=999000001, expect="unverified", why="names an MDL the registry has never heard of",
         is_available=True, sha1="aaaa000000000000000000000000000000000004", description="",
         plain_text="""Case 2:26-md-03199-ABC  Document 12  Filed 07/01/26  Page 1 of 4
IN RE: SOMETHING NOT IN THE TRACKER, MDL No. 3199
Pursuant to Federal Rule of Civil Procedure 16.1, the parties shall confer."""),

    dict(id=999000002, expect="unverified", why="no text layer; the clerk's entry names the rule and nothing else",
         is_available=False, sha1="aaaa000000000000000000000000000000000005",
         description="STATUS Report F.R.C.P. 16.1 by Daniel Snelgrove", plain_text=""),

    dict(id=999000003, expect="noise", why="the index returned it for Rule 16; no 16.1 anywhere",
         is_available=True, sha1="aaaa000000000000000000000000000000000006",
         description="Order on Rule 16 conference",
         plain_text="Case 3:25-cv-00111 ORDER setting a Rule 16 scheduling conference."),

    dict(id=999000004, expect="unverified", why="names 16.1 with no federal form and no local marker",
         is_available=True, sha1="aaaa000000000000000000000000000000000007", description="",
         plain_text="""Case 1:26-cv-04444  Document 7
The parties shall comply with Rule 16.1 in all respects and file the required report."""),
]


def part1():
    print("Part 1: the rule tier against documents whose category this repo already records\n")
    reg = triage.load_registry(os.path.join(REPO, "rule-16-1-tracker.csv"),
                               os.path.join(REPO, "maintenance/pre-effective-mdls.csv"))
    print(f"  registry: {len(reg)} MDLs "
          f"({sum(1 for v in reg.values() if v['side'] == 'pre_effective_mdl')} pre-effective)\n")
    ok, by_sha1 = [], {}
    for f in FIXTURES:
        v = triage.classify(f, reg, by_sha1)
        good = v["category"] == f["expect"]
        ok.append(good)
        print(f"  {'PASS' if good else 'FAIL'}  {f['id']}  {v['category']:<19} "
              f"{v['rule']:<3} {f['why']}")
        if not good:
            print(f"        expected {f['expect']}; evidence: {v['evidence'][:140]}")
        if v["category"] != "unverified" and f.get("sha1"):
            by_sha1[f["sha1"]] = {"document_id": f["id"], "category": v["category"],
                                  "mdl_no": v.get("mdl_no", "")}

    # R1: the same filing on a second docket, which is the case the human first got wrong.
    twin = dict(id=464112237, is_available=True, description="",
                sha1="aaaa000000000000000000000000000000000001",
                plain_text="Case 3:23-cv-06708-CRB Document 88 Trial brief. Federal Rule of "
                           "Civil Procedure 16.1 is discussed at page 4.")
    v = triage.classify(twin, reg, by_sha1)
    good = v["category"] == "pre_effective_mdl" and v["rule"] == "R1"
    print(f"\n  {'PASS' if good else 'FAIL'}  464112237 inherits pre_effective_mdl from its "
          f"sha1 twin instead of reading as an unrelated civil case (got {v['category']}/{v['rule']})")
    ok.append(good)

    # R5a: the docket the document sits on, which the search result gives free. These three
    # captions are exactly what defeated the text scan in the first live backfill.
    print()
    dockets, learned = triage.load_dockets(os.path.join(REPO, "rule-16-1-tracker.csv")), {}
    for name, expect, d in [
        ("MDL 3170 report, caption reads 'Case No. 25 CV 10320'", "post_effective_mdl",
         dict(id=1, docket_id=71221176, is_available=True, description="",
              plain_text="Case No. 25 CV 10320\nFED. R. CIV. P. 16.1 REPORT filed pursuant "
                         "to Fed. R. Civ. P. 16.1.")),
        ("MDL 3162, a MISCELLANEOUS docket no civil pattern can match", "post_effective_mdl",
         dict(id=2, docket_id=72028506, is_available=True, description="",
              plain_text="CLASS ACTION SETTLEMENT ADMINISTRATION LITIGATION 1:25-mc-00179 "
                         "INITIAL PROCEDURE ORDER under Federal Rule of Civil Procedure 16.1.")),
        ("no text layer at all, located by its docket", "post_effective_mdl",
         dict(id=3, docket_id=73170267, is_available=False, plain_text="",
              description="ORDER under Fed. R. Civ. P. 16.1")),
        ("a local-rule brief ON an MDL docket stays noise", "noise",
         dict(id=4, docket_id=71221176, is_available=True, description="",
              plain_text="OPPOSITION TO THE REQUIREMENTS OF LOCAL RULE 16.1. Local Rule "
                         "16.1(b) requires a scheduling conference.")),
        ("Rule 16 noise ON an MDL docket stays noise", "noise",
         dict(id=5, docket_id=72030009, is_available=True,
              description="Order on Rule 16 conference",
              plain_text="ORDER setting a Rule 16 scheduling conference under Rule 26(f).")),
        ("an ordinary case NOT on an MDL docket is unaffected", "non_mdl",
         dict(id=6, docket_id=99999999, is_available=True, description="",
              plain_text="Case 1:21-cv-00090-DMT-CRH conference under Fed. R. Civ. P. 16.1(a).")),
    ]:
        v = triage.classify(d, reg, {}, dockets, learned)
        g = v["category"] == expect
        ok.append(g)
        print(f"  {'PASS' if g else 'FAIL'}  R5a  {name} -> {v['category']} ({v['rule']})")

    a = triage.classify(dict(id=7, docket_id=555001, is_available=True, description="",
                             plain_text="Case 3:26-cv-00157-jdp IN RE: SHELL EGGS 26-md-3175-jdp "
                                        "under Federal Rule of Civil Procedure 16.1"),
                        reg, {}, dockets, learned)
    b = triage.classify(dict(id=8, docket_id=555001, is_available=True, description="",
                             plain_text="Case 3:26-cv-00157-jdp a later filing citing Fed. R. "
                                        "Civ. P. 16.1 with no MDL number in it at all"),
                        reg, {}, dockets, learned)
    g = a["category"] == "post_effective_mdl" and b["rule"] == "R5a"
    ok.append(g)
    print(f"  {'PASS' if g else 'FAIL'}  R5a  a member docket learned from one document is "
          f"inherited by the next ({a['rule']} then {b['rule']})")

    # classify_from_search decides only the conjunction of two positive facts. Everything
    # else must return None and get fetched. The danger of a cost optimisation is that it
    # starts deciding things it cannot see, so the negatives matter more than the positives.
    print()
    S = triage.classify_from_search
    for name, hit, want in [
        ("names the Rule, on a known MDL docket -> decided",
         dict(docket_id=71221176, is_available=True, description="ORDER under Fed. R. Civ. P. 16.1",
              snippet="pursuant to Fed. R. Civ. P. 16.1 the parties shall confer"), "decide"),
        ("names the Rule, docket NOT known -> fetch",
         dict(docket_id=99999999, is_available=True, description="",
              snippet="pursuant to Fed. R. Civ. P. 16.1"), None),
        ("known MDL docket but no naming form in the snippet -> fetch",
         dict(docket_id=71221176, is_available=True, description="Order on Rule 16 conference",
              snippet="ORDER setting a Rule 16 scheduling conference"), None),
        ("a local-rule marker present -> fetch, never decided here",
         dict(docket_id=71221176, is_available=True, description="",
              snippet="motion to stay the requirements of Local Rule 16.1 and Fed. R. Civ. P. 16.1"),
         None),
        ("empty search result -> fetch",
         dict(docket_id=71221176, is_available=False, description="", snippet=""), None),
    ]:
        got = S(hit, reg, dockets, {})
        g = (got is None) if want is None else (got is not None and got["rule"] == "S1")
        ok.append(g)
        print(f"  {'PASS' if g else 'FAIL'}  S1   {name}")

    # No key set, so the model tier must decline rather than invent an answer.
    for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        os.environ.pop(k, None)
    none = triage.ask_model(FIXTURES[-1], reg) is None
    print(f"  {'PASS' if none else 'FAIL'}  the model tier is skipped when no API key is set")
    ok.append(none)

    print(f"\n  {sum(ok)}/{len(ok)} passed\n")
    return all(ok)


# ---------------------------------------------------------------------------------------
# Part 2. The watch, against a stubbed API.
# ---------------------------------------------------------------------------------------

BASE = {
    '"Fed. R. Civ. P. 16.1"':                              list(range(1000, 1041)),
    '"Federal Rule of Civil Procedure 16.1"':              [472850310] + list(range(2000, 2034)),
    '"FRCP 16.1"':                                         list(range(3000, 3006)),
    '"F.R.C.P. 16.1"':                                     list(range(4000, 4008)),
    '"Rule 16.1 Report"':                                  list(range(5000, 5013)),
    '"Fed.R.Civ.P. 16.1"':                                 list(range(1000, 1041)),
    '"Rule 16.1 of the Federal Rules of Civil Procedure"':  [],
}
NEW_DOC, NEW_DOC2, UNDECIDABLE = 999123456, 999123457, 999888777
ST = {"data": None, "entry": 40, "calls": 0, "doc_text": None}

# The stub's corpus is built to reproduce the hand triage recorded in the CURRENT rows of
# rule-16-1-searches.csv, document for document. A stub that returned one kind of document
# would make the backfill's overrun check pass or fail for reasons that have nothing to do
# with the classifier, and the point of that check is to be sensitive.
TEXTS = {
    "post": "Case: 1:25-cv-10320 Document #: 33\nIN RE: TRANS UNION, LLC  MDL No. 3170\n"
            "Pursuant to Fed. R. Civ. P. 16.1, the parties shall confer and file a report.",
    "pre":  "CASE 0:24-md-03108-DWF-DJF  Doc. 540\nIn re: CHANGE HEALTHCARE  MDL No. 24-3108\n"
            "consistent with Federal Rule of Civil Procedure 16.1 the Court directs the parties.",
    "non":  "Case 1:21-cv-00090-DMT-CRH  Document 214\nUNITED STATES DISTRICT COURT\n"
            "Plaintiff requests a conference under Fed. R. Civ. P. 16.1 to address the schedule.",
    "noise": "Case 3:25-cv-00111  ORDER setting a Rule 16 scheduling conference under Rule 26(f).",
    "undec": "Case 5:26-cv-09999  The parties shall comply with Rule 16.1 in all respects.",
}
# The clerk's entry varies with the document, because it is searched alongside the document
# text and a stub that gave every hit the same entry would leak the Rule's name into documents
# that do not contain it. That is not a hypothetical: the first version of this stub did
# exactly that and turned twenty-five Rule 16 noise hits into ordinary civil cases.
# The docket each kind of document sits on. Added when the classifier learned to read
# docket ids: the stub previously put every document on MDL 3170's master docket, which made
# the new rule classify the entire corpus as post-effective and blew up the distribution. A
# fixture that is uniform where the real corpus is not will always flatter or wreck a rule
# that reads the field being faked.
DOCKET = {
    "post":  71221176,   # MDL 3170 master, in the tracker
    "pre":   90000001,   # MDL 3108's docket, deliberately NOT in the tracker: must fall
                         # through to the text scan and resolve as pre-effective there
    "non":   90000002,   # an ordinary civil case
    "noise": 90000003,
    "undec": 90000004,
}
DESCS = {
    "post":  "ORDER RE: INITIAL CASE MANAGEMENT CONFERENCE under Federal Rule of Civil Procedure 16.1.",
    "pre":   "MDL Pretrial Order",
    "non":   "Motion for Scheduling Conference",
    "noise": "Order on Rule 16 conference",
    "undec": "",
}
# form: [(id range, kind, count), ...] chosen so each form's totals equal its CURRENT row.
PLAN = ([("post", range(1000, 1007)), ("pre", range(1007, 1009)),
         ("non", range(1009, 1016)), ("noise", range(1016, 1041))]          # abbrev 7/2/7/25
      + [("pre", [472850310]), ("post", range(2000, 2031)),
         ("pre", range(2031, 2033)), ("noise", range(2033, 2034))]          # spelled_out 31/3/0/1
      + [("post", range(3000, 3003)), ("non", range(3003, 3006))]           # frcp_acronym 3/0/3/0
      + [("post", range(4000, 4001)), ("non", range(4001, 4007)),
         ("noise", range(4007, 4008))]                                      # frcp_periods 1/0/6/1
      + [("post", range(5000, 5012)), ("noise", range(5012, 5013))]         # report_phrase 12/0/0/1
      + [("post", [NEW_DOC, NEW_DOC2]), ("undec", [UNDECIDABLE])])
KIND = {i: kind for kind, ids in PLAN for i in ids}


class Resp(io.BytesIO):
    def __enter__(self):  return self
    def __exit__(self, *a): return False


def fake_urlopen(req, timeout=None):
    ST["calls"] += 1
    url = req.full_url if hasattr(req, "full_url") else req
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    if "docket-entries" in url:
        body = {"results": [{"entry_number": ST["entry"], "date_filed": "2026-08-10"}]}
    elif "recap-documents" in url:
        doc_id = int(re.search(r"recap-documents/(\d+)/", url).group(1))
        body = {"id": doc_id, "sha1": hashlib.sha1(str(doc_id).encode()).hexdigest(),
                "is_available": True, "page_count": 2,
                "plain_text": TEXTS[KIND.get(doc_id, "post")]}
    else:
        body = {"results": [{
            "id": i, "document_number": 6, "page_count": 2,
            "is_available": True, "entry_date_filed": "2026-08-11",
            "docket_id": DOCKET[KIND.get(i, "post")],
            "absolute_url": "/docket/71221176/33/in-re-trans-union/",
            "short_description": "Order AND ~Util - Set/Reset Deadlines",
            "description": DESCS[KIND.get(i, "post")],
            "snippet": TEXTS[KIND.get(i, "post")][:200],
        } for i in ST["data"][qs["q"][0]]], "next": None}
    return Resp(json.dumps(body).encode())


def run(label, data, entry, expect_status, expect_rc=0, argv=(), doc_text=None):
    ST.update(data=data, entry=entry, calls=0, doc_text=doc_text)
    os.chdir(TMP)
    sys.modules.pop("watch", None)
    sys.modules.pop("triage", None)
    sys.path.insert(0, TMP)
    import watch
    watch.THROTTLE = 0.0
    rc = watch.main(list(argv))
    row = list(open("maintenance/watch-log.csv"))[-1]
    got = row.split(",")[1]
    ok = (got == expect_status and rc == expect_rc)
    print(f"  {'PASS' if ok else 'FAIL'}  {label}: status={got} rc={rc} ({ST['calls']} requests)")
    if not ok:
        print(f"        expected status={expect_status} rc={expect_rc}\n        {row.strip()[:400]}")
    return ok, row


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def part2():
    print("Part 2: the watch against a stubbed API\n")
    shutil.rmtree(TMP, ignore_errors=True)
    shutil.copytree(REPO, TMP, ignore=shutil.ignore_patterns("__pycache__", ".git"))
    for p in ("maintenance/watch-log.csv", "maintenance/watch-state.json",
              "maintenance/triage-ledger.csv", "maintenance/triage-validation.json"):
        f = os.path.join(TMP, p)
        if os.path.exists(f):
            os.remove(f)
    os.environ["COURTLISTENER_TOKEN"] = "test"
    os.environ.pop("GITHUB_OUTPUT", None)
    urllib.request.urlopen = fake_urlopen

    searches_before = sha(os.path.join(TMP, "rule-16-1-searches.csv"))
    r = []

    print("scenario 1: first run, no prior state")
    r.append(run("baseline", BASE, 40, "NO_CHANGE")[0])

    print("scenario 2: a new document arrives, but the classifier has never been validated")
    grown = dict(BASE)
    grown['"Federal Rule of Civil Procedure 16.1"'] = \
        BASE['"Federal Rule of Civil Procedure 16.1"'] + [NEW_DOC]
    ok, row = run("new document, unvalidated", grown, 41, "NEW_DOCUMENTS")
    r.append(ok)
    held = sha(os.path.join(TMP, "rule-16-1-searches.csv")) == searches_before
    print(f"  {'PASS' if held else 'FAIL'}  the search log was NOT touched, because the "
          f"classifier has not been scored yet")
    r.append(held)
    r.append("never been scored" in row or "never been scored" in
             open(os.path.join(TMP, "maintenance/.watch-issue.md")).read())
    print(f"  {'PASS' if r[-1] else 'FAIL'}  the log row says why it refused")
    ledgered = os.path.exists(os.path.join(TMP, "maintenance/triage-ledger.csv")) and \
        str(NEW_DOC) in open(os.path.join(TMP, "maintenance/triage-ledger.csv")).read()
    print(f"  {'PASS' if ledgered else 'FAIL'}  it still triaged the document and recorded "
          f"the reasoning in the ledger")
    r.append(ledgered)

    print("\nscenario 3: the backfill, scoring the classifier against the hand triage")
    os.remove(os.path.join(TMP, "maintenance/triage-ledger.csv"))
    ok, _ = run("backfill", BASE, 41, "BACKFILL", argv=["--backfill"])
    r.append(ok)
    v = json.load(open(os.path.join(TMP, "maintenance/triage-validation.json")))
    print(f"        {v['summary']}")
    print(f"  {'PASS' if v['passed'] else 'FAIL'}  no category exceeded the hand triage's "
          f"totals ({v['documents']} documents in the ledger)")
    r.append(v["passed"])
    held = sha(os.path.join(TMP, "rule-16-1-searches.csv")) == searches_before
    print(f"  {'PASS' if held else 'FAIL'}  the backfill changed no published count")
    r.append(held)

    print("\nscenario 4: another new document, now that the classifier is validated")
    grown['"Federal Rule of Civil Procedure 16.1"'] = \
        BASE['"Federal Rule of Civil Procedure 16.1"'] + [NEW_DOC, NEW_DOC2]
    ok, row = run("new document, validated", grown, 42, "NEW_DOCUMENTS")
    r.append(ok)
    moved = sha(os.path.join(TMP, "rule-16-1-searches.csv")) != searches_before
    print(f"  {'PASS' if moved else 'FAIL'}  the search log was updated automatically")
    r.append(moved)
    import csv as _csv
    rows = list(_csv.DictReader(open(os.path.join(TMP, "rule-16-1-searches.csv"))))
    cur = [x for x in rows if x["status"] == "CURRENT" and x["query_form"] == "spelled_out"]
    # Both NEW_DOC, held pending since scenario 2, and NEW_DOC2 fold in together: the state
    # file never counted the first as accounted for, so it is still new.
    good = len(cur) == 1 and cur[0]["hits"] == "37" and cur[0]["triage_source"] == "MIXED" \
        and int(cur[0]["hits_in_post_effective_mdl"]) == 33
    print(f"  {'PASS' if good else 'FAIL'}  spelled_out: hits 35 -> {cur[0]['hits'] if cur else '?'}, "
          f"post-effective MDL 31 -> {cur[0]['hits_in_post_effective_mdl'] if cur else '?'}, "
          f"triage_source={cur[0]['triage_source'] if cur else '?'} "
          f"(the document held pending in scenario 2 was not lost)")
    r.append(good)
    sup = [x for x in rows if x["status"] == "SUPERSEDED" and x["query_form"] == "spelled_out"
           and x["hits"] == "35" and x["date_filter"] == "entry_date_filed_after"]
    print(f"  {'PASS' if sup else 'FAIL'}  the prior row was superseded, not edited")
    r.append(bool(sup))
    p = subprocess.run(["python3", "build.py", "--check"], capture_output=True, text=True, cwd=TMP)
    print(f"  {'PASS' if p.returncode == 0 else 'FAIL'}  build.py --check accepts the result "
          f"({p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-200:]})")
    r.append(p.returncode == 0)
    disclosed = "automatic triage" in open(os.path.join(TMP, "index.html")).read()
    print(f"  {'PASS' if disclosed else 'FAIL'}  the page now says so in its limitations")
    r.append(disclosed)

    print("\nscenario 5: a document nothing can classify")
    grown2 = dict(grown)
    grown2['"FRCP 16.1"'] = BASE['"FRCP 16.1"'] + [UNDECIDABLE]
    ok, row = run("undecidable document", grown2, 42, "NEW_DOCUMENTS")
    r.append(ok)
    rows = list(_csv.DictReader(open(os.path.join(TMP, "rule-16-1-searches.csv"))))
    cur = [x for x in rows if x["status"] == "CURRENT" and x["query_form"] == "frcp_acronym"]
    parked = cur and cur[0]["hits_unverified"] == "1" and cur[0]["hits"] == "7"
    print(f"  {'PASS' if parked else 'FAIL'}  it was counted hits_unverified, not guessed at "
          f"(unverified={cur[0]['hits_unverified'] if cur else '?'}, hits={cur[0]['hits'] if cur else '?'})")
    r.append(bool(parked))
    p = subprocess.run(["python3", "build.py", "--check"], capture_output=True, text=True, cwd=TMP)
    print(f"  {'PASS' if p.returncode == 0 else 'FAIL'}  the arithmetic still balances")
    r.append(p.returncode == 0)

    print("\nscenario 6: positive control absent")
    broken = dict(grown2)
    broken['"Federal Rule of Civil Procedure 16.1"'] = list(range(2000, 2034))
    state_before = open(os.path.join(TMP, "maintenance/watch-state.json")).read()
    searches_now = sha(os.path.join(TMP, "rule-16-1-searches.csv"))
    r.append(run("control failed", broken, 42, "CONTROL_FAILED", expect_rc=1)[0])
    untouched = open(os.path.join(TMP, "maintenance/watch-state.json")).read() == state_before
    print(f"  {'PASS' if untouched else 'FAIL'}  the state file was left as it was")
    r.append(untouched)
    held = sha(os.path.join(TMP, "rule-16-1-searches.csv")) == searches_now
    print(f"  {'PASS' if held else 'FAIL'}  no count was changed")
    r.append(held)

    print("\nthe files the watch must never touch")
    for f in ("subject-treatment.csv", "rule-16-1-tracker.csv", "party-invocations.csv",
              "subject-treatment-codebook.md", "coding-decisions.md"):
        same = sha(os.path.join(REPO, f)) == sha(os.path.join(TMP, f))
        print(f"  {'PASS' if same else 'FAIL'}  {f}")
        r.append(same)

    print(f"\n  {sum(r)}/{len(r)} passed\n")
    print("log:")
    for line in open(os.path.join(TMP, "maintenance/watch-log.csv")):
        print("  " + line.rstrip()[:190])
    return all(r)


if __name__ == "__main__":
    a = part1()
    b = part2()
    print(f"\n{'ALL PASSED' if a and b else 'FAILURES ABOVE'}")
    sys.exit(0 if (a and b) else 1)
