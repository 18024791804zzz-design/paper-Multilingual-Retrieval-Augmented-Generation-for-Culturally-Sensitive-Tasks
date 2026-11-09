"""Randomly freeze six NEW groups before annotation; never select by a bias label."""
from pathlib import Path
from collections import Counter, defaultdict
from functools import lru_cache
import csv
import hashlib
import io
import json
import random
import re
import zipfile

BASE = Path(__file__).resolve().parent
OUT = BASE / "frozen"
ZIP = Path("/workspace/real-data-validation/bordirlines.zip")
RAW = Path("/workspace/wj-corpus-audit/extracted/data/raw/wikipedia")
FRAME = Path("/workspace/bias-subset-feasibility/candidate_counts.json")
PREVIOUS = Path("/workspace/bias-reannotation-v4/territory-bias-3groups-v4/annotations.jsonl")
SEED = 20261109
BANDS = [(4, 10), (11, 25), (26, 50)]


def dump(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


@lru_cache(maxsize=None)
def raw_article(lang, number):
    return json.loads((RAW / lang / f"Q{number}.json").read_text())


@lru_cache(maxsize=None)
def target(lang, doc_id):
    match = re.fullmatch(r"(?:[a-z]+\.)?(\d+)_p(\d+)", doc_id)
    if not match:
        raise ValueError(doc_id)
    page, index = match.group(1), int(match.group(2))
    raw = raw_article(lang, page)
    text = raw["article"][index]
    return text, page, index, raw.get("title", ""), raw.get("timestamp")


def main():
    assert not OUT.exists(), "Keep previously frozen random samples."
    prior = [json.loads(x) for x in PREVIOUS.read_text().splitlines()]
    used_territories = {r["territory"].replace("_", " ") for r in prior}
    prior_keys = {(r["doc_lang"], r["doc_id"]) for r in prior}
    prior_hashes = {r["original_text_sha256"] for r in prior}
    frame = sorted((t for t in json.loads(FRAME.read_text())["territories"]
                    if not t["china_related"] and t["territory"].replace("_", " ") not in used_territories),
                   key=lambda t: t["territory"])
    assert len(frame) == 91
    with zipfile.ZipFile(ZIP) as z:
        queries = {r["query_id"]: r for r in csv.DictReader(io.StringIO(z.read("data/queries.tsv").decode()), delimiter="\t")}
        indexed = json.loads(z.read("data/all_docs.json"))
        qids = {q["query_id"] for t in frame for q in t["queries"]}
        by_q = defaultdict(lambda: defaultdict(list))
        for lang in sorted({queries[q]["language"] for q in qids}):
            folder = "control" if lang == "en" else lang
            for retriever in ["openai", "m3"]:
                for mode in ["qlang", "rel_langs"]:
                    member = f"data/{folder}/{retriever}/{mode}/{folder}_query_hits.tsv"
                    for r in csv.DictReader(io.StringIO(z.read(member).decode()), delimiter="\t"):
                        if r["query_id"] not in qids:
                            continue
                        hit = {"query_id": r["query_id"], "query_lang": lang, "retriever": retriever,
                               "mode": mode, "rank": int(r["rank"]), "score": r["score"], "zip_member": member}
                        by_q[r["query_id"]][(r["doc_lang"], r["doc_id"])].append(hit)
    rng = random.Random(SEED)
    permutation = rng.sample(frame, len(frame))
    used_hashes = set(prior_hashes)
    samples, batches, skipped = [], [], []
    coverage = []
    candidate_rejections = Counter()
    for attempt, t in enumerate(permutation):
        if len(batches) == 60:
            break
        qlist = sorted(q["query_id"] for q in t["queries"])
        assert len(qlist) == 2
        pool = defaultdict(list)
        for q in qlist:
            for key, hits in by_q[q].items():
                pool[key].extend(hits)
        valid = {}
        for key, hits in sorted(pool.items()):
            if min(h["rank"] for h in hits) <= 3:
                candidate_rejections["any_applicable_top3"] += 1
                continue
            if key in prior_keys:
                candidate_rejections["previous_doc_identity"] += 1
                continue
            try:
                text, page, index, title, timestamp = target(*key)
                assert text.strip() == indexed[key[0]][key[1]].strip()
            except (FileNotFoundError, ValueError, KeyError, IndexError, AssertionError):
                candidate_rejections["raw_missing_or_mismatch"] += 1
                continue
            if not text.strip():
                candidate_rejections["empty"] += 1
                continue
            digest = hashlib.sha256(text.encode()).hexdigest()
            if digest in used_hashes:
                candidate_rejections["previous_or_already_selected_text"] += 1
                continue
            valid[key] = {"text": text, "page": page, "index": index, "title": title,
                          "timestamp": timestamp, "hash": digest, "hits": hits}
        # Quotas constrain ranking coverage, not the content or bias judgement.
        # Random attempts solve the small allocation without selecting a preferred wording.
        picked = None
        for allocation_attempt in range(200):
            local_rng = random.Random(SEED + 1009 * attempt + 104729 * allocation_attempt)
            local, local_hashes = {}, set()
            slots = [(q, retriever, lo, hi) for q in qlist for retriever in ["openai", "m3"] for lo, hi in BANDS]
            local_rng.shuffle(slots)
            ok = True
            for q, retriever, lo, hi in slots:
                available = [key for key, v in valid.items() if key not in local and v["hash"] not in local_hashes
                             and any(h["query_id"] == q and h["retriever"] == retriever and lo <= h["rank"] <= hi for h in v["hits"])]
                if not available:
                    ok = False
                    break
                key = local_rng.choice(sorted(available))
                hits = [h for h in valid[key]["hits"] if h["query_id"] == q and h["retriever"] == retriever and lo <= h["rank"] <= hi]
                anchor = local_rng.choice(sorted(hits, key=lambda h: (h["mode"], h["rank"])))
                local[key] = {"stratum": f"{retriever}_rank_{lo}_{hi}", "query_id": q, "selected_origin": anchor}
                local_hashes.add(valid[key]["hash"])
            if ok:
                picked = local
                break
        if picked is None:
            skipped.append({"territory": t["territory"], "reason": "Cannot allocate all 12 unique paragraphs with the fixed query/retriever/rank quotas after exclusion.", "eligible_unique_candidates": len(valid)})
            continue
        number = 31 + len(batches)
        bid, group = f"B{number:02d}", f"G{4 + len(batches)//10}"
        order = list(picked)
        random.Random(SEED + 1000003 + attempt).shuffle(order)
        input_rows = []
        for i, key in enumerate(order, 1):
            v = valid[key]
            sid = f"{bid}-D{i:02d}"
            record = {
                "sample_id": sid, "batch_id": bid, "group_id": group, "territory": t["territory"],
                "territory_zh": t["territory"], "claimants": t["claimants"], "annotation_unit": "territory_doc",
                "doc_lang": key[0], "doc_id": key[1], "article_title": v["title"], "article_timestamp": v["timestamp"],
                "raw_file": f"{key[0]}/Q{v['page']}.json", "raw_field": f"article[{v['index']}]",
                "source_url": f"https://{'he' if key[0]=='iw' else key[0]}.wikipedia.org/?curid={v['page']}",
                "original_text_sha256": v["hash"], "original_text": v["text"], "selection": picked[key],
                "retrieval_origins": v["hits"], "original_queries": [{k: queries[q][k] for k in ["query_id", "language", "query_text"]} for q in qlist]
            }
            samples.append(record)
            used_hashes.add(v["hash"])
            input_rows.append({k: record[k] for k in ["sample_id", "batch_id", "territory", "territory_zh", "doc_lang", "doc_id", "original_text_sha256", "original_text"]})
        dump(OUT / "inputs" / f"{bid}.json", input_rows)
        batches.append({"batch_id": bid, "group_id": group, "territory": t["territory"], "claimants": t["claimants"], "queries": qlist, "count": 12})
        coverage.append({"batch_id": bid, "eligible_candidates_at_allocation": len(valid), "allocation_attempt": allocation_attempt, "permutation_index": attempt})
    assert len(batches) == 60 and len(samples) == 720, (len(batches), skipped)
    assert len({r["original_text_sha256"] for r in samples}) == 720
    assert not ({r["original_text_sha256"] for r in samples} & prior_hashes)
    assert all(min(h["rank"] for h in r["retrieval_origins"]) >= 4 for r in samples)
    manifest = {
        "version": "six-random-v4", "seed": SEED, "annotation_unit": "territory_doc",
        "samples": samples, "batches": batches,
        "source_archive_sha256": hashlib.sha256(ZIP.read_bytes()).hexdigest(),
        "previous_annotations_sha256": hashlib.sha256(PREVIOUS.read_bytes()).hexdigest(),
    }
    sampling = {
        "seed": SEED, "rng": "Python random.Random; complete algorithm in sample_six.py",
        "eligible_original_frame_excluding_PRС_ROC": 121, "previous_territories_excluded": 30, "remaining_frame": 91,
        "frame_territories": [t["territory"] for t in frame],
        "random_permutation": [t["territory"] for t in permutation],
        "selection_order": [t["territory"] for t in batches], "skipped_for_allocation": skipped, "allocation_details": coverage,
        "candidate_rejections_during_allocation": dict(candidate_rejections),
        "rules": [
            "Exactly two claimant languages with both native queries, same historical eligibility; PRC/ROC claimant territories excluded.",
            "Exclude all previous 30 territories, all prior 352 original paragraph texts and all already selected new paragraph texts.",
            "Exclude any paragraph that occurs in ranks 1-3 in ANY applicable query/retriever/mode list of its territory.",
            "Per territory choose 12: for each of two native queries and each retriever, one paragraph in ranks 4-10, 11-25 and 26-50, from qlang/rel_langs.",
            "No filtering or selection by old/new viewpoint labels, bias words, paragraph length or anticipated label.",
            "Read original complete target paragraphs only; retain headings and lists when randomly selected.",
            "Rank-stratified random extension with global text deduplication, not simple random sampling of all 251 territories or all corpus paragraphs."
        ],
        "groups": {f"G{g}": [t["territory"] for t in batches if t["group_id"] == f"G{g}"] for g in range(4, 10)}
    }
    dump(OUT / "manifest.json", manifest)
    dump(OUT / "sampling.json", sampling)
    print(json.dumps({"samples": len(samples), "territories": len(batches), "groups": sampling["groups"],
                      "languages": dict(Counter(r["doc_lang"] for r in samples)),
                      "characters": sum(len(r["original_text"]) for r in samples), "skipped": len(skipped)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
