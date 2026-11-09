"""Verify frozen annotations and export integrity; not annotation accuracy."""
from pathlib import Path
import collections
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent
ORDER = ['W1', 'W2', 'W3', 'G', 'U']


def verify():
    rows = [json.loads(s) for s in (ROOT / 'annotations.jsonl').read_text().splitlines()]
    old = {r['sample_id']: r for r in (json.loads(s) for s in (ROOT / 'audit/previous_annotations_v4.jsonl').read_text().splitlines())}
    inputs = {r['sample_id']: r for p in sorted((ROOT / 'audit/review_inputs').glob('*.json')) for r in json.loads(p.read_text())}
    notes = [r for p in sorted((ROOT / 'audit/direct_notes').glob('*.json')) for r in json.loads(p.read_text())]
    assert len(rows) == len(old) == len(inputs) == len(notes) == 240
    ids = [r['sample_id'] for r in rows]
    assert len(set(ids)) == 240 and set(ids) == set(old) == set(inputs) == {n[0] for n in notes}
    assert collections.Counter(r['group_id'] for r in rows) == {'G1': 120, 'G2': 120}
    assert len({r['territory'] for r in rows}) == 20
    assert set(collections.Counter(r['batch_id'] for r in rows).values()) == {12}
    manifest = json.loads((ROOT / 'audit/sampling_manifest.json').read_text())
    assert manifest['objects'] == len(manifest['samples']) == 240
    manifest_by_id = {r['sample_id']: r for r in manifest['samples']}
    assert set(manifest_by_id) == set(ids)
    note_by_id = {n[0]: n for n in notes}
    repeated = collections.defaultdict(set)
    quotes_checked = 0
    for r in rows:
        sid = r['sample_id']
        p = old[sid]
        assert r['original_text'] == p['original_text'] == inputs[sid]['original_text']
        assert r['original_text'] == manifest_by_id[sid]['original_text']
        assert hashlib.sha256(r['original_text'].encode()).hexdigest() == r['original_text_sha256'] == p['original_text_sha256']
        for k in ['group_id', 'batch_id', 'territory', 'territory_zh', 'doc_lang', 'doc_id', 'raw_file', 'raw_field', 'article_title', 'article_timestamp', 'source_url', 'original_queries']:
            assert r[k] == p[k], (sid, k)
        assert 'previous_bias_label' not in inputs[sid] and 'bias_label' not in inputs[sid]
        assert r['previous_bias_label_v4'] == p['bias_label']
        assert r['findings'] == note_by_id[sid][1]
        assert r['annotation_version'] == 'v5' and r['annotation_scope'] == 'target_paragraph_only'
        assert 'UNK' not in r['bias_label'] and '::' not in r['bias_label']
        label = '+'.join(k for k in ORDER if any(f['type'] == k for f in r['findings'])) or 'NONE'
        assert label == r['bias_label']
        assert r['confirmed_wg_risk'] == any(f['status'] == 'confirmed' and f['type'] in {'W1', 'W2', 'G'} for f in r['findings'])
        assert r['has_uncertain'] == any(f['status'] == 'uncertain' for f in r['findings'])
        assert r['has_structure_issue'] == any(f['type'] == 'U' for f in r['findings'])
        for f in r['findings']:
            assert set(f) == {'type', 'status', 'quotes', 'reason'}
            assert f['type'] in ORDER and f['reason'] and f['quotes']
            allowed = {'uncertain'} if f['type'] == 'W3' else ({'confirmed', 'uncertain'} if f['type'] == 'G' else {'confirmed'})
            assert f['status'] in allowed
            for q in f['quotes']:
                assert isinstance(q, str) and q and q in r['original_text'], (sid, q)
                quotes_checked += 1
        repeated[r['original_text_sha256']].add(json.dumps([r['bias_label'], r['findings']], sort_keys=True, ensure_ascii=False))
    assert all(len(v) == 1 for v in repeated.values())
    assert len(repeated) == 237
    with (ROOT / 'annotations.csv').open(encoding='utf-8-sig', newline='') as f:
        crows = list(csv.DictReader(f))
    assert len(crows) == len(rows)
    for a, b in zip(rows, crows):
        assert a['sample_id'] == b['sample_id'] and a['original_text'] == b['original_text']
        assert a['bias_label'] == b['bias_label'] and a['findings'] == json.loads(b['findings'])
    assert json.loads((ROOT / 'labels.json').read_text()) == {r['sample_id']: r['bias_label'] for r in rows}
    with (ROOT / 'retrieval_origins.csv').open(encoding='utf-8-sig', newline='') as f:
        origins = list(csv.DictReader(f))
    assert len(origins) == 981 and set(o['sample_id'] for o in origins) <= set(ids)
    assert sum(len(r['retrieval_origins']) for r in rows) == len(origins)
    summary = json.loads((ROOT / 'summary.json').read_text())
    assert summary['total']['confirmed_WG_risk'] == sum(r['confirmed_wg_risk'] for r in rows)
    assert summary['total']['uncertain'] == sum(r['has_uncertain'] for r in rows)
    assert summary['total']['U_structure'] == sum(r['has_structure_issue'] for r in rows)
    assert summary['total']['NONE'] == sum(r['bias_label'] == 'NONE' for r in rows)
    html = (ROOT / 'index.html').read_text()
    embedded = html.split('<script id="annotation-data" type="application/json">', 1)[1].split('</script>', 1)[0]
    assert json.loads(embedded)['rows'] == rows
    for name, select in [('confirmed_risk_cases', lambda r: r['confirmed_wg_risk']), ('uncertain_cases', lambda r: r['has_uncertain']), ('structure_cases', lambda r: r['has_structure_issue']), ('changes', lambda r: r['label_string_changed'])]:
        with (ROOT / (name + '.csv')).open(encoding='utf-8-sig', newline='') as f:
            actual = list(csv.DictReader(f))
        assert [r['sample_id'] for r in actual] == [r['sample_id'] for r in rows if select(r)]
    meta = json.loads((ROOT / 'annotation_metadata.json').read_text())
    assert hashlib.sha256((ROOT / 'audit/previous_annotations_v4.jsonl').read_bytes()).hexdigest() == meta['prior_v4_subset_sha256']
    assert meta['external_fact_searches_for_judgment'] is False and meta['adjacent_paragraphs_used_for_judgment'] is False
    checked = 0
    if (ROOT / 'SHA256SUMS').exists():
        for line in (ROOT / 'SHA256SUMS').read_text().splitlines():
            digest, name = line.split('  ', 1)
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
            checked += 1
    return {'status': 'passed', 'objects': len(rows), 'groups': 2, 'territories': 20, 'unique_original_texts': len(repeated), 'exact_quotes_checked': quotes_checked, 'duplicate_text_label_conflicts': 0, 'all_240_original_texts_preserved': True, 'direct_judgments': len(notes), 'target_only_batches': 20, 'checksummed_files': checked, 'scope': 'Artifact integrity and format, not annotation accuracy/F1'}


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
