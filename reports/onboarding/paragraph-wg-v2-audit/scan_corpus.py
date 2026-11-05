#!/usr/bin/env python3
"""Exhaustive literal-cue scan, not automated semantic bias annotation."""
import csv,hashlib,json,re,random,zipfile
from collections import Counter,defaultdict
from pathlib import Path
from seed_lexicon import entries,CATEGORIES

ROOT=Path('/workspace/bias-wg-revision-v2')
OUT=ROOT/'scan'
CORPUS=Path('/workspace/wj-corpus-audit/extracted/data/raw/wikipedia')
ARCHIVE=Path('/workspace/real-data-validation/bordirlines.zip')
SUBSTRING={'zhs','zht','ja','ko','th','lo','km','my','dz'}
def dump(p,o):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2))
def csv_write(p,rows,fields=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    assert not OUT.exists(),'Frozen scan exists'
    OUT.mkdir()
    z=zipfile.ZipFile(ARCHIVE);indexed=json.loads(z.read('data/all_docs.json'))
    rawunits=[];rawarticles={};excluded=[]
    for p in sorted(CORPUS.glob('*/*.json')):
        obj=json.loads(p.read_text())
        if not isinstance(obj,dict) or not isinstance(obj.get('article'),list):
            excluded.append(p.relative_to(CORPUS).as_posix());continue
        lang=p.parent.name;pageid=p.stem.removeprefix('Q');rawarticles[(lang,pageid)]=obj
        for i,t in enumerate(obj['article']):
            if t.strip():rawunits.append({'language':lang,'doc_id':f'{pageid}_p{i}',
                'raw_file':p.relative_to(CORPUS).as_posix(),'raw_field':f'article[{i}]','text':t,
                'article_title':obj.get('title',''),'timestamp':obj.get('timestamp')})
    langs={u['language'] for u in rawunits}
    lex=[e for e in entries() if e['language'] in langs]
    bylang=defaultdict(list)
    for i,e in enumerate(lex):
        e['term_id']=f'T{i+1:04d}';e['matching_rule']='literal_substring_ignorecase' if e['language'] in SUBSTRING else 'unicode_word_bounded_literal_ignorecase'
        pattern=re.escape(e['term'])
        if e['language'] not in SUBSTRING:pattern=r'(?<!\w)'+pattern+r'(?!\w)'
        bylang[e['language']].append((e,re.compile(pattern,re.I)))
    csv_write(OUT/'seed_lexicon.csv',lex)
    assert langs<=set(bylang),langs-set(bylang)
    terms={e['term_id']:{**e,'indexed_occurrences':0,'indexed_paragraphs':0,'raw_occurrences':0,'raw_paragraphs':0} for e in lex}
    tiers={};examples=defaultdict(list);indexed_documents=[];category_counts=defaultdict(Counter)
    fields=['tier','language','doc_id','category','term_id','term','start_codepoint','end_codepoint','matched_text','raw_file','raw_field']
    occurrence_file=(OUT/'candidate_occurrences.csv').open('w',encoding='utf-8-sig',newline='')
    writer=csv.DictWriter(occurrence_file,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for tier in ['raw','indexed']:
        if tier=='raw':units=rawunits
        else:
            units=[]
            for lang,docs in indexed.items():
                for docid,t in docs.items():
                    match=re.fullmatch(r'(?:[a-z]+\.)?(\d+)_p(\d+)',docid);assert match,docid
                    pageid,i=match[1],int(match[2]);a=rawarticles[(lang,pageid)]
                    assert t.strip()==a['article'][i].strip(),(lang,docid)
                    units.append({'language':lang,'doc_id':docid,'raw_file':f'{lang}/Q{pageid}.json',
                        'raw_field':f'article[{i}]','text':t,'article_title':a.get('title',''),'timestamp':a.get('timestamp')})
        total=Counter(u['language'] for u in units);hitdocs=Counter();allmatches=0
        for u in units:
            hits=[]
            for e,pattern in bylang[u['language']]:
                found=list(pattern.finditer(u['text']))
                if not found:continue
                terms[e['term_id']][tier+'_occurrences']+=len(found);terms[e['term_id']][tier+'_paragraphs']+=1
                for m in found:
                    item={'category':e['category'],'term_id':e['term_id'],'term':e['term'],'start_codepoint':m.start(),'end_codepoint':m.end(),'matched_text':m.group()}
                    assert u['text'][m.start():m.end()]==item['matched_text']
                    writer.writerow({'tier':tier,**{k:u[k] for k in ['language','doc_id','raw_file','raw_field']},**item})
                    hits.append(item)
            if not hits:continue
            hitdocs[u['language']]+=1;allmatches+=len(hits)
            cats={h['category'] for h in hits}
            for cat in cats:
                category_counts[(tier,u['language'])][cat]+=1
                if tier=='indexed':examples[(u['language'],cat)].append({
                    **{k:u[k] for k in ['language','doc_id','raw_file','raw_field','article_title','timestamp']},
                    'category':cat,'text':u['text'],'matches':[h for h in hits if h['category']==cat],
                    'source_url':f"https://{'he' if u['language']=='iw' else 'zh' if u['language'] in {'zhs','zht'} else u['language']}.wikipedia.org/?curid={u['raw_file'].split('/Q')[1].split('.')[0]}",
                    'semantic_verdict':'not_assessed_surface_candidate_only'})
            if tier=='indexed':indexed_documents.append({**{k:u[k] for k in ['language','doc_id','raw_file','raw_field']},'categories':sorted(cats),'match_count':len(hits),'text_sha256':hashlib.sha256(u['text'].encode()).hexdigest()})
        tiers[tier]={'paragraphs':len(units),'languages':len(total),'paragraphs_by_language':dict(total),
            'paragraphs_with_any_cue':sum(hitdocs.values()),'paragraphs_with_any_cue_by_language':dict(hitdocs),
            'literal_matches_including_overlaps':allmatches}
    occurrence_file.close()
    csv_write(OUT/'term_frequencies.csv',list(terms.values()))
    freq=[];totals=[]
    for tier,t in tiers.items():
        for cat in CATEGORIES:
            n=sum(category_counts[(tier,lang)][cat] for lang in t['paragraphs_by_language'])
            totals.append({'tier':tier,'category':cat,'paragraphs':t['paragraphs'],'paragraphs_with_cue':n,'percent_with_cue':100*n/t['paragraphs'],'semantic_bias_frequency':'not_estimated'})
            for lang,nall in sorted(t['paragraphs_by_language'].items()):
                n=category_counts[(tier,lang)][cat]
                freq.append({'tier':tier,'language':lang,'category':cat,'paragraphs':nall,'paragraphs_with_cue':n,'percent_with_cue':100*n/nall,'lexicon_entries':sum(e['language']==lang and e['category']==cat for e in lex)})
    csv_write(OUT/'category_language_frequencies.csv',freq);csv_write(OUT/'category_totals.csv',totals)
    coverage=[]
    for lang in sorted(langs):
        row={'language':lang,'raw_paragraphs':tiers['raw']['paragraphs_by_language'].get(lang,0),'indexed_paragraphs':tiers['indexed']['paragraphs_by_language'].get(lang,0),'seed_terms':sum(e['language']==lang for e in lex),'translation_validation':'not_independently_validated','matching_rule':bylang[lang][0][0]['matching_rule']}
        row.update({cat+'_terms':sum(e['language']==lang and e['category']==cat for e in lex) for cat in CATEGORIES});coverage.append(row)
    csv_write(OUT/'language_coverage.csv',coverage)
    (OUT/'indexed_candidate_documents.jsonl').write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in indexed_documents))
    rng=random.Random(20261105);chosen=[]
    # One intact paragraph for each non-empty language/category cell, to expose uneven language coverage.
    for key,items in sorted(examples.items()):chosen.append(rng.choice(items))
    (OUT/'representative_examples.jsonl').write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in chosen))
    category_examples={cat:[r for r in chosen if r['category']==cat] for cat in CATEGORIES}
    dump(OUT/'examples_by_category.json',category_examples)
    summary={'source':'frozen WJ_data and indexed all_docs.json','raw_article_files':len(rawarticles),
        'excluded_metadata_files':len(excluded),'raw_article_languages':len({k[0] for k in rawarticles}),
        'raw_paragraphs_including_blank':sum(len(v['article']) for v in rawarticles.values()),'tiers':tiers,
        'lexicon_entries':len(lex),'lexicon_languages':len(bylang),'scan_categories':CATEGORIES,
        'G5_attribution_boundary_frequency':'not_computable_from_literal_cues; ATTR is an attribution-marker control, not a G5 label',
        'examples':len(chosen),'seed':20261105,'paper_annotation_protocol_changed':False,
        'existing_360_labels_changed':False,'corpus_bias_reannotated':False,
        'limitations':['All counts are literal candidate cues, not bias labels.','Original paragraphs only; no neighboring paragraphs concatenated.','Seed lexicon is assistant-proposed; uneven lexical/morphological coverage and unvalidated translations, especially low-resource languages.','Literal counts across languages are not calibrated bias prevalence.','Term matches may overlap; paragraph counts per category are unions, across categories overlap remains.','Figures include all territories and languages, without excluding China-related material.'],
        'source_sha256':{'bordirlines.zip':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()}}
    dump(OUT/'scan_summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['tiers','limitations']},ensure_ascii=False))
    print(json.dumps(totals,ensure_ascii=False))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,default=ARCHIVE)
    parser.add_argument('--corpus',type=Path,default=CORPUS)
    parser.add_argument('--out',type=Path,default=OUT)
    args=parser.parse_args()
    ARCHIVE,CORPUS,OUT=args.archive,args.corpus,args.out
    main()
