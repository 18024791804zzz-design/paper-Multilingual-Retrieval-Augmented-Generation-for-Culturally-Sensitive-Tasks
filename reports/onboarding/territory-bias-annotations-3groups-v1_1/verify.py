#!/usr/bin/env python3
"""Check artifact integrity. This does not measure annotation accuracy."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
def main():
    root=Path(__file__).resolve().parent
    labels=json.loads((root/'labels.json').read_text())
    rows=[json.loads(line) for line in (root/'annotations.jsonl').read_text().splitlines()]
    csvrows=list(csv.DictReader((root/'annotations.csv').open(encoding='utf-8-sig',newline='')))
    samples=json.loads((root/'audit/combined_manifest.json').read_text())['samples']
    known={s['sample_id']:s for s in samples}
    assert len(rows)==len(csvrows)==len(labels)==len(known)==360
    assert {r['sample_id']:r['bias_label'] for r in rows}==labels
    assert Counter(r['group_id'] for r in rows)=={'G1':120,'G2':120,'G3':120}
    assert len({r['territory'] for r in rows})==30
    assert len({(r['territory'],r['doc_lang'],r['doc_id']) for r in rows})==360
    assert set(Counter(r['batch_id'] for r in rows).values())=={12}
    for r,c in zip(rows,csvrows):
        s=known[r['sample_id']];k,d=r['bias_label'].split('::')
        assert k in ['NONE','UNK','W','I','G','W+I','W+G','I+G','W+I+G']
        assert d in s['claimants']+['NEUTRAL','MIXED','UNKNOWN']
        assert r['original_text']==s['original_text']==c['original_text']
        assert r['bias_label']==c['bias_label']
        assert hashlib.sha256(r['original_text'].encode()).hexdigest()==r['original_text_sha256']==s['text_sha256']
        assert not r['evidence_quote'] or r['evidence_quote'] in r['original_text']
        assert k=='NONE' or r['evidence_quote']
    group1=json.loads((root/'audit/group1_labels_v1_1.json').read_text())
    assert {r['sample_id']:r['bias_label'] for r in rows if r['group_id']=='G1'}==group1
    assert labels['B10-D05']=='UNK::NEUTRAL'
    assert len(json.loads((root/'audit/new_groups_recheck_log.json').read_text()))==13
    for line in (root/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
    print(json.dumps({'integrity':'passed','samples':360,'groups':3,'territories':30,'group1_revision_preserved':True,
        'original_text_hashes':'passed','evidence_substrings':'passed','semantic_accuracy_tested':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
