"""Validate the delivered annotations; uses the Python standard library only."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent


def verify():
    rows = [json.loads(line) for line in (ROOT / "annotations.jsonl").read_text().splitlines()]
    prior = [json.loads(line) for line in (ROOT / "audit/previous_annotations_v1_1.jsonl").read_text().splitlines()]
    source = {r["sample_id"]: r for r in prior}
    manifest = {r["sample_id"]: r for r in json.loads((ROOT / "audit/previous_sampling_manifest.json").read_text())["samples"]}
    assert len(rows) == len(source) == 360
    assert set(r["sample_id"] for r in rows) == set(source)
    assert len(set(r["sample_id"] for r in rows)) == 360
    assert collections.Counter(r["group_id"] for r in rows) == {"G1": 120, "G2": 120, "G3": 120}
    assert len(set(r["territory"] for r in rows)) == 30
    assert set(collections.Counter(r["batch_id"] for r in rows).values()) == {12}
    assert len(set((r["doc_lang"], r["doc_id"]) for r in rows)) == 352
    assert len(set(r["original_text_sha256"] for r in rows)) == 352
    repeated = collections.defaultdict(set)
    quote_count = 0
    for r in rows:
        p = source[r["sample_id"]]
        m = manifest[r["sample_id"]]
        assert r["original_text"] == p["original_text"] == m["original_text"]
        digest = hashlib.sha256(r["original_text"].encode()).hexdigest()
        assert digest == r["original_text_sha256"] == p["original_text_sha256"] == m["text_sha256"]
        for key in ("group_id", "batch_id", "territory", "territory_zh", "doc_lang", "doc_id"):
            assert r[key] == p[key]
        assert r["previous_bias_label"] == p["bias_label"]
        assert r["bias_label"] in {"NONE", "UNK"} or re.fullmatch(r"(?:W[1-5]\+)*(?:W[1-5]|G)", r["bias_label"])
        if r["bias_label"] not in {"NONE", "UNK"}:
            labels = r["bias_label"].split("+")
            assert labels == sorted(set(labels), key=lambda x: (x == "G", x))
        assert "::" not in r["bias_label"]
        assert "direction" not in r
        assert r["annotation_scope"] == "target_paragraph_only"
        assert r["reason_zh"] and r["change_reason_zh"]
        if r["bias_label"] != "NONE":
            assert r["claim_quote"] and r["claim_quote"] in r["original_text"]
        for key in ("claim_quote", "attribution_quote"):
            if r[key] is not None:
                assert r[key] in r["original_text"], (r["sample_id"], key)
                quote_count += 1
        repeated[digest].add(r["bias_label"])
    assert all(len(labels) == 1 for labels in repeated.values())
    with (ROOT / "annotations.csv").open(encoding="utf-8-sig", newline="") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == 360
    assert [r["bias_label"] for r in csv_rows] == [r["bias_label"] for r in rows]
    assert [r["original_text"] for r in csv_rows] == [r["original_text"] for r in rows]
    assert json.loads((ROOT / "labels.json").read_text()) == {r["sample_id"]: r["bias_label"] for r in rows}
    for batch in sorted(set(r["batch_id"] for r in rows)):
        inputs = json.loads((ROOT / "audit/review_inputs" / f"{batch}.json").read_text())
        notes = json.loads((ROOT / "audit/direct_notes" / f"{batch}.json").read_text())
        assert {r["sample_id"] for r in inputs} == {r["sample_id"] for r in notes}
        assert len(inputs) == len(notes) == 12
        for r in inputs:
            assert set(r) == {"sample_id", "batch_id", "territory", "territory_zh", "doc_lang", "doc_id", "original_text_sha256", "original_text"}
            assert r["original_text"] == source[r["sample_id"]]["original_text"]
    meta = json.loads((ROOT / "annotation_metadata.json").read_text())
    assert hashlib.sha256((ROOT / "audit/previous_annotations_v1_1.jsonl").read_bytes()).hexdigest() == meta["original_annotations_sha256"]
    assert meta["external_fact_searches_for_judgment"] is False
    assert meta["adjacent_paragraphs_used_for_judgment"] is False
    checksums = ROOT / "SHA256SUMS"
    files_checked = 0
    if checksums.exists():
        for line in checksums.read_text().splitlines():
            expected, name = line.split("  ", 1)
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
            files_checked += 1
    result = {
        "status": "passed",
        "rows": 360, "groups": 3, "territories": 30, "unique_paragraphs": 352,
        "original_text_hashes_preserved": 360,
        "exact_quotes_checked": quote_count,
        "duplicate_text_label_conflicts": 0,
        "target_only_input_batches_checked": 30,
        "checksummed_files": files_checked,
        "scope": "Artifact integrity and format only; not annotation accuracy or F1",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    verify()
