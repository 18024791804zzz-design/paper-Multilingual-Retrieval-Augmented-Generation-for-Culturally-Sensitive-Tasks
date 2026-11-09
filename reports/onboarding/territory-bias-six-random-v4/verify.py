"""Standard-library checks of format, sampling, source preservation and exports."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import random
import re

ROOT = Path(__file__).resolve().parent


def verify():
    rows = [json.loads(x) for x in (ROOT / "annotations.jsonl").read_text().splitlines()]
    manifest = json.loads((ROOT / "audit/sampling_manifest.json").read_text())
    source = {r["sample_id"]: r for r in manifest["samples"]}
    previous = [json.loads(x) for x in (ROOT / "audit/previous_360_v4.jsonl").read_text().splitlines()]
    old_hashes = {r["original_text_sha256"] for r in previous}
    old_territories = {r["territory"].replace("_", " ") for r in previous}
    sampling = json.loads((ROOT / "audit/sampling.json").read_text())
    assert len(rows) == len(source) == 720
    assert len({r["sample_id"] for r in rows}) == 720
    assert set(r["sample_id"] for r in rows) == set(source)
    assert collections.Counter(r["group_id"] for r in rows) == {f"G{g}": 120 for g in range(4, 10)}
    assert len({r["territory"] for r in rows}) == 60
    assert set(collections.Counter(r["batch_id"] for r in rows).values()) == {12}
    assert len({r["original_text_sha256"] for r in rows}) == 720
    assert not ({r["original_text_sha256"] for r in rows} & old_hashes)
    assert not ({r["territory"].replace("_", " ") for r in rows} & old_territories)
    assert random.Random(20261109).sample(sampling["frame_territories"], 91) == sampling["random_permutation"]
    assert sampling["selection_order"] == sampling["random_permutation"][:60]
    assert not sampling["skipped_for_allocation"]
    notes = {}
    quote_count = 0
    for p in sorted((ROOT / "audit/direct_notes").glob("*.json")):
        ns = json.loads(p.read_text())
        inputs = json.loads((ROOT / "audit/review_inputs" / p.name).read_text())
        assert len(ns) == len(inputs) == 12
        assert {r[0] for r in ns} == {r["sample_id"] for r in inputs}
        for r in inputs:
            assert set(r) == {"sample_id", "batch_id", "territory", "territory_zh", "doc_lang", "doc_id", "original_text_sha256", "original_text"}
            assert r["original_text"] == source[r["sample_id"]]["original_text"]
        for n in ns:
            assert n[0] not in notes
            notes[n[0]] = n
    assert len(notes) == 720
    for r in rows:
        s = source[r["sample_id"]]
        assert r["bias_label"] == notes[r["sample_id"]][1]
        assert r["reason_zh"] == notes[r["sample_id"]][2]
        for k in ["group_id", "batch_id", "territory", "territory_zh", "doc_lang", "doc_id", "original_text", "source_url", "raw_file", "raw_field"]:
            assert r[k] == s[k], (r["sample_id"], k)
        assert hashlib.sha256(r["original_text"].encode()).hexdigest() == r["original_text_sha256"] == s["original_text_sha256"]
        assert r["bias_label"] in {"NONE", "UNK"} or re.fullmatch(r"(?:W[1-5]\+)*(?:W[1-5]|G)", r["bias_label"])
        assert "::" not in r["bias_label"] and "direction" not in r
        if r["bias_label"] not in {"NONE", "UNK"}:
            labels = r["bias_label"].split("+")
            assert labels == sorted(set(labels), key=lambda x: (x == "G", x))
        assert r["annotation_scope"] == "target_paragraph_only"
        assert r["reason_zh"]
        if r["bias_label"] != "NONE":
            assert r["claim_quote"]
        for k in ["claim_quote", "attribution_quote"]:
            if r[k] is not None:
                assert r[k] in r["original_text"], (r["sample_id"], k)
                quote_count += 1
        anchor = s["selection"]["selected_origin"]
        assert anchor in s["retrieval_origins"]
        assert 4 <= r["selected_rank"] <= 50
        assert all(4 <= h["rank"] <= 50 for h in s["retrieval_origins"])
        assert r["selected_rank"] == anchor["rank"] and r["selected_query_id"] == anchor["query_id"]
        assert r["selected_retriever"] == anchor["retriever"] and r["selected_mode"] == anchor["mode"]
    def band(rank):
        return "4-10" if rank <= 10 else "11-25" if rank <= 25 else "26-50"
    assert collections.Counter(band(r["selected_rank"]) for r in rows) == {"4-10": 240, "11-25": 240, "26-50": 240}
    assert collections.Counter(r["selected_retriever"] for r in rows) == {"openai": 360, "m3": 360}
    for bid in {r["batch_id"] for r in rows}:
        subset = [r for r in rows if r["batch_id"] == bid]
        quotas = collections.Counter((r["selected_query_id"], r["selected_retriever"], band(r["selected_rank"])) for r in subset)
        assert len(quotas) == 12 and set(quotas.values()) == {1}
        assert len({r["selected_query_id"] for r in subset}) == 2
    with (ROOT / "annotations.csv").open(encoding="utf-8-sig", newline="") as f:
        cr = list(csv.DictReader(f))
    assert len(cr) == 720
    assert [(r["sample_id"], r["bias_label"], r["original_text"]) for r in cr] == [(r["sample_id"], r["bias_label"], r["original_text"]) for r in rows]
    assert json.loads((ROOT / "labels.json").read_text()) == {r["sample_id"]: r["bias_label"] for r in rows}
    document = (ROOT / "index.html").read_text()
    data = re.search(r'<script id="dataset" type="application/json">(.*?)</script>', document, re.S).group(1)
    assert json.loads(data) == rows
    combined = [json.loads(x) for x in (ROOT / "combined_9groups/annotations.jsonl").read_text().splitlines()]
    assert len(combined) == len({r["sample_id"] for r in combined}) == 1080
    assert len({r["original_text_sha256"] for r in combined}) == 1072
    by_id = {r["sample_id"]: r for r in combined}
    for r in previous:
        for k in by_id[r["sample_id"]]:
            assert by_id[r["sample_id"]][k] == r.get(k)
    meta = json.loads((ROOT / "annotation_metadata.json").read_text())
    assert hashlib.sha256((ROOT / "audit/previous_360_v4.jsonl").read_bytes()).hexdigest() == meta["previous_360_file_sha256"] == manifest["previous_annotations_sha256"]
    assert meta["neighboring_paragraphs_used"] is False and meta["external_fact_searches_for_judgment"] is False
    files_checked = 0
    p = ROOT / "SHA256SUMS"
    if p.exists():
        for line in p.read_text().splitlines():
            expected, name = line.split("  ", 1)
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
            files_checked += 1
    result = {
        "status": "passed", "new_rows": 720, "new_groups": 6, "new_territories": 60,
        "old_territory_overlap": 0, "old_exact_text_overlap": 0, "new_duplicate_exact_texts": 0,
        "source_text_hashes_preserved": 720, "exact_quotes_checked": quote_count,
        "random_permutation_reproduced": True, "all_applicable_top3_excluded": True,
        "rank_band_and_retriever_quotas": "passed", "target_only_input_batches": 60,
        "CSV_JSONL_viewer_consistency": "passed", "combined_rows": 1080,
        "previous_360_labels_and_texts_preserved": True, "checksummed_files": files_checked,
        "scope": "Artifact and sampling integrity; not independent annotation accuracy or F1"
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    verify()
