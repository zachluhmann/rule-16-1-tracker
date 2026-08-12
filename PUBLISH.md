# v1.0 Freeze and Publication Checklist

**Purpose:** make the dataset citable *before* the note exists. The submission in
`advisory-committee-submission.md` points at a URL and a DOI; those have to
resolve when the reporters click them.

**Target: complete by ~September 1, 2026.** The Advisory Committee on Civil
Rules meets **October 21, 2026**; its agenda book historically posts about three
weeks out (the April 14, 2026 book posted March 27), so a suggestion needs to be
in the Secretary's hands by **early September** to have a realistic chance of
appearing in that book.

---

## Step 0 — close the two open rows (do this first, it takes an hour)

- [ ] **MDL 3180.** Open
      `https://www.aboutlawsuits.com/wp-content/uploads/2026-6-11-dupixent-order-1.pdf`
      in a browser. It is the court's *Initial Procedure Order*, June 11, 2026,
      ECF 3. Read it, code the row, and **check whether it cites Rule 16.1** —
      the reported terminology ("Initial Management Report," "proposed initial
      management order") suggests it may. If it does, every "six of thirteen" in
      the submission becomes **seven of fourteen**. Search the PDF and update
      before sending.
- [ ] **MDL 3187.** One PACER session, four documents:
      ECF 2 (`07907490590`), ECF 8 (`07907513132`), ECF 9 (`07907520997`),
      ECF 10 (`07907521776`). Install the RECAP extension first so the text
      lands in the public archive. Start with ECF 2.
- [ ] Re-run the counts in `README.md` → "WHERE THIS STANDS" and **propagate any
      change into the submission.** The submission quotes eleven separate
      figures; they must match the CSV exactly on the day it is sent.

## Step 0.5 — DONE (sixth pass, 2026-08-11)

- [x] MDL 3175, Peterson's June 8 leadership order — **names the Rule, as a
      document title.** `c_order_cites_rule = YES`. Now finding 40.
- [x] MDL 3175, Defendants' Statement — read. Revealed a **third Rule 16.1
      report** (ECF 74) that exists and cannot be read. Now finding 41 and
      `party-invocations.csv` INV-004.
- [x] Bates's IPO No. 1 ¶5(g) — **includes (b)(3)(B) and expands it into a
      Rule 26(a)(1) question.** There is no propagation gap; there is a better
      finding. Now finding 42 and Part VII of the submission.

## Step 0.6 — still open, and each could still move the letter

- [ ] **MDL 3175 ECF 74** (doc 477258878) — the third Rule 16.1 report. Add to
      the PACER list. Reading it would take the report layer from N=2 to N=3,
      which is the difference between "two instances" and a pattern.
- [ ] **MDL 3179's bar-side invocation.** ECF 19 was checked and contains no
      "16.1". The invocation is attributed to a **May 8, 2026** filing that has
      not been re-identified. Find it or drop the claim — do not code from
      memory, and note that README finding 7 currently rests on it.
- [ ] **The pre-effective-date question, entirely unexplored.** `PROTOCOL.md`
      defines it and the `pre_effective_date` column exists, but no MDL created
      *before* December 1, 2025 has been checked for a Rule 16.1 invocation.
      Firms are split on whether the Rule reaches pending MDLs and nobody has
      counted. MDL 3160 (Archery Products, D. Colo.) and MDL 3161 (CCell,
      N.D. Cal.) are the two nearest the line — transferred October 2025 — and
      the query is the same one already in `collect.py`, just without the
      `filed_after` restriction. **This is the largest unclaimed finding left.**

## Step 0.7 — the cite-check ledger (run 1 complete, 2026-08-11)

`Rule-16.1-Advisory-Committee-Submission.ledger.md` holds the verification
ledger. **49 items checked, 48 traced, 1 not traceable, 5 findings open.**
Three must clear before the letter goes:

- [ ] **F01 (FAILED).** The quotation "shall … constitute a tentative agenda" —
      the lead example of the four-posture typology in Part II.B — appears
      nowhere in either CSV, only in README prose. Re-read MDL 3162's Initial
      Procedure Order No. 1 (doc 464378026, ¶¶3 and 5), pin-cite the language
      into the row, **or strike the quotation.** Part I of the letter promises
      that every affirmative finding carries a pin cite; this one does not.
- [ ] **F02 (FAILED).** Part II.D's interval range is **n=11, not 13** — MDL
      3178 and MDL 3179 have no recorded conference date, and the letter does
      not disclose the exclusion inside a section framed on thirteen orders.
      One-clause fix: "The eleven orders for which a conference date is
      recorded show intervals of …"
- [ ] **F03 (FAILED).** The dataset is **two-tiered**. Six rows (3162, 3163,
      3166, 3171, 3174, 3175) carry `pin_cites` of 161–333 characters —
      paragraph pointers with no verbatim language. The other seven carry
      1,308–2,406 characters with quotes. The thin six are the earliest coded,
      and three of the four postures in Part II.B come from that tier. Either
      back-fill quotes (about an hour once the API resets) or disclose the two
      tiers in Part VIII. Doing neither is what makes a dataset attackable.
- [ ] F04 (`SHIP`): `[URL]` and `[DOI]` must resolve before sending — Part IX
      offers the dataset to the reporters at those two addresses.
- [ ] F05 (`FORM`): Part I says "fifty-plus variables"; the tracker has **61**.

**Re-verify after any edit** — editing after verification invalidates it, and if
MDL 3180 moves the headline from 6/13 to 7/14 then all thirteen numeric claims
in the letter need recomputing.

## Step 1 — verification pass

- [ ] Re-read every row where `cites_rule = YES` and confirm the quoted language
      against the order. These six carry the headline.
- [ ] Confirm the two transcription departures against the order text and the
      official rule text. *(Both verified 2026-08-11: MDL 3174 Part III carries
      the (b)(3) label onto what is (b)(4); MDL 3170 omits (b)(3)(E). Rule text
      checked against Cornell LII. Re-verify against the official
      uscourts.gov text before sending.)*
- [ ] Confirm the two chambers-email provisions by quotation (MDL 3163, 3172).
- [ ] Back-code `party_invoked_rule` across all sixteen rows. Three are now
      `YES` (3162, 3170, 3175); thirteen are `NOT_CHECKED`. **MDL 3179 must not
      be coded `YES` from memory** — an earlier search surfaced a party citation
      but the pin cite was never captured. Likely source: ECF 19, Brief in Support
      of Motion to Confirm Appointment of Interim Leadership (May 1, 2026, doc
      477865692), or the ECF 20 declarations.
- [ ] **Do not MDL-scope the invocation queries.** *In re FedEx Tariff
      Litigation* (W.D. Tenn.) is a single-district consolidation, not a Panel
      transfer, and counsel briefs Rule 16.1 there anyway. `party-invocations.csv`
      is keyed to the filing and carries `mdl_no = NON-MDL` for exactly this case.
      An MDL-scoped query would have missed the project's most novel finding.
- [ ] Consider adding `cites_committee_note` and `cites_rulemaking_record` to the
      invocation table as first-class columns. Both located reports and the FedEx
      brief source their substance to the **Note**, not the Rule text — which is
      itself a finding about where Rule 16.1's operative content lives.
- [ ] Fix the two known date typos in source orders (MDL 3163, MDL 3170) — the
      CSV records the evidently intended year and `pin_cites` preserves what the
      documents say. Confirm that is still true after any edit.

## Step 2 — permanence

- [ ] **Perma.cc every source.** Free through NYU's library. The `perma` column
      is currently `TODO` in most rows. Priority order: the six citing orders,
      then the two chambers-email orders, then everything else.
- [ ] Perma **the court's own copy**, never a firm or news mirror. Two rows
      currently rest on mirrors and both carry a re-verification instruction:
      MDL 3181 (firm-hosted copy of Judge Staton's PTO 1) and MDL 3180 (news-site
      copy). C.D. Cal. has said it will publish MDL orders to its Cases of
      Interest page — recheck for the official copy before perma-ing.
- [ ] Perma the D. Utah PDFs for MDL 3167. Those are CMS paths, not permanent
      identifiers, and they will move.

## Step 3 — the citable artifact

- [x] **Landing page BUILT — `index.html`.** Self-contained, no build step, no
      dependencies. Push to GitHub Pages as-is and the canonical URL exists today.
      It already carries: the suggested-citation block, the three coding rules,
      the limitations stated openly (including the two-tier pin-cite problem from
      ledger finding F03), the block rate, the neutrality statement, a sortable
      16-row table linking every source to CourtListener, the invocation table,
      the interval chart, and a changelog. Light and dark, palette validated.
      **Placeholders still to fill:** `[Author]`, `[canonical URL]`, the perma
      link, `[DOI]`, `[Month]`. Regenerate the embedded data from the CSVs
      whenever a row changes — the page hard-codes a snapshot.
- [ ] **Harvard Dataverse deposit** → DOI. Deposit the CSV, `PROTOCOL.md`, and
      `README.md` together. The protocol is what makes the CSV auditable; a CSV
      alone invites the objection that the coding is unexplained.
- [ ] **One canonical URL that never moves.** GitHub Pages is fine. Do not
      restructure it later — both appellate citations of the Charlotin database
      relied on a stable path, one live and one through perma.cc.
- [ ] **CC-BY**, stated on the page.
- [ ] **Visible `last updated` date** and a versioned changelog. Tag this one
      `v1.0`.
- [ ] **Suggested-citation block** on the landing page (below).
- [ ] A one-paragraph **"How to read this"** note stating the three coding rules:
      code from the order text; silence is `NOT_ADDRESSED`, never `NO`;
      undercount when unsure. The rules are the credibility.
- [ ] **Publish the block rate and the limitations openly**, next to the counts.
      A stated limitation is an asset; a quiet gap is what gets a dataset
      dismissed.

## Step 4 — capture

- [ ] CourtListener search alert on `"Federal Rule of Civil Procedure 16.1"`,
      daily, RECAP. Plus the report-layer queries now in `collect.py`.
- [ ] Docket alerts on all sixteen master dockets. Free tier gives 5; the RECAP
      extension raises it to 15; membership is unlimited and is now worth it.
      Docket alerts incur no PACER fees.
- [ ] Calendar the **monthly JPML reconciliation**. The August 3, 2026 pass
      found an entire missing MDL (3170) and rescued a row wrongly written off
      (3181). Log the reconciliation date each time.
- [ ] Calendar a **monthly recheck of the court MDL pages** in `PROTOCOL.md`.
      D. Kan. and D.N.J. maintain per-case order pages for their major MDLs and
      simply have not built these yet. A blocked row can go free at zero cost.

---

## Suggested citation

Put this verbatim on the landing page.

> **Suggested citation:**
> [Full Name], *Rule 16.1 Tracker: Initial Management Orders in Multidistrict
> Litigation Since December 1, 2025* (v1.0, [Month] 2026), [canonical URL]
> [https://perma.cc/XXXX-XXXX] (last visited [date]).
>
> **Dataset:** [Full Name], *Rule 16.1 Tracker* (Harvard Dataverse 2026),
> https://doi.org/[DOI].
>
> Licensed CC-BY 4.0. Corrections and challenges to any coding decision are
> welcome at [email] and are logged publicly in the changelog.

---

## A standing rule, from `PROTOCOL.md`, worth repeating on the site

**This dataset is not a litigation resource.** If a party asks that an entry be
added, removed, or reframed to help a position, decline and say so publicly.
Charlotin does this explicitly, and it is load-bearing for the neutrality that
makes the thing worth citing in the first place.

---

## After the submission — promotion order, unchanged

1. **Drug & Device Law** (Reed Smith; "Bexis"). He filed public comments on
   proposed Rule 16.1 and wrote the skeptical "better than nothing, but not by a
   lot" piece. Pitch him *after* the Committee submission is docketed, so the
   opening line is "I submitted this to the Advisory Committee" rather than
   "I built a spreadsheet."
2. Academics who will cite it: Nora Freeman Engstrom (Stanford Rhode Center,
   *Managing MDLs*), Duke's Bolch Judicial Institute, NYU's Center on Civil
   Justice.
3. Lawyers for Civil Justice will amplify. **Let them cite you; do not
   co-brand.** Their endorsement costs the neutrality that makes this citable.
4. Trade press last.
