# Project audit — 2026-08-11

> **Status update, 2026-08-12.** MDL 3180 was read and the headline moved from
> 6/13 to **7/14**. Of the findings below: **C1, C2 and C3 are resolved**
> (block rate defined once as 1 of 16 (6%) and used everywhere; `NOT_CHECKED`
> documented as a sixth vocabulary value; every typed enum now documented in the
> README codebook). **The two firm quotations were verified against their
> sources** and the page says so. **F01 is resolved** — the "tentative agenda"
> construction is now quoted from MDL 3180 ¶3, where it is pin-cited, rather than
> attributed to MDL 3162 where it was not.
>
> **The structural finding below is still open and is still the largest one.**
> The thin tier is unchanged at six rows; MDL 3180 was coded to the current
> standard, so the well-sourced tier is now eight. The share of unbacked
> affirmative codes fell from 57% to **52%** only because the denominator grew.

Adversarial pass over everything built in this session: the dataset, the four
prose documents, the submission, and the landing page. Mechanical checks were
run programmatically; external claims were checked against sources where the
sources were reachable.

**Result: 4 errors fixed, 3 contradictions open, 8 assertions flagged as
unverified, and one structural finding larger than the cite-check caught.**

---

## THE STRUCTURAL FINDING

### 52% of the dataset's affirmative codes are not backed by quoted language

The cite-check ledger (F03) reported this as "six thin rows." Quantified, it is
much larger:

| | |
|---|---|
| `YES` codes across the fourteen coded rows | **266** |
| In rows whose `pin_cites` contains no quoted language | **138 (52%)** |

*(Recomputed 2026-08-12. It was 138 of 242 = 57% before MDL 3180 was coded; the
numerator has not moved, only the denominator. Nothing was fixed.)*

| MDL | `YES` codes | `pin_cites` |
|---|---:|---|
| 3162 | 28 | 231 chars, paragraph pointers only |
| 3163 | 19 | 264 chars, pointers only |
| 3166 | 16 | 285 chars, pointers only |
| 3171 | 21 | 333 chars, pointers only |
| 3174 | 25 | 161 chars, pointers only |
| 3175 | 29 | 252 chars, pointers only |

**This is not a protocol violation.** `PROTOCOL.md` requires "a pin cite
(document + page or paragraph)," and these rows have that. The problem is
narrower and worse:

1. **The rows are not independently auditable.** A reader who disagrees with a
   coding decision has to go pull the order. That is a much higher bar than
   disagreeing with a quotation, and the whole design of this dataset was
   supposed to make disagreement cheap.
2. **I cannot check my own work against them either** — which is exactly how
   ledger finding F01 happened. The MDL 3162 "tentative agenda" quotation
   appears nowhere in the data because there was no quoted language in that row
   to appear in.
3. **Four of the seven citing MDLs are in this tier** (3162, 3171, 3174, 3175).
   The headline — seven of fourteen — rests substantially on rows that do not meet
   the evidentiary standard the later rows set.

**Fix:** back-fill quoted language into those six rows. One reading session once
the API resets. Until then, the submission's Part VIII should say so, and the
landing page already does.

---

## ERRORS FIXED IN THIS AUDIT

**E1 — The TPLF subcommittee chair was wrong, in two files.**
`PROTOCOL.md` and `README.md` said "Judge Vance's TPLF subcommittee." The
April 14, 2026 agenda book states the Third-Party Litigation Funding
Subcommittee is chaired by **Judge R. David Proctor** (at 10). Judge Vance's
report appears separately at 19–20. Corrected in both files, with the error left
visible.
*The submission was not affected* — it says only "the funding subcommittee's
continuing work" and names no chair. That was luck, not care.

**E2 — "Actively soliciting exactly this information" overstated the record.**
The agenda book describes the subcommittee as having "spent the last year
educating itself on these issues" and posing framing questions ("What would be
disclosed and to whom?"). It does not solicit empirical data. Corrected to claim
only what the book supports.

**E3 — `PROTOCOL.md` still carried the superseded sequence-gap warning.**
It told the reader that 3164, 3165, 3168–3170, 3173, 3177, 3182–3184 and 3186
"may be real MDLs missing from the seed." The third pass resolved that: they are
denied or withdrawn petitions, with 3170 the single real exception. Replaced with
the resolved finding.

**E4 — One non-ISO date, and it was silently dangerous.**
MDL 3178's `a_conference_date` read `2026-05 (early May, exact date TBD)`. Any
interval computation over that column would have thrown or silently skipped it.
Cleared to empty with the underlying fact preserved in `pin_cites`.

---

## CODING INCONSISTENCY — found and resolved 2026-08-12

**MDLs 3167 and 3175 contained materially equivalent provisions and were coded
differently.** Judge Shelby's Pretrial Order No. 1 in MDL 3167 requires "a Joint
Case Management Report addressing the matters included in Rule 16.1(b), Federal
Rules of Civil Procedure." Judge Peterson's order in MDL 3175 requires a joint
report "that addresses each of the matters listed in the rule." Both are blanket
incorporation clauses of the same scope.

The original dataset treated them differently. **MDL 3167 received credit only for
subjects independently addressed elsewhere in the order** (8 of 19), which is why
its `pin_cites` show `b2a=PTO 1 para 3.d`, `b2e=para 3.b`, `b3g=para 3.a` and
nothing further. **MDL 3175 received credit for all incorporated subjects**
(19 of 19) on the strength of the blanket clause alone.

**The codebook had not specified how blanket incorporation should be treated.**
Neither row was wrong under a stated rule, because there was no stated rule.

### Why the binary was underdetermined

The defect was not a mis-applied rule. It was **construct validity**. The single
`YES`/`NO` per subject was carrying two distinct constructs:

1. Did the court bring this subject within the initial management process?
2. Did the court itself do anything with this subject?

Those questions have different answers for the same order, and any single binary
had to silently pick one. Choosing a rule would have hidden the problem rather
than fixed it.

### Resolution

The subject-level variable is **split into four stored booleans** — `reached`,
`express`, `party_direction`, `court_resolution` — recorded per subject per
order in a new file, `subject-treatment.csv`, with the interpretive categories
derived rather than stored. See `subject-treatment-codebook.md`.

Under that scheme both orders are coded identically and the difference between
them becomes visible rather than lost: each is `reached = TRUE` and
`express = FALSE` on the incorporated subjects.

The order-level subject columns in `rule-16-1-tracker.csv` become derived output
equal to `reached`, which **corrects MDL 3167 upward** from 8 of 19.

### Quantitative effect on reported statistics

The comparison of subject coverage between citing and non-citing orders, computed
three ways:

| | citing median | citing spread | non-citing median |
|---|---:|---|---:|
| As originally coded (inconsistent) | 19 | 8–19 | 12 |
| Conservative rule (3175 corrected down) | 18 | 3–19 | 12 |
| **Adopted: inclusive `reached` (3167 corrected up)** | **19** | **13–19** | **12** |

The headline median is unchanged at 19 versus 12. What moves is the spread, which
was the more honest half of that sentence.

**This inconsistency did not manufacture any published finding.** The strongest
result in the dataset — that 5 of 7 citing orders provide for periodic review of
leadership against 0 of 7 non-citing orders — is unaffected under every treatment,
because both 3167 and 3175 are `YES` on that subject and no non-citing order
addresses it at all.

### Status

The coverage comparison is **withheld from the site** until subject-level coding
is complete and all three derived metrics (inclusive coverage, express coverage,
substantive engagement) can be reported together. Correcting 3167 in the
order-level file without the depth axis would trade one underdetermined number
for another.

---

## CONTRADICTIONS — all three resolved 2026-08-12

**C1 — The block rate was published as two different numbers.** ✅ **RESOLVED.**
`README.md` and `index.html` said **13%**; README's seventh pass said **6%**.
Reading MDL 3180 collapsed the ambiguity: the `PUBLIC_COPY_LOCATED` status no
longer exists in the data. **The published definition is now one sentence — the
block rate is the share of MDLs whose existing order could not be read, currently
1 of 16 (6%)** — and it appears in that form in the README status block, the
landing page limitations, and `build.py`'s output.

**C2 — `party_invoked_rule` used `NOT_CHECKED`, outside the five-value
vocabulary.** ✅ **RESOLVED.** Added to the codebook as a documented sixth value
meaning "this variable has not been examined for this row," which is genuinely
different from `UNCLEAR`. Still 13 of 16 rows.

**C3 — The enum columns had grown without documentation.** ✅ **RESOLVED.** The
codebook now carries a **Typed enums** table listing every value that actually
appears in the CSV for `source_status`, `rule_role`, `report_form`,
`rule_vocabulary` and `report_channel`, marked exhaustive as of 2026-08-12.
`rule_role`'s `TRANSCRIPTION` value, which drove two rows and appeared in no
documentation, is now in the typology with worked examples.

---

## THE ASYMMETRY THE AUDIT ACTUALLY FOUND

This project applied ferocious sourcing discipline to court orders — pin cites,
quoted language, `NOT_ADDRESSED` versus `NO`, deliberate undercounting — and
**almost none of it to its own background claims.** Eight assertions about the
outside world drive strategy or appear on the public page and were never checked
against a source. They are now listed in `PROTOCOL.md` under
**"Unverified assertions ledger."** The two that matter most:

- **Two firm quotations are on the public landing page** ("it will likely be
  several years before the impact of Rule 16.1 is clear"; "courts have taken
  varied approaches") attributed to Crowell and Sidley. Neither was verified.
  Publishing an unverified quotation attributed to a named firm, on a page whose
  entire pitch is quotation discipline, is the most self-undermining thing in
  the project. ✅ **RESOLVED** — both checked against the source alerts on
  2026-08-11; the page now links each alert and says the quotations were
  verified, with the date.
- **"Nobody has counted"** is the premise of the whole thing. It rests on one
  preemption search. The submission hedges it correctly ("To my knowledge no one
  has assembled the population"); the landing page states it flat. Match the
  page to the letter. ✅ **RESOLVED** — the page now reads "To my knowledge
  nobody has assembled the population and counted it."

Also worth internalizing: **the April 14, 2026 agenda book does not mention Rule
16.1 or MDL practice anywhere.** I have been describing the Advisory Committee as
the highest-value citation target for this data, which is still a reasonable
strategic bet — Lawyers for Civil Justice has docketed Rule 16.1 suggestions
(24-cv-G), so the topic is not foreign to the Committee — but it is not a
committee waiting for your number. A suggestion is how a topic gets *onto* an
agenda. That is a different and more modest claim than the one I was making.

---

## WHAT PASSED

Recorded because a clean check is information too.

| Check | Result |
|---|---|
| CSV integrity — 16 rows, 61 cols, no duplicates, no ragged rows | pass |
| `days_transfer_to_conference` recomputed from the two date fields | **0 mismatches** |
| Intervals with no underlying dates | none |
| Landing page snapshot vs. CSV, field by field | **0 drift** |
| All 13 numeric claims in the submission vs. CSV | all reconcile |
| MDL-number lists in the submission (the six, the seven) | exact match |
| 36 of 37 quoted passages in the submission traceable to the dataset | 1 failure (F01) |
| Agenda-book posting date — the basis for the early-September deadline | **verified**: the April 14, 2026 book is `..._final_3-27.pdf`, posted March 27, ≈18 days before the meeting. The October 21 meeting implies an early-September window. **The deadline holds.** |

---

## Order of operations

1. ~~**C1** — pick a block-rate definition.~~ ✅ done 2026-08-12.
2. ~~**Strike or verify the two firm quotations**, and hedge "nobody has
   counted."~~ ✅ done.
3. ~~**F01** — the unpinned "tentative agenda" quotation.~~ ✅ done — now quoted
   from MDL 3180 ¶3, where it is pin-cited.
4. ~~**C2 and C3** — codebook maintenance.~~ ✅ done 2026-08-12.
5. **The 52% back-fill — the one that is still open, and the biggest.** One
   reading session against six rows (3162, 3163, 3166, 3171, 3174, 3175), and it
   converts the project's largest structural weakness into its strongest claim.
   Do it before the DOI deposit, since the codebook and the CSV ship together.
6. **MDL 3187** — one PACER pull, four documents. The last blocked row.
7. **The pre-effective-date question**, still entirely unexplored. `PROTOCOL.md`
   Guardrail 10 defines the method; the `pre_effective_date` column exists and is
   empty. It is the largest unclaimed finding left.
8. Everything else in `PUBLISH.md` Steps 1–4.

---

## 12 August 2026 — corrections and findings from the subject-level reading pass

Three corrections to previously recorded facts, all from reading MDL 3162's order
in full rather than from the summary that stood in for it.

### 1. Bates ¶ 7 contains an evidence-preservation duty

The earlier beyond-Rule catalogue was built by keyword search and missed it. MDL
3162 ¶ 7 is a full preservation paragraph, extending the duty to "any employees,
agents, contractors, carriers, bailees, or other nonparties who possess materials
reasonably anticipated to be subject to discovery," and holding until "the parties
reach an agreement on a preservation plan."

**Effect.** Evidence preservation now appears in five orders across four districts
(3162 D.D.C., 3166 N.D. Cal., 3171 N.D. Cal., 3180 D.N.J., 3181 C.D. Cal.), which
strengthens rather than weakens the finding that it is the one genuinely convergent
topic courts add beyond the Rule. It also confirms the warning already recorded
that a keyword catalogue cannot substitute for hand-coding: "webpage" versus
"website" was the first instance, this is the second.

### 2. Bates ¶ 4 displaces Local Civil Rule 16.3, not 16.1

Recorded earlier as a Rule 16.1 versus Local Rule 16.1 collision, on the strength
of MDL 3180 ¶ 4 (D.N.J.), which does displace a local rule of the same number.
Bates displaces **Local Civil Rule 16.3**. So the local-rule displacement is a
shared structural feature of the form order, but the rule number is
district-specific and the same-number coincidence is D.N.J.'s alone. The finding
survives in a narrower form: one instance, not two.

### 3. The shared form order is wider than four report items

MDLs 3162 and 3180 were recorded as sharing three verbatim report items plus the
agenda formula. The shared text also runs through ¶ 7 (preservation), ¶ 11 (answer
deadlines stayed), ¶ 12 (discovery stayed, Rules 26–37 tolled) and ¶ 13 (transferor
orders remain in effect), which are the same paragraph numbers in both. The form
order is a substantially complete initial management template, not an agenda with
a few additions.

### 4. The em dash is a provenance marker, and the first reading of it was backwards

Rule 16.1(b)(2)(E) reads, in the Rule's own text, "whether related actions have
been—or are expected to—be filed in other courts." The dash placement is unusual
and the construction is awkward. MDLs 3170 and 3174 reproduce it exactly. MDL 3162
and the form order it shares with MDL 3180 regularize it to "are expected to
be—filed."

This was first recorded as a transcription slip in MDL 3174. It is the opposite:
3174 is faithful and 3162 is the deviation. Corrected after re-verifying the Rule
text against Cornell LII on 12 August 2026. The punctuation now works as a
provenance marker separating transcribers from re-typers.

### 5. Two orders in the set carry a year typo in a deadline

MDL 3163 sets position statements due "January 8, 2025" in an order dated
23 December 2025. MDL 3170 sets the report due "January 15, 2025" and the hearing
for "January 27, 2025" in an order dated 18 December 2025. All three must mean
2026. Recorded as observed; no inference drawn.

### 6. MDL 3170 omits one of the Rule's eighteen items

Case Management Order #2 reproduces seventeen of the eighteen enumerated report
items, in the Rule's own sequence, and drops (b)(3)(E), measures to facilitate
resolving some or all actions. The list runs from "Any likely pretrial motions"
straight to "Whether any matters should be referred to a magistrate judge or a
master." The order cites Rule 16.1 in its opening words.

This is the first documented instance of a court adopting the Rule's list and
editing it, and the edited-out item is one of the five the marginal-contribution
analysis attributes to the Rule.

### 7. MDL 3174 miscites the Rule's permitted-content subdivision

Part III reads "Pursuant to Rule 16.1(b)(3), the report may also include any other
matters that the parties wish to bring to the court's attention." Permitted content
is Rule 16.1(b)(4). The subdivision cite from Part II is carried down.


---

## 12 August 2026 — pass 1 of the subject-level coding, results and one negative finding

**Status: 260 of 280 cells coded, 13 of 14 orders.** MDL 3180 is blocked; see below.
`validate_treatment.py` reports all logical constraints satisfied. Every one of the
157 subjects coded `express` carries a verbatim quotation and a pin cite.

### Reconciliation against the order-level file

The twenty subject columns in `rule-16-1-tracker.csv` agree with derived `reached`
on **233 of 260 cells (89.6%)**. The 27 differences fall into three groups.

**Nineteen NOT_ADDRESSED → reached TRUE.** Fourteen are the incorporation
correction the redesign was built for: eleven in MDL 3167 and three in MDL 3171,
all subjects reached by a blanket or residual clause that the single binary could
not represent. The other five are substantive upgrades from reading the full text:
`b2d_direct_filing` in MDLs 3166, 3172 and 3181, `b3d_pretrial_motions` in
MDL 3166, and `b2a_selection_procedure` in MDL 3178.

**Four UNCLEAR → reached TRUE.** Resolved by the full read, which is what a full
read is for.

**Four YES → reached FALSE**, all traceable to two rules applied uniformly:
setting the initial conference is not "a schedule for **additional** management
conferences" (MDLs 3172 and 3178), and leadership timing is express only where the
appointment process runs on a stated calendar (MDL 3179). MDL 3172's
`b3f_magistrate_master` is the fourth: the June 22 letter says a magistrate judge
"is assigned to this litigation with me," which states an assignment rather than a
referral.

The order-level columns are **not** being overwritten yet. That is step 6 of the
agreed sequence, after the reliability re-code.

### The headline comparison, and why it now has to be stated twice

| | citing (n=6) | non-citing (n=7) |
|---|---|---|
| Inclusive coverage (`reached`), median | **20** | 12 |
| Express coverage (`express`), median | 17.5 | 12 |
| Substantive engagement, median | 17.5 | 10 |
| **Subjects resolved, median** | **2** | **5** |

Two things the single binary could not have shown.

**The direction reverses depending on the metric.** Orders that cite Rule 16.1
put more subjects in play and decide fewer of them: 15% of their subject-order
cells carry a court resolution, against 28% for orders that never mention the Rule.
Breadth and depth run in opposite directions.

**And the strongest finding does not survive the robustness check.**

### The negative finding

Periodic review of leadership appointments was the project's single cleanest
result: no non-citing order raises it. It still holds on inclusive coverage,
6 of 6 against 0 of 7, Fisher exact **p = 0.0006**.

On **express** coverage it falls to 3 of 6 against 0 of 7, **p = 0.07**.

Half the apparent effect was the incorporation clause, not the court. MDLs 3167
and 3175 reach periodic review only because their orders incorporate Rule 16.1(b)
wholesale; neither court wrote a word about it. Once blanket incorporation is
stripped out, **no subject separates citing from non-citing orders at conventional
significance** at this sample size. The largest remaining express gaps are
periodic review (0.50), magistrate or master (0.38), factual-basis exchange (0.38),
settlement facilitation (0.36) and limits on nonleadership counsel (0.36), none
below p = 0.07.

This is the result the construct-validity rebuild was supposed to make visible, and
it points the other way from the earlier claim. Nothing derived from the five-item
marginal-contribution analysis should be published without stating which coverage
metric it uses.

**Direct filing drops out of that five-item set entirely.** It was 5/7 against 1/7
at the order level. At the subject level it is 6/6 against 4/7 inclusive and 5/6
against 4/7 express, because the full read found automatic-consolidation and
later-filed-case clauses in the non-citing orders that a subject-column pass had
recorded as NOT_ADDRESSED.

**Caveat.** n = 13, and the missing order is a citing one. MDL 3180 shares a form
order with MDL 3162, which codes 20/20/20/5, so adding it should raise citing
express coverage and citing resolutions. The express comparison above is
provisional until it is coded.

### MDL 3180 could not be retrieved

Six routes tried on 12 August 2026, all exhausted: the RECAP document (482384743)
has no text layer; the recap-documents record shows `is_available: false` with no
stored file; `njd.uscourts.gov/multi-district-litigation` returns 404; two web
searches surface no mirror of the D.N.J. order; the docket-entry descriptions on
CourtListener docket 73443394 are empty.

The order was read in full from the court's PDF on 11 August 2026 and the
order-level file carries an item-by-item pin-cite map from that reading. **That map
was deliberately not used to code these rows.** Coding `party_direction` or
`court_resolution` TRUE requires a verbatim quotation, and the only way to supply
one here would be to copy it from MDL 3162's near-identical form order or to
reconstruct it from a paraphrase. Either would put a sentence in the dataset that
no one verified against Judge Quraishi's text. The twenty rows stay blank.

### A methodological problem with the reliability protocol, raised now rather than later

The codebook specifies intra-rater reliability: recode all 280 cells after a
washout of not less than 21 days, and report per-attribute agreement and Cohen's
kappa. That design assumes a human coder who forgets.

Pass 1 was executed in a single session by a model. A second pass in a fresh
session is not intra-rater agreement after a washout; it is closer to
**inter-rater** agreement between two instances of the same system, with a shared
prior and no independent judgment. It will almost certainly overstate agreement on
the mechanical attributes and understate the difficulty of the contested ones.

`coding-decisions.md` records the eight application rules that pass 1 actually
used, and is sealed from pass 2 for that reason. But sealing a file does not
recreate forgetting. The reliability section should say plainly what pass 2 is
before it is run, and the honest options are to relabel it as an independent
re-code rather than intra-rater reliability, or to have a human code a sample and
report agreement against that instead.

---

## 12 August 2026 — pass 1 complete, 280 of 280 cells

MDL 3180 was obtained from the docket PDF and coded. Every figure below is over all
14 readable orders, 7 citing and 7 not.

| | citing (n=7) | non-citing (n=7) |
|---|---|---|
| Inclusive coverage (`reached`), median of 20 | 20 | 12 |
| Express coverage (`express`), median of 20 | 19 | 12 |
| Subjects resolved, median | 3 | 5 |
| Share of subject-order cells resolved | **16%** | **28%** |

On the 19-column scale the site uses: inclusive medians 19 against 11, spreads 18 to 19
and 4 to 14; express medians 18 against 11, citing spread 1 to 19.

**Everything held when the fourteenth order landed.** Periodic review is still a perfect
discriminator on inclusive coverage, now 7 of 7 against 0 of 7, Fisher exact p = 0.0006.
And it still fails on express coverage, 4 of 7 against 0 of 7, p = 0.07. Adding a citing
order moved neither result. The negative finding recorded earlier today stands: **no
subject separates citing from non-citing orders at conventional significance once blanket
incorporation is stripped out.**

The universal set is unchanged at two subjects, now 14 of 14: whether leadership counsel
should be appointed, and the procedure for selecting leadership. The least-addressed are
periodic review and measures to facilitate resolution, 7 of 14 each. Direct filing is
11 of 14.

### MDL 3180: the numbering gap

The order runs paragraph 8, LOCAL CIVIL RULES GENERALLY, then paragraph 10, HEARINGS.
**There is no paragraph 9.** Verified twice: by regex across the extracted text, and by
rendering page 7 of the PDF and reading it.

In MDL 3162 the same form order's paragraph 9 is "LOCAL CIVIL RULE 23.1(b) WAIVED," a
D.D.C.-specific provision about class certification motions with no D.N.J. counterpart.
It was deleted and nothing was renumbered.

This is the strongest copying evidence in the dataset. Shared phrasing can be coincidence
or common drafting practice. A gap in an ordinal sequence is the negative space left by an
edit to a specific document.

It also changes one coding. MDL 3162 fires application rule R2 twice on
`b3d_pretrial_motions`, at paragraph 9 and paragraph 11. MDL 3180 has only paragraph 11, so
nothing there fixes class certification timing.

### Four smaller divergences between the two copies

| | MDL 3162 (D.D.C.) | MDL 3180 (D.N.J.) |
|---|---|---|
| Local rule displaced by ¶ 4 | Local Civil Rule 16.**3** | Local Civil Rule 16.**1** |
| ¶ 5(d) cross-reference | "in light of Section 1 **supra**" | "in light of Section 1, **above**" |
| ¶ 5(h)(ii) | "whether any **protective** orders" | "whether any **protective or confidentiality** orders" |
| ¶ 5(k) | "a magistrate judge or a **master**" | "a magistrate judge or a **special master**" |

The same-number collision between Rule 16.1 and a Local Civil Rule 16.1 is D.N.J.'s alone.
The displacement itself is a feature of the form.

**The em dash resolves as predicted.** MDL 3180 ¶ 5(e) reads "are expected to be—filed,"
the same regularisation as MDL 3162 and against the Rule's own "are expected to—be filed,"
which MDLs 3170 and 3174 reproduce exactly. The marker travels with the form, not with the
Rule.

### Site changes made today

Three findings corrected or added, all asserted by `build.py` against
`subject-treatment.csv` rather than against the order-level subject columns, which the
subject-level pass supersedes and which still disagree on 27 of 260 previously reconciled
cells. Four mutation tests confirm the new guards fire: altering the universal set, the
least-addressed set, the direct-filing count, or the resolution rate each trips the build.
An earlier version of those guards was satisfiable by a substring and passed a mutation
that should have failed; they are now anchored at both ends.

### Still open

1. **Regenerate the order-level subject columns from `reached`.** This is the step that
   makes one source canonical. It changes the published CSV, so it is a decision, not a
   chore.
2. **Relabel the reliability protocol** before pass 2, for the reason recorded earlier
   today.
3. **MDL 3187**, four documents, the last blocked row.
4. Nothing in this pass is committed to GitHub.

---

## 12 August 2026 — the order layer becomes derived output

`migrate_subject_columns.py` rewrote the twenty subject columns in
`rule-16-1-tracker.csv` to equal `reached` in `subject-treatment.csv`, which is the
migration the codebook committed to. Mapping: `reached` TRUE to `YES`, FALSE to
`NOT_ADDRESSED`, because silence is never coded `NO`.

**27 of 280 cells changed**, matching the reconciliation recorded earlier today exactly.

| change | cells |
|---|---|
| `NOT_ADDRESSED` to `YES` | 19 |
| `UNCLEAR` to `YES` | 4 |
| `YES` to `NOT_ADDRESSED` | 4 |

The 19 upgrades are 14 incorporation-clause corrections (11 in MDL 3167, 3 in MDL 3171)
and 5 substantive upgrades from the full-text read: `b2d_direct_filing` in MDLs 3166, 3172
and 3181, `b3d_pretrial_motions` in MDL 3166, `b2a_selection_procedure` in MDL 3178. The 4
`UNCLEAR` cells were resolved by reading the orders in full. The 4 downgrades follow two
rules applied uniformly: setting the initial conference is not a schedule for *additional*
conferences, and leadership timing is express only on a stated calendar.

MDLs 3176 and 3187 were left untouched at `PENDING` across all twenty, having no
subject-level coding. **MDL 3180's twenty cells needed no change**, which is a small
independent check on the coding: its order-level values had been recorded from the same
document a day earlier and agreed with the subject-level pass on every subject.

### Three safeguards, each verified

**Byte fidelity.** The file uses CRLF terminators. A no-op round trip through
`csv.DictWriter` with the default terminator was confirmed byte-identical before the
migration ran, so the diff contains only intended changes: 7 of 18 lines, 132 bytes.

**Non-destructive by design.** The migration is a one-shot script, not a build step.
`build.py` writes `index.html`; letting it also write the data file would risk clobbering
hand-maintained columns on an unrelated run. Instead `build.py` now calls
`assert_subject_columns()` and exits non-zero on any divergence. Mutation-tested: flipping
one cell in the order layer trips the build with the cell named.

**Two code paths, one answer.** The site's coverage figures are computed from the
subject-level table; the older figures are computed from the order-level `TOPICS` columns.
After migration both paths return citing median 19, spread 18 to 19, non-citing median 11,
spread 4 to 14. They agreed cell for cell, which is what makes the order layer safe to
treat as derived.

Re-running the migration now reports 0 cells changing, so it is idempotent.

---

## 12 August 2026 — codebook reliability section amended

Scope of the amendment: **no field definition, logical constraint, derived view or metric
changed.** The freeze holds and pass 1 stands. What changed is the description of pass 2,
which was written for a human coder working over weeks and does not describe what pass 2 can
actually be here. The original text is quoted inside the amendment so it can be audited.

Substance: pass 2 is relabelled an **independent re-code**, not intra-rater reliability. A
washout period does nothing when the first pass was executed in one session by a model, and
a fresh session is closer to a second rater from the same population than to the same rater
later. The amendment records the design that would actually be informative, a human coding a
stratified sample of about fifty cells blind to pass 1, and says plainly that sealing
`coding-decisions.md` is not the same as forgetting it.

### Ex post contestability map, recorded before pass 2

Added to the codebook alongside the untouched ex ante prediction. Every coding note that
invokes an application rule, records a partial resolution, rejects an adjacent provision,
invokes the instruction to undercount, or says a rebuilder could flip the row counts as
contestable.

| | cells | share |
|---|---|---|
| Contestable by any marker | 41 of 280 | 15% |
| Of which `court_resolution` is TRUE | 20 of 41 | 49% |
| `court_resolution` TRUE across all cells | 62 of 280 | 22% |

Contestable cells are more than twice as enriched for resolution decisions as the corpus,
which is the direction the ex ante expectation predicted. The concentration by subject is
sharper than predicted: `b3d_pretrial_motions` alone is 12 of the 41, every one turning on
application rule R2.

By order, contestability tracks how operative the order is, not how thin it is. MDL 3181 has
8 and MDL 3166 has 6; the pure transcription orders, MDLs 3170 and 3174, have 1 each. An
order that only reproduces the Rule's list is nearly mechanical to code. An order that
decides things is where the definitions have to work.

A narrower count, the 7 cells where pass 1 explicitly recorded doubt rather than merely
applying a rule, points at `express` instead. Both are recorded because they disagree.

---

## 12 August 2026 — the pre-effective-date question, answered

`PROTOCOL.md` called this "the largest unclaimed finding left in the project": **has any
court invoked Rule 16.1 in an MDL centralized before December 1, 2025?** Firms are split on
whether the Rule reaches pending MDLs and nobody has counted.

Method as specified in Guardrail 10, executed 12 August 2026. Both query forms, RECAP
document text, `filed_after=2025-12-01` retained.

| Query | Hits |
|---|---|
| `"Fed. R. Civ. P. 16.1"` | 25 |
| `"Federal Rule of Civil Procedure 16.1"` | 28 |

### The answer is zero

**No hit sits in an MDL centralized before December 1, 2025.** Every MDL hit resolves to one
of the seven post-effective-date MDLs already in the universe, or to one of their member-case
dockets carrying the same order.

Three member-case clusters were verified individually rather than inferred from the
sequential document IDs that suggested them:

| Docket | Case | Court | Filed | Belongs to |
|---|---|---|---|---|
| 72025969 | Price v. Cal-Maine Foods | W.D. Wis. | 2025-12-11 | MDL 3175 |
| 72249068 | Re v. The Boeing Co. | W.D. Wash. | 2026-02-09 | MDL 3174 |
| 73197949 | Unified Gov't of Wyandotte County v. REV Group | E.D. Wis. | 2026-04-15 | MDL 3179 |

**Limits, which matter for a null.** RECAP coverage is incomplete and text layers are
missing on some documents; MDL 3180's own order had no text layer and would not have been
found by this search. Only the two specified query forms were run, so an order writing
"FRCP 16.1" or a bare "Rule 16.1" would be missed, and Guardrail 10 explains why the bare
form is unusable. The honest claim is therefore: **across both specified query forms, every
Rule 16.1 invocation captured in RECAP's text index since the effective date sits either in a
post-effective-date MDL or in a case that is not an MDL at all.** That is a real datum on a
live dispute, and its value depends on the limits being stated with it.

### What the noise turned out to contain

Guardrail 10 predicted the index would not distinguish `16.1` from `16`. It was right about
19 of the 25 abbreviated-form hits, which are ordinary Rule 16 scheduling material in
S.D.N.Y., E.D.N.Y., S.D. Ind., and E.D. Mich. **Every one was verified by literal search
rather than assumed**, in five batches, and all returned zero occurrences of the string
"16.1" except the E.D. Mich. filing, which cites Rule 16 and E.D. Mich. Local Rule 16.1
correctly.

### The finding that came out of the noise: RULE 16.1 IS BEING CITED OUTSIDE MDL PRACTICE

Four orders, one magistrate judge, five and a half months, all in the District of New Jersey,
all in ordinary two-party civil cases with no JPML involvement. Now `INV-006` through
`INV-009` in `party-invocations.csv`.

| | Case | Docket | Order filed |
|---|---|---|---|
| INV-006 | DeBartolo v. Borough of Palisades Park | 2:26-cv-01394 | 2026-02-17 |
| INV-007 | Obuygyei v. Bonsu | 2:26-cv-01564 | 2026-04-27 |
| INV-008 | Meisner v. First Advantage Background Services | 2:26-cv-03194 | 2026-06-24 |
| INV-009 | Rinaldi v. N.J. Dep't of Children and Families | 2:26-cv-05694 | 2026-07-30 |

Each is a chambers letter order setting an initial scheduling conference. INV-007 is
captioned **"LETTER ORDER PURSUANT TO RULE 16.1."** Each cites, verbatim:

> "See Fed. R. Civ. P. 16.1 and L. Civ. R. 16.1(a)."

Rule 16.1(a) by its terms operates "[a]fter the Judicial Panel on Multidistrict Litigation
transfers actions." None of these four cases involves a transfer, a consolidation, or a
class. A civil rights removal, a Section 1983 action, a background-check case, and a
two-party dispute.

**Why this is the number collision, not a coincidence.** D.N.J. has its own Local Civil
Rule 16.1(a), which is the district's scheduling-conference rule and is cited correctly in
the same sentence. The federal companion cite of the same number sits beside it. The project
first recorded this collision as a search trap in `collect.py`, then as a substantive
phenomenon when MDL 3180 displaced D.N.J. Local Civil Rule 16.1 expressly. This is the third
form it takes, and the only one where the Rule is applied to cases it does not reach.

Recorded as observed. No inference is drawn about intent, and the orders are described by
what they say.

**Why it is worth publishing.** It is a concrete, checkable instance of rule numbering
producing citation error in a district with a same-numbered local rule, which is the kind of
practice datum a rules committee can act on. It is also a caution for anyone counting Rule
16.1 uptake by search: four of the twenty-five abbreviated-form hits are genuine citations to
the Rule in cases the Rule does not govern.

**Not generalised.** Four orders, one judge, one district, found through a search Guardrail
10 warns is imprecise. Whether other D.N.J. judges do the same, and whether other districts
with same-numbered local rules show the same pattern, is unexamined.

---

## 12 August 2026 — a third query form, and what it cost the null

After the two query forms Guardrail 10 specifies were complete and the null was written up,
I ran a third that the protocol does not list: **`"FRCP 16.1"`**. It returned **4 hits that
neither specified form returned.**

That is a finding about the method before it is a finding about the Rule. Guardrail 10 was
written to stop a false positive problem, the index not distinguishing `16.1` from `16`. It
did not anticipate a false negative problem: courts and counsel abbreviate the Rule's name in
at least three ways, and a two-form search misses one of them. **The project's own
"uptake measured by full-text search is biased upward" finding now has a companion: it is
also biased downward, by naming form.**

### What the four hits are

**Two are a Rule 16.1 report the dataset did not have.** MDL 3175, ECF 74 on the master
docket, filed 27 April 2026: "Joint Report for Initial Judicial Management Conference
Pursuant to FRCP 16.1," filed by plaintiffs. Now `INV-010`, the **third** Rule 16.1 report
located and the second filed by one side rather than jointly across sides. Judge Peterson's
order required a joint report from all parties; what arrived was a plaintiffs' report plus a
separate defendants' statement (`INV-004`). That bears directly on the published finding that
parties are departing from Rule 16.1(b)(1)'s single-report structure.

**Two are unverified and the null now discloses them.** Recap documents 470618735 and
468438384 on docket 71985711, orders granting discovery-extension stipulations before
Magistrate Judge Maximiliano D. Couvillier III. Whether the "16.1" in them is the federal rule
or a local rule is **UNCHECKED**: the CourtListener daily cap of 125 requests was reached
mid-call. Docket 71985711 carries a lower internal ID than dockets filed 11 December 2025, so
it cannot be assumed to postdate the effective date.

Almost certainly a local rule in an ordinary civil case. That is a prediction, not a finding,
and the dataset does not record predictions.

### Consequences, applied rather than noted

**The site claim was already published and is now corrected.** It read "both forms ... returns
53 hits." It now reads three forms, 57 hits, and states that two hits on one docket are still
being checked. Leaving the old sentence up would have been literally true and materially
misleading, which is the failure mode this audit log exists to catch.

**Search results are now data.** `rule-16-1-searches.csv` records each query form, the date
run, the corpus, the date filter, the hit count, and the triage outcome including an explicit
`hits_unverified` column. `build.py` asserts the site's figures against it, and three
mutation tests confirm the guards fire: altering the hit count, zeroing the unverified count,
or deleting a query form each trips the build. Before this, those numbers were the only public
figures on the page with no file behind them.

**`INV-010` is recorded with every content field marked `NOT_CHECKED`** rather than left out
until it could be read. A row that exists with honest gaps is better than a silent absence,
and the gaps name the document ID to read.

### Open, in priority order, when the cap resets

1. **Read recap documents 470618735 and 468438384.** Until then the null carries a disclosed
   hole. This is the only item blocking a clean claim.
2. **Read recap document 477258878** and complete `INV-010`.
3. **Run further naming forms** before treating the uptake count as complete:
   "Fed.R.Civ.P. 16.1" without spaces, and "Rule 16.1 of the Federal Rules of Civil
   Procedure". The third form found four documents; there is no reason to think a fourth
   would find none.
4. **MDL 3187**, still blocked, RECAP re-checked today with nothing available.

---

## 13 August 2026 — the two unverified hits resolved; the null is clean

Recap documents 470618735 and 468438384, the only thing standing between the project and an
unqualified pre-effective-date null, are read. Both recite the same stipulation language:

> "All parties have made their initial and supplemental disclosures pursuant to FRCP 16.1."

The docket is **Evans v. United Natural Foods, Inc.**, No. 2:25-cv-02393 (D. Nev.), filed
2 December 2025, diversity personal injury, `mdl_status` empty. **Not an MDL.**

**The null therefore holds without qualification.** Across all three query forms and 57 hits,
no Rule 16.1 invocation captured in RECAP since the effective date sits in an MDL centralized
before it. `rule-16-1-searches.csv` now shows `hits_unverified` at zero, and the site sentence
that disclosed the open check has been replaced.

The prediction recorded yesterday was that these would turn out to be a local rule in an
ordinary civil case. Half right: ordinary civil case, but the citation is to the federal rule
by name, "FRCP 16.1." The dataset records what happened, not what was predicted.

### A second district, and a second mechanism

These two are now `INV-011` and `INV-012`, and they change the shape of the miscitation
finding rather than merely adding to it.

| | Actor | What the Rule was cited for | Where |
|---|---|---|---|
| INV-006 to INV-009 | The **court** | Authority for an initial scheduling conference | D.N.J., one magistrate judge, 4 orders |
| INV-011, INV-012 | **Counsel**, in a stipulation the court granted | Having made initial and supplemental disclosures | D. Nev., 2 orders |

Initial disclosures are governed by Rule 26(a)(1). Rule 16.1 says nothing about them.

Yesterday's finding was four orders, one judge, one district, and was flagged as not
generalised. It is now six orders, two districts, two different actors, and two different
propositions the Rule does not support. The D.N.J. instances are explicable by the local-rule
number collision; the D. Nev. ones are not, since D. Nev. has no Local Rule 16.1 in play in
that sentence. What the two share is a new rule number entering circulation faster than
accurate knowledge of what it covers.

The second D. Nev. order repeats the first a month later, so the miscitation was carried
forward rather than corrected.

**Still not generalised.** Six orders, three judges, two districts. The systematic question,
whether districts with a same-numbered local rule show this more than districts without one,
is unexamined and is in Monday's watch task.

---

## 13 August 2026 — the naming-form sweep completed, and it changes a published number

Four further forms run, closing the query set opened yesterday.

| Form | Hits | Documents no earlier form returned |
|---|---|---|
| `"Fed. R. Civ. P. 16.1"` | 25 | 25 |
| `"Federal Rule of Civil Procedure 16.1"` | 28 | 28 |
| `"FRCP 16.1"` | 4 | 4 |
| `"F.R.C.P. 16.1"` | 0 | 0 |
| `"Rule 16.1 Report"` | 11 | 11 |
| `"Fed.R.Civ.P. 16.1"` | 25 | **0** |
| `"Rule 16.1 of the Federal Rules of Civil Procedure"` | 0 | 0 |

**The published figure was wrong and is corrected.** The site said 57 hits across three forms.
The union across all seven is **68 unique documents**. Summing per-form hits gives 93, which
double-counts; `rule-16-1-searches.csv` now carries a `new_documents` column so the union is
computed rather than added up, and `build.py` asserts the site against it.

### Three things worth more than the corrected count

**The productive forms are mutually exclusive.** Verified by comparing full ID sets: the
abbreviated form, the spelled-out form, the FRCP acronym, and the report phrase share **not one
document** between them. A filing commits to one way of naming the Rule. Any single-form search
therefore returns a strict subset and gives no signal about the size of what it missed. The
project's existing finding that phrase search is biased upward now has a sharper companion: it
is also biased downward, by an amount a single-form search cannot estimate.

**Two of the seven forms are not distinct queries.** `"Fed.R.Civ.P. 16.1"` returns exactly the
same twenty-five documents as `"Fed. R. Civ. P. 16.1"`. The index normalises internal spacing.
It does not normalise periods inside an acronym, since `"F.R.C.P. 16.1"` returns zero while
`"FRCP 16.1"` returns four. Recorded so no future run spends a call rediscovering it.

**Hits are not filings.** The eleven `"Rule 16.1 Report"` documents are one filing, the
Defendants' Statement in MDL 3175 already recorded as `INV-004`, replicated across the master
docket and ten member dockets. Counting documents would have inflated the invocation layer by
ten. The null is unaffected: all eleven are a post-effective-date MDL.

### INV-010 is a hard block, not a rate limit

Retried once the daily cap reset. **Neither copy of the MDL 3175 plaintiffs' report has a text
layer** — `read_document` returns "No text is available" for the master-docket copy (477258878)
and the member-docket copy (477258871). Same failure mode as MDL 3180's order and MDL 3187's
documents, and it needs a PACER or Bloomberg pull rather than another CourtListener attempt.
The row's identity fields come from the docket entry text and are reliable; every content field
stays `NOT_CHECKED`.

That makes **three** documents in this project blocked by a missing text layer, which is worth
stating plainly as a coverage limit rather than treating as bad luck: RECAP's text coverage is
the binding constraint on this dataset, not RECAP's document coverage.

---

## 13 August 2026 — the pass 2 instrument, built and self-tested

The amended reliability protocol says the only design that measures whether the codebook
travels to a different reader is a human coding a blind sample. That instrument now exists.

**`reliability-sample.csv`** — 50 cells, stratified so every one of the 14 orders appears
(three or four cells each), drawn with a fixed seed so the sample is reproducible and
auditable. 18 of the 20 subjects are represented. Rows are shuffled rather than grouped by
order, so the coder does not work down one order at a time and carry an impression forward.

Each row carries the MDL number, a full citation to the source document, the subject id, and
the Rule's own text for that subject, so it can be coded from the sheet without cross-
referencing anything. The four boolean columns are blank.

**It is blind, and that was checked rather than assumed.** A leak test greps the finished
file for `TRUE`, `FALSE`, `¶`, `INCORPORATED` and `IDENTIFIED`; all absent. No pin cite, no
quotation, and no coding note from pass 1 appears anywhere in it.

**`score_reliability.py`** — reports per attribute: raw agreement, disagreement count,
Cohen's kappa, and each coder's TRUE prevalence. Writes every disagreement to
`reliability-disagreements.csv` with pass 1's pin cite, quotation and coding note attached,
plus an empty `resolution` column, because the protocol requires each disagreement to end as
either a codebook amendment or a recorded ambiguity.

Self-tested two ways. Fed a copy of pass 1 back to itself it returns 100% and kappa 1.000 on
all four attributes, and prints a warning that a perfect score on 50 cells is itself a reason
to check the sample was coded blind. With six deliberate flips injected it returns 97%
overall, correctly localises them (three in `court_resolution`, matching where the ex ante
prediction says disagreement should land), and writes the disagreement file.

The script says in its own docstring what it does not measure, so a later reader cannot
mistake it for intra-rater reliability, and it explains why kappa is printed next to raw
agreement rather than instead of it: `reached` is TRUE in about three quarters of cells, and
at that prevalence kappa punishes near-total agreement.

**Handoff.** Zach codes the 50 cells without opening `subject-treatment.csv`, then runs
`python3 score_reliability.py`. Nothing else in the project depends on it, so it can wait.

### Blocked routes re-checked today, both still closed

- `ksd.uscourts.gov/special-cases/` lists five matters and MDL 3187 is not among them.
- `njd.uscourts.gov/mdl-cases` exists and lists eleven MDL pages, but not MDL 3180. Worth
  knowing that the district does maintain such pages, including for recent MDLs 3055, 3080
  and 3113, so one may appear for 3180 later. The correct URL is recorded here because
  `/multi-district-litigation`, tried on 12 August, returns 404.

### A contradiction the new finding introduced, caught and fixed

Adding the naming-form finding put two claims on the page that could not both be true. The
older finding read:

> "A phrase search cannot understate a rule's uptake, which is a limit on the method rather
> than a fact about this Rule."

That sentence is now false on this project's own evidence. A phrase search understates uptake
whenever the corpus splits across naming forms, which it demonstrably does: the four
productive forms share no document.

The two findings are not really in conflict once the quantities are separated. Selecting
cases by the phrase inflates the **rate**, because the sample is drawn on the dependent
variable. Searching one naming form deflates the **count**, because the forms are disjoint.
Both are limits on the method, they pull in opposite directions, and neither corrects the
other. The finding has been rewritten to say exactly that.

Recorded because it is the second time today that adding a true finding made an existing
sentence false. The lesson is narrow and worth keeping: after adding a finding, re-read the
neighbouring ones for claims the new evidence has quietly undermined. The prose guards in
`build.py` cannot catch this class of error, since both sentences reconcile against the data
individually.

---

## 13 August 2026 — the local-rule collision hypothesis, tested and partly disconfirmed

The miscitation finding came with an explanation attached: districts with a same-numbered
local rule produce citations to the federal Rule 16.1 in cases it does not reach. That
explanation was plausible and untested. It is now tested, and it does not survive intact.

### Verified: which districts actually have a Local Rule 16.1

`collect.py` has warned since the project began that D. Mass. and S.D. Fla. each have a local
Rule 16.1 that floods a bare `"Rule 16.1"` query. That was an unverified assertion sitting in
the published methodology. Both are now confirmed against the rules themselves.

| District | Rule | Title | Miscitation instances found |
|---|---|---|---|
| D.N.J. | L. Civ. R. **16.1** | scheduling conferences, cited at 16.1(a) in the orders | **4** |
| D. Mass. | L.R. **16.1** | "Early Assessment of Cases" | 0 |
| S.D. Fla. | L.R. **16.1** | "Pretrial Procedure in Civil Actions" | 0 |
| D. Nev. | LR **16-1** (hyphen) | "Scheduling and Case Management" | **2** |

### The hypothesis explains four of six instances and fails on two

**D. Mass. and S.D. Fla. are the control cases, and they are clean.** Both have an exact
same-numbered local rule about pretrial scheduling, which is precisely the configuration said
to cause the error, and neither produced a single instance in the corpus. A collision is
evidently not sufficient.

**D. Nev. is the disconfirming case, and it is the more interesting one.** D. Nev. numbers its
local rules with hyphens, so there is no rule "16.1" to collide with at all. More to the point,
the proposition being cited was that the parties made initial and supplemental disclosures.
That is governed by Fed. R. Civ. P. 26(a)(1) and by D. Nev. LR **26-1**, "Discovery Plans and
Mandatory Disclosures." Nothing numbered 16 is in the neighbourhood. The number collision
cannot be what pulled counsel toward "FRCP 16.1."

### What survives

The D.N.J. instances remain well explained by the collision: the court's own sentence pairs
"Fed. R. Civ. P. 16.1" with "L. Civ. R. 16.1(a)," and the local rule is the correct authority
for what the order actually does.

The D. Nev. instances need a different account, and the honest one is thinner: a new rule
number entered circulation and was reached for on a subject it does not cover. That is a
weaker claim than a mechanism, and it is stated as such.

**A prediction worth recording before it can be checked retrospectively.** If the collision
hypothesis has any force, D. Mass. and S.D. Fla. should eventually produce instances as the
Rule becomes more familiar, and they should look like D.N.J.'s: a court, in a scheduling
order, pairing the federal and local rules. If instead the next instances look like D. Nev.'s,
scattered across subjects with no numbering pattern, then familiarity rather than collision is
doing the work. Monday's watch task checks both districts.

### Scope of this test

Six instances is not a sample. The four-district comparison rests on RECAP's text coverage,
which this project has already found to be the binding constraint, and on three query forms
that turn out to be mutually exclusive. A district could be producing these orders without a
single one being searchable. The table above is what the corpus shows, not what the courts do.

---

## 13 August 2026 — a numeral audit of the page, and one gap closed

`build.py`'s prose guards catch a figure that goes stale, but only for sentences someone
thought to guard. Nothing had ever checked for the gaps. `audit_numbers.py` now does: it
extracts every numeral from the visible findings prose and reports the ones that appear in no
guard literal and in no prerendered span.

**34 distinct numerals, 9 unasserted.** Eight are legitimately outside the data and belong
in the assertions ledger rather than in a guard: the JPML's 158 pending MDLs, the industry
count of 340,000 actions, rule numbers, dates, and the rhetorical "an apparent 100%."

**One was a real gap. "61 variables" appears three times, including inside the schema.org
JSON-LD, and is simply the column count of `rule-16-1-tracker.csv`.** Nothing tied it to the
file. Add a column and the page would have kept saying 61 while serving 62, and the structured
data a search engine reads would have been wrong with it. Now guarded in both places and
mutation-tested: adding a scratch column to the CSV trips the build.

The script's own docstring records what it cannot do, which is the more important half. It
cannot tell whether a guarded number is the *right* number, and it cannot tell whether two
guarded sentences contradict each other. Both failures have happened here in two days: the
"57 hits" figure was guarded and wrong, and the phrase-search finding was guarded and
contradicted by a new one. Guards catch staleness, not error.

---

## 13 August 2026 — the search filter was wrong, and it manufactured a null

**This is the most serious error the project has made. A published headline finding was
false, and the method that produced it could not have produced any other answer.**

### What was published

> **No court has applied Rule 16.1 to an MDL that predates it.** Practitioner commentary is
> divided on whether the Rule reaches MDLs centralized before December 1, 2025. Searching the
> full text of federal court filings for seven different forms of the Rule's name, limited to
> documents filed on or after the effective date, returns 68 documents. Every one sits in an
> MDL centralized after that date, in a member case of one, or in a case that is not an MDL at
> all. None is a pre-Rule MDL, and Zero hits remain unverified.

### What the query actually did

Every row of `rule-16-1-searches.csv` was run with `filed_after=2025-12-01`. In CourtListener's
RECAP index that parameter restricts by the date the **case** was filed. The document-level
filter is `entry_date_filed_after`. The sentence "limited to documents filed on or after the
effective date" described something the query did not do.

A pre-Rule MDL is, by definition, a case filed before the effective date. So the filter removed
the entire population the finding was about, the search returned none of them, and the absence
was written up as a result. The null was circular. It could not have failed.

Measured the same day, same index, same query string:

| form | `filed_after` | `entry_date_filed_after` |
|---|---:|---:|
| `"Fed. R. Civ. P. 16.1"` | 25 | **41** |
| `"Federal Rule of Civil Procedure 16.1"` | 28 | **35** |
| `"FRCP 16.1"` | 4 | **6** |
| `"F.R.C.P. 16.1"` | **0** | **8** |
| `"Rule 16.1 Report"` | 11 | **13** |
| `"Fed.R.Civ.P. 16.1"` | 25 | 41 |
| `"Rule 16.1 of the Federal Rules of Civil Procedure"` | 0 | 0 |
| **union** | **68** | **101** |

The diagnosis is not inferred. For every form, the old count is *exactly* the subset of the
corrected result whose docket `date_filed` falls on or after the cutoff — 25, 28, 4, 0 and 11
reproduce to the document. That reconciliation is in `CORRECTION-NOTES.md`.

### The counterexample

*In re Change Healthcare, Inc., Customer Data Security Breach Litigation*, MDL No. 3108,
0:24-md-03108-DWF-DJF (D. Minn., Frank, J.), centralized June 2024. **Pretrial Order No. 28,
Doc. No. 540, filed 19 March 2026**, one page:

> "Pursuant to the Court's Pretrial Order No. 2 (Doc. No. 69 ¶ 12) and consistent with Federal
> Rule of Civil Procedure 16.1 aimed at providing case-management guidance in MDLs, the Court
> directs the parties to place the following items on the agenda for the March 24, 2026 Status
> Conference"

Recorded as INV-013. Also recorded: INV-014 and INV-015, two party filings in MDL 3084 (Uber,
N.D. Cal., centralized October 2023), one of them a 44-page joint discovery letter brief in
which **both sides** argue from the Rule 16.1 committee notes.

Note what the corrected finding does **not** say. PTO 28 says "consistent with," and spends
"pursuant to" on the court's own earlier order. This is a court aligning with the Rule as
guidance, not holding that it governs a pre-existing MDL. Reporting it as "Rule 16.1 applies
retroactively" would be the mirror image of the error being corrected, and the finding on the
page is written to foreclose that reading.

### Three further findings were wrong, all in the same direction

1. **"F.R.C.P. 16.1" returns zero.** It returns eight. A claim about how the index handles
   punctuation rested entirely on a zero the filter produced. The narrower claim survives: the
   eight are disjoint from the `"FRCP 16.1"` results, so periods really are not normalized.

2. **"Not one document in the corpus names the Rule two different ways."** One does. RECAP
   464150837 — the Rule 16.1 report in MDL 3170, which this project had *already recorded as
   INV-002* — uses the abbreviation, the period-separated acronym and the phrase "Rule 16.1
   Report" in thirteen pages. The sweep never returned it, because MDL 3170's docket carries
   the filing date of its lead member case, 28 August 2025. **The search was blind to a
   document already in the dataset.** Nothing flagged the inconsistency, because the two layers
   were never reconciled against each other.

3. **The local-rule collision hypothesis was recorded as failing.** The control test — do
   D. Mass. and S.D. Fla., each with a Local Rule 16.1, generate 16.1 references? — was run
   under the same broken filter and returned zero. Under the correct filter a bare `"Rule 16.1"`
   query returns **2,164 dockets**, dominated by exactly those districts. The hypothesis is
   well supported, not refuted. The entry recording it as refuted is superseded; the control is
   now logged as the `bare_rule` REFERENCE row in `rule-16-1-searches.csv`.

### What is now on the page

The null is replaced by a positive finding about MDL 3108, followed by a new finding that
states the methodological failure plainly, because a reader who relied on the old claim is
owed the reason it changed. Counts corrected to 101 documents with **29 unverified** — the
newly exposed documents have not each been read, and the page says so rather than implying the
old "Zero unverified."

`rule-16-1-searches.csv` now carries `search_type`, `date_filter` and `status` columns and
retains all seven superseded rows marked `SUPERSEDED`, so the error is inspectable in the data
and not only in this log. `search_stats()` refuses to compute from anything but `CURRENT` rows.

### The lesson, stated so it is usable

**A null result is only as good as a demonstration that the search could have returned a
counterexample.** This one never had that demonstration. Nobody asked what the filter would do
to a case filed in 2023, and the parameter name — `filed_after`, next to a corpus of documents
— read as though it answered the question.

The project's existing defences all passed while the finding was false. Prose guards checked
that 68 matched the CSV; the CSV said 68. The numeral audit checked that figures were asserted;
they were. Validation checked logical constraints; they held. **Every check verified internal
consistency, and the error was upstream of all of them, in the relationship between a query and
the world.** Guards catch staleness. Only an adversarial question catches this.

Added to the protocol as a standing requirement: any null in this project must be accompanied
by a recorded positive control showing the method returning a known instance of the thing said
to be absent.

---

## 13 August 2026 — triage of the newly exposed documents, part 1 of 2

Eleven of the 29 documents the corrected filter exposed have now been read. The pattern is
mostly reassuring and contains one real addition.

**Nine are Rule 16 noise.** RECAP 462266622, 465828995, 461413897, 467474059, 485442538,
461253327, 462306811, 480535618 and 472234065 contain **no literal "16.1" anywhere in their
text**, checked by string search rather than assumed. They are ordinary scheduling and
discovery filings citing Rule 16, returned because the index does not treat `16.1` as a token
distinct from `16`. This is Guardrail 10 operating exactly as it was written to, and it is why
the sweep's raw hit counts have never been reportable as a measure of anything.

**Two are court orders in MDL 3170 and were already known.** RECAP 462459060 is Case
Management Order #2 of 18 December 2025 — "Pursuant to Fed. R. Civ. P. 16.1, the parties are
directed to meet and confer and submit a report addressing the parties' views on the following
matters" — and RECAP 464150837 is the Rule 16.1 report answering it, recorded since INV-002.
Both were in the dataset already. **The sweep had never returned either**, because MDL 3170's
docket carries the filing date of its lead member case, 28 August 2025.

**One is new and it extends a published finding.** *Tesoro High Plains Pipeline Company, LLC
v. United States*, 1:21-cv-00090 (D.N.D.), RECAP 479971934, filed 20 May 2026. An ordinary
civil case begun in April 2021, not an MDL. The motion asks the court to set a status
conference and cites "Local Civil Rule 16.1; **Fed. R. Civ. P. 16.1(a)**." Three pages later
the same brief cites the same local rule alongside "Fed. R. Civ. P. 16(a)(1), (2)," which is
correct.

One document, both versions. That is the local-rule collision hypothesis operating inside a
single filing, and it is the best evidence for the hypothesis the project has: not two
different lawyers making different choices, but one lawyer citing the neighbouring federal
rule correctly in one paragraph and incorrectly in another, next to a local rule numbered 16.1
both times. Recorded as INV-017.

**It also broke a count that had been right by accident.** The finding reads "Six orders across
two districts." Every outside-scope record until now happened to be a court order, so a single
count served for both orders and party filings. INV-017 is a party's motion. `invocation_stats`
now splits them: six court orders across two districts, plus one party filing in a third. The
resemblance to the filter error is worth naming — a figure that was correct only because the
world had not yet produced the case that distinguished it, with nothing in the code recording
which of the two things it meant.

`assert_search_arithmetic()` added to `build.py`: for every current query form, the five triage
columns must sum to `hits`, and a duplicate form must carry zeroes across all five so the union
is not double counted. The build now refuses if a document is triaged into two categories or
none.

Eighteen documents remain unread. The site says so.

---

## 13 August 2026 — triage complete, and a third assumption falls

All 33 documents the corrected filter exposed have now been read individually. **Zero remain
unverified.** The breakdown:

| what it turned out to be | n |
|---|---:|
| No literal "16.1" anywhere — ordinary Rule 16 filings | 13 |
| A local rule numbered 16.1, never the federal Rule | 7 |
| Real invocations of Fed. R. Civ. P. 16.1 | 13 |

The thirteen real invocations: two court orders in MDL 3170 (Case Management Order #2 and the
report answering it, both already in the dataset and neither ever returned by the old sweep);
four in MDL 3084 (Uber); one in MDL 3108 (Change Healthcare), which is Pretrial Order No. 28;
three in member cases of MDLs 3174 and 3175 filed before the cutoff; a third copy of the MDL
3175 report; and two non-MDL miscitations, INV-017 and INV-018.

### The index searches the clerk's docket text, not just the filing

Six of the eight results for `"F.R.C.P. 16.1"` are filings in *Garcia v. Garcia, Jr.*,
adversary proceeding 25-01354 (Bankr. S.D. Fla.). **None of the six has a text layer.** RECAP
returns "No text is available" for every one. They matched anyway, because the search index
covers the **docket entry description** — the clerk's text — alongside the document's own.

The entries read: "Notice of Filing Scheduling Report Pursuant to F.R.C.P. 16.1"; "Motion to
Proposals Pursuant to **F.R.C.P. 16.1(2)(D)**"; a response; a hearing notice; a mailing
certificate; and "Order Denying Defendant Roberto Garcia, Jr.s Motion to Proposals Pursuant to
F.R.C.P. 16.1(2)(D) as Moot." Recorded as INV-019.

`F.R.C.P. 16.1(2)(D)` designates nothing. The federal Rule runs (a), (b)(1)–(4), (c). S.D. Fla.
Local Rule 16.1 is "Pretrial Procedure in Civil Actions" and requires a scheduling report,
which is exactly what the plaintiff filed. The inference that this is the local rule under a
federal caption is strong, and it is labelled an inference in the record, because the documents
cannot be read. The court's order is **not** counted as a court invoking the Rule: it repeats
the movant's caption while denying the motion as moot.

**This overturns a conclusion reached earlier the same day.** Before the correction work
began, this project had concluded that `type=rd` could not see orders whose text lives only in
the docket entry, and that `type=r` was needed for them. That was wrong. Tested directly: a
`type=rd` search for "non-argumentative summary of the member cases," a phrase that exists only
in MDL 3178's text-only order, returns that order (RECAP 475686411). Both search types reach
docket text. There is no coverage hole of the kind suspected.

The `corpus` column in `rule-16-1-searches.csv` said "RECAP document text" on every row. It now
says "RECAP document text and docket entry descriptions," which is what was actually searched
the whole time.

**The interpretive consequence is the part that matters.** A hit can be the clerk's summary of
a filing rather than anything the filer or the judge wrote. Those are different kinds of
evidence and the project had been treating them as one. It also caught the project mildly
overclaiming in prose written hours earlier: the finding that MDL 3170's report "uses the
abbreviation, the period-separated acronym and the phrase Rule 16.1 Report" was two-thirds
right. The filing uses two of those forms. The third, "F.R.C.P. 16.1," appears only in the
clerk's entry — "STATUS Report F.R.C.P. 16.1 by Daniel Snelgrove." Corrected on the page.

### Two more counts moved

`INV-017` (D.N.D.) and `INV-019` (Bankr. S.D. Fla.) are party-side miscitations, so
`invocation_stats` now separates court orders from party filings: **six court orders across two
districts, plus three party filings across two more.** Before INV-017 every outside-scope record
happened to be a court order and one number served for both, which is the same failure shape as
the filter — a count that was right only because the world had not yet produced the case that
distinguished it.

`assert_search_arithmetic()` enforces that each query form's five triage columns sum to its hit
count, and that a duplicate form carries zeroes so the union is not double counted.

---

## 13 August 2026 — controls logged, two open MDLs re-checked, and the working copy synced

### Guardrail 11's control is now a row in the data, not a promise in a document

`rule-16-1-searches.csv` gains a `CONTROL` row. The requirement is that any null carry a run
of the same method returning a known instance of the thing said to be absent. The instance is
RECAP 472850310, Pretrial Order No. 28 in MDL 3108. Run the spelled-out form under
`entry_date_filed_after` and it comes back; run it under `filed_after` and it does not.

That discrimination is the point. A control that passes under both the broken method and the
corrected one tests nothing. This one fails on the method that produced the false null, which
is what makes it a control rather than a reassurance. If a future run of the sweep does not
return 472850310, the sweep is broken and not the record.

`search_stats()` computes from `CURRENT` rows only, so the control is counted nowhere.

### The status column is now a closed vocabulary

`assert_search_arithmetic()` rejects any status outside `CURRENT`, `SUPERSEDED`, `REFERENCE`,
`CONTROL`. Without that, `CURENT` in one row would drop it from every published figure and
nothing would complain — the same failure shape as the date filter, a query that quietly stops
seeing part of its corpus. Tested by introducing the typo; the build refuses.

### MDL 3176 — still no order, and the reservation theory needs qualifying

Master docket enumerated: 40 entries through today. No management order, no Rule 16.1
conference, 133 days since transfer. That is **inside** the 21-to-198-day range of intervals
this dataset has actually observed, so it is not evidence of delay. It is evidence that the
Rule does not compel promptness.

The tracker had explained the silence by the docket's 21 May 2026 notice that the MDL case
number "is reserved for Transfer Orders and Orders of Remand, etc." That explanation is now
qualified in the row. Entries 5 through 13 are substantive motions filed on this very docket,
and entry 27 is the court setting reply and sur-reply deadlines on a preliminary injunction.
**The court is actively managing this litigation on the master docket and has not held the
conference Rule 16.1(a) contemplates.** Read the reservation notice as boilerplate. The
negative is a real negative.

### MDL 3187 — worse than recorded, and the record now says how

116 docket entries, up from the four documents enumerated on 12 August. **Every one has an
empty description and no available document.** This is not a text-layer problem on particular
PDFs. RECAP holds the docket's shape and none of its text, so no search of any kind can reach
this MDL and no amount of query work will help. PACER, Bloomberg or Westlaw, or nothing.

Both rows carry `date_accessed = 2026-08-13`.

### Working copy synced to the user's machine

All 24 repository files written to the local project folder. The copy there had been badly
stale — `build.py` was 3,982 bytes against 31,919 here, `AUDIT.md` 8,881 against 70,354 — and
eleven files, including every one created during the subject-level coding pass, had never been
written there at all. Uploading from that folder would have published a version of the project
that predates most of this month's work.

---

## 13 August 2026 — reading the docket text changed four records

Having established that the index covers docket entry descriptions, the obvious move was to
pull those descriptions for the two productive naming forms rather than reading documents. Two
API calls covered 76 hits. It settled things no amount of document reading had.

### INV-015 was wrong and is now right

Recorded that morning as a "brief opposing a pleading restriction" in MDL 3084, alongside a
separate D. Ariz. filing counted as non-MDL because its text was identical and the connection
could not be confirmed. The docket text settles both at once:

> TRIAL BRIEF Re: Duty and Superseding Cause Issues by Jaylynn Dean (3:23-cv-06708-CRB)

**One filing, not two.** It is a trial brief in *Dean*, a bellwether member case of MDL 3084,
appearing on the transferee docket and on the originating District of Arizona docket. The
apparent non-MDL hit was the second copy.

It is also the loosest use of the Rule in the dataset, and loose in a different way from the
miscitations. INV-006 through INV-019 cite the wrong rule. This one cites the right rule for
something it does not address: Rule 16.1 governs initial management conferences, and here it
is invoked in a **trial** brief, on duty and superseding cause, as evidence that MDL procedure
favours flexibility. Worth watching as a distinct pattern.

`spelled_out` retriaged: pre-effective-date MDL hits 2 to 3, non-MDL 1 to 0.

### Three party-invocation flags resolved without opening a document

`party_invoked_rule` had sat at `NOT_CHECKED` for MDLs 3171, 3174 and 3179. Docket text
answers all three:

- **3171** — YES. "CASE MANAGEMENT STATEMENT filed by Lyft, Inc.," 12 March 2026.
- **3179** — YES. "STATUS REPORT OF ZELLE/AMC/COTCHETT PLAINTIFFS," 8 May 2026, replicated
  across the master docket and two member dockets.
- **3174** — **NO**, and this is the useful one. Both hits on that docket are the court's own
  orders of 16 April and 28 May, replicated onto member dockets. A count that read hits as
  filings would have called this a party invocation. It is the same order twice.

Five of the sixteen MDLs now carry `party_invoked_rule = YES`, up from two. The filings
themselves have not been read and nothing is coded from them beyond the fact of invocation,
which is what Guardrail 12 requires: docket text establishes that a document exists and what
the clerk called it, and nothing more.

### Two courts have issued a second order citing the Rule

MDL 3162 (D.D.C., Bates, J.) has "INITIAL PROCEDURE ORDER No. 1" of 7 January and "CASE
MANAGEMENT ORDER NO. 1: Setting initial pre-trial schedule" of 30 April, both returned by the
naming form. MDL 3174 (W.D. Wash., Robart, J.) has its 16 April order and a 28 May scheduling
order. Neither is the MDL 3163 or MDL 3175 pattern, where a court that ignored the Rule in its
first order reached for it later. These are courts that cited it and kept citing it.

That distinction now has four instances behind it and is worth a finding once the remaining
post-effective-date hits are separated into first orders, later orders and party filings. That
separation is the open analytic gap and it is in the weekly task.

---

## 13 August 2026 — MDL 3187 unblocked, coded, and it moves every headline number

The last blocked MDL is no longer blocked. **Coverage is now 15 of 16, and every order that
exists has been read.** The sixteenth, MDL 3176, has issued no qualifying order at all.

### How it was obtained, and why that matters for the record

The full public-source ladder was re-run first and every rung failed: RECAP holds no document
for any of the six orders; CourtListener's opinion database does not have it, confirmed
indirectly through Legal Data Hunter, whose US federal coverage is CourtListener-derived;
ksd.uscourts.gov returns 404 for the MDL page and for the court's MDL index; Justia and
PACERMonitor carry case metadata and route the docket sheet back to PACER; govinfo's USCOURTS
collection carries opinions, not management orders. CourtListener's `recap-fetch` endpoint,
the one programmatic route to PACER, requires `pacer_username` and `pacer_password`.

The order came from Bloomberg Law, in the user's own authenticated browser session, opened in
the document viewer rather than downloaded. Text extracted from the viewer and stored at
`sources/mdl3187-doc9-initial-procedure-order-no1.txt` with page breaks preserved. This is the
second order in the dataset obtained outside RECAP, after MDL 3180.

### The order

**INITIAL PROCEDURE ORDER NO. 1**, ECF 9, 15 July 2026, ten pages, Melgren, J. The same title
Judge Bates used in MDL 3162, which is worth noting given how much of this dataset is courts
borrowing each other's forms.

**All twenty subjects reached, all twenty express, seven resolved.** Seven is the joint highest
in the dataset. ¶ 4 makes "[t]he items listed in Federal Rule of Civil Procedure 16.1" a
tentative agenda **alongside** five sections of the Manual for Complex Litigation, Fourth, and
¶ 6 then re-states every topic in the court's own words as required content of a mandatory
joint report. This is the first order to put the Rule and the Manual side by side as co-equal
agenda sources rather than choosing between them, which cuts against the reading that
non-citing courts use the Manual *instead* of the Rule.

Resolutions, each under a sealed pass-1 rule: `b2a_selection_procedure` (¶ 6(a)(viii) imposes
an application procedure rather than asking about one), `b2b_vacate_modify` (¶ 14),
`b2d_direct_filing` (¶¶ 1 and 20), `b3b_factual_basis_exchange` (R1, on the MDL 3162 facts
exactly), `b3c_discovery` (R1), `b3d_pretrial_motions` (R2, via the ¶ 12 stay of "answer or
otherwise respond"), and `b3g_principal_issues` (¶ 7).

### Three findings this order adds

**The report goes to chambers by email.** ¶ 6 directs it to two chambers addresses; ¶ 7 says
the issue statements "will not be filed with the Clerk." Third instance of the invisible-report
problem and the most complete: neither the report nor the issue summaries will leave a docket
trace. The limitation on the page moves from 2 of 14 courts to 3 of 15.

**Paragraph 15 does not exist.** The order runs 14 then 16. Verified by regex over the
extracted text. Second numbering gap in the dataset after MDL 3180's missing ¶ 9, and unlike
that one there is no obvious donor provision to point at.

**¶ 6(m) is unique.** It directs the parties to state whether there are ongoing **criminal**
investigations or proceedings related to the allegations, and lets defendants answer ex parte
and under seal. Nothing else in the dataset asks this.

### What moved on the page

| figure | was | now |
|---|---:|---:|
| Readable orders | 14 | 15 |
| Citing | 7 of 14 | 8 of 15 |
| Coverage | 14 of 16 | 15 of 16 |
| Blocked | 1 | 0 |
| Citing-order resolution rate | 16% | 19% |
| Universal subjects | 14 of 14 | 15 of 15 |
| Least-addressed | 7 of 14 | 8 of 15 |
| Direct filing | 11 of 14 | 12 of 15 |
| Chambers-routed reports | 2 of 14 | 3 of 15 |
| Third-party funding | 0 of 14 | 0 of 15 |

Eleven of those were caught by `build.py`'s prose guards rather than by anyone remembering to
look, which is the first time the guard set has had to carry a change this wide. The
non-citing figures did not move, as expected: 3187 cites.

**The headline finding is unchanged in direction and slightly stronger.** Citing orders raise
more subjects and settle fewer of them; the gap narrows from 16-versus-28 to 19-versus-28
because 3187 resolves seven. One order does not overturn the inversion.
