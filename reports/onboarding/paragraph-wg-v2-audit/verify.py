#!/usr/bin/env python3
"""Artifact integrity, not semantic accuracy."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
root=Path(__file__).resolve().parent
def read(name):return list(csv.DictReader((root/name).open(encoding='utf-8-sig',newline='')))
summary=json.loads((root/'scan/scan_summary.json').read_text())
terms=read('scan/term_frequencies.csv');counts=Counter();docs=defaultdict(set)
for r in read('scan/candidate_occurrences.csv'):
    tier,tid=r['tier'],r['term_id'];counts[(tier,tid)]+=1
    docs[(tier,tid)].add((r['language'],r['doc_id']))
for t in terms:
    for tier in ['raw','indexed']:
        assert counts[(tier,t['term_id'])]==int(t[tier+'_occurrences'])
        assert len(docs[(tier,t['term_id'])])==int(t[tier+'_paragraphs'])
examples=[json.loads(s) for s in (root/'scan/representative_examples.jsonl').read_text().splitlines()]
for r in examples:
    for m in r['matches']:assert r['text'][m['start_codepoint']:m['end_codepoint']]==m['matched_text']
assert len(terms)==1663
assert summary['tiers']['indexed']['paragraphs']==25311
assert summary['tiers']['raw']['paragraphs']==62349
assert len(json.loads((root/'rubric_v2.json').read_text())['categories'])==10
for line in (root/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split('  ',1);assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
print(json.dumps({'integrity':'passed','terms':len(terms),'examples':len(examples),'semantic_bias_accuracy_tested':False,'old_labels_changed':False},ensure_ascii=False))
