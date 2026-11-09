"""Export frozen direct judgments. This script is not a bias classifier."""
from pathlib import Path
import collections
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent
ORDER = ['W1', 'W2', 'W3', 'G', 'U']


def dump(name, obj):
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def write_csv(name, rows, fields):
    with (ROOT / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fields, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(row.get(k), ensure_ascii=False) if isinstance(row.get(k), (dict, list)) else row.get(k) for k in fields})


def aggregate(rows, name):
    return {
        'group_id': name, 'objects': len(rows),
        'confirmed_WG_risk': sum(r['confirmed_wg_risk'] for r in rows),
        'uncertain': sum(r['has_uncertain'] for r in rows),
        'U_structure': sum(r['has_structure_issue'] for r in rows),
        'NONE': sum(r['bias_label'] == 'NONE' for r in rows),
        **{k: sum(any(f['type'] == k for f in r['findings']) for r in rows) for k in ORDER},
        'G_confirmed': sum(any(f['type'] == 'G' and f['status'] == 'confirmed' for f in r['findings']) for r in rows),
        'G_uncertain': sum(any(f['type'] == 'G' and f['status'] == 'uncertain' for f in r['findings']) for r in rows),
    }


def transition(old, label, findings):
    if old == 'NONE' and label == 'U':
        return 'NONE→U：新版文本结构标准下定位到具体缺失或指代问题，非新增确认偏见。'
    if old == 'UNK':
        return 'UNK→' + label + '：按疑难原因重新判断并分流，仍保留uncertain状态。'
    if old != label:
        return 'W子类合并：v4/' + old + '→v5/' + label + '，保留原有表达判断标准。'
    return '逐段重读后保留原判断。'


def assemble():
    old = [json.loads(s) for s in (ROOT / 'audit/previous_annotations_v4.jsonl').read_text().splitlines()]
    notes = [n for p in sorted((ROOT / 'audit/direct_notes').glob('*.json')) for n in json.loads(p.read_text())]
    assert len(notes) == len({n[0] for n in notes}) == len(old) == 240
    notes_by_id = {n[0]: n for n in notes}
    with (ROOT / 'retrieval_origins.csv').open(encoding='utf-8-sig', newline='') as f:
        origins = list(csv.DictReader(f))
    origins_by_id = collections.defaultdict(list)
    for o in origins:
        origins_by_id[o['sample_id']].append(o)
    rows = []
    for p in old:
        sid, findings, review_note = notes_by_id[p['sample_id']]
        label = '+'.join(k for k in ORDER if any(f['type'] == k for f in findings)) or 'NONE'
        row = {k: p[k] for k in ['sample_id', 'group_id', 'batch_id', 'territory', 'territory_zh', 'doc_lang', 'doc_id']}
        row.update({
            'annotation_version': 'v5', 'bias_label': label, 'findings': findings,
            'confirmed_wg_risk': any(f['status'] == 'confirmed' and f['type'] in {'W1', 'W2', 'G'} for f in findings),
            'has_uncertain': any(f['status'] == 'uncertain' for f in findings),
            'has_structure_issue': any(f['type'] == 'U' for f in findings),
            'reason_zh': '；'.join(f['reason'] for f in findings) if findings else review_note,
            'previous_bias_label_v4': p['bias_label'],
            'label_string_changed': label != p['bias_label'],
            'comparison_note_zh': transition(p['bias_label'], label, findings),
            'annotation_scope': 'target_paragraph_only',
            **{k: p[k] for k in ['article_title', 'article_timestamp', 'source_url', 'raw_file', 'raw_field', 'original_text_sha256', 'original_text', 'original_queries']},
            'retrieval_origins': origins_by_id[sid],
        })
        rows.append(row)
    (ROOT / 'annotations.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    dump('labels.json', {r['sample_id']: r['bias_label'] for r in rows})
    fields = list(rows[0])
    write_csv('annotations.csv', rows, fields)
    subsets = {
        'confirmed_risk_cases': [r for r in rows if r['confirmed_wg_risk']],
        'uncertain_cases': [r for r in rows if r['has_uncertain']],
        'structure_cases': [r for r in rows if r['has_structure_issue']],
        'changes': [r for r in rows if r['label_string_changed']],
    }
    for name, subset in subsets.items():
        write_csv(name + '.csv', subset, fields)
    comparison_fields = ['sample_id', 'group_id', 'territory_zh', 'doc_lang', 'doc_id', 'previous_bias_label_v4', 'bias_label', 'confirmed_wg_risk', 'has_uncertain', 'has_structure_issue', 'comparison_note_zh', 'reason_zh']
    write_csv('label_comparison.csv', rows, comparison_fields)
    groups = [aggregate([r for r in rows if r['group_id'] == group], group) for group in ['G1', 'G2']]
    total = aggregate(rows, 'TOTAL')
    write_csv('group_summary.csv', groups + [total], list(total))
    territories = []
    for batch in sorted({r['batch_id'] for r in rows}):
        rs = [r for r in rows if r['batch_id'] == batch]
        territories.append(dict(aggregate(rs, rs[0]['group_id']), batch_id=batch, territory=rs[0]['territory'], territory_zh=rs[0]['territory_zh']))
    write_csv('territory_summary.csv', territories, list(territories[0]))
    risk_ids = {r['sample_id'] for r in subsets['confirmed_risk_cases']}
    risk_origins = [dict(o, bias_label=next(r['bias_label'] for r in rows if r['sample_id'] == o['sample_id'])) for o in origins if o['sample_id'] in risk_ids]
    write_csv('confirmed_risk_retrieval_ranks.csv', risk_origins, list(origins[0]) + ['bias_label'])
    transitions = [{'old_v4': a, 'new_v5': b, 'objects': n} for (a, b), n in sorted(collections.Counter((r['previous_bias_label_v4'], r['bias_label']) for r in rows).items())]
    write_csv('transitions.csv', transitions, ['old_v4', 'new_v5', 'objects'])
    summary = {
        'annotation_version': 'v5', 'objects': len(rows), 'groups': 2, 'territories': 20,
        'unique_original_texts': len({r['original_text_sha256'] for r in rows}),
        'languages': len({r['doc_lang'] for r in rows}),
        'by_group': groups, 'total': total,
        'finding_counts': dict(collections.Counter(f['type'] + '/' + f['status'] for r in rows for f in r['findings'])),
        'previous_v4_counts': dict(collections.Counter(r['previous_bias_label_v4'] for r in rows)),
        'label_string_changes': len(subsets['changes']),
        'new_structure_cases_from_NONE': sum(r['previous_bias_label_v4'] == 'NONE' and r['bias_label'] == 'U' for r in rows),
        'previous_UNK_reassessed': sum(r['previous_bias_label_v4'] == 'UNK' for r in rows),
        'transitions': transitions, 'retrieval_origin_rows': len(origins),
        'sampling': 'Existing G1/G2 unchanged, not new random groups',
        'annotation_accuracy_or_F1': None,
        'interpretation': 'Protocol-based weak annotations; changes do not establish improved accuracy, corpus bias prevalence or RAG effects.',
    }
    dump('summary.json', summary)
    (ROOT / 'RESULTS.md').write_text(make_results(rows, groups, total, subsets))
    (ROOT / 'README.md').write_text(make_readme(summary))
    template = (ROOT / 'audit/viewer_template.html').read_text()
    data = json.dumps({'rows': rows, 'summary': summary}, ensure_ascii=False).replace('</', '<\\/')
    (ROOT / 'index.html').write_text(template.replace('__DATA__', data))
    make_workbook(rows, groups, total, subsets)
    (ROOT / 'SHA256SUMS').unlink(missing_ok=True)
    from verify import verify
    result = verify()
    result.pop('checksummed_files')
    result['checksum_check'] = 'Run python verify.py after unpacking to verify SHA256SUMS.'
    dump('verification.json', result)
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name != 'SHA256SUMS' and '__pycache__' not in p.parts and p.suffix != '.pyc')
    (ROOT / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(ROOT).as_posix() + '\n' for p in files))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def make_results(rows, groups, total, subsets):
    lines = ['# 两组240条：W/G/U v5重新标注', '',
             '沿用既有G1、G2各120条，20个领土；全部重新阅读完整目标原段落，未重新抽样。原文未编辑，不使用邻段或外部事实搜索，也未运行RAG或CS。', '',
             '|组|对象|确认W/G风险|待判断|U结构问题|NONE|', '|---|---:|---:|---:|---:|---:|']
    for r in groups + [total]:
        lines.append('|' + '|'.join(str(r[k]) for k in ['group_id', 'objects', 'confirmed_WG_risk', 'uncertain', 'U_structure', 'NONE']) + '|')
    lines += ['', '统计分别按段落对象去重，允许不同维度重叠；本批各对象未出现多标签，所以四列可相加。U不是确认偏见，W3和G/uncertain也不是确认偏见。', '',
              '新版W1为褒贬与情绪修辞，W2为确定性与可信度预设，W3为语义／修辞疑难。它们不能与v4的同编号直接比较。G保留来源归属标准并区分confirmed/uncertain。U仅为文本结构问题。', '',
              '## 与v4的关系', '',
              '- 原4条W和2条G仍为确认风险，W只按新版机制合并；不是因为改名就改变风险数量。',
              '- 原7条UNK全部重读后分流为2条W3/uncertain、5条G/uncertain，仍是待判断。',
              '- 原NONE中新增4条U：关系对象缺失、指代无法唯一恢复或被引述命题缺失；不计入偏见数量。',
              '- 223条保持NONE；15条标签字符串变化包含重新分组，不能解释为15条旧判断错误。', '',
              '## 已确认W/G风险（6条）', '']
    for r in subsets['confirmed_risk_cases']:
        lines += case_lines(r)
    lines += ['## 待判断（7条）', '', '不是已检测出偏见但不知子类；它们尚未达到确认W/G问题的条件。', '']
    for r in subsets['uncertain_cases']:
        lines += case_lines(r)
    lines += ['## U结构问题（4条）', '', '不是所有缺日期、缺数字、标题或列表都标U。以下问题影响关系对象、指称或被引述命题的辨认。', '']
    for r in subsets['structure_cases']:
        lines += case_lines(r)
    lines += ['## 使用边界', '',
              '240个领土—段落对象含237个不同原文，22种文档语言；重复原文没有不一致标签。981条检索来源记录保留查询、模型、模式、排名和分数，仅作溯源。', '',
              '这是本会话助手直接依据规范完成的弱标注，无独立金标准或已测准确率/F1，也未证实任何标签会改变RAG输出。NONE不代表事实正确或完全中立；U不代表政治偏见。已有样本的取样方式与六组随机样本不同，不将本批比例外推全库。', '',
              '后续可分别测试W编辑、G来源处理和U处理；本包只提供标注，不自动更改或删除原段落。', '']
    return '\n'.join(lines)


def case_lines(r):
    lines = [f"### {r['sample_id']}｜{r['territory_zh']}｜{r['doc_lang']}｜{r['doc_id']}", '', f"v4：{r['previous_bias_label_v4']}；v5：{r['bias_label']}。", '']
    for f in r['findings']:
        lines += [f"{f['type']} / {f['status']}：{f['reason']}", '']
        for q in f['quotes']:
            lines += ['> ' + q.replace('\n', '\n> '), '']
    return lines


def make_readme(summary):
    return '''# 两组原样本重新标注：W/G/U v5

本包沿用G1/G2各120条，共240个领土—段落对象、20个领土、237个不同原文、22种文档语言。不是新随机抽样，原始样本身份和文本保持不变。

## 直接查看

- 双击index.html：完全离线，按组、语言、类型、确认风险／待判断／结构问题筛选；展开后查看原文高亮、中文理由、新旧标签和全部检索排名。
- annotations.xlsx：全部240条、确认风险6条、待判断7条、结构问题4条、新旧比较及组汇总。
- annotations.csv（UTF-8 BOM）和annotations.jsonl：包含原文、定位、findings、状态、查询及检索溯源。
- RESULTS.md：结果与全部17条非NONE案例说明。
- protocol/PROMPT.txt：可复用精简提示词；protocol/PROTOCOL.md：版本及判断边界。

## 新版字段

核心输出为bias_label与findings。findings每项仅含type/status/quotes/reason。NONE时findings为空。

- W1：原W1/W2/W4合并，褒贬及情绪修辞，confirmed。
- W2：原W3/W5合并，确定性及可信度预设，confirmed。
- W3：原U1原因，语义／修辞边界含混，uncertain。新W3与旧W3含义不同。
- G：来源及观点归属问题，confirmed或uncertain；不校准来源真假、条款或法律解释。
- U：仅文本结构问题，confirmed指确认结构缺陷，不代表确认政治偏见。

可多标签；确认W/G风险、待判断和结构问题分别按对象去重。不能把全部非NONE当作偏见文档。程序生成的定位、原文、新旧比较和检索字段不是额外要求模型生成的判断字段。

## 方法与范围

240条均由当前会话助手重新读取完整原段后逐条判断，输入只含目标段与定位信息；不读邻段、不联网查事实、不标答案方向、不编辑原文、不运行RAG/CS。不是另一次固定模型API运行；历史会话讨论过部分案例，不宣称盲评。标注无已测准确率/F1，不是金标准，不设置额外人工审核前置要求。

audit/review_inputs保存20批完整目标段输入，audit/direct_notes保存240条直接判断与逐条复核备注。audit/previous_annotations_v4.jsonl保存完整旧标注；旧结果没有被覆盖。assemble.py只导出已写好的直接判断，不会自动识别偏见或调用模型。

## 来源

doc_id的数字为相应语言维基百科pageid；p后为article数组零基下标，不是Wikidata Q编号。raw_file、raw_field与original_text_sha256定位冻结原段。原文按字符保持，未补全缺失日期、数字或引语。

retrieval_origins.csv保留981条OpenAI/M3、qlang/rel_langs排名来源。original_queries只作原查询溯源，不作为主权真值或标注证据。标签不含任何声索方方向后缀。

## 校验

运行python verify.py检查格式、逐字引文、原文哈希、分组和重复文本一致性及文件校验和。它验证交付物完整性，不验证标注准确率。Excel重建需要openpyxl，普通核验只需Python标准库。
'''


def make_workbook(rows, groups, total, subsets):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook()
    wb.remove(wb.active)
    fields = ['sample_id', 'group_id', 'territory_zh', 'doc_lang', 'doc_id', 'bias_label', 'confirmed_wg_risk', 'has_uncertain', 'has_structure_issue', 'reason_zh', 'findings', 'previous_bias_label_v4', 'comparison_note_zh', 'original_text', 'source_url', 'raw_file', 'raw_field', 'original_text_sha256']
    tables = [('全部240条', rows, fields), ('确认风险', subsets['confirmed_risk_cases'], fields), ('待判断', subsets['uncertain_cases'], fields), ('结构问题', subsets['structure_cases'], fields), ('新旧比较', rows, ['sample_id', 'group_id', 'territory_zh', 'previous_bias_label_v4', 'bias_label', 'comparison_note_zh', 'reason_zh']), ('分组汇总', groups + [total], list(total))]
    for title, records, columns in tables:
        ws = wb.create_sheet(title)
        ws.append(columns)
        for r in records:
            ws.append([json.dumps(r.get(k), ensure_ascii=False) if isinstance(r.get(k), (dict, list)) else r.get(k) for k in columns])
        for cells in ws:
            for c in cells:
                if isinstance(c.value, str):
                    c.data_type = 's'
                c.alignment = Alignment(vertical='top', wrap_text=True)
        for c in ws[1]:
            c.font = Font(bold=True, color='FFFFFF')
            c.fill = PatternFill('solid', fgColor='24445C')
        for i, k in enumerate(columns, 1):
            ws.column_dimensions[ws.cell(1, i).column_letter].width = 90 if k == 'original_text' else (65 if k in {'reason_zh', 'findings', 'comparison_note_zh'} else 22)
        for i in range(2, ws.max_row + 1):
            ws.row_dimensions[i].height = 65
        ws.freeze_panes = 'A2'
        ws.auto_filter.ref = ws.dimensions
    wb.save(ROOT / 'annotations.xlsx')


if __name__ == '__main__':
    assemble()
