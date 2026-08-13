#!/usr/bin/env python3
"""
Which numerals in the findings prose are asserted against the data, and which are not.

    python3 audit_numbers.py

build.py's prose guards catch a figure that goes stale, but only for the sentences
someone thought to write a guard for. This finds the gaps: every number in the visible
findings text that neither appears in a prose_claims literal nor is prerendered from a
CSV. Run it after adding a finding.

What it CANNOT tell you is whether a guarded number is the right number, or whether two
guarded sentences contradict each other. Both of those have happened in this project.

Numbers legitimately outside the data are expected in the output: figures attributed to
an outside source (the JPML's 158 pending MDLs, an industry count of 340,000 actions),
rule numbers, and dates. Those belong in PROTOCOL.md's unverified-assertions ledger
instead, which is where they are.
"""
import sys; sys.path.insert(0, ".")
import re, build, io, contextlib
page = open('index.html').read()

# visible prose only: drop script, style, and the collapsed Rule text
body = re.sub(r'<script.*?</script>', ' ', page, flags=re.S)
body = re.sub(r'<style.*?</style>', ' ', body, flags=re.S)
rule = body.find('Text of Rule 16.1')
findings = body[:body.find('The dataset')] if 'The dataset' in body else body
text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', findings))

# what build.py asserts
claims = " ".join(lit for _, lit, _ in build.prose_claims(page))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    pass
prer = build.prerender(page, build.stats(build.rows()))
span_vals = re.findall(r'<span id="[^"]+">([^<]*)</span>', prer)
guarded = claims + " " + " ".join(span_vals)

IGNORE = {'16','1','2','3','4','16.1','2025','2026','26','23','12','36','83','5','7','10','20','53.1'}
nums = re.findall(r'(?<![\w.])(\d[\d,]*)(?:%)?(?![\w])', text)
unguarded = []
for n in sorted(set(nums), key=lambda x: -len(x)):
    if n in IGNORE: continue
    if n in guarded: continue
    ctx = [m for m in re.finditer(r'.{55}\b'+re.escape(n)+r'\b.{55}', text)]
    unguarded.append((n, ctx[0].group(0).strip() if ctx else ''))
print(f"numerals in the findings prose: {len(set(nums))} distinct")
print(f"asserted by build.py or prerendered from data: {len(set(nums))-len(unguarded)-len(IGNORE & set(nums))}")
print(f"\nNOT asserted ({len(unguarded)}):\n")
for n, c in unguarded:
    print(f"  {n:>6}   ...{c}...")
