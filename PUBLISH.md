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

## Step 0 — close the open rows

- [x] **MDL 3180 — DONE 2026-08-11.** *Initial Procedure Order No. 1* obtained
      and read in full. **It cites Rule 16.1 twice and is an AGENDA-type order.**
      Headline moved 6/13 → **7/14**. The submission was rewritten: every figure
      updated, a new Part III added on the MDL 3162 / MDL 3180 form order, and
      ledger findings F02 and F05 fixed in the process.
- [ ] **MDL 3187.** One PACER session, four documents:
      ECF 2 (`07907490590`), ECF 8 (`07907513132`), ECF 9 (`07907520997`),
      ECF 10 (`07907521776`). Install the RECAP extension first so the text
      lands in the public archive. Start with ECF 2.
- [x] **Re-run the counts in `README.md` → "WHERE THIS STANDS" — DONE
      2026-08-12.** Every figure in that section, and every figure on the landing
      page, was recomputed from the CSV. The landing page's four stat tiles, the
      uptake percentage, and the chart's `n` are now **computed from the embedded
      data at load time**, so the page cannot drift from the CSV again — which is
      exactly what had happened: the site published 6/13 for a day after the CSV
      said 7/14. **The submission still quotes the old figures and has not been
      re-run.**

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

- [x] **F01 — RESOLVED 2026-08-12** *(in the README and on the site; the letter
      still needs the same edit)*. The "tentative agenda" construction is now
      quoted from **MDL 3180 ¶3**, where it is pin-cited verbatim, instead of
      being attributed to MDL 3162 where it was not. Judge Bates's IPO No. 1 is
      cited alongside as the same form order, by paragraph.
- [ ] **F02 (FAILED).** Part II.D's interval range is **n=12 of 14** — MDL
      3178 and MDL 3179 have no recorded conference date, and the letter does
      not disclose the exclusion. One-clause fix: "The twelve orders for which a
      conference date is recorded show intervals of …" *(The landing page and
      README now state this correctly; the letter does not.)*
- [ ] **F03 (FAILED) — the one that still matters.** The dataset is
      **two-tiered**. Six rows (3162, 3163, 3166, 3171, 3174, 3175) carry
      `pin_cites` of 161–333 characters — paragraph pointers with no verbatim
      language — and hold **138 of the 266 affirmative codes (52%)**. The other
      eight carry 685–2,406 characters with quotes. The thin six are the earliest
      coded, and **four of the seven citing orders are in that tier**. Either
      back-fill quotes (about an hour once the API resets) or disclose the two
      tiers in Part VIII. *(The landing page and `AUDIT.md` disclose it; the
      letter does not.)*
- [ ] F04 (`SHIP`): the URL now resolves —
      https://zachluhmann.github.io/rule-16-1-tracker/ — and should replace
      `[URL]`. **`[DOI]` still does not exist**; either deposit to Dataverse
      first or cut the DOI offer from Part IX rather than send a dead address.
- [ ] F05 (`FORM`): Part I says "fifty-plus variables"; the tracker has **61**.

**Re-verify after any edit** — editing after verification invalidates it. **MDL
3180 did move the headline from 6/13 to 7/14, so all thirteen numeric claims in
the letter need recomputing before it is sent.** The README, the landing page and
`AUDIT.md` have been recomputed; the letter has not.

## Step 1 — verification pass

- [ ] Re-read every row where `cites_rule = YES` and confirm the quoted language
      against the order. These seven carry the headline.
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

- [x] **Landing page LIVE — 2026-08-12 —
      https://zachluhmann.github.io/rule-16-1-tracker/** Self-contained, no build
      step, no dependencies. Repo: https://github.com/zachluhmann/rule-16-1-tracker
      **The canonical URL exists and resolves. Do not restructure the path.**
      It already carries: the suggested-citation block, the three coding rules,
      the limitations stated openly (including the two-tier pin-cite problem from
      ledger finding F03), the block rate, the neutrality statement, a sortable
      16-row table linking every source to CourtListener, the invocation table,
      the interval chart, and a changelog. Light and dark, palette validated.
      **All placeholders filled** — author, canonical URL and month resolve; the
      perma link and DOI were cut rather than published as dead brackets, and the
      page says both are pending. **The four stat tiles, the uptake percentage
      and the chart's `n` are computed from the embedded data at load**, so the
      page can no longer disagree with the CSV. Still run `python build.py` after
      any row change — the *data* is a snapshot even though the *figures* are not.
- [ ] **Harvard Dataverse deposit** → DOI. Deposit the CSV, `PROTOCOL.md`, and
      `README.md` together. The protocol is what makes the CSV auditable; a CSV
      alone invites the objection that the coding is unexplained. **Do this before
      the letter goes** — Part IX offers the reporters a DOI that does not exist.
- [x] **One canonical URL that never moves** —
      https://zachluhmann.github.io/rule-16-1-tracker/. Do not restructure it —
      both appellate citations of the Charlotin database relied on a stable path,
      one live and one through perma.cc.
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

**This is now live on the landing page in exactly this form:**

> **Suggested citation:**
> Zach Luhmann, *Rule 16.1 Tracker: Initial Management Orders in Multidistrict
> Litigation Since December 1, 2025* (v1.0, August 2026),
> https://zachluhmann.github.io/rule-16-1-tracker/ (last visited [date]).
>
> Licensed CC BY 4.0. Corrections and challenges to any coding decision are
> welcome and are logged publicly in the changelog. A permanent archival copy
> and a dataset DOI are pending and will be added here when they issue.

The perma.cc link and the Dataverse DOI were **cut rather than published as dead
brackets.** Add them back, in this form, once they exist:

> … https://zachluhmann.github.io/rule-16-1-tracker/ [https://perma.cc/XXXX-XXXX]
> (last visited [date]).
>
> **Dataset:** Zach Luhmann, *Rule 16.1 Tracker* (Harvard Dataverse 2026),
> https://doi.org/[DOI].

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
