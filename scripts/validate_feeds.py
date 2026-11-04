#!/usr/bin/env python3
"""Feed validation for the MoneyBall site (DESIGN §2.2/§5: render verbatim or fail loud).
Checks data/book-feed.json: schema, subject/position referential integrity, B5 boundary
(no numeric win_probability anywhere). Also checks data/cards-feed.json (DESIGN §2):
schema moneyball-cards-feed/v1, unique card_ids, every non-null stat carries a receipt,
moniker_v2 only with a graduation receipt, null stats carry an honest state. Exit 1 on
any violation."""
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
# --- cards feed (DESIGN §2) ---
cpath = root / "data" / "cards-feed.json"
if not cpath.exists():
    errs.append("data/cards-feed.json missing")
else:
    cf = json.loads(cpath.read_text())
    if cf.get("schema") != "moneyball-cards-feed/v1":
        errs.append(f"cards schema mismatch: {cf.get('schema')!r}")
    cards = cf.get("cards", [])
    cids = [c.get("card_id") for c in cards]
    if len(cids) != len(set(cids)):
        errs.append("duplicate card_ids in cards feed")
    for c in cards:
        fields = {r.get("field") for r in c.get("receipts", [])}
        s = c.get("stats", {})
        flat = {"provenance_units": s.get("provenance_units"),
                "landed_prs": s.get("landed_prs"),
                "mirror_scores": s.get("mirror_scores"),
                "book.forecasts_issued": (s.get("book") or {}).get("forecasts_issued"),
                "book.brier": (s.get("book") or {}).get("brier"),
                "book.hit_rate": (s.get("book") or {}).get("hit_rate"),
                "book.open_positions": (s.get("book") or {}).get("open_positions"),
                "subjects_active": s.get("subjects_active"),
                "countdown_refs": s.get("countdown_refs")}
        states = c.get("stat_null_states", {})
        for name, v in flat.items():
            if v is not None and name not in fields and name.split(".")[-1] not in fields:
                errs.append(f"card {c.get('card_id')}: stat {name} non-null without receipt")
            if v is None and name not in states:
                errs.append(f"card {c.get('card_id')}: stat {name} null without honest state")
        if c.get("moniker_v2") is not None and "moniker_v2" not in fields:
            errs.append(f"card {c.get('card_id')}: moniker_v2 without graduation receipt")
        if not c.get("receipts"):
            errs.append(f"card {c.get('card_id')}: no receipts (identity/stat receipts required)")
    scan(cf, path="$cards")
    print(f"cards feed checked: {len(cards)} cards, {sum(1 for c in cards if c.get('moniker_v2'))} graduated")
if errs:
    print("FEED VALIDATION FAILED:"); [print(" -", e) for e in errs]; sys.exit(1)
print(f"feed ok: {len(subs)} subjects, {len(feed.get('positions', []))} positions, {len(feed.get('settlements', []))} settlements, B5 clean")

# --- proposals feed (DESIGN §13): chain valid, obligations
# complete, NONE exits classified, no probability-shaped data
proposals_path = root / "data" / "proposals-feed.json"
if proposals_path.exists():
    pf = json.loads(proposals_path.read_text())
    if pf.get("schema") != "moneyball-proposals-feed/v1":
        errs.append(f"proposals schema mismatch: {pf.get('schema')!r}")
    if not (pf.get("chain") or {}).get("valid"):
        errs.append("proposals feed chain not verified valid")
    for row in pf.get("proposals", []):
        p = row.get("proposal", {})
        ob = p.get("proof_obligation") or {}
        for f in ("record_of_record_ref", "settling_receipt_shape",
                  "stamping_role", "corroboration_leg", "dispute_rule"):
            if not ob.get(f):
                errs.append(f"proposal {p.get('proposal_id')}: proof obligation missing {f}")
        if p.get("state") == "NONE_FOUND":
            if (p.get("exit") or {}).get("class") not in ("N1", "N2", "N3"):
                errs.append(f"proposal {p.get('proposal_id')}: NONE_FOUND without exactly one primary class")
        if p.get("state") == "CONTRACT_DERIVED" and not p.get("stamp"):
            errs.append(f"proposal {p.get('proposal_id')}: CONTRACT_DERIVED without the doctrine-fit stamp")
    def pscan(o, path="$"):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("p", "odds") or "win_probability" in k:
                    errs.append(f"§13/Q1 violation: probability-shaped field at {path}.{k}")
                pscan(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                pscan(v, f"{path}[{i}]")
    pscan({"proposals": pf.get("proposals", [])})
    if errs:
        print("FEED VALIDATION FAILED:"); [print(" -", e) for e in errs]; sys.exit(1)
    print(f"proposals feed checked: {len(pf.get('proposals', []))} proposals, chain valid")

# --- pools feed (DESIGN §3): pools must reference real cards, styles stated ---
pools_path = root / "data" / "pools-feed.json"
if pools_path.exists():
    pf = json.loads(pools_path.read_text())
    if pf.get("schema") != "moneyball-pools-feed/v1":
        errs.append(f"pools schema mismatch: {pf.get('schema')!r}")
    cards_path = root / "data" / "cards-feed.json"
    card_ids = set()
    if cards_path.exists():
        card_ids = {c.get("card_id") for c in json.loads(cards_path.read_text()).get("cards", [])}
    for p in pf.get("pools", []):
        if card_ids and p.get("card_id") not in card_ids:
            errs.append(f"pool {p.get('pool_wallet_id')} references unknown card {p.get('card_id')}")
        if not p.get("styles"):
            errs.append(f"pool {p.get('pool_wallet_id')} missing styles")
        if not p.get("receipts"):
            errs.append(f"pool {p.get('pool_wallet_id')} missing receipts")
    scan(pf)
    if errs:
        print("FEED VALIDATION FAILED:"); [print(" -", e) for e in errs]; sys.exit(1)
    print(f"pools feed checked: {len(pf.get('pools', []))} pools")
