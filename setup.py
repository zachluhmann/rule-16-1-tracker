#!/usr/bin/env python3
"""
One-time setup. Fills every placeholder across every file.

    python3 setup.py

Asks four questions, then rewrites index.html, LICENSE, CITATION.cff, README.md
and the submission source. Run it once before you push, and again later if you
add a perma link or a DOI.
"""
import re, os, datetime

FILES = ["index.html", "LICENSE", "CITATION.cff", "README.md",
         "build_letter.js", "advisory-committee-submission.md", "DEPLOY.md"]

def ask(label, example, current=""):
    v = input(f"  {label}\n    e.g. {example}\n  > ").strip()
    return v or current

print("\nRule 16.1 Tracker — setup\n" + "-"*46)
full  = ask("Your full name, as it should appear in a citation", "Zachary Q. Example")
first = full.split()[0]
last  = full.split()[-1]
user  = ask("Your GitHub username", "zqexample")
repo  = ask("Repo name [rule-16-1-tracker]", "rule-16-1-tracker") or "rule-16-1-tracker"
perma = ask("Perma.cc link for the site (blank if not yet)", "https://perma.cc/ABCD-1234")
doi   = ask("Dataverse DOI (blank if not yet)", "10.7910/DVN/XXXXXX")

url = f"https://{user}.github.io/{repo}/"
month = datetime.date.today().strftime("%B")

subs = [
    (r"\[FULL NAME\]", full), (r"\[AUTHOR NAME\]", full), (r"\[Author\]", full),
    (r"\[FIRST\]", first), (r"\[LAST\]", last),
    (r"\[canonical URL\]", url), (r"\[URL\]", url), (r"<canonical URL>", url), (r"<URL>", url),
    (r"\[Month\]", month),
]
if perma:
    subs += [(r"\[https://perma\.cc/XXXX-XXXX\]", f"[{perma}]"),
             (r"https://perma\.cc/XXXX-XXXX", perma),
             (r"the perma link", perma)]
if doi:
    subs += [(r"\[DOI\]", doi), (r"https://doi\.org/\[DOI\]", f"https://doi.org/{doi}")]

total = 0
for f in FILES:
    if not os.path.exists(f):
        continue
    s = orig = open(f, encoding="utf-8").read()
    for pat, rep in subs:
        s = re.sub(pat, rep.replace("\\", r"\\"), s)
    if s != orig:
        open(f, "w", encoding="utf-8").write(s)
        n = sum(len(re.findall(p, orig)) for p, _ in subs)
        total += n
        print(f"  updated {f:38s} {n} replacements")

print("-"*46)
print(f"  {total} placeholders filled")
print(f"  your site will be at: {url}")

left = []
for f in FILES:
    if os.path.exists(f):
        for m in re.findall(r"\[(?:FULL NAME|AUTHOR NAME|Author|FIRST|LAST|canonical URL|URL|DOI|Month)\]",
                            open(f, encoding="utf-8").read()):
            left.append((f, m))
if left:
    print("\n  STILL UNFILLED (expected if you left perma/DOI blank):")
    for f, m in sorted(set(left)):
        print(f"    {f}: {m}")

print("\n  Next:  python3 build.py   then push to GitHub.")
if not perma or not doi:
    print("  Re-run this script once you have the perma link and the DOI.\n")
