# Maintenance protocol

Three layers. The first runs on GitHub's servers and depends on nothing else existing.

## 1. Weekly, GitHub Actions, unattended

`.github/workflows/watch.yml` runs `watch.py` every Monday at 13:00 UTC, and on demand from
the Actions tab. It needs one repository secret, `COURTLISTENER_TOKEN`, and nothing else. No
laptop, no chat session, no subscription, no person.

Each run:

- reruns the seven naming forms under `entry_date_filed_after`, never `filed_after`
- checks **Guardrail 11's positive control** inside that sweep: the spelled-out form must
  return RECAP 472850310, Pretrial Order No. 28 in MDL 3108. If it does not, the run records
  the failure, refuses to write a measurement, leaves the state file untouched so the next
  run compares against the same baseline, opens an issue, and exits red.
- diffs the returned document IDs against `maintenance/watch-state.json`, so a document that
  is added and one that is removed do not cancel out into "no change"
- checks the docket of every MDL marked `NO_ORDER_YET`, today MDL 3176 only. The naming
  sweep cannot see an order that does not name the Rule, so that docket is watched directly.
- runs `validate_treatment.py` and `build.py --check`
- appends a row to `maintenance/watch-log.csv` **on every run, including runs that find
  nothing**, and commits it. An unlogged check is indistinguishable from one that never
  happened, and the weekly commit also keeps GitHub from disabling the schedule for inactivity.
- opens a labelled issue when there is something to read, carrying for each new document the
  court, the docket, the clerk's entry text, the matching snippet, the page count, and
  whether a text layer exists. Retrieval is mechanical and no person should be doing it.

### Triage: what the machine may decide, and on what terms

Triage assigns a hit to one of five categories: post-effective MDL, pre-effective MDL,
non-MDL, Rule 16 noise, or unverified. That is a different kind of question from coding an
order. Coding asks whether a provision fires `court_resolution`, which two trained coders
split on 22 times out of 300. Triage asks which case a document sits in, and the document's
own first line answers it, because every federal filing carries an ECF header stamping its
docket number.

So triage runs in tiers, in `triage.py`:

- **By rule, where a rule decides it.** Eight published rules, R0 through R8. No literal
  "16.1" in the document or the clerk's entry means the index returned it for Rule 16 (R2).
  A local-rule marker with no federal naming form means the other 16.1 (R3). An MDL number in
  the text resolved against the registry gives the side of the effective date (R5). A sha1
  identical to a document already classified inherits that classification (R1), which is what
  catches the same filing appearing on a master and a member docket. That case is not
  hypothetical: the human first misfiled RECAP 464112237 as an unrelated civil case.
- **By model, only where no rule decides,** and only if it returns a passage of at least 40
  characters that is found verbatim in the document. A quote that is not there means the
  answer came from somewhere other than the document, and the answer is discarded rather than
  argued with. This is the discipline the codebook already imposes on human coders.
- **By nobody, otherwise.** The hit is counted `hits_unverified`, a real column that already
  sums into the arithmetic, so no figure on the page is wrong while it sits there, and an
  issue names it. An MDL number in neither the tracker nor
  `maintenance/pre-effective-mdls.csv` always lands here: inferring a centralization date
  from an MDL number would be right most of the time and wrong invisibly.

Every verdict records the rule that fired and the string it fired on, in
`maintenance/triage-ledger.csv`. Rows the machine touched carry `triage_source` of MACHINE or
MIXED, `build.py` enforces that vocabulary, and the page's limitations section says so in a
sentence generated from the data rather than written once and forgotten.

**Automatic triage is off until it has been scored.** `watch.py --backfill`, run once from
the Actions tab, classifies the whole existing corpus and compares the result to the triage a
person did by reading. The comparison is one-sided and is described that way: the hand triage
survives only as per-form totals, so it can prove a disagreement (the classifier put more
documents in a category than the human's total allows) and can only bound agreement. Until
that check passes, `watch.py` triages new documents into the ledger and refuses to change any
published count.

### What it will not touch, and why

**`subject-treatment.csv`.** Whether a provision fires `court_resolution` is judgment, and a
wrong call becomes a published finding in a dataset meant to be cited. The watch detects that
a new order exists, opens an issue, and stops.

**Any count it has not earned.** The watch never recomputes an existing row: it carries the
hand triage forward and adds this week's documents to it. It never edits a historical row, it
supersedes. If a gate fails after an update, the files are restored from bytes read before
it, not with `git checkout`, because a revert that assumes a clean working tree quietly does
nothing when there is not one.

`test_watch.py` runs the whole thing offline, with no network and no token: the rule tier
against nine documents whose category this repository already records, then the watch across
six scenarios including an unvalidated classifier, an undecidable document, and a control
failure. It asserts that the coding files are byte-identical afterwards.

## 2. Weekly, scheduled Cowork session, reading layer

Fires Mondays after the Action. It reads the open watch issue and does the work the Action
deliberately refuses: reads each new document, assigns it a triage category, checks whether
any new order qualifies for coding, and prepares the edits. It does not publish.

## 3. Monthly, scheduled Cowork session, universe reconciliation

Fires at 10am Eastern on the 1st, 2nd and 3rd. "First business day" cannot be expressed in
cron, so it fires three times and is built to no-op twice: it reads the last logged
reconciliation date in PROTOCOL.md and stops if one has already run this month, and stops if
the new JPML report has not posted.

It pulls *Pending MDL Dockets By MDL Number* from jpml.uscourts.gov/pending-mdls-0 and
compares every MDL numbered 3162 or higher against the tracker. **The universe comes from
that PDF and never from a search**, because a search only finds MDLs whose orders use the
phrase, which is the selection bias this dataset exists to avoid. This is the step that
caught MDL 3170, missing from the seed entirely and invisible to any phrase search. It also
knows the trap: a JPML "MDL No." is a docket number for a motion, not proof an MDL exists, so
a gap in the numbering is usually a denied or withdrawn petition rather than a missing row.

## What is genuinely not automated

Coding an order. That stays a person's, and the reason is not squeamishness about machines:
it is that the reliability pass measured how far two careful readers diverge on exactly this
question and found 22 cells out of 300, concentrated in the provisions whose language is
thinnest. A number produced by one machine pass would carry no such measurement and could not
be given one.

Two published findings also quantify over the whole corpus in a way no count can recheck:
finding 3a says that across all returned documents exactly one names the Rule two different
ways, and the local-rule collision finding rests on which districts generate 16.1 references.
`build.py` verifies the numbers in those sentences and cannot verify the word "exactly." The
issue opened for any week that adds documents says so.

## What must never be skipped

**`build.py` before every upload.** It refuses to build when a hand-written figure in the
findings no longer matches the CSVs, and it has caught real drift repeatedly, including four
times in one session.

**`entry_date_filed_after`, never `filed_after`.** The second restricts by case filing date
and once produced a published finding that was false and unfalsifiable by its own method.

**Two coders on anything contestable.** One coder produces a number nobody can check.

## What is still open

- MDL 3176 has issued no qualifying order at 133 days. The dataset's only true negative;
  watched weekly at the docket level.
- R4 has never been independently tested and has the largest effect of any application rule
  on the published figures. Every R4 coding is provisional until a targeted pass covers it.
- Fifteen tiebreak cells await a human reading. Nothing in this dataset has yet been read by
  a lawyer other than its author.
