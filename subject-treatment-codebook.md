# Subject-treatment codebook

**VERSION 1.1, 14 August 2026.**

**Status of v1.0:** definitions frozen 12 August 2026 after testing against five
awkward provisions (below), then used for the whole of pass 1.

**Status of v1.1:** amended after a blind second pass on 49 cells showed that pass 1
had relied on unpublished application rules. Those rules are now published in full
below, two of them changed. **v1.1 supersedes v1.0 as the coding instrument.** Every
cell in `subject-treatment.csv` was coded under v1.0 and is being re-read under v1.1.

Changes from v1.0, all dated 14 August 2026:

| | change |
|---|---|
| Unit of observation | Restated. The source document rule was already in the schema and was departed from once; the closure test is now explicit. |
| Application rules | R1 through R8 moved from a sealed working file into this codebook. |
| R3 | **Replaced.** The "aboutness" test conflicted with this codebook's own partial-resolution language. |
| R6 | **Tightened.** The old wording swept selection calendars into appointment timing. |
| R1, R2, R4, R5, R7, R8 | Published unchanged. |

Nothing in the four field definitions changed. The definitions were never the
problem; what was missing was the record of how they had been applied.

Governing principle, which applies to this project generally:

> **Store observations. Derive interpretations.**

The categories a reader eventually sees (`INCORPORATED`, `IDENTIFIED`, `DIRECTED`,
`RESOLVED`) are **not stored**. Four booleans are stored, and the categories are
views over them. Anyone who disagrees with a category boundary can rebuild it from
the primitives without re-reading a single order.

---

## Why this file exists

The original dataset coded each Rule 16.1 subject as a single `YES`/`NO` on the
question "does this order address subject X." That binary was carrying **two
different constructs at once**:

1. Did the court bring this subject within the initial management process?
2. Did the court itself do anything with this subject?

For most orders the two answers coincide, so the defect was invisible. It became
visible in MDLs 3167 and 3175, which contain materially equivalent
blanket-incorporation clauses and received opposite treatment. See `AUDIT.md`,
entry of 12 August 2026.

The fix is not to pick one construct. It is to stop conflating them.

---

## Unit of observation

**Subject × order.** One row per Rule 16.1 subject per source document.

Not per MDL. An order may reach one subject through a residual catch-all and
another through a page of specific instruction; MDL 3171 (Lin) does exactly that.
Coding at the order level would erase the distinction the file exists to capture.

**What counts as one source document (v1.1, made explicit).** The `order_id` column
has always said "the specific source document, not just the MDL. An MDL with two
orders produces two sets of rows." That rule was departed from once, in MDL 3172,
where a February order and a June chambers letter were coded as a single row set.
The closure test:

- The **anchor** is the first judicial document setting the Rule 16.1(b) report or
  the Rule 16.1(a) initial management conference.
- A **companion** joins the anchor only if it is entered by the same court **on the
  same day** as the anchor.
- Anything entered later is its own source document and gets its own `order_id`, or
  is not coded at all if it falls outside the initial-management window.

A court that manages an MDL through a sequence of documents is doing something this
dataset's order-level unit cannot express, and the answer is a separate
episode-level view with its own `episode_id` and source manifest, not a silent
widening of the order unit for the one MDL where it was noticed.

---

## The four stored fields

| Field | Question | Type |
|---|---|---|
| `reached` | Is the subject within the scope of what this order requires, whether named or swept in by a blanket or residual incorporation clause? | boolean |
| `express` | Is the subject named in the order's own text? | boolean |
| `party_direction` | Does the order instruct the parties to say or do something on this subject? | boolean |
| `court_resolution` | Does the order itself fix the operative treatment of this subject at the relevant stage? | boolean |

### Logical constraints

These hold by construction and are enforced by `validate_treatment.py`:

```
party_direction  →  express  →  reached
court_resolution →  express  →  reached
```

You cannot decide direct filing without mentioning direct filing. A row violating
either implication is a coding error, not a finding.

`party_direction` and `court_resolution` are **independent within `express`**.
Both may be true. Neither implies the other.

---

## Field definitions

### `reached`

TRUE if the order requires the parties to address the subject, by any route.

Includes subjects swept in only by a general clause, for example:

- MDL 3167 (Shelby), PTO 1 ¶1: "A Joint Case Management Report addressing the
  matters included in Rule 16.1(b), Federal Rules of Civil Procedure"
- MDL 3175 (Peterson): a joint report "that addresses each of the matters listed
  in the rule"
- MDL 3171 (Lin), ¶9(xviii): "any topics not already listed but included in
  Federal Rule of Civil Procedure 16.1(b)"

FALSE where the order is simply silent on the subject and contains no clause that
sweeps it in. Most subjects in `NOT_INVOKED` orders are FALSE.

**Note on scope.** A clause incorporating "Rule 16.1(b)" reaches the subjects in
(b)(2) and (b)(3). A clause incorporating only "Rule 16.1(b)(2)" does not reach
(b)(3) subjects. Record the incorporated scope in `coding_note`.

### `express`

TRUE if the subject is named or described in the order's own words, so that a
reader of the order alone would know the subject is in play without consulting
Rule 16.1.

FALSE if the only route to the subject is a general or residual incorporation
clause. This is the field that separates `INCORPORATED` from `IDENTIFIED`.

### `party_direction`

TRUE if the order tells the parties to address, propose, submit, confer about, or
otherwise act on the subject.

The paradigm case is a report agenda item: MDL 3162 ¶5(g), directing the parties
to address how and when they will exchange information about the factual bases of
their claims and defenses.

### `court_resolution`

TRUE if the order itself **fixes the operative treatment of the subject at the
relevant stage of the proceeding**, such that the parties cannot alter that
treatment through the Rule 16.1 report alone. Changing it requires further court
action: a motion, a later conference, or an expressly reserved reconsideration
procedure.

**The diagnostic question:**

> After this order, can the parties still shape the operative treatment of this
> subject merely through their Rule 16.1 report?
>
> Yes → `court_resolution = FALSE`. No → `court_resolution = TRUE`.

**Permanence is not part of the construct.** A resolution may be:

- **interim** — an interim leadership appointment or a provisional direct-filing
  procedure is an operative determination even though the court plainly expects
  to revisit it;
- **conditional** — "if the parties cannot agree, then X" fixes what happens upon
  the condition. The condition does not make the treatment open to party choice;
- **preservative or continuing** — electing to leave transferor-court orders in
  force is a decision. Continuation is resolution;
- **simultaneous with `party_direction`** — an order routinely both instructs the
  parties on a subject and fixes some part of it. Both attributes fire.

**Partial resolution within a subject.** Several of the twenty subject IDs are
broad enough that a court may resolve one component and leave another open. An
order might keep interim lead counsel in place while directing the parties to
propose the scope of leadership authority; both fall within `b2a_leadership`.

`court_resolution = TRUE` therefore means **the court has made at least one
operative determination within the coded subject.** It does not assert that the
whole subject is closed. Record what remains open in `coding_note`.

**Do not use a verb list as the test.** Verbs mislead: "sets" appears both in
"sets a briefing schedule" (resolution) and in "sets a deadline for the parties to
propose a leadership structure" (direction, not resolution).

---

## Test cases, run against the definitions before freezing

Five deliberately awkward provisions, coded here to check that the rules produce
the expected answer without special pleading. **These are worked examples, not
data**; nothing here is entered in `subject-treatment.csv`.

Language marked *(paraphrase)* comes from the order-level coder's summary rather
than a captured quotation, and must be verified against the order during the
coding pass.

### 1. Staton, MDL 3181 — procedure as the subject
Subject `b2a_selection_procedure`. Four-factor lead counsel criteria, a prescribed
application format of a two-page resume plus a three-page letter, and five minutes
of argument per applicant *(paraphrase, ¶¶4.b–4.d)*.

`reached` T · `express` T · `party_direction` T · `court_resolution` **T**

The subject *is* the selection procedure, and the court fixed it. The parties
cannot rewrite the criteria or the format in their report. The old "prescribes a
process by which the subject will later be determined" formulation would have
coded this FALSE, which was the error the foreclosure test exists to prevent.

### 2. Quraishi, MDL 3180 — both attributes, from different paragraphs
Subject `b3c_discovery`. ¶5(h)(i)–(iv) directs the parties to address discovery;
¶12 stays all discovery and tolls the Rules 26–37 timing *(paraphrase)*.

`reached` T · `express` T · `party_direction` T · `court_resolution` **T**

The report can propose what happens next but cannot make discovery commence. Two
pin cites, one per attribute.

### 3. Quraishi, MDL 3180 — resolution by continuation
Subject `b2b_vacate_modify`. ¶13 leaves transferor-court orders in effect unless
modified *(paraphrase)*.

`reached` T · `express` T · `party_direction` **F** · `court_resolution` **T**

Nothing is asked of the parties, and nothing new is decided, but the court has
selected the operative rule. Continuation is resolution.

### 4. Griesbach, MDL 3179 — conditional
Subject `b2a_selection_procedure`. "In the event counsel for the plaintiffs are
unable to reach agreement, counsel for each of the plaintiffs shall submit a
status report regarding the selection of lead and liaison counsel for the
plaintiffs no later than three da[ys]…"

`reached` T · `express` T · `party_direction` T · `court_resolution` **T**

The court has fixed what happens on the condition. Agreement extinguishes the
report; disagreement triggers competing submissions. Either branch is set by the
order, not choosable by the report. Record the condition in `coding_note`.

### 5. Shelby, MDL 3167 — incorporation plus a fork
Blanket clause, PTO 1 ¶1: "A Joint Case Management Report addressing the matters
included in Rule 16.1(b), Federal Rules of Civil Procedure, and any other matters
the parties wish to address."

For a subject reached *only* by that clause, for example `b3e_settlement_facilitation`:

`reached` **T** · `express` **F** · `party_direction` F · `court_resolution` F

This is the row that the old binary got wrong. Under the four booleans it is
recorded as reached but unnamed, and MDL 3175's identical clause codes identically.

The proposed-order fork, "To the extent the parties cannot jointly agree on a
proposed Case Management Order, the parties may submit their own proposed Orders…"
*(paraphrase)*, is the same conditional structure as case 4 and codes the same way
on the subjects it touches.

**Result: all five code without special pleading.** The definitions are frozen for
pass 1 on that basis. Any change after coding begins invalidates the pass.


---

## Application rules

**New in v1.1.** These eight rules record how the frozen definitions were applied to
recurring situations the five worked examples did not settle. Each was written the
first time it was needed and back-applied to earlier orders.

They were kept in a separate working file during pass 1 and withheld from the blind
second pass, so that the second pass would test the definitions rather than the
notes. It worked, and the result was unambiguous: **every sampled cell whose coding
depended on one of these rules was disputed, against three of the other forty-five.**
A codebook that cannot reproduce its own codings without a private annex is
incomplete, so the annex is now part of the codebook.

Two rules changed on the way in. Both changes are marked.

### R1. A general discovery stay

A stay of discovery resolves `b3c_discovery`. It resolves any **other** subject only
where the order's own text ties that subject to the stayed machinery.

*Applied:* MDL 3162 `b3b_factual_basis_exchange` is TRUE, because ¶ 5(g) expressly
names Rule 26(a)(1) and ¶ 12 tolls Rules 26 through 37. MDL 3171 on materially
similar facts is FALSE, because ¶ 9(x) makes no reference to the discovery rules.

Without R1 a single stay paragraph cascades resolution across most of (b)(3).

### R2. Fixing motion timing

A provision that fixes when a pretrial motion may be filed, must be renoticed, or is
due is an operative determination within `b3d_pretrial_motions`. A Rule 12 response
to a complaint counts, because "answer or otherwise respond" reaches Rule 12 motions.

### R3. Independently prescribed treatment *(REPLACED in v1.1)*

**v1.1 text.** A provision fires `court_resolution` for a subject where its language
**independently prescribes, prohibits, continues or solicits** treatment mapped to
that subject. The provision's principal topic is irrelevant. A single paragraph may
fire more than one subject, because the twenty subjects are not mutually exclusive.

**What v1.0 said, and why it went.** The sealed rule asked whether a provision was
*about* the subject, and refused resolution where the subject appeared inside a
paragraph as an instance of something else. That test conflicts with this codebook's
own definition of `court_resolution`, which says the field is TRUE where the court
has made **at least one operative determination within the coded subject**, and which
expressly contemplates partial resolution of a broad subject. An outside review put
the objection this way: aboutness is not observable, and a dominant-purpose test
silently imports subject exclusivity that this codebook never states.

*Consequence.* MDL 3166 ¶ 6 makes liaison counsel responsible for transmitting the
court's orders and notices to nonleadership counsel. Under v1.0 that did not fire
`b2a_communication` because the paragraph is principally about liaison authority.
Under v1.1 it does, because the duty independently prescribes a method of
communicating with nonleadership counsel. Eleven cells across seven MDLs were coded
under the old R3 and are being re-read.

### R4. Anticipated topics versus directed content

An agenda topic that the **court** anticipates discussing is not a
`party_direction`. A topic list that specifies the **content of a filing the parties
must make** is.

*Applied:* MDL 3163 Part IV.B opens "the Court anticipates discussing the following
topics," so its ten topics are identified but not directed. MDL 3185 reads "The
parties shall file preliminary status reports … Suggested topics include," so its
seven topics are directed despite the word "suggested."

**R4 changes twelve cells and no published figure.** Without it MDL 3163 would show
14 directed subjects instead of 4, which is a real change to the published data. It is
not a change to any published number. R4 governs `party_direction` alone, and every
statistic on the landing page is computed from `reached`, `express` and
`court_resolution`. Reversing every R4 call in the dataset, which moves twelve of the
twenty-three cells the rule governs, leaves the page identical and passes both integrity
gates unchanged. The rules that do move published figures are R1, R6 and R7 through
`express`, R3 through `express` and `court_resolution`, and R8 through all four.

A targeted pass on 20 August 2026 found R4 applied consistently. In MDL 3163 direction
tracks the pin cite exactly: every cell resting only on the Part IV.B agenda is
undirected, every cell reaching Parts I to III is directed, and the single exception,
`b2d_direct_filing`, is resolution without direction, which the codebook permits. What
that pass could not check is the framing sentence itself. It is quoted in none of the
twenty-three cells it decides, so those cells cannot be verified from their own
evidence. Until it is quoted, treat the framing, not the application, as the open
question.

### R5. What counts as one order

Superseded by the closure test under **Unit of observation** above, which states the
same rule and adds what happens to a later document: it becomes its own source
document or is not coded.

### R6. When leadership timing is express *(TIGHTENED in v1.1)*

**v1.1 text.** `b2a_timing` is express only where the order states, or asks the
parties to propose, **when the court will make appointments**. Deadlines for
applications, conferral, objections or proposals belong to
`b2a_selection_procedure` unless the order connects them to the appointment
decision.

**What v1.0 said, and why it changed.** The old wording also fired where the order
"places the appointment process on a fixed calendar." Nearly every selection
procedure has deadlines, so that phrase swept selection calendars into the timing
cell and double-counted one set of facts across two subjects. The point was made
independently by a reader who had the orders and not the rule.

### R7. Naming a coordinating role

A court-created coordinating role is coded as leadership counsel where the order
gives it a leadership title, and not where it does not. The `express` test is
nominal by design: it asks what a reader of the order alone would know without
consulting the Rule.

*Applied:* MDL 3166 ¶ 6 "Interim liaison counsel" is leadership; MDL 3171 ¶ 7 "Point
of contact," the same provision renamed, is not. The two are functionally identical
and both rows say so, so a rebuilder applying a functional test can flip MDL 3171.

### R8. Expense sharing is not compensation

Allocating the expenses of one administrative role among a group of counsel is not
"a means for compensating leadership counsel" under (b)(2)(A)(vii). Coded FALSE
under the instruction to undercount when unsure, with the reasoning in both rows so
a rebuilder can flip them.


---

## Derived views

Never stored. Computed by `build.py`.

```
INCORPORATED  =  reached AND NOT express
IDENTIFIED    =  express AND NOT party_direction AND NOT court_resolution
DIRECTED      =  party_direction
RESOLVED      =  court_resolution
```

`DIRECTED` and `RESOLVED` co-occur freely and are **not ordered relative to one
another**. The scale is partial:

```
INCORPORATED  <  IDENTIFIED  <  { DIRECTED , RESOLVED }
```

Do not compute a mean over these categories. A court that resolves a subject in
its initial order may be doing the opposite of what Rule 16.1 contemplates, which
is gathering the parties' views before entering the (c) order. Resolution is a
different posture, not a deeper one.

## Derived metrics

Every published figure must name which of these it uses. `build.py` rejects an
unlabelled coverage claim.

| Metric | Definition |
|---|---|
| **Inclusive coverage** | `reached` |
| **Express coverage** | `express` |
| **Substantive engagement** | `party_direction OR court_resolution` |

---

## Reliability protocol

> **Amended 12 August 2026, after pass 1 was complete.** No field definition, logical
> constraint, derived view or metric changed; the freeze above is intact and pass 1 stands.
> What changed is this section's description of pass 2, which was written for a human coder
> and did not survive contact with how pass 1 was actually executed. The original text is
> quoted below so the amendment can be audited.

### What the protocol originally said

> One coder, no second rater, so the design substitutes **intra-rater** agreement.
> Code all 280 cells; wait not less than 21 days for a genuine washout; recode all 280
> without consulting the first pass; report per-attribute agreement and Cohen's kappa.

### Why that does not work here

Pass 1 was executed **in a single session on 12 August 2026**, order by order, by a model
rather than by a person coding over days. Two consequences follow.

**A washout period does not do what it was meant to do.** The design assumed a coder who
forgets. Nothing here forgets and then remembers imperfectly; a fresh session simply starts
without the first pass. Waiting 21 days changes nothing about the second coder's state.

**A second session is not the same rater.** It is closer to a second rater drawn from the
same population: same training, same priors, same reading of the same codebook. That will
inflate agreement on the mechanical attributes and will not surface the disagreements the
protocol exists to find. Calling the result intra-rater reliability would overstate what it
measures.

`coding-decisions.md` records the eight application rules pass 1 actually used and is
sealed from pass 2 for this reason. Sealing a file is not the same as forgetting it.

### What pass 2 is instead

Pass 2 is an **independent re-code**, and is to be reported under that name. It is worth
running: it detects codebook ambiguity, because two readers working from the same
definitions still diverge where the definitions underdetermine the answer. It does not
estimate what a different human coder would produce.

Report per attribute: raw percent agreement, the raw disagreement count, and Cohen's kappa,
each labelled **independent re-code**, never "intra-rater reliability."

### The estimate that would actually be informative

A human codes a random sample of the 280 cells, blind to pass 1, and agreement is reported
against that. Fifty cells stratified across the fourteen orders would be enough to say
something real, and it is the only design here that measures whether the codebook travels
to a different reader rather than to a different instance of the same one.

### Publish the disagreements

Unchanged from the original protocol. Disagreement cells are the debugging corpus for these
definitions; every disagreement should either produce a codebook amendment or be recorded as
genuinely ambiguous.

### Ex ante expectation, recorded 12 August 2026, before any cell is coded

> Agreement should be highest for `reached` and `express`, which are close to
> mechanical. Disagreement is expected to **concentrate in `party_direction` and
> `court_resolution`**, and within those, on provisions that simultaneously
> structure future party submissions and fix an interim management rule.

This is written down now so that the second pass cannot be explained
retrospectively. If disagreement lands somewhere else, that is itself a finding
about the codebook.

### Ex post map of contestable cells, recorded 12 August 2026, after pass 1 and before pass 2

The prediction above cannot be tested until pass 2 runs, but pass 1 left a record of where
its own reasoning was strained. Every coding note that invokes an application rule, records
a partial resolution, rejects an adjacent provision, invokes the instruction to undercount,
or says a rebuilder could reasonably flip the row is counted here as **contestable**.

| | cells | share |
|---|---|---|
| Contestable by any of those markers | 41 of 280 | 15% |
| Of which `court_resolution` is TRUE | 20 of 41 | **49%** |
| `court_resolution` TRUE across all cells | 62 of 280 | 22% |

**Contestable cells are more than twice as enriched for resolution decisions as the corpus
as a whole**, which is the direction the ex ante expectation predicted.

The concentration by subject is sharper than the prediction anticipated. `b3d_pretrial_motions`
alone accounts for 12 of the 41, all of them turning on application rule R2, which decides
when a provision fixing motion timing counts as an operative determination. If pass 2
disagrees anywhere, that is where to look first.

By order, the contestable cells cluster in the most operative orders rather than the
thinnest: MDL 3181 has 8 and MDL 3166 has 6, while the pure transcription orders, MDLs 3170
and 3174, have 1 each. Orders that only reproduce the Rule's list are close to mechanical to
code. Orders that decide things are where the definitions have to work.

A narrower count, restricted to the seven cells where pass 1 explicitly recorded doubt rather
than merely applying a rule, points instead at `express`, three of seven. Both numbers are
reported because they disagree, and because neither is a substitute for the disagreement set
that pass 2 will produce.

Disagreement cells are written to **`reliability-disagreements.csv`**, one row per
cell, carrying both codings, both pin cites, and a resolution note. Each
disagreement must either produce a codebook amendment or be recorded as genuinely
ambiguous. Those cells are the most informative output of the exercise.

**Interpret kappa cautiously where prevalence is extreme.** If nearly every
subject is `reached`, kappa can look poor despite near-total agreement. Raw
agreement and raw disagreement counts stay visible alongside it for exactly that
reason.

---

## Schema: `subject-treatment.csv`

| Column | Notes |
|---|---|
| `mdl_no` | JPML number, or `NON-MDL` |
| `order_id` | The specific source document, not just the MDL. An MDL with two orders produces two sets of rows. |
| `subject_id` | From the registry below |
| `reached` | `TRUE` / `FALSE` |
| `express` | `TRUE` / `FALSE` |
| `party_direction` | `TRUE` / `FALSE` |
| `court_resolution` | `TRUE` / `FALSE` |
| `pin_cite` | Paragraph or page. Required whenever `express` is TRUE. |
| `quote` | Verbatim language. Required whenever `party_direction` or `court_resolution` is TRUE. |
| `coding_note` | Nullable. Edge cases, incorporated scope, conditions. **Never put interpretation in `quote`.** |
| `coder` | Initials |
| `date_coded` | ISO date |
| `pass` | `1` or `2`, for the reliability re-code |

### Subject registry

Twenty subjects: the Rule's eighteen enumerated items, plus the (b)(2)(A) chapeau,
plus (b)(2)(A)(iii) split into selection and periodic review because the Rule
combines two distinct questions in one clause.

| `subject_id` | Rule cite | Subject |
|---|---|---|
| `b2a_leadership` | (b)(2)(A) | whether leadership counsel should be appointed |
| `b2a_timing` | (b)(2)(A)(i) | timing of the appointments |
| `b2a_structure` | (b)(2)(A)(ii) | structure of leadership counsel |
| `b2a_selection_procedure` | (b)(2)(A)(iii) | procedure for selecting leadership |
| `b2a_periodic_review` | (b)(2)(A)(iii) | whether appointments should be reviewed periodically |
| `b2a_responsibilities` | (b)(2)(A)(iv) | responsibilities and authority |
| `b2a_communication` | (b)(2)(A)(v) | communicating with and reporting to the court and nonleadership counsel |
| `b2a_nonleadership_limits` | (b)(2)(A)(vi) | limits on activity by nonleadership counsel |
| `b2a_compensation` | (b)(2)(A)(vii) | whether and when to establish a means for compensating leadership counsel |
| `b2b_vacate_modify` | (b)(2)(B) | previously entered orders that should be vacated or modified |
| `b2c_conference_schedule` | (b)(2)(C) | schedule for additional management conferences |
| `b2d_direct_filing` | (b)(2)(D) | how to manage direct filing of new actions |
| `b2e_related_actions` | (b)(2)(E) | related actions elsewhere and methods for coordinating |
| `b3a_consolidated_pleadings` | (b)(3)(A) | whether consolidated pleadings should be prepared |
| `b3b_factual_basis_exchange` | (b)(3)(B) | how and when the parties will exchange information about the factual bases |
| `b3c_discovery` | (b)(3)(C) | discovery, including difficult issues |
| `b3d_pretrial_motions` | (b)(3)(D) | likely pretrial motions |
| `b3e_settlement_facilitation` | (b)(3)(E) | measures to facilitate resolving some or all actions |
| `b3f_magistrate_master` | (b)(3)(F) | referral to a magistrate judge or master |
| `b3g_principal_issues` | (b)(3)(G) | principal factual and legal issues |

Subdivision (b)(4), permitted content, is **not** a subject here. Matters raised
beyond the Rule are recorded in the order-level file, because they are defined by
not appearing in this registry.

---

## Migration

`subject-treatment.csv` becomes the canonical subject-level evidence table.
`rule-16-1-tracker.csv` remains the public order-level summary, and its twenty
subject columns become **derived output** equal to `reached`, regenerated by
`build.py`.

Nothing published today changes shape. Anyone who has already downloaded the
order-level CSV keeps a file with the same columns and the same meaning, except
that MDL 3167's subject columns are corrected upward to reflect the incorporation
clause its order actually contains.
