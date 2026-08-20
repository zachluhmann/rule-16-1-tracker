# Pass 1 application decisions

**This file is not part of the codebook.** `subject-treatment-codebook.md` was frozen on
12 August 2026 and nothing here changes a definition. What follows is a log of how the
frozen definitions were *applied* to recurring situations that the five worked test cases
did not settle. Each rule was written the first time it was needed, applied to every
later order, and back-applied to earlier ones.

**This file is sealed for the reliability re-code.** Pass 2 must be coded from the orders
and the codebook alone. If pass 2 consults this log, the agreement statistic measures
whether the log is legible, not whether the definitions are. After pass 2 is complete,
this file becomes the primary tool for diagnosing where the disagreements came from.

---

## R1. A general discovery stay

A stay of discovery resolves `b3c_discovery`. It resolves any **other** subject only where
the order's own text ties that subject to the stayed machinery.

Applied: MDL 3162 `b3b_factual_basis_exchange` is TRUE, because ¶ 5(g) expressly names
Rule 26(a)(1) and ¶ 12 tolls Rules 26 through 37. MDL 3171 `b3b_factual_basis_exchange` is
FALSE on materially similar facts, because ¶ 9(x) makes no reference to the discovery
rules and ¶ 6 speaks only of "discovery proceedings."

Without R1 a single stay paragraph would cascade resolution across most of (b)(3).

## R2. Fixing motion timing

A provision that fixes when a pretrial motion may be filed, must be renoticed, or is due
is an operative determination within `b3d_pretrial_motions`. A Rule 12 response to a
complaint counts, because "answer or otherwise respond" reaches Rule 12 motions.

Applied: MDL 3162 ¶¶ 9 and 11; MDL 3163 Part II and Part IV.B.8; MDL 3166 ¶ 12;
MDL 3171 ¶¶ 6 and 13; MDL 3185 (FINALLY ORDERED).
Not fired: MDLs 3170, 3174, 3179, where nothing fixes any motion deadline.

## R3. About the subject, not merely an instance of it

A provision fires `court_resolution` for a subject only where its operative language is
**about** that subject. A provision whose subject matter is something else does not fire
merely because the coded subject appears inside it as an instance.

Applied: MDL 3166 ¶ 6 fixes interim liaison counsel's authority, so it fires
`b2a_responsibilities`; its notice-transmittal duty is an instance of communication but
the paragraph is not about communication methods, so `b2a_communication` is FALSE.
Also used to keep MDL 3163's conference-cadence topic out of `b2a_communication`, and to
keep MDL 3179's "jurisdictional issues" out of `b3d_pretrial_motions`.

## R4. Anticipated topics versus directed content

An agenda topic that the **court** anticipates discussing is not a `party_direction`. A
topic list that specifies the **content of a filing the parties must make** is.

Applied: MDL 3163 Part IV.B opens "the Court anticipates discussing the following topics,"
so its ten topics are IDENTIFIED but not DIRECTED; the mandatory directions in that order
are all in Part III. MDL 3185 reads "The parties shall file preliminary status reports …
Suggested topics include," so its seven topics are DIRECTED despite the word "suggested."
MDL 3179's conference purpose clause is IDENTIFIED for the same reason as MDL 3163.

Without R4, MDL 3163 would show 14 directed subjects instead of 4. That is the largest
change any application rule makes to the coded cells, and it is worth being exact about
what it does not change: R4 governs `party_direction`, which no published statistic
reads. Reversing every R4 call moves no figure on the landing page and passes both
integrity gates. See AUDIT.md, 20 August 2026.

## R5. What counts as one order

The coded unit is the order that sets up the Rule 16.1(a) conference and the Rule 16.1(b)
report, together with any companion document entered the same day by the same judge.
A later Rule 16.1(c) initial management order is a different document type answering a
different question and is not coded here.

Applied: MDL 3170's Case Management Orders #1 and #2, both entered 18 December 2025 by
Judge Gettleman, are one record. MDL 3167's Pretrial Order No. 2 (19 February 2026,
Judge Barlow), which actually appointed interim leadership, is **not** coded, which is why
that MDL shows no resolution on `b2a_leadership`. The order-level file records the
appointment.

## R6. When leadership timing is express

`b2a_timing` is express only where the order states when appointments will be made, or
places the appointment process on a fixed calendar.

Applied: TRUE for MDLs 3166, 3171 (application, objection, and appointment sequence all
dated) and 3185 (application deadline fixed). FALSE for MDL 3179, whose conditional status
report is keyed to a conference date that the order does not yet fix.

## R7. Naming a coordinating role

A court-created coordinating role is coded as leadership counsel where the order gives it a
leadership title, and not where it does not. The codebook's `express` test is nominal by
design: it asks what a reader of the order alone would know without consulting the Rule.

Applied: MDL 3166 ¶ 6 "Interim liaison counsel" is coded as leadership; MDL 3171 ¶ 7
"Point of contact," which is the same provision renamed, is not. The two roles are
functionally identical and the divergence is flagged in both rows, so a rebuilder applying
a functional test can flip MDL 3171 `b2a_responsibilities` to TRUE.

## R8. Expense sharing is not compensation

Allocating the expenses of one administrative role among a group of counsel is not
"a means for compensating leadership counsel" under (b)(2)(A)(vii).

Applied: MDL 3166 ¶ 6 and MDL 3171 ¶ 7 are both coded FALSE on `b2a_compensation`, under
the codebook instruction to undercount when unsure. The reasoning is recorded in both rows
so a rebuilder can flip them. Contrast MDL 3163 Part IV.B.4 and MDL 3171 ¶ 8, which name a
common benefit fund and are coded TRUE on express.

---

## Quote convention

Quotations are verbatim, with two normalizations that carry no meaning:

1. **Line-wrap whitespace is collapsed.** Court PDFs break lines mid-sentence; the
   extracted text carries those breaks as blank lines. A quotation joins them with a
   single space.
2. **A word hyphenated across a line break is rejoined** only where the compound is
   genuinely hyphenated ("cross-motions"), never to invent or delete a hyphen.

Everything else is preserved exactly, including the courts' own em dashes, curly
apostrophes, and typographical errors. An ellipsis " … " marks an elision between two
verbatim passages, which occurs where `party_direction` and `court_resolution` are
supported by different paragraphs.

Quotations were checked against the retrieved source text passage by passage at the time
of coding. They are not machine-verified, because the only local copy of an order would be
one this project transcribed, and checking a quotation against one's own transcription
proves nothing. A future improvement is a fetch-and-cache step that stores court text
byte-for-byte so `build.py` can assert every quotation against it.
