# Rule 16.1 Tracker — Start Here

A complete, continuously updated record of how federal transferee courts have
applied **Fed. R. Civ. P. 16.1** since it took effect December 1, 2025.

Nobody is doing this. Every major firm alert on Rule 16.1 admits the data
doesn't exist yet. This produces it.

```
PROTOCOL.md              The coding discipline, universe definition, the
                         retrieval ladder, and the promotion plan. Read first.
rule-16-1-tracker.csv    The order layer. 16 rows, 61 columns, 13 coded.
party-invocations.csv    The invocation layer — Rule 16.1 reports and party
                         filings that cite the Rule. Keyed to the FILING, not
                         the MDL, because one of them is not in an MDL.
collect.py               CourtListener collection, the retrieval ladder,
                         the two search traps, and alert config.
PUBLISH.md               v1.0 freeze checklist and the dated path to the
                         Advisory Committee (meets Oct. 21, 2026).
README.md                This file — setup, codebook, and findings log.

PUBLISH.md               v1.0 freeze checklist, suggested-citation block,
                         and the dated path to the Advisory Committee.
advisory-committee-      Draft suggestion to the Committee on Rules of
  submission.md          Practice and Procedure (source text).
Rule-16.1-Advisory-      The same, formatted as a letter, ready to send.
  Committee-Submission.docx
```

> ⏰ **The next Advisory Committee on Civil Rules meeting is October 21, 2026.**
> Its agenda book historically posts ~3 weeks out, so a suggestion needs to be
> with the Secretary by **early September 2026**. `PUBLISH.md` is the checklist
> to get there.

## CURRENT STATUS — 2026-08-11

| | |
|---|---|
| Universe (post-2025-12-01 MDLs), reconciled to the JPML Aug. 3, 2026 report | **16** |
| Readable initial order in hand and coded | **13** |
| No qualifying order yet *(a finding, not a gap)* | **1** — 3176 |
| Order identified, free public copy located, not yet read | **1** — 3180 |
| Blocked, orders confirmed to exist, no public copy found | **1** — 3187 |
| Block rate | **6%** (was 57% before the retrieval ladder) |

**HEADLINE: 6 of 13 MDLs with a readable initial order cite Fed. R. Civ. P. 16.1.
Seven never mention it.** The first three rows coded said 3/3 — because they came
from a full-text search, which can only find documents that use the phrase. See
"SECOND PASS" below; that selection-bias result is the most citable thing here.

**Read the findings log from the bottom up**, or skip to
**"WHERE THIS STANDS"** at the end for the consolidated state of the dataset.
The dated passes supersede each other, and early entries contain conclusions that
later passes corrected — deliberately left visible, because a research log that
only records the times you were right is not a research record.

---

## Setup, about 15 minutes

1. **Free CourtListener token** at courtlistener.com → `export COURTLISTENER_TOKEN=...`
2. **Install the RECAP browser extension.** Every PACER document you pull then
   flows back into the free archive — which is also what keeps your own
   citations stable and free for whoever cites you.
3. `pip install requests && python collect.py`
4. **Set the search alert** (instructions at the bottom of `collect.py`):
   save `"Federal Rule of Civil Procedure 16.1"` as a daily RECAP alert.
5. **Reconcile the universe against the JPML's monthly PDF** —
   https://www.jpml.uscourts.gov/pending-mdls-0 — every month, and log the date.
   *This was done on 2026-08-11 against the August 3, 2026 report and it found an
   entire missing MDL (3170) plus a row wrongly written off as out of scope
   (3181).* Read the **DATE CLOSED** column: for a pending MDL that is the
   transfer date, and it is what puts the MDL in or out of the post-2025-12-01
   universe — not DATE FILED, which is when the petition was filed.
   **Completeness is the entire product.**
6. **Apply for a PACER fee exemption** as an NYU student researcher. You
   probably won't need it — fees are waived below $30/quarter and you'll run
   maybe $6/year — but the exemption removes the ceiling.

---

## Codebook

Every column takes one of five values — `YES`, `NO`, `NOT_ADDRESSED`,
`UNCLEAR`, `PENDING` — except the free-text fields marked *(text)*.

`NOT_ADDRESSED` means the order is silent. `NO` means the order affirmatively
declines. **That distinction is the most common coding error and it is the one
that will get the dataset attacked**, so be strict about it.

### Identity

| Column | Meaning |
|---|---|
| `mdl_no` | JPML MDL number |
| `caption`, `court`, `judge` | As they appear on the JPML list, not as reported secondhand |
| `jpml_transfer_date` | Date the JPML docketed the MDL |
| `subject_area` | Free text; keep the vocabulary small and consistent |
| `pre_effective_date` | `YES` if the MDL predates Dec. 1, 2025 but a court invoked 16.1 anyway. **Firms are split on whether the rule reaches pending MDLs and nobody has counted — this column is that count.** |

### The headline variables

| Column | Meaning |
|---|---|
| `cites_rule` | Does any order in this MDL **cite Rule 16.1 by name**? |
| `rule_role` | **What the court does with it.** `AGENDA` · `RESIDUAL` · `INCORPORATION` · `NOT_INVOKED` |
| `report_form` | `JOINT` · `SEPARATE_BY_SIDE` · `OTHER` — 16.1(b)(1) contemplates the parties "meet and submit **a** report"; not everyone orders one |

`cites_rule` was the original headline. **After coding three MDLs it is already
clear that it is the less interesting half.** All three cite the rule — and each
does something structurally different with it:

- **`AGENDA`** — the rule *is* the conference agenda. Judge Bates (MDL 3162):
  the items listed in Rule 16.1 "shall … constitute a tentative agenda," and the
  order then reproduces (b)(2)(A)–(E) and (b)(3)(A)–(G) essentially verbatim
  before adding four topics of its own.
- **`RESIDUAL`** — the court sets its own agenda and bolts the rule on as a
  catch-all. Judge Lin (MDL 3171) enumerates seventeen items, then adds "any
  topics not already listed but included in Federal Rule of Civil Procedure
  16.1(b)."
- **`INCORPORATION`** — bare reference, no enumeration at all. Judge Peterson
  (MDL 3175), in a two-page order: a joint report "that addresses each of the
  matters listed in the rule."

A binary `cites_rule` cannot see that distinction, and that distinction is the
most interesting thing in the data so far. **This is the schema iteration the
first-weekend plan predicts — it arrived at N=2, not N=3.** Expect more.

An order that does everything 16.1 contemplates without ever naming the rule is
`cites_rule = NO`, `rule_role = NOT_INVOKED`, and is a *finding*, not a failure.

### Threshold application

| Column | Rule | Meaning |
|---|---|---|
| `a_conference_held` / `a_conference_date` | 16.1(a) | Court scheduled/held an initial management conference |
| `b1_report_ordered` / `b1_report_filed_date` | 16.1(b)(1) | Court ordered parties to meet and submit a report |
| `c_order_entered` / `c_order_date` | 16.1(c) | Court entered an initial management order |

### 16.1(b)(2) — leadership and other required topics

`b2a_leadership` is the umbrella: did the report or order address whether
leadership counsel should be appointed? The sub-columns track the specific
items the rule enumerates — `b2a_timing`, `b2a_structure`,
`b2a_selection_procedure`, `b2a_periodic_review`, `b2a_responsibilities`,
`b2a_communication`, `b2a_nonleadership_limits`, `b2a_compensation`.

**The rule supplies no leadership-selection criteria at all.** What courts
actually require — applications, conflict disclosures, prior-service limits,
diversity considerations, and how it interacts with Rule 23(g) — is unmapped.
The `b2a_*` block is where that finding lives.

Then: `b2b_vacate_modify` (prior orders to vacate/modify), `b2c_conference_schedule`,
`b2d_direct_filing` (managing direct filing of new actions), `b2e_related_actions`.

### 16.1(b)(3) — initial views

`b3a_consolidated_pleadings`, `b3c_discovery`, `b3d_pretrial_motions`,
`b3e_settlement_facilitation`, `b3f_magistrate_master`, `b3g_principal_issues`.

**`b3b_factual_basis_exchange` is the contested one.** The rule requires the
report to address how and when parties exchange information about the factual
bases for claims and defenses. The defense bar pushed for **mandatory** plaintiff
fact sheets and census orders during rulemaking — **and lost**. Whether courts
are imposing them anyway is a live fight with real stakes.

Use `b3b_mechanism` *(text)* to record what was actually ordered: `census`,
`plaintiff fact sheet`, `defendant fact sheet`, `none`, or a short description.
The mechanism field is where the paper is.

### 16.1(b)(4) — the catch-all, and the expansion

| Column | Meaning |
|---|---|
| `b4_tplf_disclosure` | Did the court order third-party litigation funding disclosure? |
| `b4_tplf_scope` *(text)* | What had to be disclosed, to whom, and under what protection |
| `b4_other` *(text)* | Anything else added under the (b)(4) catch-all |

TPLF disclosure was **deliberately omitted** from Rule 16.1. Whether courts
order it anyway under "any other matter" is unmeasured — and the **April 14,
2026 Advisory Committee agenda book** shows Judge Vance's TPLF subcommittee
actively soliciting exactly this data.

**Code these from day one even when the answer is `NOT_ADDRESSED`.** If the
answer turns out to be "yes, frequently," you already own the seed of a second,
larger dataset with a better citation path. The denominator is the finding.

### Beyond the rule

`beyond_bellwether`, `beyond_remand_timing` — the rule doesn't address either;
do orders anyway? `beyond_common_benefit_fees` — the Committee Note says defer
until "well into" proceedings; do judges defer or front-load?

### Provenance — non-negotiable

`source_doc_type`, `courtlistener_url` (free and stable — **never link PACER**),
`cl_docket_entry_id` (**the dedupe key**), `perma` (perma.cc, free through NYU's
library), `pin_cites`, `date_accessed`, `coder`, `notes`.

`pin_cites` convention: `field=doc @ page; field=doc @ page`.
**Every `YES` needs a pin cite. A `YES` without one is not yet data.**

---

## Your first weekend

| | |
|---|---|
| **Sat AM** | Token, extension, `collect.py`, alerts. Download the JPML PDF and reconcile the universe. |
| **Sat PM** | Code three MDLs end to end. You will discover the schema is wrong somewhere. Fix it now, while N=3, not at N=30. |
| **Sun** | Code the rest of the seed. ~15 MDLs is two weekends total, and that's the whole backfill — this is the advantage of a small-N universe. |
| **Then** | Weekly: review alerts, code new orders. Monthly: reconcile against the JPML PDF, log the reconciliation date, publish. |

Publish the CSV the day it's complete, even with no website. A complete CSV
with a stable URL and a suggested citation *is* the citable artifact. The site
is presentation.

---

## What the paper is

Rule 16.1 is structurally strange: the mandates run to the parties' **report**,
not to the judge. As one commentator put it, it has "lots of 'shoulds' but
practically no 'shalls'." It is the only Federal Rule with essentially no
mandatory requirement.

So the empirical question writes itself: **given a rule that commands nothing,
did anything change?**

Fifteen MDLs times roughly forty coded variables is a real dataset and a
publishable empirical note. Then:

- Deposit the CSV on **Harvard Dataverse** for a DOI, so the dataset is citable
  independently of any article and survives you losing interest in the website.
- Place the note. Given 3L timing, plan on an online supplement, a
  peer-reviewed venue, or a co-authored piece with an NYU faculty member —
  most journals took notes from 2Ls for 3L publication, so your own journal's
  slot may already be closed.
- Then work `PROTOCOL.md`'s promotion list, in order, starting with Drug &
  Device Law.

**Honest expectation:** Charlotin got cited by two circuits because judges
needed a number for a factual proposition. Judges rarely need a number about
Rule 16.1 uptake. Your citations will more likely come from firm alerts, the
Advisory Committee, and law reviews — real, but quieter, and probably not an
appellate opinion inside twelve months.

The floor, though, is a complete original dataset nobody else has, a
publishable note, and a DOI. That floor is better than the alternative you were
weighing, which was just the note.

---

## Findings log

Kept here so the paper's argument accumulates as you code rather than being
reconstructed at the end. Update it every session. **These are N=3 observations,
not results** — they are hypotheses to test against the full universe.

**As of 2026-08-11 · 10 of 15 dockets reviewed · 5 coded · 2 non-invoking · 4 blocked**

1. **Uptake looks high; uniformity does not.** 3/3 cite Rule 16.1 by name. But
   `rule_role` splits 3 ways across 3 MDLs — AGENDA, RESIDUAL, INCORPORATION.
   If that variance holds, the paper's finding is not "did judges adopt the
   rule" but **"the rule was adopted three different ways, and the differences
   are consequential."** That is a better paper than a compliance count.

2. **Nobody has ordered a census or plaintiff fact sheet.** 0/3. Bates *asked*
   whether "an initial census or some similar process would be beneficial"
   (¶5(o)) without ordering one. Lin **inverted** it — no plaintiff fact sheet,
   but ¶11 orders *Defendant* to build the case inventory: every member and
   tag-along action charted by law firm, incident state, plaintiff residence,
   alleged incident type, and posture, filed as an Excel. Given that the defense
   bar pushed for mandatory plaintiff-side vetting during rulemaking and lost,
   a defendant-side inventory order is a genuinely unexpected result.

3. **TPLF is 0/3.** No court has ordered litigation-funding disclosure under the
   (b)(4) catch-all. Early, but if this holds it is itself the answer to the
   question Judge Vance's subcommittee is asking — and a clean, citable null.

4. **Two of three judges independently added a government-investigation topic
   the rule does not contain.** Bates ¶5(p) (ongoing criminal investigations,
   may be filed ex parte and under seal); Peterson (status of related DOJ and
   other government investigations and their effect on the proceedings). If this
   recurs, it is a concrete, well-evidenced suggestion to the Advisory Committee
   — the kind of thing that gets a dataset cited in an agenda book.

5. **Common benefit fees are being front-loaded, contra the Committee Note.**
   The Note advises deferring "until well into" proceedings. Lin put a "potential
   common benefit fund approach" into the *lead counsel application* case plan;
   Peterson's June 8 leadership order adopts management of common benefit time
   and expenses. 2/3.

6. **16.1(b)(1) says "a report." Lin ordered two** — separate consolidated
   statements, one per side. Watch whether `report_form` diverges further; it is
   the cleanest textual-compliance variable in the schema.

### Coded rows are worked examples
3162, 3171, and 3175 are fully coded with pin cites. Use them as the reference
for how tight `pin_cites` should be and where the `NOT_ADDRESSED` / `UNCLEAR`
line falls before you code the remaining twelve.

### Update — 9 dockets reviewed

**7. Uptake has a bar side, and nobody is counting it.** In MDL 3179 (Fire
Apparatus) the court's order reads as an ordinary status conference — propose
dates for a telephonic hearing, confer on lead and liaison counsel — with no
mention of Rule 16.1 and no report ordered on the rule's topics. But on May 8,
2026 the Zelle/AMC/Cotchett plaintiffs invoked it directly in a contested
leadership fight: *"Federal Rule of Civil Procedure 16.1(b)(2)(A), enacted last
December, encourages MDL transferee courts to appoint leadership counsel."*

That is a new variable — `party_invoked_rule` — and a genuinely different
measure of whether a rule is doing work. A rule the bar cites in briefing is
operating even where no judge has invoked it. **No firm alert and no existing
survey measures this.** Worth back-coding across every MDL, including the ones
where the court plainly did invoke the rule.

Note also the coding discipline this required: the party's characterization —
that the subsection "encourages courts to appoint leadership counsel" — is a
party's framing, and by its terms (b)(2)(A) requires the parties' *report* to
address whether leadership counsel should be appointed. That distinction is
recorded in `notes` and left unadjudicated. Do not correct litigants in your
own dataset.

**8. Rule 16.1 has a category of case it simply does not reach.** MDL 3176
(Rare Breed Triggers, patent) has no conference order four months in; the master
docket is administratively reserved for transfer orders while the parties fight
a consolidated preliminary injunction. Watch whether the negatives cluster by
subject matter — patent and other injunction-driven MDLs may be systematically
outside the rule's practical scope. If so, that is a finding about the rule's
design, not about individual judges.

**9. The block rate is worse than first measured and is trending up: 4 of 9
(44%).** MDL 3166 (Roblox), 3167 (Broiler Chicken), 3172 (Cartiva), and 3179
(Fire Apparatus) all have their key order missing a RECAP text layer. Cartiva is
the worst — even its later docket entries have empty descriptions.

Three implications, sharper than before:

- **Roughly half this project is a PACER retrieval exercise, not a reading
  exercise.** Plan the time and the fee exemption accordingly.
- **A search-based version of this dataset would be close to worthless.** All
  four blocked MDLs are invisible to the precision query. Anyone building this
  from search results would have silently recorded four of nine as non-citing —
  and would have missed the Fire Apparatus bar-side invocation entirely, since
  it surfaced only from a party's *status report*, not any order.
- **This is the project's real moat.** The reason nobody has built this is that
  it cannot be built from a search index. That is precisely why it is worth
  building, and why "complete" is a claim only you will be able to make.

### Update — 10 dockets reviewed

**10. A fifth posture: the minimalist rider.** MDL 3178 (ByHeart, Judge
Subramanian) ordered a joint letter covering **three items** where the rule
enumerates twelve — a non-argumentative summary of the member cases, views on
next steps including lead counsel selection, and availability for a hearing.
It was issued as a rider to a discovery-motion ruling, not as a standalone
initial management order, and it never mentions Rule 16.1.

Coded `NOT_ADDRESSED` and `NOT_INVOKED`, not `NO` — silence is not refusal.
That gives the emerging distribution five shapes across ten dockets: agenda,
residual, incorporation, transcription, and now minimalist rider. **The variance
is the finding, and it is holding.**

**11. New `source_status` value: `TEXT_ORDER_ON_DOCKET`.** Some orders have no
separate PDF because the docket entry *is* the complete order — signed, SO
ORDERED, substantive. Guardrail 3 (a clerk's entry is not the order) does not
bite here, because this is not a clerk's summary of an order; it is the order.
Distinguish it from `NEEDS_PACER_PULL`. Conflating the two would either
understate your coverage or overstate your sourcing, depending on direction.

**12. I was wrong about MDL 3163, and the seed was right.** I previously flagged
that row as possibly conflated with MDL 3094. It is not. MDL No. 3163 is the
NAION-specific GLP-1 MDL (JPML docket 71180992); MDL 3094 is the separate,
general GLP-1 products liability MDL — **before the same judge**, which is what
tripped me. The seed row was correct.

Two lessons worth keeping. First, adjacent MDLs before the same judge on related
subject matter are a live conflation risk; check the JPML docket number, never
the caption or the judge. Second, log corrections to your own corrections. A
findings log that only records the times you were right is not a research
record.

One open item on that row: a second E.D. Pa. docket exists, `2:01-md-03163`
"(Streamlined Docket)," alongside `2:25-md-03163`. Determine which carries the
initial management order before coding.

**13. MDL 3181 may not belong in the universe at all.** Its JPML docket opened
Feb. 20, 2026 and reads **"Not Assigned"** — no transferee court designated on
that record. The seed's 2026-07-01 transfer date is unverified. If no transferee
court has been designated, there is no court that could hold a 16.1 conference
and the row is out of scope. This is exactly what the JPML reconciliation is
for.

---

# FIRST PASS COMPLETE — 2026-08-11

All 15 seed dockets reviewed. Here is where the project actually stands.

## Coverage

| | |
|---|---|
| MDLs in universe | **14** (3181 scope-questionable — JPML docket reads "Not Assigned") |
| Court posture established | **6** |
| Blocked pending PACER retrieval | **8** |
| **Block rate** | **57%** |

The block rate rose at every stage of review — 29%, then 44%, now 57%. It did
not improve with familiarity. **Treat 50–60% as the planning assumption.**

## What the six codeable MDLs show

| MDL | Judge | Posture | Report form |
|---|---|---|---|
| 3162 | Bates | `AGENDA` — rule *is* the agenda, reproduced verbatim, plus 4 added topics | JOINT |
| 3171 | Lin | `RESIDUAL` — own 17-item list, rule as catch-all | **SEPARATE_BY_SIDE** |
| 3174 | Robart | `TRANSCRIPTION` — rule reproduced with its own subsection labels, nothing added | JOINT |
| 3175 | Peterson | `INCORPORATION` — bare reference, no enumeration | JOINT |
| 3176 | Mazzant | `NOT_INVOKED` — no conference order at all, 4 months in | — |
| 3178 | Subramanian | `NOT_INVOKED` — 3-item joint letter as a rider to a discovery ruling | JOINT |

**Six MDLs, six different postures. Not one pair is alike.** Four invoke the
rule and do four different things with it; two do not invoke it at all, for two
different reasons — one has no order, one has a minimalist substitute.

If that variance survives contact with the other eight, the paper is not a
compliance count. It is: **a rule with no mandatory requirement produced no
common practice.** That is a finding about rule design, and it is directly
responsive to what the Advisory Committee will want to know.

## Cross-cutting counts (n=5 with orders)

- **Census or plaintiff fact sheet ordered: 0/5.** Bates asked whether one
  "would be beneficial." Lin inverted it onto the defendant. Nobody ordered one
  from plaintiffs. The defense bar lost this in rulemaking and has not won it
  back in practice.
- **TPLF disclosure under (b)(4): 0/5.** A clean null so far, and the null is
  the answer to what Judge Vance's subcommittee is asking.
- **Common benefit fees front-loaded, contra the Committee Note: 2/5** (Lin,
  Peterson).
- **Government-investigation topic added though absent from the rule: 2/5**
  (Bates, Peterson).
- **Report form:** JOINT 4, SEPARATE_BY_SIDE 1. 16.1(b)(1) says "a report."
- **Bar-side invocation: 1 confirmed** (MDL 3179), in a contested leadership
  fight, in an MDL where the court had *not* invoked the rule. Needs
  back-coding across all rows.

## The PACER queue, in priority order

Earliest orders first — the early ones are the most interesting, because they
show what judges did before any practice had settled.

1. **3166 Roblox** — PTO No. 1, **Dec. 17, 2025**, 16 days post-effective-date.
   Earliest located. Chief Judge Seeborg.
2. **3163 GLP-1 NAION** — CMO No. 1, **Dec. 23, 2025**. Second-earliest, and a
   pharma products liability MDL — the paradigm case the rule was written for.
3. **3167 Broiler Chicken** — MDL PTO No. 1, Dec. 31, 2025.
4. **3172 Cartiva** — Order Upon Transfer, Feb. 18, 2026.
5. **3179 Fire Apparatus** — Order for Telephone Conference, Apr. 10, 2026.
   Already has confirmed bar-side invocation.
6. **3185 Cognizant/TriZetto** — two orders, June 11, 2026. Both truncate to
   "SEE ORDER FOR DETAILS," and the suggested-topics list is the whole question.
7. **3180 Dupixent** — full docket sheet purchase; all 8 entries empty.
8. **3187 NPK Fertilizer** — full docket sheet purchase; all 104 entries empty.

Items 1–6 are single-document pulls, capped at $3.00 each. Items 7–8 need
docket sheets. Total well under the $30/quarter waiver threshold.

## The two things only you can do next

1. **The PACER pulls.** Eight documents. This is the binding constraint on the
   entire dataset and no amount of further public-source work moves it.
2. **The JPML reconciliation.** Download the *Pending MDL Dockets By MDL Number*
   PDF and resolve the sequence gaps (3164, 3165, 3168–3170, 3173, 3177,
   3182–3184, 3186) plus the 3181 scope question. Until that is done, "complete"
   is not a claim you can make — and completeness is the entire product.

---

# SECOND PASS — 2026-08-11 (later same day)

The first pass ended at a 57% block rate and a declared impasse. It was wrong to
stop there. A retrieval technique described in `PROTOCOL.md` (Guardrail 4)
unblocked five of the eight blocked rows. The numbers below supersede the first-pass
table.

## Coverage, revised

| | |
|---|---|
| MDLs in universe | **14** (3181 scope-questionable — JPML docket reads "Not Assigned") |
| Readable initial order in hand | **10** |
| No qualifying order yet (a finding, not a gap) | **1** (3176) |
| Blocked pending PACER retrieval | **3** (3167, 3180, 3187) |
| **Block rate** | **21%**, down from 57% |

`NEEDS_PACER_PULL` and `NO_ORDER_YET` remain separate and must never be summed.

## THE HEADLINE NUMBER, AND IT REVERSED

**4 of 10 MDLs with a readable initial order cite Fed. R. Civ. P. 16.1. Six
never mention it.**

The first three rows coded said 3/3. That was not a small sample — it was a
**biased** one, and the bias is structural: those three rows came from the
precision full-text query `"Federal Rule of Civil Procedure 16.1"`, so by
construction every MDL it returned cites the rule. Docket-by-docket review over
the JPML universe moved uptake from 100% to 40%.

That is the most citable thing in this project so far, and it is a finding about
*method*, not just about Rule 16.1:

> Any measurement of rule uptake built from full-text search of court documents
> will report near-total uptake, because the search can only find the documents
> that use the phrase. Measuring non-adoption requires enumerating the universe
> first and reading every docket in it — including the documents that have no
> text layer and therefore cannot be searched at all.

Firm alerts saying "courts have taken varied approaches" are built from search.
None of them can see the 60%.

## Ten MDLs, ten different postures

| MDL | Judge | Cites 16.1 | Posture | Report form |
|---|---|---|---|---|
| 3162 | Bates (D.D.C.) | YES | `AGENDA` — rule *is* the agenda, verbatim, +4 topics | JOINT |
| 3171 | Lin (N.D. Cal.) | YES | `RESIDUAL` — own 17-item list, rule as catch-all | SEPARATE_BY_SIDE |
| 3174 | Robart (W.D. Wash.) | YES | `TRANSCRIPTION` — rule reproduced with its own labels | JOINT |
| 3175 | Peterson (W.D. Wis.) | YES | `INCORPORATION` — bare reference, no enumeration | JOINT |
| 3163 | Marston (E.D. Pa.) | no | `NOT_INVOKED` — richest order in the set; court-initiated census | SEPARATE_BY_PARTY_GROUP |
| 3166 | Seeborg (N.D. Cal.) | no | `NOT_INVOKED` — N.D. Cal. form order, 12 topics tracking (b) | SEPARATE_BY_SIDE |
| 3172 | Baker (E.D. Ark.) | no | `NOT_INVOKED` — designates the **MCL 4th** as its framework | SEPARATE_BY_SIDE |
| 3178 | Subramanian (S.D.N.Y.) | no | `NOT_INVOKED` — 3-item joint letter as a rider to a discovery ruling | JOINT |
| 3179 | Griesbach (E.D. Wis.) | no | `NOT_INVOKED` — one page; report required **only on disagreement** | **CONDITIONAL_ON_DISAGREEMENT** |
| 3185 | Ross (E.D. Mo.) | no | `NOT_INVOKED` — 7 topics; asks about scheduling a **"Rule 16"** conference | SEPARATE_BY_SIDE |
| 3176 | Mazzant (E.D. Tex.) | — | `NOT_INVOKED` — no conference order at all, 4+ months in | — |

**Ten readable orders. No two alike.** The thesis from the first pass holds and
strengthens: *a rule with no mandatory requirement produced no common practice.*

## Findings log, continued

**14. THE COMPETING AUTHORITY (MDL 3172).** Judge Baker's Order Upon Transfer,
entered February 18, 2026 — eleven weeks after Rule 16.1 took effect — states:
*"The Court will be guided by the Manual for Complex Litigation, Fourth,
approved by the Judicial Conference of the United States. Counsel are directed
to familiarize themselves with that publication."* It is the only order in the
set that names a governing framework for MDL management, and the framework it
names is not the rule. Rule 16.1's Committee Note draws on MCL practice; here
the MCL is designated and the rule is not mentioned. Recorded as observed.

**15. NEW SOURCE-DOCUMENT FORM: THE CHAMBERS LETTER (MDL 3172).** The operative
initial-conference document is ECF 15 — a signed letter on chambers letterhead
("Dear Counsel: … Sincerely, Kristine G. Baker"), docketed as an order. It sets
the conference, orders leadership proposals, sets page limits, and requests a
procedural-posture summary. **Any collection method keyed to captions containing
"Order" misses it entirely.** Add letters, notices, and minute entries to the
retrieval net.

**16. THE OFF-DOCKET REPORT — the most serious methodological threat found so
far.** Two of ten courts route the 16.1(b)(1)-equivalent submission to chambers
email rather than the docket:

- MDL 3163 (Marston): position statements go to `PAED_MDL_GLP1_RA@paed.uscourts.gov`
  and *"should not be filed."*
- MDL 3172 (Baker): leadership proposals and procedural-posture summaries
  *"should be submitted only by email to KGBchambers@ared.uscourts.gov."*

If this generalizes, **the content of Rule 16.1 reports is systematically
unobservable to docket research — including this project.** The orders remain
observable; the reports do not. This limitation must be stated on the landing
page, not buried. It is also, in itself, a finding worth reporting to the
Advisory Committee: a rule whose only mandates run to the parties' report has
produced reports that in some districts leave no public record at all.

**17. THE CONDITIONAL REPORT — new `report_form` value (MDL 3179).** Rule
16.1(b)(1) contemplates that the parties meet and submit a report. Judge
Griesbach requires one **only if leadership talks fail**: *"In the event counsel
for the plaintiffs are unable to reach agreement, counsel for each of the
plaintiffs shall submit a status report …"* Agreement extinguishes the report.
Coded `CONDITIONAL_ON_DISAGREEMENT`. That is structurally different from JOINT
or SEPARATE_BY_SIDE and the vocabulary now carries four values plus
`SEPARATE_BY_PARTY_GROUP`.

**18. THE WRONG-RULE TELL (MDL 3185).** Judge Ross's seventh agenda topic asks
the parties to address *"[t]he scheduling of a Rule 16 conference, if
necessary."* Rule 16.1(a) is the MDL-specific initial management conference;
plain Rule 16(b) is the ordinary-case scheduling conference the MDL rule was
written to supplement. Recorded as observed, with no inference about awareness —
and note that 16.1(a) is itself permissive ("the court **should** schedule"), so
"if necessary" is not inconsistent with the rule. Judge Griesbach's order in
MDL 3179 likewise uses the Rule 16(b) term *"case management plan"* rather than
Rule 16.1(c)'s *"initial management order,"* and imports Rule 1's *"just,
speedy, and inexpensive"* language. **Track which rule's vocabulary an order
speaks in, separately from whether it cites 16.1.**

**19. LENGTH VARIES BY AT LEAST 3x AMONG MEASURED ORDERS.** Character counts of
the initial management documents measured so far: MDL 3179 (Griesbach) **1,995**;
MDL 3185 (Ross) **3,501**; MDL 3172 (Baker) **6,092** + **6,684** across two
documents. The transcription-type orders (Bates, Robart) are longer still and
have not been measured. Length range is a reportable measure of non-uniformity
in its own right, and it is trivially reproducible.

**20. FIRST EXPLICIT COMPENSATION ITEM, IN A NON-CITING ORDER (MDL 3172).**
Judge Baker's letter asks the leadership proposal to address *"the proposed fee
and compensation structure."* That is the clearest analogue yet to the
16.1(b)(2)(A) compensation item — in an order that never cites the rule. It
sharpens finding 1: courts are doing the rule's work without the rule's name,
which means `cites_rule` alone would badly misdescribe practice.

**21. TWO-DOCUMENT PATTERN AND A 28-WEEK GAP (MDL 3172).** Transfer docketed
Feb. 9; administrative Order Upon Transfer Feb. 18; conference-setting letter
June 22; conference Aug. 26. The administrative order and the substantive
conference document are four months apart. **The coding unit cannot be "the
first order" — it has to be "the first order that does 16.1(a)/(b) work,"** and
in some MDLs that document does not exist for months. Time-to-initial-conference
is worth its own column.

**22. STALE CROSS-REFERENCES SURVIVE IN FORM ORDERS (MDL 3172).** ECF 5 ¶7
authorizes liaison counsel to receive Panel orders *"pursuant to Rule 8(e) of the
Panel's Rules of Procedure."* ECF 15 repeats the sentence citing *"Rule 4.1."*
Rule 4.1 is current; Rule 8(e) is from the pre-2011 JPML rules. Recorded as
observed. Whether template inheritance explains non-citation of Rule 16.1 is a
**hypothesis**, not a coded value — it belongs in the paper's discussion, never
in the CSV.

**23. MDL 3180 IS CONFIRMED BLOCKED, NOT ORDERLESS.** Direct enumeration of the
D.N.J. master docket shows seven entries, zero available in RECAP, and ECF 3
(June 11, 2026) is an order setting hearings. The row stays `NEEDS_PACER_PULL`.
One PACER pull of `pacer_doc_id` 119024034589 closes it. This is what the
`source_status` distinction is for.

## What to do next, in order

1. **Three PACER pulls close the dataset**: MDL 3180 ECF 3, MDL 3187, MDL 3167
   ECF 11. Total cost under $1 and free under the $30/quarter waiver. Install
   RECAP first so the text lands in the public archive.
2. **Reconcile against the JPML monthly PDF.** The seed's ceiling is 3187 and a
   search incidentally surfaced **MDL 3193 (Epic Systems)** — so the universe is
   already larger than the seed. Sequence gaps remain at 3164, 3165, 3168–3170,
   3173, 3177, 3182–3184, 3186. Resolve 3181's "Not Assigned" status.
3. **Back-code `party_invoked_rule`** across every row. MDL 3179's bar-side
   invocation is currently held at `NOT_CHECKED` because the pin cite was not
   captured — do not code it `YES` from memory.
4. **Add columns** the second pass earned: `order_char_count`,
   `days_transfer_to_conference`, `rule_vocabulary` (16.1 / 16 / MCL / Rule 1),
   `report_channel` (docket / chambers email).
5. Only then write. The note's spine is now: *search-based measurement reports
   100% uptake; universe-based measurement reports 40%; and the 60% is doing the
   rule's work under other names.*

---

# THIRD PASS — 2026-08-11 · JPML RECONCILIATION + THE REPORT LAYER

Two things happened in this pass that change the project's shape.

## 1. The universe was wrong, and the JPML report fixed it

Reconciled against the JPML's authoritative
**Pending MDL Dockets By MDL Number, report date August 3, 2026**
(`jpml.uscourts.gov/sites/jpml/files/Pending_MDL_Dockets_By_MDL_Number-August-3-2026.pdf`).

Four corrections, each of which would have been a defect in a published dataset:

**a. MDL 3170 was missing entirely — and it is one of the best rows in the set.**
*In re Trans Union, LLC, Customer Data Security Breach Litigation*, N.D. Ill.,
Judge Robert W. Gettleman, transferred **December 16, 2025**. A docket-research
seed missed a whole in-scope MDL. Note the tell: its master docket is
`1:25-cv-10320`, a **-cv-** number, not **-md-**. Any collection method keyed to
MDL-style docket numbers misses it.

**b. MDL 3181 is in scope; my earlier "may not belong in the universe" call was
backwards.** Its JPML docket read "Not Assigned" because **the petition had not
been decided yet**. The Panel created the MDL on June 5, 2026 and assigned it to
**Judge Josephine L. Staton, C.D. Cal.**, master docket `2:26-ml-3181` — note
C.D. Cal. uses a **-ml-** prefix. *"Not Assigned" means undecided, not phantom.*

**c. The sequence gaps are not gaps.** 3164, 3165, 3168, 3169, 3173, 3177,
3182–3184 and 3186 do not appear on the pending-MDL report at all. They are JPML
docket numbers assigned to **petitions that were denied or withdrawn**. Confirmed
independently from inside a party filing: counsel in MDL 3170 describes having
"filed briefs in MDL 3164 as well as MDL 3170" — 3164 was a competing petition in
the same litigation. **A JPML "MDL No." is a docket number for a motion, not
proof an MDL exists.** The same correction retires my earlier claim that MDL 3193
(Epic Systems) enlarged the universe — 3193 is a pending petition; the highest
actual MDL on the August 3 report is **3187**.

**d. 3160 and 3161 exist but are out of the primary denominator.** *Archery
Products Antitrust* (D. Colo., Brimmer) and *CCell* (N.D. Cal., Chhabria) were
transferred October 16 and October 1, 2025 — **before** Rule 16.1 took effect.
They belong under the `PRE_EFFECTIVE_DATE` flag if a court there invoked the rule
anyway, not in the main count.

**The universe is 16 post-effective-date MDLs**, not the 14 or 15 the seed
implied: 3162, 3163, 3166, 3167, 3170, 3171, 3172, 3174, 3175, 3176, 3178, 3179,
3180, 3181, 3185, 3187.

| | |
|---|---|
| MDLs in universe | **16** |
| Readable order in hand | **12** |
| No qualifying order yet | **1** (3176) |
| Not yet reviewed | **1** (3181, created June 2026) |
| Blocked pending PACER retrieval | **2** (3180, 3187) |
| **Block rate** | **13%**, down from 57% |

**Headline, revised again: 6 of 13 MDLs with a readable initial order cite
Fed. R. Civ. P. 16.1. Seven never mention it.**

## 2. MDL 3170 is the model order — and it drops exactly one item

Judge Gettleman entered two orders the same day, December 18, 2025. **CMO #2 is
two pages and is the most faithful Rule 16.1 order located anywhere in the set:**

> "Pursuant to Fed. R. Civ. P. 16.1, the parties are directed to meet and confer
> and submit a report addressing the parties' views on the following matters:"

Then it reproduces **seventeen of the rule's eighteen enumerated report topics** —
all seven leadership sub-items of 16.1(b)(2)(A)(i)–(vii), all four of (b)(2)(B)–(E),
and six of the seven in (b)(3). It adds nothing of its own. It is the first row in
the dataset where every one of the eight `b2a_*` leadership columns codes `YES`,
and that happened *because the judge copied the rule instead of writing his own list.*

**The one item it omits is 16.1(b)(3)(E) — measures to facilitate resolution.**
Coded `NOT_ADDRESSED`, never `NO`: an omission from a transcription is silence,
not refusal. But it is precise, checkable, and it is the **second defect in a
transcription-type order**: Judge Robart's order in MDL 3174 labels the permissive
catch-all "16.1(b)(3)" when it is (b)(4).

**24. TRANSCRIPTION IS ERROR-PRONE — 2 of 2.** Both orders that reproduce the
rule contain a discrepancy from its text: one drops a topic, one mislabels a
subsection. That is a specific, non-accusatory, actionable suggestion to the
Advisory Committee: **publish an official model Rule 16.1 order or checklist.**
Judges who want to follow the rule closely are transcribing it by hand, and hand
transcription introduces errors. This is the kind of finding a rules committee can
act on, which is exactly the citation path PROTOCOL identifies as highest-value.

**25. FIRST DIRECT-FILING PROCEDURE ACTUALLY ORDERED.** Everywhere else,
16.1(b)(2)(D) appears as a *topic*. Gettleman's CMO #1 ¶6 *establishes the
procedure*: any plaintiff whose case would be subject to transfer "may file their
case directly in the United States District Court for the Northern District of
Illinois, noting on the civil cover sheet that the case is related to Case Number
25 CV 10320 and MDL No. 3170," on payment of the standard fee.

**26. SECOND DATE TYPO.** CMO #2, signed December 18, **2025**, sets the report
deadline as "January 15, **2025**" and the hearing as "January 27, **2025**" —
both a year in the past. MDL 3163's order carries the same class of error. Two of
twelve orders contain a year error in the Rule 16.1 report deadline. Recorded as
observed; the CSV records the evidently intended 2026 dates and `pin_cites`
preserves what the documents say. **Anyone computing intervals from order text
needs to know this.**

---

## 3. THE REPORT LAYER — a second dataset, and it may be the better one

MDL 3170 ECF 33 is captioned **"FED. R. CIV. P. 16.1 REPORT."** Thirteen pages,
filed January 5, 2026, on the public docket. It is the **first actual Rule 16.1
report** located in this project, and reading it reframes what this dataset should
measure.

Rule 16.1's only real mandates run to *the parties' report*. Every finding so far
has been about **orders** — the half of the rule that commands nothing. The
reports are where the rule actually bites, and at least some of them are on the
docket and searchable by their own caption.

**27. THE SINGLE-REPORT MECHANISM FAILED, ON THE RECORD, IN WEEK SIX.** The court
ordered one joint report per 16.1(b)(1). What was filed: a **one-paragraph Joint
Status Report** and, the same day, this **13-page unilateral report**. Counsel
quotes the Committee Note's own words — *"This should be a single report, but it
may reflect the parties' divergent views on these matters"* — and states plainly:
*"The Snelgrove Plaintiffs were unable to achieve this despite efforts to confer
with Defendant's and other Plaintiffs' counsel."*

**28. COUNSEL DISAGREED ON THE RECORD ABOUT WHAT COMPLIANCE MEANS.** This is the
best single piece of evidence in the project for the paper's thesis:

> *"Although other counsel may not agree that a robust approach to this Report was
> necessary, in an abundance of caution, the Snelgrove Plaintiffs submit this
> Report detailing a response to each of the requirements in Rule 16.1 …"*
>
> *"CVN explained that it believed the truncated report did not comply with the
> Court's CMO #2. CVN explained that CMO #2 appears to require a much more robust
> discussion of each of the subparts therein."*

A rule of "shoulds" produced a documented, on-the-docket fight between counsel
about how much the rule requires — one paragraph or thirteen pages. **That is what
"no shalls" looks like in practice**, and no firm alert has it.

**29. THE ADVISORY COMMITTEE NOTE IS OPERATIVE AUTHORITY, AND SO IS THE
RULEMAKING RECORD.** The report quotes the Note four times (single report;
"appointment of leadership counsel is not universally needed"; committee structure
under (b)(2)(A)(ii); MDL websites). Footnote 4 goes further and cites **written
testimony submitted to the Committee on Rules of Practice and Procedure on
January 16, 2025 about the *proposed* rule.** The rulemaking record is being
briefed as interpretive material within weeks of the effective date. Worth its own
column: `cites_committee_note`, `cites_rulemaking_record`.

**30. THE BAR FILLS THE RULE'S SILENCE WITH THE MANUAL — same as the bench.** The
report cites Manual for Complex Litigation, Fourth §§ 10.221, 14.211–14.216,
21.11, 21.272, 40.22 and 40.23, plus the Third Circuit Task Force on the Selection
of Class Counsel Final Report (2002). Judge Baker's order in MDL 3172 designates
the Manual as the court's framework. **Court side and bar side independently reach
for the same pre-16.1 authority.** If that holds across the universe, the finding
is not that Rule 16.1 was ignored — it is that **Rule 16.1 did not displace the
Manual**, which is a much more interesting claim and one the Committee will care
about.

**31. THE COURT'S OMISSION PROPAGATED INTO THE REPORT.** The report's numbered
sections track CMO #2 one-for-one, so it likewise has no section answering
16.1(b)(3)(E). Resolution issues surface anyway — a proposed special master for
settlement, settlement approval motions, deferred compensation pending the
litigation's trajectory — so the topic was not lost, only unhoused. Stated as
observed. But it suggests a testable mechanism: **the parties answer the questions
the order asks, so a transcription error in the order becomes a gap in the
report.**

**32. THE BAR ARGUES FOR DEFERRING COMMON BENEFIT FEES — the opposite of the
bench.** Finding 5 recorded courts front-loading common benefit compensation
contra the Committee Note (Lin, Peterson). Here plaintiffs' counsel argues the
discussion is *"probably premature at this time"* and should be *"deferred until
at least a second case management conference"* — taking the Note's position
against a court-side trend. Front-loading may be judge-driven, not bar-driven.

### What this means for the project

Add a second table, `reports.csv`, keyed to `mdl_no` + `docket_entry_id`, coding:
who filed, joint or unilateral, page count, which of the 18 topics are answered,
whether the Committee Note is cited, whether the Manual is cited, whether the
rulemaking record is cited, and whether the filing itself records a meet-and-confer
failure.

Retrieval is easier than for orders: **reports name the rule in their own docket
text.** `"STATUS Report F.R.C.P. 16.1"` was sitting in a docket-entry description
the whole time, invisible to every order-focused query I ran. Add these to
`collect.py`:

```
"Rule 16.1 Report"  ·  "F.R.C.P. 16.1"  ·  "16.1 Report"
"Fed. R. Civ. P. 16.1 Report"  ·  description:"16.1"
```

**The report layer is probably the better paper.** The orders show a rule that
commands nothing producing no common practice. The reports show what the parties
did with a rule that commands only them — including the first documented failure
of its single-report mechanism, in week six.

---

# WHERE THIS STANDS — 2026-08-11, end of day

Everything above is the working log, in order, corrections and all. This section
is the state of the dataset. **Read only this if you read only one thing.**

## Coverage

| | |
|---|---|
| Universe of post-2025-12-01 MDLs, reconciled to the JPML's Aug. 3, 2026 report | **16** |
| Readable initial order in hand and coded | **13** |
| No qualifying order yet *(a finding about the court, not a gap in the data)* | **1** — 3176 |
| Blocked pending PACER retrieval | **2** — 3180, 3187 |
| Block rate | **13%** — down from 57% |

Two PACER pulls finish the backfill. Total cost under a dollar, and free under the
$30/quarter waiver.

## The headline

**6 of 13 MDLs with a readable initial order cite Fed. R. Civ. P. 16.1.**

| Cite the rule | Do not mention it |
|---|---|
| 3162 Bates · 3167 Shelby · 3170 Gettleman · 3171 Lin · 3174 Robart · 3175 Peterson | 3163 Marston · 3166 Seeborg · 3172 Baker · 3178 Subramanian · 3179 Griesbach · 3181 Staton · 3185 Ross |

The first three rows coded said 3/3, because they came out of a full-text search
and a full-text search can only find documents that use the phrase. Enumerating
the JPML universe and reading every docket moved it to 46%.

## Cross-cutting counts, n = 13 orders

**The rule's own topics** — how often the initial order addresses each:

| 16.1 topic | Column | n |
|---|---|---|
| Leadership counsel (umbrella) | `b2a_leadership` | **13/13** |
| Discovery (b)(3)(C) | `b3c_discovery` | 11/13 |
| Additional conferences (b)(2)(C) | `b2c_conference_schedule` | 11/13 |
| Principal issues (b)(3)(G) | `b3g_principal_issues` | 11/13 |
| Related actions (b)(2)(E) | `b2e_related_actions` | 10/13 |
| Consolidated pleadings (b)(3)(A) | `b3a_consolidated_pleadings` | 10/13 |
| Pretrial motions (b)(3)(D) | `b3d_pretrial_motions` | 10/13 |
| Vacate/modify prior orders (b)(2)(B) | `b2b_vacate_modify` | 9/13 |
| Magistrate or master (b)(3)(F) | `b3f_magistrate_master` | 8/13 |
| Factual-basis exchange (b)(3)(B) | `b3b_factual_basis_exchange` | 7/13 |
| **Direct filing (b)(2)(D)** | `b2d_direct_filing` | **5/13** |
| **Facilitating resolution (b)(3)(E)** | `b3e_settlement_facilitation` | **5/13** |

Leadership is universal — every single order addresses it, including the seven
that never name the rule. The two least-addressed topics are direct filing and
settlement facilitation, at 5 of 13 each.

**The leadership sub-items** — this is where the rule is most detailed and courts
are least uniform:

| 16.1(b)(2)(A) sub-item | n |
|---|---|
| Structure (ii) | 12/13 |
| Timing (i) | 11/13 |
| Selection procedure (iii) | 11/13 |
| Responsibilities (iv) | 9/13 |
| **Compensation (vii)** | **8/13** |
| Communication with nonleadership (v) | 6/13 |
| Limits on nonleadership (vi) | 5/13 |
| **Periodic review (iii)** | **4/13** |

**The contested and the null:**

- **TPLF disclosure under (b)(4): 0/13.** Still a clean null, and the null is the
  answer to what Judge Vance's subcommittee is asking.
- **Census or plaintiff fact sheet: still nobody has ordered one from
  plaintiffs.** Marston is closest — a **court-initiated** census inquiry. Lin
  inverted it onto the defendant. The defense bar lost this in rulemaking and has
  not won it back in practice.
- **Bellwether: 1/13.** The rule says nothing about bellwethers and neither, so
  far, do the courts.
- **Common benefit fees front-loaded contra the Committee Note: 4/13** — Marston,
  Lin, Peterson, Staton. (Baker's MDL 3172 asks for a "proposed fee and
  compensation structure" and is coded `UNCLEAR`, not `YES` — it does not say
  whether a common-benefit assessment is contemplated.) Staton's is the most explicit: applicants must state
  the percentages they expect to seek from a common fund. Meanwhile, in MDL 3170
  plaintiffs' counsel argues *for* the Note's deferral position. **Front-loading
  looks judge-driven, not bar-driven.**

## Time from transfer to initial conference — a 9x spread

| Days | MDL | Judge |
|---:|---|---|
| 21 | 3185 | Ross |
| 29 | 3163 | Marston |
| 42 | 3170 | Gettleman |
| 48 | 3171 | Lin |
| 49 | 3166 | Seeborg |
| 61 | 3181 | Staton |
| 65 | 3167 | Shelby |
| 84 | 3175 | Peterson |
| 105 | 3162 | Bates |
| 126 | 3174 | Robart |
| **198** | 3172 | Baker |

Rule 16.1(a) says the court "should schedule an initial management conference"
and sets no time. Practice ranges from three weeks to twenty-eight. **This is the
cleanest single number in the dataset**: one variable, no coding judgment, and it
answers a question the rule left completely open.

## What the whole thing says

Three claims the data now supports, in ascending order of interest:

1. **A rule with no mandatory requirement produced no common practice.** Thirteen
   readable orders, thirteen distinguishable approaches, a 9x spread in
   time-to-conference and a 3x+ spread in order length.

2. **Search-based measurement of rule uptake is systematically biased upward.**
   It reports ~100%; universe-based measurement reports 46%. That is a finding
   about method that applies far beyond Rule 16.1.

3. **The most likely story is not that Rule 16.1 was ignored — it is that Rule
   16.1 did not displace the Manual for Complex Litigation.** Judge Baker
   designates the MCL as the court's framework (MDL 3172); Judge Staton tells
   counsel to be familiar with it (MDL 3181); plaintiffs' counsel briefs six
   different MCL sections in the first located Rule 16.1 report (MDL 3170). Bench
   and bar, three districts, independently. Every order that never cites the rule
   still does the rule's work — under the Manual's name, or under no name at all.

And one thing the report layer says that the orders cannot: **the rule's single
report mechanism failed on the record in week six**, in MDL 3170, with counsel
quoting the Committee Note while explaining why they could not comply with it.

## The four things to do next

1. **Two PACER pulls** — MDL 3180 ECF 3 (`pacer_doc_id` 119024034589) and MDL
   3187's initial order. Install RECAP first so the text lands in the public
   archive.
2. **Build `reports.csv`.** The report layer is probably the better paper, and
   reports are easier to find than orders because they name the rule in their own
   docket text. `collect.py` now has the queries.
3. **Back-code `party_invoked_rule`** across all sixteen rows. Two are confirmed
   (3170 by document, 3179 by an earlier search whose pin cite was not captured —
   do **not** code that one `YES` from memory).
4. **Then write.** The spine: *search says 100%, the universe says 46%, and the
   54% is doing the rule's work under the Manual's name.*

---

# FOURTH PASS — 2026-08-11 · the last two rows

Pushed the retrieval ladder to its end on the two remaining blocked rows. Neither
is coded, but both moved, and one of them moved a long way.

## MDL 3180 (Dupixent, D.N.J., Quraishi) — order identified, copy located

The order is **"Initial Procedure Order," June 11, 2026, ECF 3.** A free public
copy of the court's PDF sits at

> `https://www.aboutlawsuits.com/wp-content/uploads/2026-6-11-dupixent-order-1.pdf`

That host's `robots.txt` blocks this session's fetcher, so I have not read it —
but it opens normally in a browser, which is why the row is now
`PUBLIC_COPY_LOCATED` rather than `NEEDS_PACER_PULL`. **Ten seconds in a browser
closes this row. No PACER account needed.**

What the secondary source reports the order does — **recorded as a lead, coded
nowhere:**

| Date | Requirement |
|---|---|
| July 24, 2026 | Parties meet and confer on the conference agenda |
| **Sept. 10, 2026** | Parties submit an **"Initial Management Report"** addressing leadership appointments, their structure, timing and periodic review; previously entered schedules and orders; scheduling of future conferences |
| **Oct. 1, 2026** | Initial case management conference |
| **Nov. 1, 2026** | Parties jointly prepare a **"proposed initial management order"** |

**33. STRONG LEAD, NOT A CODED VALUE.** "Initial Management Report" and
"initial management order" are Rule 16.1(b)(1) and 16.1(c) terms of art, and the
reported contents track 16.1(b)(2)(A)(i)–(iii), (B) and (C) in the rule's own
sequence. The sequence itself — report, then conference, then management order —
is the rule's structure exactly. **If that survives reading, MDL 3180 is a
seventh citing MDL and the headline moves from 6/13 to 7/14.** It is *not* coded
that way. `cites_rule`, `rule_role` and every `b2`/`b3` column stay `UNCLEAR`
until someone opens the PDF, because the protocol's first rule is to code from
the order and never from a description of it. This is the single highest-value
unread document in the project.

Note also the interval: 119 days from transfer to conference, second only to
MDL 3172's 198.

## MDL 3187 (NPK Fertilizer, D. Kan., Melgren) — blocked, but the block is now documented

Full docket enumeration settles the question the `source_status` distinction
exists to answer. **Four transferee-court orders exist and none is available:**

| ECF | Type | `pacer_doc_id` |
|---|---|---|
| 1 | Order + Schedule A (JPML transfer) | 07907486884 |
| **2** | **Order — the likely initial order** | **07907490590** |
| 8 | Order | 07907513132 |
| 9 | Order + 7-page Exhibit | 07907520997 |
| 10 | Order + 7-page Exhibit A | 07907521776 |

`NO_ORDER_YET` is now **affirmatively ruled out**. The court has plainly been
managing this litigation; the gap is in my collection, not in its conduct, and
this row must never be reported alongside MDL 3176's genuine `NO_ORDER_YET`.
That is a four-document shopping list for one PACER session — a few dollars at
most, and probably nothing under the quarterly waiver. Start with ECF 2.

## Routes tried and exhausted on these two

RECAP search · the duplicate-record technique · D. Kan.'s Special/MDL Cases page
and D.N.J.'s MDL Cases and Case Management Orders pages (both maintain rich
per-case order pages for older MDLs and had not added these yet) · member-case
and transferor-court dockets · news-site and firm PDF mirrors · the courts' free
`show_public_doc` CGI endpoints · Legal Data Hunter (case law only; district
management orders are not in it) · govinfo (its USCOURTS collection carries
written opinions, and case management orders are not designated as such).

**Recheck the two court pages on every monthly reconciliation.** D. Kan. clearly
builds per-case order pages for its major MDLs — EpiPen, Hill's Pet Nutrition,
Syngenta all have them — and simply has not built this one yet. A row blocked
today can be free next month, at no cost and with better provenance than PACER.

---

# FIFTH PASS — 2026-08-11 · THE INVOCATION LAYER

Ran the report-layer queries that the fourth pass added to `collect.py`. They
found more than expected, and one finding sits entirely outside the MDL
universe. New file: **`party-invocations.csv`** — four rows, keyed independently
of the order table, because a party filing is a different unit of analysis from
an order.

## 34. A SECOND RULE 16.1 REPORT — and it is the counter-example

**MDL 3162, ECF 73, March 6, 2026: "JOINT INITIAL MANAGEMENT REPORT," 49 pages,
filed by all plaintiffs and all defendants.** It is the first Rule 16.1 report in
time, and the joint-report mechanism of 16.1(b)(1) **worked**:

> "Unless otherwise noted, the positions set forth below reflect the joint
> position of undersigned counsel for the Parties. Where undersigned counsel for
> the Parties could not reach agreement, the current positions of the Parties are
> set forth separately under the labeled headings."

That is the Committee Note's design executed as written. **This materially
corrects the fourth pass.** Finding 27 reported the mechanism failing in MDL 3170
and it would have been easy — and wrong — to let that stand as the general case.
It is not. Report both.

Its seventeen headings track Judge Bates's IPO No. 1 ¶5 (A–Q). Note what is
missing: **no heading answers 16.1(b)(3)(B)**, factual-basis exchange. The nearest
thing is "G. Initial Disclosures Required by Fed. R. Civ. P. 26(a)(1)." Open
question for the next pass: did Bates's order omit (b)(3)(B), or did the parties
fold it into G/H? Either answer is interesting, and it is the same
order-to-report propagation question MDL 3170 raised.

## 35. THE REAL QUESTION THE REPORTS RAISE: negotiation document or advocacy document?

Both located reports record a dispute — but not the same dispute, and that is
what makes the pair useful:

- **MDL 3170:** the parties could not produce a joint report at all, and divided
  over *how much detail* the Rule demands. One paragraph, or thirteen pages?
- **MDL 3162:** they produced one, then divided over *what may go in it*.
  Plaintiffs' counsel objected in footnote 1 that defendants "elected to
  incorporate alleged quotations from meet and confer discussions to support
  Defendants' positions in this Initial Joint Report," and that "doing so is
  antithetical to the purpose and spirit of the meet-and-confer process."

Rule 16.1(b)(1) and the Note say the report should be single and may reflect
divergent views. **Neither says whether it is a negotiation document or an
advocacy document** — whether meet-and-confer positions are usable in it, or how
complete an answer to each topic is expected. Two of two reports fought over
exactly that. N=2 supports no generalization; it does identify a discrete
question guidance could settle at no cost.

## 36. THE CENSUS QUESTION GOT ANSWERED — jointly, and in the negative

Judge Bates is the only judge in the dataset who **asked** the parties whether a
census would be beneficial (IPO No. 1 ¶5(o)). Section O of the joint report, in
its entirety:

> "At this time, the Parties do not see the benefit or utility of conducting a
> census of the current consolidated or future filed cases."

That is a **joint** position — plaintiffs *and* defendants. The defense bar
sought mandatory plaintiff-side vetting during rulemaking and lost; in the one
MDL where a court put the question to the parties, the defense did not press for
it. This is the strongest single line the project has for the census/PFS
question, and it is the kind of concrete answer the Committee wants.

Section P: no known criminal investigations — answering Bates's other added topic.

## 37. RULE 16.1 IS BEING BRIEFED OUTSIDE SECTION 1407

**The most novel finding in the project, and no MDL-scoped study would ever see
it.** *In re FedEx Tariff Litigation*, No. 2:26-cv-02181 (W.D. Tenn.), ECF 32,
June 29, 2026 — a **single-district consolidation, not a Panel transfer**.
Counsel opposing competing leadership motions briefs Rule 16.1 as persuasive
authority, twice conceding it does not apply:

> "Although new Rule 16.1, effective December 1, 2025, governs Section 1407
> proceedings and so does not control this consolidation, its leadership
> instruction is squarely on point and reflects the considered judgment of the
> federal rulemakers …"

and treats it as interchangeable with existing authority: "[w]hether the source
is Rule 23(g)(1)(B), the Duke Guidelines, or the Rule 16.1 leadership note, the
federal standard is the same, and it is a standard of fit, not headcount." It
then urges the court to follow "the [course] the federal rulemakers have now
modeled in Rule 16.1."

**Two implications.** First, if this recurs, Rule 16.1 is becoming a general
standard for leadership appointment in aggregate litigation, well beyond §1407 —
and the order layer of this project is structurally blind to it. Second,
**every substantive proposition in that brief is sourced to the Advisory
Committee Note, not the Rule text.** Unsurprising, since the Rule supplies no
leadership-selection criteria at all. The operative content of Rule 16.1, as the
bar is using it, currently lives in the Note. The MDL 3170 report says the same
thing a different way: it quotes the Note four times and cites written testimony
submitted to the Committee on the *proposed* Rule.

**Scope consequence for the project:** `party_invoked_rule` cannot be a
per-MDL variable, because the population of party invocations is not the MDL
population. `party-invocations.csv` is keyed to the filing, not the MDL, and
carries an `mdl_no` of `NON-MDL` where appropriate.

## 38. SECOND SUBSECTION MISLABEL, THIS ONE AT THE BAR

The FedEx brief cites "Fed. R. Civ. P. 16.1(b)(3)" for the leadership provision,
which is 16.1(b)(2)(A). With Judge Robart's order in MDL 3174 carrying the (b)(3)
label onto what is (b)(4), that is **two mislabels in eight months, one on the
bench and one at the bar**, in a rule whose enumerated topics run to four levels
of subdivision. Both strengthen the model-order/checklist suggestion, though the
fix for the bar is different from the fix for the bench.

*(Careful: this is two, not three. An omission — MDL 3170 dropping (b)(3)(E) —
is not a mislabel, and the submission was corrected on that point before
sending.)*

## Running counts, updated

| | |
|---|---|
| `party_invoked_rule = YES` | **3 of 16** (3162, 3170, 3175) — 13 still `NOT_CHECKED` |
| Rule 16.1 reports located and read | **2** (3162 joint, 3170 unilateral) |
| Party invocations outside the MDL universe | **1** (*FedEx Tariff*, W.D. Tenn.) |
| Reports on the public docket | **2 of 2** located — but 2 of 13 courts route theirs off-docket |

---

# SIXTH PASS — 2026-08-11 · three verifications, and one of them cut a claim

Chased the three items `PUBLISH.md` flagged as able to move the letter. All three
resolved. One added a finding, one added a better finding than the one I was
going to make, and one killed a claim I had been about to rely on.

## 39. THE RULE'S NUMBER IS BECOMING THE NAME OF A DOCUMENT

Four instances, three MDLs, bench and bar:

| Source | Language |
|---|---|
| MDL 3167 — Judge Shelby, order | "the Rule 16.1(b) Report" |
| MDL 3170 — party filing, caption | "FED. R. CIV. P. 16.1 REPORT" |
| MDL 3175 — Judge Peterson, leadership order | "drafting the **Rule 16.1 conference report** on behalf of plaintiffs" |
| MDL 3175 — defendants' statement | "[i]n their **Rule 16.1 report**, the current parties proposed …" |

In none of these is the Rule number a citation to authority. It is the **name of
a filing**. This is the best single indicator the project has that the Rule is
embedding into practice, and `cites_rule` — a binary — scores it identically to a
citation to authority, which it is not. Now Part II.G of the submission.

## 40. MDL 3175's `c_order_cites_rule` = YES, and that is the whole story

Judge Peterson's June 8, 2026 leadership order — the 16.1(c)-analogue initial
management order — does contain "Rule 16.1." Once. Naming the parties' filing,
while crediting a leadership applicant for having drafted it. **It is the first
management order in the dataset shown to name the Rule, and it names it as a
document title rather than applying it.** Both halves of that go in the row.

## 41. A THIRD RULE 16.1 REPORT EXISTS AND CANNOT BE READ

MDL 3175 ECF 74 (doc 477258878, docketed "Status Report") — `is_available=false`,
and no copy exists on any of the ~20 member dockets. Its content is known only
because defendants quoted it three weeks later:

> "[i]n their Rule 16.1 report, the current parties proposed that … any plaintiff
> whose action would be subject to transfer to this Court as a tag-along action
> to the MDL may file directly in this MDL before this Court, without the
> necessity of first filing in another federal district court and awaiting
> transfer."

That is a substantive **16.1(b)(2)(D)** proposal, made in the report and
evidently adopted — legible only in secondhand quotation. It is the sharpest
available illustration of the point in Part V of the submission: the reports are
where the information is, and they are the part that goes missing. Added to the
PACER list.

## 42. I CHECKED THE (b)(3)(B) GAP AND THERE ISN'T ONE — the real finding is better

The fifth pass flagged that MDL 3162's joint report has no heading answering
16.1(b)(3)(B) and asked whether Judge Bates's order had omitted it. **It had not.**
IPO No. 1 ¶5(g) includes the topic and *expands* it:

> "how and when the parties will exchange information about the factual bases for
> their claims and defenses, **including whether the parties should stipulate to
> dispense with the initial disclosures required by Rule 26(a)(1) of the Federal
> Rules of Civil Procedure, and, if not, what if any changes should be made in the
> scope, form or timing of those disclosures**"

The parties answered under a heading named for the court's gloss ("Initial
Disclosures Required by Fed. R. Civ. P. 26(a)(1)") rather than the Rule's words.
So: **not a propagation gap — do not report it as one.**

What it is instead is better. **The only court that told the parties how to
operationalize the contested factual-basis-exchange topic operationalized it as a
Rule 26(a)(1) question** — keep, dispense with, or modify initial disclosures —
not as a plaintiff-vetting question. Read with Section O's joint "no census,"
the one MDL where (b)(3)(B) was actually worked through came out on Rule 26(a)(1),
not on fact sheets. That now sits in Part VII of the submission, next to the
census answer.

## 43. CORRECTION: the MDL 3179 document I suspected does not contain the string

I had flagged ECF 19 (Brief in Support of Motion to Confirm Appointment of Interim
Leadership, May 1, 2026, doc 477865692, ~60k chars) as the likely source of MDL
3179's bar-side invocation. **A full-text search of it for "16.1" returns zero
matches.** Finding 7 attributes the invocation to a May 8 filing — a week later —
and that document has not been re-identified.

`party_invoked_rule` for MDL 3179 stays `NOT_CHECKED`. This is the concrete
vindication of the rule against coding from memory: the specific document I would
have pin-cited turns out not to contain the phrase.

## Running counts

| | |
|---|---|
| Rule 16.1 reports **read** | 2 (MDL 3162 joint, MDL 3170 unilateral) |
| Rule 16.1 reports **known to exist and unreadable** | 1 (MDL 3175 ECF 74) |
| `party_invoked_rule = YES` | 3 of 16 (3162, 3170, 3175) |
| Invocations outside the MDL universe | 1 (*FedEx Tariff*, W.D. Tenn.) |
| `c_order_cites_rule = YES` | 1 of 16 (3175) — 12 still `PENDING` |
| "Rule 16.1" used as the **name of a filing** | 4 instances, 3 MDLs |

---

# SEVENTH PASS — 2026-08-11 · stopped by the daily cap, with two things learned on the way

Went after the pre-effective-date question — *has any court invoked Rule 16.1 in
an MDL created before December 1, 2025?* — and hit CourtListener's **125/day**
ceiling partway in. It resets on a rolling window, roughly eight hours out. The
question stays open, but the run was not wasted: it established how the question
has to be asked, and it exposed a flaw in the query set the project has been
relying on since day one.

## 44. THE PHRASE QUERY IS MUCH LESS PRECISE THAN IT LOOKS

Running `"Federal Rule of Civil Procedure 16.1" OR "Fed. R. Civ. P. 16.1"` with
**no** `filed_after` returns **~697 documents**, overwhelmingly plain Rule 16
scheduling orders. The index does not treat `16.1` as a token distinct from `16`,
so every order reciting "pursuant to Fed. R. Civ. P. 16" matches. The first page
is almost entirely S.D.N.Y. initial case management orders from 2017 through 2024.

**The precision this project has relied on comes substantially from
`filed_after=2025-12-01`, not from the phrase.** The rule did not exist before
that date, so the date filter is silently removing all the Rule 16 noise. That is
fine for the post-effective-date universe and it is a real limitation everywhere
else. Now Guardrail 10, and flagged as TRAP 2 at the top of `collect.py`.

Two consequences worth carrying into the published methodology:

- **State the date filter as part of the query**, not as a convenience. Anyone
  reproducing this without it gets a different and meaningless number.
- **Never report a raw hit count** from these queries as a measure of anything.

## 45. WHICH MEANS THE PRE-EFFECTIVE-DATE QUESTION NEEDS A DIFFERENT METHOD

The obvious approach — drop the date filter and see what turns up in old MDLs —
is exactly the approach that breaks. The right method inverts it, and it is now
written into `PROTOCOL.md`:

1. **Keep** `filed_after=2025-12-01`. An order *applying* Rule 16.1 must have been
   *filed* after the effective date no matter when the MDL was created.
2. Collect every unique `docket_id` in the results.
3. For each, ask one question: **was this MDL centralized before December 1,
   2025?** Cross-check against the JPML monthly report.
4. Any hit in a pre-December-2025 MDL is a `pre_effective_date = YES` row — and
   the first real datum in a dispute firms are currently arguing from intuition.
5. Any hit that is not an MDL at all goes to `party-invocations.csv` with
   `mdl_no = NON-MDL`, per the *FedEx Tariff* precedent.

Step 3 costs one API call per docket. **Budget the day around that**, because the
binding constraint on this project is now the rate limit, not the research.

## 46. RATE LIMITS ARE NOW THE PROJECT'S CRITICAL PATH

Measured, not estimated, on 2026-08-11: **5/minute · 50/hour · 125/day.** The
daily cap was reached inside one working session and resets on a rolling window.

Two batching facts that are worth real time:

- `read_document` accepts a **list** of chunk indexes, up to ten per call. Reading
  a 49-page report in four calls instead of twelve is the difference between
  finishing a document and losing the day.
- `search_document` accepts a **list** of up to ten document IDs — the cheapest
  possible way to ask "does this string appear in any of these ten filings."

A Free Law Project membership lifts all three. The project is now past the point
where that is optional.

---

## Where the open questions stand

| Open item | What it needs | Could it move the letter? |
|---|---|---|
| MDL 3180 order | One click in a browser | **Yes — 6/13 could become 7/14** |
| MDL 3187, four orders | One PACER session, ~$3 | Yes |
| MDL 3175 ECF 74 — third Rule 16.1 report | PACER | Yes — report layer N=2 → 3 |
| MDL 3179 bar-side invocation | Re-identify the May 8 filing | No, but finding 7 rests on it |
| **Pre-effective-date question** | **~1 API call per docket, tomorrow** | **Yes — an entirely new section** |
| Back-code `party_invoked_rule` (13 rows) | Bulk, low risk | No |
