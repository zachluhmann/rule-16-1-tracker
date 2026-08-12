# Verification ledger — Rule-16.1-Advisory-Committee-Submission.docx

**Run 1 · 2026-08-11 · verified against `rule-16-1-tracker.csv` and
`party-invocations.csv`**

**Coverage:** 49 items inventoried (37 quoted passages ≥25 chars · 12 numeric
claims) · 48 traced to the dataset · 1 not traceable · 5 findings open
(0 carried forward)

**Scope of this run.** This checks the letter against *the project's own
dataset* — every quotation and figure must trace to language or a value already
recorded in the CSVs. It does **not** re-retrieve the underlying court documents;
CourtListener's daily cap (125/day) was exhausted before this pass began. Items
marked `TRACED` mean "the dataset supports this as written," not "the source
document was re-read today." Six rows were coded from documents read earlier in
the session; seven were read and quoted into the CSV directly.

---

## Findings

| ID | Status | Class | Finding | Instances | Location(s) |
|----|--------|-------|---------|-----------|-------------|
| **F01** | **FAILED** | `PIN` / `QUOTATION` | The quotation `"shall … constitute a tentative agenda"` — the **lead example of the four-posture typology in Part II.B** — appears nowhere in either CSV. It exists only in `README.md` prose. Under the project's own protocol ("a `YES` without a pin cite is not yet data"), the letter's most prominent characterization of MDL 3162 rests on an unpinned quotation. | 1 quote, but it anchors a 4-item typology | Part II.B, first bullet |
| **F02** | **FAILED** | `ARITHMETIC` / `SCOPE` | Part II.D states the transfer-to-conference interval "ranges from 21 days to 198" and lists **11 values**, inside a section framed on **13 orders**. Two rows — MDL 3178 (Subramanian) and MDL 3179 (Griesbach) — have **no recorded conference date**. The denominator is 11 of 13 and the letter does not say so. A reader will infer n=13. | 1 statement, 2 undisclosed exclusions | Part II.D |
| **F03** | **FAILED** | `PIN` | **The dataset is two-tiered and the letter does not distinguish the tiers.** Six rows carry `pin_cites` of 161–333 characters giving paragraph pointers only (3162, 3163, 3166, 3171, 3174, 3175); the other seven carry 1,308–2,406 characters with verbatim quoted language (3167, 3170, 3172, 3178, 3179, 3181, 3185). The thin six are the earliest-coded. Three of the four cited postures in Part II.B come from that tier. | 6 rows | Part II.B, II.C, II.E |
| **F04** | OPEN | `SHIP` | Unfilled placeholders: `[FULL NAME]` ×3, `[Street Address]`, `[Date]`, `[URL]`, `[DOI]`. Intentional, but `[URL]` and `[DOI]` must resolve before sending — the letter offers the dataset to the reporters at those two addresses. | 7 | letterhead; Part IX |
| **F05** | OPEN | `FORM` | Part I says the dataset codes "fifty-plus variables." The tracker has **61 columns**. Accurate but understated; "sixty" is both truer and stronger. | 1 | Part I ¶2 |

---

## Numeric claims — all reconciled against the CSV

| Claim in the letter | Dataset | Status |
|---|---|---|
| "sixteen MDLs" in the universe | 16 rows | `TRACED` |
| "thirteen" with readable orders | 13 (`TEXT_AVAILABLE` + `TEXT_ORDER_ON_DOCKET`) | `TRACED` |
| "six cite Rule 16.1" — 3162, 3167, 3170, 3171, 3174, 3175 | exact match | `TRACED` |
| "seven do not" — 3163, 3166, 3172, 3178, 3179, 3181, 3185 | exact match | `TRACED` |
| "zero of thirteen" TPLF | 0/13 | `TRACED` |
| "Every one of the thirteen … addresses leadership counsel" | 13/13 | `TRACED` |
| "Four of thirteen" front-load compensation | 4/13 (3163, 3171, 3175, 3181) | `TRACED` |
| "Two of the thirteen" route the report to chambers email | 2 (3163, 3172) | `TRACED` |
| "Two orders designate the Manual" | 2 (3172, 3181) | `TRACED` |
| "Three orders frame the … conference under Rule 16" | 3 (3179, 3181, 3185) | `TRACED` |
| "eighteen enumerated report topics" | 7 + 4 + 7 = 18 | `TRACED` |
| "seventeen of the … eighteen," omitting only (b)(3)(E) | MDL 3170 `b3e = NOT_ADDRESSED` | `TRACED` |
| Interval list: 21, 29, 42, 48, 49, 61, 65, 84, 105, 126, 198 | exact match, n=11 | `TRACED` — but see **F02** |

---

## Quotation fidelity

37 distinct quoted passages ≥25 characters, extracted from `build_letter.js`
(the letter's source text) and matched against the full text of both CSVs after
normalizing curly quotes, dashes and whitespace.

- **36 trace to the dataset.** The 19 scoring 60–98% rather than 100% are
  explained in every case by **bracketed alterations** (`[a]ttorney`, `[t]he`,
  `[u]nless`, `[w]hether`, `[i]n`) and **ellipses** — i.e. by correct quotation
  practice, which by construction cannot match raw source text.
- **1 does not: F01.**

Spot-verified individually, all `TRACED`: the MDL 3171 residual-clause quote; the
MDL 3175 incorporation quote; the MDL 3167 "Joint Case Management Report" quote;
the MDL 3174 (b)(3) label quote; the MDL 3162 census-inquiry quote; both MCL
designations (3172, 3181); the MDL 3162 joint-report and footnote-1 quotes; the
*FedEx Tariff* scope concession; the MDL 3181 common-fund quote.

---

## Could not verify

| Item | What was attempted | What this leaves open |
|---|---|---|
| Every quotation, against the **source court documents** | CourtListener daily cap (125/day) exhausted; resets ~8 hours out | The letter is verified against the dataset, not against the orders. For the seven quote-carrying rows the CSV records verbatim language captured at read time, so the exposure is small. For the six thin rows (**F03**) there is no recorded verbatim language to check against, so the exposure is real. |
| MDL 3162 "tentative agenda" quote | Searched both CSVs and README | **F01.** Re-read the order (doc 464378026, IPO No. 1, ¶3 and ¶5) and either pin-cite the language into the CSV or strike the quotation from Part II.B. |

---

## Open questions for the author

1. **F01 is the one that has to be resolved before sending.** A rules committee
   reading a submission built on quotation discipline will not check whether a
   quote is pinned — but the letter's own Part I promises that "every affirmative
   finding carries a pin cite to the document and paragraph." One does not.
2. **F03 asks a design question, not just a fix.** Options: (a) back-fill
   verbatim quotes into the six thin rows before publishing the dataset;
   (b) state the two tiers openly in Part VIII's limitations. (a) is better and
   costs about an hour of reading once the API resets. (b) is honest and free.
   Doing neither is what makes a dataset attackable.
3. **F02 is a one-clause fix**: "The eleven orders for which a conference date is
   recorded show intervals of …" — and the missing two become a disclosed fact
   rather than a silent exclusion.

---

## Notes for the next run

- Keep these IDs stable. F01–F05 carry forward until each shows `FIXED`.
- **Re-verify after any edit.** Editing after verification invalidates it.
- The next run should re-retrieve the underlying orders for at least the six
  rows in F03, since this run could not.
- If MDL 3180 gets read and the headline moves from 6/13 to 7/14, **every
  numeric row in the table above needs recomputing** — the letter states 13
  figures that depend on those denominators.
