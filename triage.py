#!/usr/bin/env python3
"""
Triage: assigning a search hit to one of the five categories the search log counts.

    hits_in_post_effective_mdl   an MDL centralized on or after 1 Dec 2025
    hits_in_pre_effective_mdl    an MDL centralized before it
    hits_non_mdl                 an ordinary civil case
    hits_noise_rule_16           the index returned it because it treats 16.1 as 16,
                                 or because the document is about a LOCAL rule 16.1
    hits_unverified              not decided

This is a different kind of decision from coding an order, and the difference is the whole
reason this file exists. Coding asks whether a provision fires `court_resolution`, which two
trained coders split on twenty-two times out of three hundred. Triage asks which case a
document sits in, which the document itself answers on its first line, because every federal
filing carries an ECF header stamping its own docket number.

So triage is done by rule wherever a rule can decide it, by a model only where no rule can,
and by nobody at all where the model cannot produce a verbatim quote to stand behind. The
third outcome is not a failure. `hits_unverified` is a real category that already sums into
the arithmetic, and a hit parked there is visible on the page as undecided rather than
silently miscounted.

Every verdict carries the rule that produced it and the text it relied on, and both go into
maintenance/triage-ledger.csv, so any figure derived from machine triage can be walked back
to the string that produced it.
"""
import csv, json, os, re, urllib.request, urllib.error

EFFECTIVE = "2025-12-01"

# The Rule's name, in every form the sweep looks for and a few it does not. A document that
# contains "16.1" but none of these is either Rule 16 noise or about some other 16.1.
FEDERAL_FORMS = re.compile(
    r"Fed\.?\s?R\.?\s?Civ\.?\s?P\.?\s*16\.1"
    r"|F\.\s?R\.\s?C\.\s?P\.?\s*16\.1"
    r"|FRCP\s*16\.1"
    r"|Federal\s+Rule[s]?\s+of\s+Civil\s+Procedure\s+16\.1"
    r"|Rule\s+16\.1\s+of\s+the\s+Federal\s+Rules", re.I)
# A bare subsection reference, "Rule 16.1(b)", is deliberately NOT in that list. It reads like
# a federal citation and is not one: local rules have subsections too, and the first draft of
# this file misfiled RECAP 466008549, a brief about the Southern District of Florida's own
# rule, because "Local Rule 16.1(b)" matched a pattern for "Rule 16.1(b)". The cost of
# leaving it out is that a filing which cites only "Rule 16.1(a)" and never spells out the
# Rule's name goes to `unverified` instead of being counted. That is the correct direction to
# be wrong in.

# The collision this project has already been bitten by. Three districts number a local rule
# 16.1, and a bare-number search in those districts returns thousands of them. RECAP 466008549
# is a pro se opposition captioned "MOTION TO STAY THE REQUIREMENTS OF LOCAL RULE 16.1" that
# uses the string twenty-three times and never once means the federal rule.
LOCAL_FORMS = re.compile(
    r"Local\s+(?:Civil\s+)?Rule[s]?\s*(?:No\.?\s*)?16\.1"
    r"|L\.?\s?R\.?\s?Civ\.?\s?P\.?\s*16\.1"
    r"|\bL\.?R\.?\s*16\.1"
    r"|\bLoc\.?\s?R\.?\s*16\.1"
    r"|(?:S\.D\.|N\.D\.|D\.)\s*(?:Fla|Mass|Pa|Cal|Tex)\.?\s*L\.?\s?R\.?\s*16\.1", re.I)

# The ECF header stamp every federal PDF carries, and the caption block. Either yields the
# MDL number directly: "CASE 0:24-md-03108-DWF-DJF", "Case 2:26-md-03174-JLR",
# "MDL No. 24-3108", "MDL 3174".
MDL_PATTERNS = [
    re.compile(r"\b\d+:\d{2}-md-0*(\d{3,4})\b", re.I),
    re.compile(r"\b\d{2}-md-0*(\d{3,4})\b", re.I),
    re.compile(r"\bMDL\s*(?:No\.?|Case)?\s*(?:\d{2}-)?0*(\d{4})\b", re.I),
]
# A civil docket number with no MDL anywhere is evidence of an ordinary case, but only weak
# evidence: an MDL member case carries its own civil number and may never print the MDL's.
CIVIL_PATTERN = re.compile(r"\b\d+:\d{2}-cv-\d{3,6}\b", re.I)
BANKRUPTCY_PATTERN = re.compile(r"\b\d{2}-\d{5}\b|\bBankr\.|\badversary\s+proceeding\b", re.I)


def load_registry(tracker="rule-16-1-tracker.csv",
                  pre="maintenance/pre-effective-mdls.csv"):
    """Which MDL numbers this project knows about, and which side of the Rule they fall on.

    Post-effective MDLs come from the tracker, which is the dataset's own universe and is
    reconciled monthly against the JPML's pending list. Pre-effective ones come from a small
    hand-maintained file, because they are outside that universe by construction and got into
    the record only by turning up in a search.

    An MDL number in NEITHER is never guessed at. Inferring a centralization date from the
    number would be reasonable most of the time and wrong occasionally, and the occasions
    would be invisible.
    """
    reg = {}
    for r in csv.DictReader(open(tracker)):
        d = (r.get("jpml_transfer_date") or "").strip()
        if r["mdl_no"].isdigit() and d:
            reg[int(r["mdl_no"])] = {
                "side": "post_effective_mdl" if d >= EFFECTIVE else "pre_effective_mdl",
                "centralized": d, "source": "rule-16-1-tracker.csv"}
    if os.path.exists(pre):
        for r in csv.DictReader(open(pre)):
            if r["mdl_no"].isdigit():
                reg[int(r["mdl_no"])] = {"side": "pre_effective_mdl",
                                         "centralized": r["centralized"],
                                         "source": r["established_by"]}
    return reg


def mdl_numbers(text):
    """Every MDL number the text names. Plural on purpose: a transfer order names two."""
    found = set()
    for pat in MDL_PATTERNS:
        for m in pat.finditer(text or ""):
            n = int(m.group(1))
            if 1000 <= n <= 9999:
                found.add(n)
    return found


def verdict(cat, rule, evidence, **kw):
    v = {"category": cat, "method": "RULE", "rule": rule,
         "evidence": " ".join((evidence or "").split())[:400], "mdl_no": "",
         "escalate": "", "no_text_layer": False}
    v.update(kw)
    return v


def classify(doc, reg, by_sha1=None):
    """One document, one category, plus the rule and the string that decided it.

    `doc` is a RECAP document: id, plain_text, description, is_available, sha1. `description`
    is the clerk's docket entry, which the RECAP index searches alongside the document text.
    That is Guardrail 12 and it matters here: a hit whose document has no text layer was
    matched on the clerk's summary, and the summary is then the only evidence there is.
    """
    text = doc.get("plain_text") or ""
    desc = doc.get("description") or ""
    both = text + "\n" + desc
    no_text = not (doc.get("is_available") and text.strip())

    # R0. Nothing to read at all. Not a decision, an absence of one.
    if not both.strip():
        return verdict("unverified", "R0", "", no_text_layer=no_text,
                       escalate="no document text and no docket entry text")

    # R1. A document already classified under a different id. Two copies of one filing on a
    # master docket and a member docket are one filing, and RECAP gives them the same sha1.
    # This is the rule that catches the case the human first got wrong: RECAP 464112237 read
    # as an unrelated D. Ariz. civil case and is in fact the same brief as 464110936 in MDL
    # 3084, appearing on the originating docket.
    sha = doc.get("sha1")
    if sha and by_sha1 and sha in by_sha1:
        prior = by_sha1[sha]
        return verdict(prior["category"], "R1",
                       f"identical to document {prior['document_id']} (sha1 {sha[:12]})",
                       mdl_no=prior.get("mdl_no", ""), no_text_layer=no_text)

    # R2. The index treats 16.1 as 16. A document with no literal "16.1" anywhere is a Rule 16
    # document the tokeniser handed back, not a Rule 16.1 document.
    if "16.1" not in both:
        return verdict("noise", "R2", "no literal '16.1' in the document or the docket entry",
                       no_text_layer=no_text)

    fed = FEDERAL_FORMS.search(both)
    loc = LOCAL_FORMS.search(both)

    # R3. "16.1" present, no federal naming form, and a local-rule marker. The other 16.1.
    if not fed and loc:
        return verdict("noise", "R3", _around(both, loc.start()), no_text_layer=no_text)

    # R3b. Both. A filing that argues about a district's local rule 16.1 AND cites the federal
    # Rule is a real thing and no rule here can say which one the hit is for.
    if fed and loc:
        return verdict("unverified", "R3b", _around(both, loc.start()), no_text_layer=no_text,
                       escalate="names both the federal Rule 16.1 and a local rule 16.1")

    # R4. "16.1" present and nothing says which 16.1 it is. A rule cannot settle this.
    if not fed:
        return verdict("unverified", "R4", _around(both, both.find("16.1")),
                       no_text_layer=no_text,
                       escalate="names 16.1 but no federal naming form and no local-rule marker")

    # R5 to R7 locate the federal-rule reference in a case.
    nums = mdl_numbers(both)
    known = {n for n in nums if n in reg}
    unknown = nums - known

    if unknown and not known:
        return verdict("unverified", "R6", f"names MDL {sorted(unknown)}, none in the registry",
                       no_text_layer=no_text,
                       escalate=f"MDL {sorted(unknown)[0]} is in neither the tracker nor "
                                f"maintenance/pre-effective-mdls.csv. Either the universe is "
                                f"missing an MDL or the number is a JPML motion docket.")

    if known:
        sides = {reg[n]["side"] for n in known}
        if len(sides) > 1:
            return verdict("unverified", "R6", f"names MDLs {sorted(known)} on both sides",
                           no_text_layer=no_text,
                           escalate="document names MDLs from both sides of the effective date")
        n = sorted(known)[0]
        return verdict(sides.pop(), "R5", _around(both, _first_mdl_span(both)),
                       mdl_no=str(n), no_text_layer=no_text)

    # R7. A civil or bankruptcy docket number, no MDL named anywhere. Ordinary case.
    # Weak on its own, which is why R1's sha1 check runs first: an MDL member-case filing
    # carries a civil number and may never print the MDL's.
    if CIVIL_PATTERN.search(both) or BANKRUPTCY_PATTERN.search(both):
        m = CIVIL_PATTERN.search(both) or BANKRUPTCY_PATTERN.search(both)
        return verdict("non_mdl", "R7", _around(both, m.start()), no_text_layer=no_text)

    return verdict("unverified", "R8", _around(both, fed.start()), no_text_layer=no_text,
                   escalate="names the federal rule but no docket number of any kind")


def _around(text, i, w=160):
    if i is None or i < 0:
        return " ".join(text.split())[:2 * w]
    return " ".join(text[max(0, i - w):i + w].split())


def _first_mdl_span(text):
    best = None
    for pat in MDL_PATTERNS:
        m = pat.search(text)
        if m and (best is None or m.start() < best):
            best = m.start()
    return best


# ---------------------------------------------------------------------------------------
# The model tier. Reached only by R4, R6 and R8, which is to say only where no rule decides.
# ---------------------------------------------------------------------------------------

PROMPT = """You are triaging one document from a federal court docket for a research \
dataset about Fed. R. Civ. P. 16.1, which took effect 1 December 2025.

Assign exactly one category:
- post_effective_mdl : the document is in a multidistrict litigation centralized ON OR AFTER \
1 December 2025
- pre_effective_mdl  : the document is in an MDL centralized BEFORE 1 December 2025
- non_mdl            : the document is in an ordinary civil or bankruptcy case, not an MDL
- noise              : the document's "16.1" is NOT Fed. R. Civ. P. 16.1. Most often it is a \
district's own LOCAL rule numbered 16.1, or the search index returned a Rule 16 document.
- unverified         : you cannot tell from this text

These MDLs are known to the dataset (number: side):
%(registry)s

Rules you must follow:
1. Answer only from the text given. Do not use outside knowledge about these cases.
2. You must supply `quote`: a span of AT LEAST 40 characters copied EXACTLY from the text, \
character for character, that is your reason. It will be checked against the text \
mechanically and your answer discarded if it does not match.
3. If no such quote exists, answer "unverified". Answering "unverified" is a correct and \
expected outcome, not a failure.
4. If the text names an MDL number that is not in the list above, answer "unverified" and \
say so in `reason`. Do not guess when it was centralized.

Return only JSON: {"category": "...", "quote": "...", "reason": "one sentence"}

DOCUMENT %(id)s
Docket entry text (written by the clerk): %(desc)s

Document text:
%(text)s
"""


def ask_model(doc, reg, timeout=90):
    """Consult a model, then check its answer against the document before believing any of it.

    The check is the point. The model returns the passage it relied on and this function
    looks for that passage, whitespace-normalised, in the text it was given. A quote that is
    not there means the answer was produced from something other than the document, and the
    answer is thrown away rather than argued with. This is the same discipline the codebook
    already applies to human coders, which require an `evidence_quote` for every positive.
    """
    key_a, key_o = os.environ.get("ANTHROPIC_API_KEY"), os.environ.get("OPENAI_API_KEY")
    if not (key_a or key_o):
        return None
    text = (doc.get("plain_text") or "")[:60000]
    prompt = PROMPT % {"id": doc.get("id"), "desc": doc.get("description") or "(none)",
                       "text": text or "(no text layer; decide from the docket entry alone)",
                       "registry": "\n".join(f"  {n}: {v['side']} (centralized {v['centralized']})"
                                             for n, v in sorted(reg.items()))}
    try:
        if key_a:
            body = {"model": os.environ.get("TRIAGE_MODEL", "claude-sonnet-4-5"),
                    "max_tokens": 600, "messages": [{"role": "user", "content": prompt}]}
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages", method="POST",
                data=json.dumps(body).encode(),
                headers={"content-type": "application/json", "x-api-key": key_a,
                         "anthropic-version": "2023-06-01"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.load(r)["content"][0]["text"]
        else:
            body = {"model": os.environ.get("TRIAGE_MODEL", "gpt-4o"),
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}}
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions", method="POST",
                data=json.dumps(body).encode(),
                headers={"content-type": "application/json",
                         "authorization": f"Bearer {key_o}"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.load(r)["choices"][0]["message"]["content"]
    except Exception as e:
        return {"category": "unverified", "method": "MODEL_ERROR", "rule": "",
                "evidence": "", "mdl_no": "", "no_text_layer": False,
                "escalate": f"model call failed: {type(e).__name__}: {e}"}

    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        return _reject("model did not return JSON")
    try:
        ans = json.loads(m.group(0))
    except json.JSONDecodeError:
        return _reject("model returned malformed JSON")

    cat = str(ans.get("category", "")).strip()
    quote = str(ans.get("quote", "") or "")
    if cat not in ("post_effective_mdl", "pre_effective_mdl", "non_mdl", "noise", "unverified"):
        return _reject(f"model returned an unknown category {cat!r}")
    if cat == "unverified":
        return {"category": "unverified", "method": "MODEL", "rule": "",
                "evidence": "", "mdl_no": "", "no_text_layer": False,
                "escalate": "model declined to classify: " + str(ans.get("reason", ""))[:200]}

    # The verification. Whitespace is normalised on both sides because court PDFs break lines
    # mid-sentence and no quotation of one survives a character-for-character comparison.
    # Nothing else is normalised: not case, not punctuation, not hyphens.
    hay = " ".join(((doc.get("plain_text") or "") + " " +
                    (doc.get("description") or "")).split())
    needle = " ".join(quote.split())
    if len(needle) < 40:
        return _reject(f"quote too short to verify ({len(needle)} chars)")
    if needle not in hay:
        return _reject("quote does not appear in the document")
    if "16.1" not in needle and cat != "noise":
        return _reject("quote does not contain '16.1'")

    return {"category": cat, "method": "MODEL_VERIFIED", "rule": "",
            "evidence": needle[:400], "mdl_no": "", "no_text_layer": False,
            "escalate": ""}


def _reject(why):
    return {"category": "unverified", "method": "MODEL_REJECTED", "rule": "", "evidence": "",
            "mdl_no": "", "no_text_layer": False,
            "escalate": f"model answer discarded: {why}"}
