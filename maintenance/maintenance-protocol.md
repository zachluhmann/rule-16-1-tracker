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

The same workflow runs a second schedule at 02:00 UTC on every day except Monday, which
resumes the one-time triage backfill and does nothing else. It skips Monday so the weekly
sweep has the day's API allowance to itself. Once the backfill is finished this schedule
costs nothing at all: the run reads `maintenance/triage-validation.json`, sees the corpus is
complete under the current rules version, and returns without making a request.

### The API allowance, and why it is a shared budget rather than a pacing problem

CourtListener's documented limits for an authenticated account are 5 a minute, 50 an hour and
125 a day, all applying at once. Those numbers are exactly what the server meters. Three
backfills were nevertheless lost to refusals before the reason was read off the reply itself:

    Rate limit exceeded: 125/day. Expected available in 54227 seconds.

**The 125 belongs to the account, not to the run.** The weekly sweep, the backfill, and every
interactive CourtListener call made anywhere under the same token draw on one pool, and it
refills one slot at a time over a rolling 24 hours rather than resetting at midnight. A
process cannot see how much of the day is already gone and no endpoint will tell it, so
correct pacing is not sufficient and a run can be refused on its first request.

Two rules follow, and they are the opposite of the obvious ones:

- **Do not wait it out.** The refusal carries a `Retry-After` that has been observed at 15.2
  hours, far longer than any job here is allowed to live. `watch.py` raises `QuotaExhausted`
  instead of sleeping, keeps what it has read, and stops. The next scheduled run continues.
- **Do not pace slower.** Pacing does not create quota. A run that is out of allowance and
  slows down only reads fewer documents before it dies.

For a session doing this work by hand the practical consequence is a budget, not a delay:
before spending requests on reading documents, consider that the weekly sweep needs about
eight and the backfill resume needs whatever is left. A session that burns the day's pool
will show up the following Monday as `QUOTA_EXHAUSTED` in the watch log.

`QUOTA_EXHAUSTED` is not a finding about the record or about the search. It means the sweep
never ran, so the positive control was never evaluated. Guardrail 11 answers whether the
query still finds what it should, and that is a question about a query that was actually
sent. Do not read a quota failure as a control failure.

### Two things were called R4, and now only one is

Until 31 August 2026 `triage.py` numbered its rules R0 to R8 and the codebook numbered its
application rules R1 to R8. They are unrelated, they were discussed in the same week, and
codebook R4 and triage R4 mean entirely different things. The triage rules are now **T0, T1,
T2, T3, T3b, T4, T5, T5a, T5b, T6, T7, T8**, plus S1 for the search-result tier. The codebook
keeps R.

AUDIT.md entries dated before 31 August 2026 use the old triage names and are left as written,
because rewriting a log to match a later rename is how a log stops being evidence. Read `R4`
in an entry from August as `T4` if the entry is about triage, and as itself if it is about
coding.

### The curated docket registry, `maintenance/known-dockets.csv`

The tracker maps each MDL to one docket, its master. Every filing on a member docket is
invisible to that map, and member dockets turn out to be where a good deal of Rule 16.1
practice happens: on 31 August 2026 every hit the `report_phrase` form returned was an
individual Cal-Maine action in W.D. Wis. filing its own Rule 16.1 report under its own civil
number, and rule T4 abandoned all eleven because nothing tied the docket to MDL 3175.

Reading the docket NUMBER instead would have been worse than abandoning them. A member case
carries an ordinary civil number and never prints the MDL's, so T7 would have filed eleven MDL
documents under `non_mdl`, which is a category the published findings are computed over.

So membership is decided by a person, once, and written down. Each row carries the docket id,
what it resolves to (an MDL number, or `non_mdl`), the case name, the docket number, the court
and the date it was checked. Rule **T5b** applies it, positioned after T3 and T3b so that a
brief about a district's own local rule 16.1 is still noise no matter whose docket it is on,
and before T4 so that a curated docket answers the question T4 gives up on.

**Add a row only after reading the docket.** The registry is authoritative precisely because
nothing in it was inferred, and one guessed row makes the whole file a guess.

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
eighteen scenarios including an unvalidated classifier, an undecidable document, quota
exhaustion mid-run, a frozen validation baseline, and a control failure. It asserts that the
coding files are byte-identical afterwards. 103 checks.

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

## The guards, and the suite that breaks them on purpose

`build.py --check` runs ten guards before it will write the page. They are listed here in the
order it runs them, which is deliberate: a guard that reads a column is useless if a guard
that checks the table's shape has not run first.

| guard | the question it asks |
|---|---|
| `assert_rectangular` | does every data CSV row carry the header's field count |
| `assert_subject_columns` | do the tracker's 20 derived columns equal the order layer's `reached` |
| `assert_search_arithmetic` | do the search ledger's categories sum, and use the recorded vocabulary |
| `assert_links` | is every docket URL a form CourtListener will actually serve |
| `assert_citation_version` | do CITATION.cff, index.html, PUBLISH.md and README.md name one version |
| `check_prose` | is the correct figure present in each hand-written finding |
| `check_contradictions` | is a WRONG copy of any finding also present |
| `check_readme` | does any count in the README disagree with the CSVs |
| the stale block | does the embedded JSON match the CSVs, and the prerender match the page |

Anything the page states as a figure should be **prerendered from the data rather than
guarded**, where that is possible. A prerendered value cannot drift, and a hand edit to one
fails the stale check. The version badge in the header was hand-written, said `v1.0-draft`
for nineteen days while the citation box said v1.1, and was invisible to the guard written
for exactly that drift because the guard matches the parenthesised citation form. It is
prerendered now. Reach for a guard when a sentence has to be written by hand, which is true
of the findings and is not true of a number.

`validate_treatment.py` guards the coding files rather than the page: the logical constraints
that hold by construction, the evidence requirements, the one cross-layer constraint between
the report layer and the order layer, and the subject registry itself, which is read out of
the codebook's own table so neither CSV can drift from the definitions coding was done under.

**`test_build.py` is the suite that proves those guards fire.** It copies the repository to a
temporary directory, breaks exactly one thing, runs `build.py --check` as a subprocess, and
requires a non-zero exit AND output that names what was broken. Seventeen cases. Naming is
scored because a guard that dies with the wrong message sends the next reader to the wrong
file. Run it whenever a guard is added or changed, and add a case in the same commit: a guard
with no case has only ever been observed passing, which is the state every guard in this
repository was in until 31 August 2026.

Writing it found two live defects on its first run. `rule-16-1-tracker.csv` had been ragged
for eight days, one field wide on the MDL 3180 row, and every guard passed because they were
all reading contents and none was reading shape. And `check_prose` could not see a wrong copy
of a finding sitting beside a correct one, a defect `check_readme`'s docstring had described
in writing seventeen days earlier while the page's own guard kept the shape the README's had
abandoned. Both are in `AUDIT.md` under 31 August.

## What must never be skipped

**`build.py` before every upload.** It refuses to build when a hand-written figure in the
findings no longer matches the CSVs, and it has caught real drift repeatedly, including four
times in one session.

**`python3 test_build.py` after touching `build.py`.** A guard nobody has watched break is a
guard nobody has tested.

Both are now enforced. `.github/workflows/test.yml` runs `build.py --check`,
`validate_treatment.py`, `test_watch.py` and `test_build.py` on every push and pull request,
in that order, cheapest and most fundamental first so the log names the real problem rather
than a consequence of it. It needs no token and no network, so it also runs on a fork.

That workflow exists because of an asymmetry. The watch gates itself: `watch.py` runs
`validate_treatment.py` and `build.py` and refuses to commit unless both pass, so a bad
automated run publishes nothing. **Nothing gated a human commit.** This repository is updated
through a browser upload page, so there is no local hook and no staging step between an edit
and a live page. The eight-day ragged row went up that way.

**`entry_date_filed_after`, never `filed_after`.** The second restricts by case filing date
and once produced a published finding that was false and unfalsifiable by its own method.

**Two coders on anything contestable.** One coder produces a number nobody can check.

## What is still open

- MDL 3176 has issued no qualifying order at 133 days. The dataset's only true negative;
  watched weekly at the docket level.
- Twenty-three cells cannot be checked against their own quotes. They are the ones governed
  by application rule R4, and the sentence that decides them is quoted in none of them. The
  targeted pass of 20 August 2026 found the rule applied consistently and found that it moves
  no published figure, so this ranks lower than it used to, but it is still the one place
  where a cell rests on a reading rather than on a quotation.
- Fifteen tiebreak cells await a human reading. Nothing in this dataset has yet been read by
  a lawyer other than its author.
