#!/usr/bin/env python3
"""Feed validation for the MoneyBall site (DESIGN §2.2/§5: render verbatim or fail loud).
Checks data/book-feed.json: schema, subject/position referential integrity, B5 boundary
(no numeric win_probability anywhere). Exit 1 on any violation."""
import json, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
feed = json.loads((root / "data" / "book-feed.json").read_text())
errs = []
if feed.get("schema") != "agentic-gambling-book-feed/v1":
    errs.append(f"schema mismatch: {feed.get('schema')!r}")
subs = feed.get("subjects", [])
ids = [s.get("id") for s in subs]
if len(ids) != len(set(ids)):
    errs.append("duplicate subject ids")
for p in feed.get("positions", []):
    if p.get("subject_id") not in ids:
        errs.append(f"position {p.get('position_id')} references unknown subject {p.get('subject_id')}")
for s in subs:
    er = s.get("expectation_record") or {}
    for leg in ("prior", "posterior"):
        v = (er.get(leg) or {}).get("value", "MISSING")
        if v == "MISSING":
            errs.append(f"{s.get('id')}: expectation {leg} missing (must be value or explicit null)")
def scan(o, path="$"):
    if isinstance(o, dict):
        for k, v in o.items():
            if "win_probability" in k and isinstance(v, (int, float)):
                errs.append(f"B5 violation: numeric win_probability at {path}.{k}")
            scan(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            scan(v, f"{path}[{i}]")
scan(feed)
if errs:
    print("FEED VALIDATION FAILED:"); [print(" -", e) for e in errs]; sys.exit(1)
print(f"feed ok: {len(subs)} subjects, {len(feed.get('positions', []))} positions, {len(feed.get('settlements', []))} settlements, B5 clean")
