#!/usr/bin/env python3
"""Gộp dữ liệu mới vào paperlens_pack.json (chạy bởi tác vụ hằng ngày).
Cách dùng: python3 tools/merge_pack.py [--papers new_papers.json] [--rules new_rules.json] [--confirm confirm.json]
- new_papers.json: danh sách bài báo (xem SCHEMA.md)
- new_rules.json : danh sách tiêu chí chung mới
- confirm.json   : {"rule_id": số_bài_ủng_hộ_thêm, ...}
Không cần mạng. In ra tóm tắt thay đổi."""
import json, re, sys, statistics, argparse, datetime, hashlib, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "paperlens_pack.json")
MAX_PAPERS = 8000
RX = {"HER", "OER", "ORR", "CO2RR", "NRR", "HOR", "OWS", "other"}
VAL_KEYS = {"eta10": (0, 1500), "eta100": (0, 2000), "tafel": (5, 400), "stab_h": (0, 20000), "stab_j": (0, 5000), "cell_v": (1.0, 3.0), "h2_usd_kg": (0.3, 30)}
CHK_T = {"text", "val", "flag", "and", "or"}
SECS = {"abs", "intro", "methods", "results", "disc", "concl", "all"}
VKEYS = {"eta10", "etaHigh", "tafel", "cdl", "stab", "cycles", "cell", "fe"}
FKEYS = {"ir", "rhe", "refel", "compTable", "bench", "highJ", "electrolyte"}

def norm_title(t): return re.sub(r"[^a-z0-9]", "", str(t or "").lower())[:120]
def norm_doi(d):
    d = str(d or "").strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d or None
def key(p): return "d:" + norm_doi(p.get("doi")) if norm_doi(p.get("doi")) else "t:" + norm_title(p.get("title"))
def now(): return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def clean_paper(p):
    if not isinstance(p, dict) or not str(p.get("title", "")).strip(): return None
    q = {"title": str(p["title"]).strip()[:400], "doi": norm_doi(p.get("doi")), "year": p.get("year"), "venue": (p.get("venue") or None),
         "url": p.get("url") or None, "abstract": str(p.get("abstract") or "")[:600], "cites": p.get("cites"),
         "reaction": p.get("reaction") if p.get("reaction") in RX else "other", "electrolyte": p.get("electrolyte") if p.get("electrolyte") in ("acidic", "alkaline", "neutral") else None,
         "material": (str(p.get("material") or "")[:120] or None), "mclass": (str(p.get("mclass") or "")[:60] or None), "synth": (str(p.get("synth") or "")[:80] or None),
         "src": p.get("src") or "SciSpace", "added": p.get("added") or now()}
    for k, (lo, hi) in VAL_KEYS.items():
        v = p.get(k)
        try: v = float(v)
        except (TypeError, ValueError): v = None
        q[k] = v if v is not None and lo <= v <= hi else None
    try: q["year"] = int(q["year"]) if q["year"] else None
    except (TypeError, ValueError): q["year"] = None
    return q

def chk_ok(c, d=0):
    if c is None: return True
    if not isinstance(c, dict) or d > 4 or c.get("t") not in CHK_T: return False
    t = c["t"]
    if t in ("and", "or"): return isinstance(c.get("of"), list) and len(c["of"]) > 0 and all(chk_ok(x, d + 1) for x in c["of"])
    if t == "text":
        if c.get("sec", "all") not in SECS: return False
        pats = list(c.get("any") or []) + list(c.get("all") or [])
        if not pats: return False
        for x in pats:
            try: re.compile(str(x))
            except re.error: return False
        return True
    if t == "val": return c.get("key") in VKEYS and c.get("op") in (">=", "<=", "present")
    if t == "flag": return c.get("key") in FKEYS
    return False

LEAK = re.compile(r"\b[A-Z][a-z]?\d+(?:[A-Z][a-z]?\d*)*\b|\b[A-Z][a-z]?(?:[A-Z][a-z]?\d*)+\d\b")
OKF = {"H2", "O2", "CO2", "H2O", "H2SO4", "HClO4", "RuO2", "IrO2", "N2"}
def clean_rule(r):
    if not isinstance(r, dict): return None
    text = str(r.get("text") or "").strip(); sub = str(r.get("sub") or "").strip()
    if len(text) < 15 or not re.match(r"^\d{1,2}\.[0-9A-Z]{1,2}$", sub): return None
    if any(t not in OKF for t in LEAK.findall(text)): return None  # công thức vật liệu cụ thể → bỏ
    if not chk_ok(r.get("chk")): r["chk"] = None
    rid = r.get("id") or "G" + hashlib.sha1((sub + "|" + text.lower()).encode()).hexdigest()[:10]
    return {"id": rid if str(rid).startswith("G") else "G" + str(rid), "field": r.get("field") if r.get("field") in ("HER", "OER", "GEN") else "HER", "sub": sub, "text": text[:400],
            "basis": str(r.get("basis") or "")[:300], "chk": r.get("chk"), "status": "proposed", "n": int(r.get("n") or 1), "date": r.get("date") or now()}

def quant(v):
    v = sorted(v)
    if not v: return None
    q = lambda f: round(v[min(len(v) - 1, int(f * (len(v) - 1) + 0.5))], 1)
    return {"n": len(v), "p25": q(.25), "median": round(statistics.median(v), 1), "p75": q(.75), "best": round(v[0], 1)}

def bench(papers):
    out = {}
    for p in papers:
        rx, el = p.get("reaction"), p.get("electrolyte") or "unknown"
        for k in ("eta10", "eta100", "tafel"):
            if p.get(k) is not None: out.setdefault(rx, {}).setdefault(el, {}).setdefault(k, []).append(p[k])
        if p.get("stab_h") is not None: out.setdefault(rx, {}).setdefault(el, {}).setdefault("stab_h", []).append(-p["stab_h"])
    res = {}
    for rx, d in out.items():
        for el, dd in d.items():
            for k, v in dd.items():
                qv = quant(v)
                if k == "stab_h": qv = {"n": qv["n"], "p25": -qv["p75"], "median": -qv["median"], "p75": -qv["p25"], "best": -qv["best"]}
                res.setdefault(rx, {}).setdefault(el, {})[k] = qv
    return res

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--papers"); ap.add_argument("--rules"); ap.add_argument("--confirm"); a = ap.parse_args()
    pk = json.load(open(PACK, encoding="utf-8")) if os.path.exists(PACK) else {"version": 1, "papers": [], "rules": []}
    P = {key(p): p for p in pk.get("papers", [])}; added = upd = 0
    if a.papers:
        for raw in json.load(open(a.papers, encoding="utf-8")):
            p = clean_paper(raw)
            if not p: continue
            k = key(p)
            if k in P:
                o = P[k]; ch = False
                for f, v in p.items():
                    if f == "added": continue
                    if v not in (None, "") and o.get(f) in (None, ""): o[f] = v; ch = True
                upd += ch
            else: P[k] = p; added += 1
    papers = sorted(P.values(), key=lambda p: p.get("added", ""), reverse=True)[:MAX_PAPERS]
    R = {r["id"]: r for r in pk.get("rules", [])}; seen = {re.sub(r"\W+", " ", r["text"].lower()).strip() for r in R.values()}; nr = 0
    if a.rules:
        for raw in json.load(open(a.rules, encoding="utf-8")):
            r = clean_rule(raw)
            if not r: continue
            t = re.sub(r"\W+", " ", r["text"].lower()).strip()
            if r["id"] in R or t in seen: continue
            R[r["id"]] = r; seen.add(t); nr += 1
    nc = 0
    if a.confirm:
        for rid, n in json.load(open(a.confirm, encoding="utf-8")).items():
            if rid in R: R[rid]["n"] = int(R[rid].get("n", 1)) + max(0, int(n)); nc += 1
    pk.update({"version": 1, "updated": now(), "papers": papers, "rules": sorted(R.values(), key=lambda r: (r["sub"], r["id"])), "bench": bench(papers),
               "note": "PaperLens data pack. Public literature metadata and general review criteria only; no manuscripts."})
    json.dump(pk, open(PACK, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({"papers_total": len(papers), "papers_added": added, "papers_updated": upd, "rules_total": len(R), "rules_added": nr, "rules_confirmed": nc}, ensure_ascii=False))

if __name__ == "__main__": main()
