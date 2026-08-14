# Standing prompt: code a new Rule 16.1 initial management order

Use this whenever a new order needs coding. Start a **fresh conversation with memory off**,
attach `codebook-v1.1.md` and `new-order-template.csv`, and paste the block below after
filling in the two blanks.

---

```
I maintain a public dataset coding how federal transferee courts apply Fed. R. Civ. P. 16.1.
A new order needs coding.

MDL: ____
Order: ____   (CourtListener link)

Read codebook-v1.1.md in full first, and the Application rules section carefully. Then read
the order at the link. Do not code from a docket description or a summary.

Then fill in every row of new-order-template.csv:

- mdl_no, order_id (use MDLNUMBER-order1), source_document (title, court, date, judge, ECF
  number), courtlistener_url: the same values on all twenty rows
- reached, express, party_direction, court_resolution: TRUE or FALSE
- pin_cite: paragraph or page for every row where express is TRUE
- quote: verbatim language for every row where party_direction or court_resolution is TRUE
- coding_note: your reasoning. Where an application rule decides the cell, name it (R1, R3,
  R6 and so on). Where you were torn, say so and say why.

Binding constraints: party_direction implies express implies reached, and court_resolution
implies express implies reached. If your values break one, re-read the definitions.

Silence is FALSE, never a judgment about what the court should have done.

Do not look up the Rule 16.1 Tracker site, its GitHub repository, or subject-treatment.csv.
They contain existing codings for other orders and would anchor you.

Return the completed CSV, twenty rows, nothing else.
```

---

Save what comes back as `new-MDLNUMBER.csv` and hand it to Claude, which validates it, merges
it, rebuilds the page and tells you what moved.

## Why the split

ChatGPT reads orders and applies the codebook. It cannot run `validate_treatment.py`, cannot
run `build.py`, cannot check that the new row set does not break the prose guards, and cannot
commit. Those are the steps that keep the published page honest, and they run here.

Coding without validation is how a wrong figure reaches the site. Validation without coding is
just a clean build of stale data. Neither half is optional.
