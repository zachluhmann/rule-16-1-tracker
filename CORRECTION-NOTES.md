# Working notes: the date-filter error (13 Aug 2026)

## What happened

Every search in `rule-16-1-searches.csv` was run with `filed_after=2025-12-01`.
In CourtListener's RECAP index that parameter filters on the **case** filing date,
not the document filing date. The document-level filter is
`entry_date_filed_after`.

Measured, same query, same day:

    type=rd  q="Fed. R. Civ. P. 16.1"  filed_after=2025-12-01             ->  25 documents
    type=rd  q="Fed. R. Civ. P. 16.1"  entry_date_filed_after=2025-12-01  ->  41 documents

The 16 missing documents are missing *because their case was filed before
December 1, 2025*. That is precisely the population the null was about.

## Why this matters more than a count

The published null reads: "No court has applied Rule 16.1 to an MDL that
predates it... Searching the full text of federal court filings for seven
different forms of the Rule's name, limited to documents filed on or after the
effective date, returns 68 documents. Every one sits in an MDL centralized after
that date..."

The search could not have returned anything else. A pre-Rule MDL is a case filed
before the effective date, and `filed_after=2025-12-01` excluded every one of
them. The null was circular: it searched a corpus defined to exclude its own
counterexamples, then reported finding none.

## The counterexample

`In re: Uber Technologies, Inc., Passenger Sexual Assault Litigation`,
MDL No. 3084, 3:23-md-03084-CRB (N.D. Cal., Breyer, J.), docket filed
2023-10-04 -- centralized more than two years before the Rule took effect.

RECAP document 476945536, ECF 5979, filed 2026-04-23, 123,162 characters,
44 pages. A joint discovery letter brief. Four occurrences of "16.1":

1. Plaintiffs cite the Rule 16.1(c) advisory committee note -- "[b]ecause active
   judicial management of MDL proceedings must be flexible, the court should be
   opens to modifying its initial management order in light of developments in
   the MDL proceedings" -- as authority for modifying PTO 10.
   (Note: "should be opens" is the filing's own typo, reproduced as it appears.)
2. Defendants answer that the Court's approach in PTO 10 "is wholly consistent
   with the Fed. R. Civ. P. 16.1 Advisory Committee Notes cited by Plaintiffs
   above."
3. and 4. Both sides read the Rule 16.1 advisory committee notes as recognizing
   the "narrow purpose of fact sheets" as "a management method for planning and
   organizing the proceedings."

So in a pre-Rule MDL, in April 2026, both sides briefed a live discovery dispute
out of Rule 16.1's advisory committee notes.

## What this does and does not falsify

It does not by itself falsify "no COURT has APPLIED the Rule" -- this is a party
filing, and it argues from the advisory notes rather than from the Rule's text.
The distinction is real and worth keeping.

But the null cannot stand on the search that produced it either way, because
that search was incapable of returning a counterexample. The finding has to be
rebuilt from a corpus that could have refuted it.

## Open

- [ ] Read RECAP 476945490 (the companion document in MDL 3084)
- [ ] Did the court rule on this dispute, and did the order cite 16.1
- [ ] Re-run all seven forms under entry_date_filed_after
- [ ] MDL 3163 (GLP-1, E.D. Pa.) is coded NOT_ADDRESSED but now shows hits
- [ ] The "cited in cases it does not govern" finding says six orders, two
      districts; the corrected search shows many more, across at least a dozen


## CONFIRMED COUNTEREXAMPLE: the null is false

`In Re: Change Healthcare, Inc. Customer Data Security Breach Litigation`,
MDL No. 3108, 0:24-md-03108-DWF-DJF (D. Minn., Frank, J.), docket filed
2024-06-07 -- centralized roughly seventeen months before the Rule took effect.

RECAP document 472850310, Doc. No. 540, PRETRIAL ORDER NO. 28, filed 2026-03-19.
One page. The operative sentence, in full:

    "Pursuant to the Court's Pretrial Order No. 2 (Doc. No. 69 P 12) and
     consistent with Federal Rule of Civil Procedure 16.1 aimed at providing
     case-management guidance in MDLs, the Court directs the parties to place
     the following items on the agenda for the March 24, 2026 Status Conference"

Eight agenda items follow: TFAP loan collection efforts; status of discovery;
potential for amended master complaints; insurance company complaints and
potential for a third track; position of State Court/MDL Liaison Counsel;
noticing appearance for Co-Lead Counsel; applicability of orders to counsel in
underlying cases; newly filed state court complaints and coordination with state
court cases.

That is a court, in an MDL centralized before December 1, 2025, invoking Rule
16.1 by name as the frame for a status-conference agenda. The published finding
"No court has applied Rule 16.1 to an MDL that predates it" is false.

Read the verb carefully. The order says "consistent with," not "pursuant to" --
"pursuant to" is spent on the court's own PTO 2. The court is aligning with the
Rule, not claiming the Rule governs. That is the more interesting fact and the
tracker should record it as such rather than flatten it into "applied."

### Party invocations in pre-Rule MDLs

`In re: Uber Technologies, Inc., Passenger Sexual Assault Litigation`,
MDL No. 3084, 3:23-md-03084-CRB (N.D. Cal., Breyer, J.), filed 2023-10-04.

  - RECAP 464110936, entry 2026-01-05, 49,861 chars. A party brief: a proposed
    restriction "is incompatible with both the procedural flexibility underlying
    28 U.S.C. s 1407 and Federal Rule of Civil Procedure 16.1, as well as the
    liberal approach to pleading reflected in Rules 8 and 15."
  - RECAP 476945536, ECF 5979, entry 2026-04-23, 123,162 chars, 44 pages. Joint
    discovery letter brief; both sides argue from the Rule 16.1 advisory
    committee notes. Detailed above.

### Still to identify

  - docket 71221176, `IN RE: TRANS UNION, LLC, CUSTOMER DATA SECURITY BREACH
    LITIGATION`, 1:25-cv-10320 (N.D. Ill.), filed 2025-08-28. Three hits:
    462459060 (2025-12-18) and 464150837 (2026-01-05) on the abbreviated form,
    and 464150837 again on "Rule 16.1 Report". A consolidation predating the
    effective date, apparently filing a Rule 16.1 report.
  - docket 71870485, one hit on "Rule 16.1 Report", entry 2026-01-22.
  - docket 71935884, one hit on "FRCP 16.1", entry 2026-02-10.
  - MDL 3163 (GLP-1, E.D. Pa.) is coded NOT_ADDRESSED in the tracker but two of
    its dockets return hits under the corrected filter.
