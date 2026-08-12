# Project audit — 2026-08-11

> **Note added after the audit:** MDL 3180 was read later the same day and the
> headline moved from 6/13 to 7/14. The 57% pin-cite finding below is unchanged
> in substance — MDL 3180 was coded to the current standard, with verbatim
> quotations, so the well-sourced tier is now eight rows and the thin tier is
> still six.

Adversarial pass over everything built in this session: the dataset, the four
prose documents, the submission, and the landing page. Mechanical checks were
run programmatically; external claims were checked against sources where the
sources were reachable.

**Result: 4 errors fixed, 3 contradictions open, 8 assertions flagged as
unverified, and one structural finding larger than the cite-check caught.**

---

## THE STRUCTURAL FINDING

### 57% of the dataset's affirmative codes are not backed by quoted language

The cite-check ledger (F03) reported this as "six thin rows." Quantified, it is
much larger:

| | |
|---|---|
| `YES` codes across the dataset | **242** |
| In rows whose `pin_cites` contains no quoted language | **138 (57%)** |

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
3. **Four of the six citing MDLs are in this tier** (3162, 3171, 3174, 3175).
   The headline — six of thirteen — rests substantially on rows that do not meet
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

## CONTRADICTIONS STILL OPEN — these need your decision, not mine

**C1 — The block rate is published as two different numbers.**
`README.md`'s status block and `index.html` both say **13%**; README's seventh
pass says **6%**. Both are defensible and they measure different things:

- **13%** = 2 of 16 not readable (MDL 3180 + MDL 3187)
- **6%** = 1 of 16 with no public copy anywhere (MDL 3187 alone; 3180's order
  has a located free copy that simply has not been opened)

Pick one, define it in one sentence, and use it everywhere. **My recommendation
is 13%**, because it measures what a reader cares about — how much of the
universe you have actually read — and because 6% requires explaining a
`PUBLIC_COPY_LOCATED` status that exists nowhere but this project.

**C2 — `party_invoked_rule` uses `NOT_CHECKED`, which is outside the five-value
vocabulary** and is not documented in the codebook. It is the only out-of-vocab
value in any coded column. Either add it to the codebook as a sixth value
(meaning "this variable has not been examined for this row," which is genuinely
different from `UNCLEAR`) or convert those thirteen rows to blank.

**C3 — The enum columns have grown without documentation.**
`report_form` now carries seven values, `source_status` five, `rule_vocabulary`
six. Every one was added for a good reason and none is in the README codebook,
which still describes `report_form` as "`JOINT` · `SEPARATE_BY_SIDE` · `OTHER`."
Anyone reading the codebook and then the CSV will think the data is corrupt.

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
  the project.
- **"Nobody has counted"** is the premise of the whole thing. It rests on one
  preemption search. The submission hedges it correctly ("To my knowledge no one
  has assembled the population"); the landing page states it flat. Match the
  page to the letter.

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

1. **C1** — pick a block-rate definition. Five minutes, and it is publicly
   inconsistent right now.
2. **Strike or verify the two firm quotations on the landing page**, and hedge
   "nobody has counted" to match the submission's phrasing.
3. **F01** from the cite-check ledger — the unpinned "tentative agenda"
   quotation in the submission's lead example.
4. **The 57% back-fill** — one reading session, and it converts the project's
   biggest structural weakness into its strongest claim.
5. **C2 and C3** — codebook maintenance, low risk, do it before the DOI deposit
   since the codebook ships with the data.
6. Everything in `PUBLISH.md` Steps 0–4, unchanged.
