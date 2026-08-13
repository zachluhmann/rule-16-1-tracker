# Subject-treatment codebook

**Status: definitions frozen 12 August 2026 after testing against five awkward
provisions (below). No cells coded yet. Any change after pass 1 begins invalidates
the pass.**

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
