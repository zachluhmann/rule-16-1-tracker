# Rule 16.1 Tracker — Coding Protocol

**Project:** A complete, continuously updated record of how federal transferee
courts have applied Fed. R. Civ. P. 16.1 since its effective date of
December 1, 2025.

**Why this exists:** Every major firm alert on Rule 16.1 says the same thing —
that it is too early to know what courts are doing. Crowell: *"it will likely be
several years before the impact of Rule 16.1 is clear."* Sidley: *"courts have
taken varied approaches"* — citing none. Nobody has counted. This counts.

---

## The one rule that makes this citable

**Record only what the court did. Never what you think it meant.**

This is the discipline that got Damien Charlotin's hallucination database cited
by name in the Fifth and Eleventh Circuits, and it is the entire product. Every
coding decision follows from it:

- Code from the **order text**, not from a party's characterization of the order,
  not from a firm alert describing it, not from a docket entry summary.
- Where an order is ambiguous, code `UNCLEAR` and quote the language in
  `notes`. Do not resolve the ambiguity yourself.
- Where the record is silent, code `NOT_ADDRESSED` — not `NO`. Silence is a
  finding; inferred absence is an argument.
- **Deliberately undercount.** If you are unsure whether something qualifies,
  it doesn't. An undercount is a floor a court can rely on. An overcount is a
  number a court will not touch.
- Never characterize a judge's motives, competence, or compliance in the public
  data. `CITES_RULE = NO` is a fact. "Ignored the rule" is not.

**Do not let anyone use this in litigation strategy.** If a party asks you to
add, remove, or reframe an entry to help a position, decline and say why on the
site. Charlotin does this explicitly, and it is load-bearing for the neutrality
that makes the thing worth citing.

---

## Universe definition

**In scope:** every MDL docketed by the JPML on or after December 1, 2025.

**Also tracked, separately flagged:** any MDL created *before* December 1, 2025
in which a court has expressly invoked Rule 16.1. Firms are split on whether
16.1 reaches pending MDLs and nobody has counted — the `PRE_EFFECTIVE_DATE`
flag turns that dispute into a number.

**Authoritative universe list:** the JPML's own monthly
*Pending MDL Dockets By MDL Number* PDF at
https://www.jpml.uscourts.gov/pending-mdls-0 — not any secondary source, and
not a list you assembled by search. Completeness is the product; reconcile
against the JPML PDF every month and log the reconciliation date.

> ⚠️ The seed CSV is a starting point assembled from docket research, and it has
> gaps in the MDL number sequence (3164, 3165, 3168–3170, 3173, 3177,
> 3182–3184, 3186). Some are denied petitions; some may be real MDLs missing
> from the seed. **Reconcile against the JPML PDF before publishing anything.**

---

## Coding values

Use these five values everywhere and nowhere else. Consistency beats nuance.

| Value | Means |
|---|---|
| `YES` | The order affirmatively does this, in text you can quote |
| `NO` | The order affirmatively declines or forecloses this |
| `NOT_ADDRESSED` | The order is silent |
| `UNCLEAR` | The order touches it ambiguously — quote the language in `notes` |
| `PENDING` | No qualifying order has issued yet in this MDL |

Every `YES` requires a pin cite in the corresponding `_cite` column
(document + page or paragraph). A `YES` without a pin cite is not yet data.

---

## Workflow

1. **Monthly:** pull the JPML pending-MDL PDF, reconcile the universe, add new rows.
2. **Weekly:** review CourtListener alert hits (see `collect.py`).
3. **Per new order:** read the order, code the row, pin-cite every `YES`,
   perma.cc the source, record `date_accessed`.
4. **Never** backfill from a firm alert. Alerts tell you an order exists; the
   order tells you what it says.

---

## Citation plumbing — this is empirically load-bearing

Both appellate citations of the Charlotin database used different paths, and you
need to support both:

- *Fletcher v. Experian Info. Sols., Inc.*, No. 25-20086 (5th Cir. Feb. 18, 2026)
  cited the live URL in a footnote.
- *Parnell v. Fla. Dep't of Corrections*, No. 25-11166 (11th Cir. July 10, 2026)
  cited it **through perma.cc**.

So:

- **Stable URLs that never move.** One canonical page. No restructuring.
- **A "Suggested citation" block** on the landing page, in Bluebook form,
  with a `last visited` convention.
- **A perma.cc link for every entry**, free through NYU's library. Put it in
  the `perma` column and surface it in the UI.
- **A visible `last updated` date** and a versioned changelog.
- **A Harvard Dataverse DOI** for the CSV, so the dataset is citable
  independently of the website — and survives you losing interest in the site.
- **CC-BY license**, stated on the page.
- Link every source to the free, stable **CourtListener** document URL. Never
  to PACER.

---

## Promotion — niche blog first, never mainstream first

Charlotin's actual path: launch (~May 2025) → *eDiscovery Today*, a one-man
practitioner blog (June 9) → **Forbes (July 18, ~10 weeks)** → Fifth Circuit
(Feb. 2026). The niche blog fed the mainstream writer. Do not pitch Forbes.

Order of operations once you have complete coverage of the seed universe:

1. **Drug & Device Law** (Reed Smith; "Bexis") — highest leverage by far. He
   filed public comments on proposed Rule 16.1 and wrote the skeptical
   *"better than nothing, but not by a lot"* piece. Your data answers his exact
   question. This is your *eDiscovery Today*.
2. **The Advisory Committee on Civil Rules** — submit the dataset as a
   suggestion. For a procedure tracker this is the highest-value citation
   target that exists.
3. **Academics who will cite it:** Nora Freeman Engstrom (Stanford Rhode
   Center, authored *Managing MDLs*), Duke's Bolch Judicial Institute (which
   runs the MDL certificate program that trains MDL judges), and NYU's own
   **Center on Civil Justice**.
4. **Lawyers for Civil Justice** will amplify — they've campaigned for MDL
   rules since 2018 and need empirical ammunition. **Let them cite you; do not
   co-brand.** Their endorsement costs you the neutrality that makes this
   citable in the first place.
5. Trade press last: Law360, Bloomberg Law, ABA Litigation Section Mass Torts
   newsletter, mdlupdate.com.

**Set expectations honestly.** Charlotin got cited because judges needed a
number for a factual proposition. Judges rarely need a number about Rule 16.1
uptake. Expect citations from firm alerts, the Rules Committee, and law
reviews — real, but quieter, and probably not an appellate opinion inside
twelve months. The guaranteed floor is a complete original dataset that
supports a publishable empirical note.

---

## The TPLF expansion — designed in from day one

Third-party litigation funding disclosure was **deliberately omitted** from
Rule 16.1. The question of whether courts order it anyway under the
16.1(b)(4) "any other matter" catch-all is therefore live, contested, and
unmeasured.

The `b4_tplf_*` columns exist so that if the answer turns out to be "yes,
frequently," you already own the seed of a second and larger dataset — and one
with a better citation path, because the **April 14, 2026 Advisory Committee
agenda book** shows Judge Vance's TPLF subcommittee actively soliciting exactly
this information.

Code these columns from day one even when the answer is `NOT_ADDRESSED`. The
denominator is the finding.

---

## Two guardrails learned while coding (added 2026-08-11)

**1. Absence from the search index is NOT evidence of `NO`.**

MDL 3167 does not appear in the `"Federal Rule of Civil Procedure 16.1"` search.
It is tempting to code it `cites_rule = NO`. That would be wrong, and it is the
single error most likely to destroy the dataset's credibility.

Its initial order — *Notice and Order of Case Management Hearing (MDL Pretrial
Order No. 1)*, ECF 11 — **has no text layer in RECAP**, so it is not searchable
and its contents are unknown. A search index reflects what has been digitized,
not what courts did.

Never code `NO` from a null search result. Code `NO` only from order text you
have read that affirmatively declines or forecloses. Otherwise the row is
blocked, not negative.

**2. ~~Trust docket text over metadata fields.~~ → A single MDL can have more
than one judge. Record the judge PER ORDER.**

> ⚠️ **This guardrail originally said the opposite, and it was wrong.** The
> correction is left visible on purpose — see PROTOCOL's own rule about logging
> corrections to corrections.

The original text read: *"CourtListener's `assignedTo` field for MDL 3167 reads
'David Barlow.' The JPML transfer order assigns the MDL 'to the Honorable Robert
J. Shelby,' and every subsequent order is signed by Shelby. The metadata field is
wrong."*

**Both records were accurate; they described different moments.** In MDL 3167:

| Date | Event | Case number |
|---|---|---|
| 2025-12-16 | JPML transfers to D. Utah, assigns **Judge Robert J. Shelby** | 2:25-MD-03167-RJS-JCB |
| 2025-12-31 | MDL Pretrial Order No. 1, signed **Shelby** — cites Rule 16.1(b) twice | 2:25-MD-03167-RJS-JCB |
| 2026-02-10 | JPML **reassigns to Judge David B. Barlow** ("the need to reassign the above litigation to another judge in the District of Utah") | — |
| 2026-02-17 | **Magistrate Judge Jared C. Bennett recuses**; referral to Magistrate Judge Cecilia M. Romero | — |
| 2026-02-19 | MDL Pretrial Order No. 2, signed **Barlow** — never mentions Rule 16.1 | 2:25-MD-03167-**DBB-CMR** |

CourtListener's `assignedTo` was current and correct. My reading of it was not.

The real rules:

1. **`judge` is a per-order fact, not a per-MDL fact.** Where the bench changes
   mid-MDL, record it as `Shelby (PTO 1); Barlow (PTO 2 onward, reassigned
   2026-02-10)` and pin-cite the reassignment order.
2. **The case-number suffix is the tell.** `-RJS-JCB` → `-DBB-CMR` announces both
   changes at a glance. Watch the suffix across documents on the same docket.
3. **Metadata is a lead, and so is a transfer order.** A transfer order is
   authoritative for the assignment it makes and stale the moment a reassignment
   issues. Neither is a substitute for reading the signature block on the specific
   document you are coding.
4. Do still take court and date from the order text. That part was right.

### `source_status` — added for exactly this reason

| Value | Means |
|---|---|
| `TEXT_AVAILABLE` | Order text read; the row can be coded |
| `NEEDS_PACER_PULL` | Order exists on the docket but has no RECAP text layer |
| `NO_ORDER_YET` | Docket checked; no qualifying order has issued |
| `NOT_CHECKED` | Docket not yet reviewed |

`NEEDS_PACER_PULL` and `NO_ORDER_YET` are different facts and must never be
merged. The first is a gap in your data collection; the second is a finding
about the court. Reporting them as one number would be the kind of error that
gets a dataset dismissed rather than cited.

This is also the concrete reason to install the RECAP extension and apply for
the PACER fee exemption: every blocked row is a document you have to buy, and
buying it puts the text into the public archive for everyone who cites you next.

**3. A clerk's docket entry is not the order.**

Clerk-generated deadline-setting entries ("Set Deadlines/Hearings per 2 Pretrial
Order No. 1. Case Management Statements due by …") are court-generated and
reliable **for dates**. They are not the order and say nothing about whether the
court cited Rule 16.1, which topics it required, or how it framed them.

Where an order is blocked but the clerk's entry establishes a schedule, you may
code the date fields from it — but **flag the provenance in `pin_cites`** and
leave every rule-content variable `UNCLEAR`. Never let a scheduling entry
populate `cites_rule`, `rule_role`, or any `b2`/`b3` column.

---

## Operational finding: RECAP text availability is the real bottleneck

Of the first six master dockets reviewed, **two of the key initial orders have
no text layer in RECAP** — MDL 3166 (Roblox, Pretrial Order No. 1) and MDL 3167
(Broiler Chicken Grower, MDL Pretrial Order No. 1). Both exist on the docket;
neither is readable or searchable.

That is a roughly one-in-three block rate on the most important document type in
the entire project, and it has three consequences:

1. **Budget for PACER pulls from the start.** This is the concrete reason the
   fee exemption and the RECAP extension matter. Each pull also puts the text
   into the public archive permanently, which is what keeps your own citations
   free and stable for whoever cites you next.
2. **Search-only coverage would have produced a badly wrong dataset.** Both
   blocked MDLs are invisible to the `"Federal Rule of Civil Procedure 16.1"`
   query. A researcher working from search results alone would have silently
   recorded them as non-citing. Docket-by-docket review over the JPML universe
   is not optional rigor — it is the only method that produces a defensible
   denominator.
3. **Report the block rate publicly.** A stated "N orders reviewed, M blocked
   pending retrieval" is a credibility asset. A quiet gap is a liability.

---

## Guardrail 4 — THE DUPLICATE-RECORD TECHNIQUE (added 2026-08-11)

**This is the single most valuable operational discovery in the project. It cut
the block rate from 57% to 21%.**

The same court filing can exist in RECAP as **more than one `recap_document`
record**. Some of those records have a text layer; others do not. If the record
you find first has `is_available = false` and empty `plain_text`, **the document
is not necessarily blocked — you may simply have the wrong record.**

How to find the good record:

```
# 1. Enumerate every AVAILABLE document on the master docket:
call_endpoint(
  endpoint_id = "recap-documents",
  query = {"docket_entry__docket__id": <CL docket id>,
           "is_available": true,
           "fields": ["id","document_number","attachment_number",
                      "description","page_count","is_available"]},
  num_results = 50)

# 2. Or search with available_only, scoped tightly:
search(type="rd", docket_number="4:26-md-03172", available_only=true,
       fields=["id","docket_id","entry_number","entry_date_filed",
               "description","short_description","is_available","page_count"])
```

Two hard-won notes on the tooling:

- **`type="rd"` search results use different field names than dockets.** Ask for
  `id`, `docket_id`, `entry_number`, `entry_date_filed`, `description`,
  `short_description`, `is_available`, `page_count`. Asking for `caseName` or
  `dateFiled` silently returns empty objects.
- **Scope by docket, not by keyword.** A caption search like
  `"Fire Apparatus" AND MDL` returns the *JPML's* docket, which is a different
  docket from the transferee court's master docket and is full of party filings.
  Use the CourtListener docket id.

Documents unblocked this way so far: MDL 3166 (462309351, not 447553818),
MDL 3163 (462954586), MDL 3172 (469251458 and 483580211), MDL 3179 (475479617,
not 478654407), MDL 3185 (482432333, not 467174925).

**Do not declare a row blocked until you have run this.** A prematurely declared
`NEEDS_PACER_PULL` is a soft version of the same error as a wrongly coded `NO`.

---

## Guardrail 5 — the operative document is not always captioned "Order"

MDL 3172's initial-conference document (ECF 15) is a **signed letter on chambers
letterhead** — *"Dear Counsel: … Sincerely, Kristine G. Baker"* — docketed as an
order. It sets the conference date, orders leadership proposals, imposes page
limits, and requests a procedural-posture summary. It is unambiguously the
operative 16.1(a)/(b) document, and a retrieval net keyed to the word "Order"
would never see it.

Sweep the whole low-numbered docket. Letters, notices, minute entries, and
riders to unrelated motions (see MDL 3178) all carry initial-management content.

---

## Guardrail 6 — "remand" is ambiguous and must not be keyword-coded

In an MDL order, *"motions to remand"* usually means **remand to state court
under 28 U.S.C. § 1447** after removal — not **§ 1407 remand to the transferor
court**, which is what `beyond_remand_timing` is about.

MDL 3185's agenda topic 4 references "motions to remand" in a removed data-breach
class action. That is § 1447. It was coded `NOT_ADDRESSED`, correctly.

Read the surrounding sentence every time. Never let a string match populate this
column.

---

## Guardrail 7 — ECF 1 on a transferee docket is usually not the court's order

When the JPML transfers, the Panel's own transfer order is docketed in the
transferee court, frequently as ECF 1, and conditional transfer orders follow as
later entries. **Those are Panel documents, not transferee-court orders**, and
they say nothing about how the transferee judge is applying Rule 16.1.

MDL 3179: ECF 1 is the Panel's Transfer Order and ECF 5 is CTO-1. The transferee
court's own initial order is **ECF 2**, one page long.

Check the header. Panel documents carry `Case MDL No. XXXX Document NNN` in the
top line; transferee-court documents carry the district case number.

---

## The off-docket report — state this limitation publicly

Two of the first ten courts direct the parties' pre-conference submissions to a
**chambers email address instead of the docket**:

- MDL 3163 (Marston, E.D. Pa.) — position statements to
  `PAED_MDL_GLP1_RA@paed.uscourts.gov`; the order says they *"should not be filed."*
- MDL 3172 (Baker, E.D. Ark.) — leadership proposals and procedural-posture
  summaries *"submitted only by email to KGBchambers@ared.uscourts.gov."*

Rule 16.1's only real mandates run to the **parties' report**. Where the report
never reaches the docket, no docket-based method — this one included — can
observe what the rule actually produced.

Put this on the landing page in plain language, next to the block rate. A stated
limitation is a credibility asset; a silent one is the thing a critic uses to
dismiss the whole dataset. It is also independently newsworthy to the Advisory
Committee.

---

## Coding-unit rule (added 2026-08-11)

**The coding unit is the first order that does Rule 16.1(a)/(b) work — not the
first order on the docket.**

MDL 3172 shows why: an administrative *Order Upon Transfer* on Feb. 18, 2026
(ECF and filing mechanics, pro hac vice, stay of discovery, MCL 4th) and the
substantive conference-setting letter on **June 22, 2026** — four months apart.
Coding the first document would have recorded that MDL as having no leadership,
no discovery, and no conference provisions.

Where two documents split the work, record **both** in `source_doc_type` and
`cl_docket_entry_id` (semicolon-separated), and pin-cite by document in
`pin_cites`.

---

## Provenance-honesty rule for partially-read dockets

When a docket has more orders than you have read, say exactly which ones you
read in full, which you only text-searched, and which you have not touched.
MDL 3179's `pin_cites` field is the model:

> ECF 2 read in full and coded. ECF 1 and ECF 5 read in full — both are Panel
> documents. ECF 6 and ECF 17 text-searched for "16.1" with zero matches but
> **not** read in full; their substantive content is not reflected in the b2/b3
> columns. ECF 4 and 14 not yet retrieved.

A zero-match text search supports `cites_rule`. It supports **nothing else**.
Never let it populate a `b2`/`b3` column.

---

## Guardrail 8 — CHECK THE DISTRICT COURT'S OWN WEBSITE FIRST (added 2026-08-11)

**This is a better source than PACER and it is free.** It closed MDL 3167, which
two rounds of RECAP work could not.

Many districts maintain a public MDL page that posts every pretrial order as a
PDF, in order, with dates and titles. The District of Utah's is the model:

> https://www.utd.uscourts.gov/multi-district-litigation-mdl-cases

For MDL 3167 that single page listed the transfer order, Pretrial Orders 1
through 4, the JPML reassignment order, and the magistrate's recusal order — all
directly downloadable. RECAP had exactly one of those documents with a text
layer, and it was not the one that mattered.

**Why this beats PACER for this project specifically:**

- Free, no account, no fee-exemption paperwork.
- The court is the publisher, so provenance is unimpeachable.
- It surfaces the *sequence* of orders, which is how you find out that a
  conference order and the management order it produced say different things.
- It surfaces reassignment and recusal orders, which RECAP metadata flattens.

**Its one weakness: these are live pages and the file URLs are not stable.**
`.../sites/utd/files/225md3167 MDL Pretrial Order No 2.pdf` is a CMS path, not a
permanent identifier. **Perma.cc every one of them the day you cite it** — the
`perma` column exists exactly for this.

**Do this before concluding a row is blocked.** The retrieval order is now:

1. RECAP, then the duplicate-record technique (Guardrail 4).
2. **The district court's own MDL page.** Search
   `site:<district>.uscourts.gov "md<MDL number>"` or look for a
   "Multidistrict Litigation" link in the court's main navigation.
3. Member-case dockets — MDL pretrial orders are usually entered in every member
   case, and one of those copies may have a text layer.
4. govinfo.gov (free, permanent, but coverage of district-court orders is thin).
5. PACER, last.

Only after all five is a row honestly `NEEDS_PACER_PULL`.

---

## `cites_rule` must be split by document type

MDL 3167 is the proof. Judge Shelby's conference-setting order (PTO 1,
Dec. 31, 2025) cites Rule 16.1(b) twice and calls the required filing
**"the Rule 16.1(b) Report."** The initial management order that came out of that
very conference (PTO 2, Feb. 19, 2026) contains neither "16.1" nor "Rule 16.1."

A single per-MDL `cites_rule` cannot express that. Two columns now do:

| Column | Question |
|---|---|
| `a_order_cites_rule` | Does the order scheduling the 16.1(a) conference cite the rule? |
| `c_order_cites_rule` | Does the resulting 16.1(c) initial management order cite it? |

`cites_rule` stays as the roll-up (`YES` if any order in the MDL cites it) so the
headline number remains simple, but **report the split.** "The rule structures the
conference and disappears from the order" is a sharper finding than any single
percentage, and it is invisible to a per-MDL variable.

---

## Guardrail 9 — NEWS-SITE AND FIRM MIRRORS OF THE COURT'S OWN PDF (added 2026-08-11)

**Read the mirrored PDF. Never read the article.** These are two completely
different things and conflating them would destroy the dataset.

Mass-tort news sites and plaintiff firms routinely upload the court's actual
signed PDF alongside their coverage. That PDF is the primary source — it is the
court's document, byte for byte — and reading it is exactly as legitimate as
reading it from PACER. The article wrapped around it is a secondary source and
PROTOCOL's rule against backfilling from alerts applies to it in full.

Worked example, MDL 3181 (Boston Scientific, C.D. Cal.): **zero** of the 35
documents on that master docket are available in RECAP. A plaintiff firm had
posted Pretrial Order No. 1 as a PDF. The row is fully coded from that PDF, with
`source_doc_type` recording the mirror and a standing instruction to re-verify
against the court's own copy once C.D. Cal.'s MDL webpage goes live.

Where mirrors are usually found: `nighgoldenberg.com`, `robertkinglawfirm.com`,
`mdlcases.com`, `aboutlawsuits.com`, and the case-specific pages of the firms
seeking leadership in that MDL. Search
`"<MDL caption>" "pretrial order" OR "case management order" filetype:pdf`.

**Three hard rules when you use one:**

1. **Corroborate identity against the docket before coding.** The docket entry
   gives you title, date, judge and ECF number independently. If those do not
   match the PDF exactly, stop.
2. **Record the mirror in `source_doc_type`**, verbatim, and carry a
   re-verification instruction.
3. **Perma.cc the court's own copy, never the mirror.** A firm's marketing page
   is not a citation you want under a claim in a law review.

### New `source_status` value: `PUBLIC_COPY_LOCATED`

| Value | Means |
|---|---|
| `TEXT_AVAILABLE` | Order text read; the row can be coded |
| `PUBLIC_COPY_LOCATED` | **A free, non-PACER copy is known to exist at a specific URL, but has not been read.** The URL goes in `source_doc_type`. |
| `NEEDS_PACER_PULL` | Order exists on the docket, no text layer, no public copy found |
| `NO_ORDER_YET` | Docket checked; no qualifying order has issued |
| `TEXT_ORDER_ON_DOCKET` | The docket entry *is* the complete signed order |
| `NOT_CHECKED` | Docket not yet reviewed |

MDL 3180 is the reason this value exists. The order — *Initial Procedure Order*,
June 11, 2026, ECF 3 — is not in RECAP, but a free copy sits at a known URL that
this session's fetcher cannot retrieve (that host's `robots.txt` disallows it).
Anyone with a browser can open it. That is a different fact from MDL 3187, where
the full retrieval ladder found no public copy at all, and reporting them as one
number would be the same category error as merging `NEEDS_PACER_PULL` with
`NO_ORDER_YET`.

---

## Court MDL pages found so far — check these first for any new row

| District | URL |
|---|---|
| D. Utah | https://www.utd.uscourts.gov/multi-district-litigation-mdl-cases |
| D.N.J. | https://www.njd.uscourts.gov/case-management-orders · /mdl-cases |
| E.D. Mo. | https://www.moed.uscourts.gov/mdl-multidistrict-litigation-cases |
| N.D. Cal. | https://cand.uscourts.gov/cases-e-filing/newly-filed-cases/cases-interest |
| C.D. Cal. | https://www.cacd.uscourts.gov/newsworthy/cases-of-interest-all |
| N.D. Fla. | https://flnd.uscourts.gov/cases-interest (per-MDL pages: `/mdl<NNNN>-orders-by-date`) |
| D. Kan. | https://www.ksd.uscourts.gov/special-cases/ |

**Coverage is by court, not by rule, and it is uneven.** D. Utah posts every
pretrial order for its current MDLs. D.N.J. and D. Kan. maintain rich pages for
older MDLs and had not yet added their newest ones (3180, 3187) as of
2026-08-11 — **so recheck these pages on the monthly reconciliation**, because a
row that is blocked today may be free next month. Judge Staton's Pretrial Order
No. 1 in MDL 3181 says C.D. Cal. will publish key orders to an MDL webpage
"shortly"; that is a row to recheck too.

---

## Guardrail 10 — THE PHRASE QUERY IS NOT AS PRECISE AS IT LOOKS (added 2026-08-11)

`collect.py` warns against querying bare `"Rule 16.1"` because of local rules.
There is a second, worse problem, and it was invisible until the date restriction
came off.

**Run `"Federal Rule of Civil Procedure 16.1" OR "Fed. R. Civ. P. 16.1"` with no
`filed_after` and CourtListener returns ~697 documents, overwhelmingly plain
Rule 16 scheduling orders.** The index does not treat `16.1` as a token distinct
from `16`, so any order reciting "pursuant to Fed. R. Civ. P. 16" matches. The
first page is almost entirely S.D.N.Y. initial case management orders from 2017–2024.

**The precision this project has been relying on comes substantially from
`filed_after=2025-12-01`, not from the phrase.** The rule did not exist before
that date, so the date filter removes essentially all of the Rule 16 noise for
free. That is fine for the post-effective-date universe and it is a real
limitation everywhere else.

**Consequences:**

1. **Never report a raw hit count** from these queries as a measure of anything.
   Dedupe on `docket_entry_id` *and* read every hit.
2. **The pre-effective-date question cannot be answered by lifting the date
   filter.** See below.
3. Reproducibility note for the published methodology: state the date filter as
   part of the query, not as a convenience.

### How to actually answer the pre-effective-date question

`PROTOCOL.md` defines it and the `pre_effective_date` column exists to hold the
answer: **has any court invoked Rule 16.1 in an MDL created before December 1,
2025?** Firms are split on whether the Rule reaches pending MDLs; nobody has
counted. It is the largest unclaimed finding left in the project.

The method is not "remove `filed_after`." Any order *applying* Rule 16.1 must
have been *filed* after the effective date regardless of when the MDL was
created. So:

1. Keep `filed_after=2025-12-01`. Run the precise and abbrev queries.
2. Collect every unique `docket_id` in the results.
3. For each, resolve the docket and ask one question: **was this MDL centralized
   before December 1, 2025?** Cross-check against the JPML monthly report.
4. Any hit in a pre-December-2025 MDL is a `pre_effective_date = YES` row — and
   the first real datum in a live dispute.
5. Any hit that is not an MDL at all belongs in `party-invocations.csv` with
   `mdl_no = NON-MDL`, per the *FedEx Tariff* precedent.

Budget it properly: step 3 is one API call per docket, and see the rate limits
below.

---

## Rate limits will gate this work — plan around them

Free authenticated CourtListener tier, measured in practice on 2026-08-11:

| Window | Cap | What it feels like |
|---|---|---|
| Per minute | 5 | Sleep ~13s between calls, or batch |
| Per hour | 50 | Reached after roughly one focused hour |
| **Per day** | **125** | **A hard stop; resets on a rolling window** |

`read_document` accepts a **list** of chunk indexes — up to ten windows in one
call. Use it. Reading a 49-page report in four chunked calls instead of twelve
single ones is the difference between finishing a document and losing the day.
Likewise `search_document` takes a list of up to ten document IDs, which is the
cheapest way to ask "does this string appear in any of these ten filings."

A Free Law Project membership lifts all three. Once the weekly alert review plus
a monthly reconciliation is routine, the membership costs less than the time lost
to 429s — and this project is now large enough that the daily cap, not the
research, is the binding constraint.
