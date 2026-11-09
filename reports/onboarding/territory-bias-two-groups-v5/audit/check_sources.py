"""Check locators against separately supplied frozen raw and retrieval archives."""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import io
import json
import re
import zipfile


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--raw-root', type=Path, required=True)
    p.add_argument('--retrieval-zip', type=Path, required=True)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    root = Path(__file__).resolve().parent.parent
    rows = [json.loads(s) for s in (root / 'annotations.jsonl').read_text().splitlines()]
    files = {}
    for r in rows:
        path = args.raw_root / r['raw_file']
        if path not in files:
            files[path] = json.loads(path.read_text())
        idx = int(re.fullmatch(r'article\[(\d+)\]', r['raw_field'])[1])
        assert files[path]['article'][idx] == r['original_text'], r['sample_id']
    with (root / 'retrieval_origins.csv').open(encoding='utf-8-sig', newline='') as f:
        origins = list(csv.DictReader(f))
    by_member = collections.defaultdict(list)
    for o in origins:
        by_member[o['zip_member']].append(o)
    with zipfile.ZipFile(args.retrieval_zip) as z:
        docs = json.loads(z.read('data/all_docs.json'))
        for r in rows:
            assert docs[r['doc_lang']][r['doc_id']].strip() == r['original_text'].strip(), r['sample_id']
        ranks_checked = 0
        for member, expected in by_member.items():
            with z.open(member) as binary:
                rs = list(csv.DictReader(io.TextIOWrapper(binary, encoding='utf-8-sig'), delimiter='\t'))
            hit_map = {(r['query_id'], r['doc_lang'], r['doc_id']): r for r in rs}
            for o in expected:
                hit = hit_map[(o['query_id'], o['doc_lang'], o['doc_id'])]
                assert int(hit['rank']) == int(o['rank'])
                assert abs(float(hit['score']) - float(o['score'])) < 1e-8
                ranks_checked += 1
    result = {'status': 'passed', 'raw_paragraph_matches': len(rows), 'raw_article_files': len(files), 'indexed_paragraph_matches': len(rows), 'retrieval_rank_and_score_matches': ranks_checked, 'retrieval_tsv_files': len(by_member), 'retrieval_zip_sha256': hashlib.sha256(args.retrieval_zip.read_bytes()).hexdigest(), 'scope': 'Original paragraph and provenance integrity only, not annotation accuracy'}
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
