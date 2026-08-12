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
