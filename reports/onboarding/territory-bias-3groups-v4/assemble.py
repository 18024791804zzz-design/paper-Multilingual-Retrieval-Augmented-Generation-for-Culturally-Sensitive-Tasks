"""Rebuild report files from the frozen direct annotations, not a classifier."""
from pathlib import Path
import collections
import csv
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parent


def dump(name, obj):
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def csvwrite(name, rows, fields=None):
    if fields is None:
        fields = list(rows[0]) if rows else []
    with (ROOT / name).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def broad(label):
    if label in {"NONE", "UNK"}:
        return label
    members = label.split("+")
    return "+".join(k for k, present in (("W", any(x.startswith("W") for x in members)), ("G", "G" in members)) if present)


def assemble():
    prior = [json.loads(x) for x in (ROOT / "audit/previous_annotations_v1_1.jsonl").read_text().splitlines()]
    manifest = json.loads((ROOT / "audit/previous_sampling_manifest.json").read_text())
    meta_by_id = {r["sample_id"]: r for r in manifest["samples"]}
    notes = {r["sample_id"]: r for p in sorted((ROOT / "audit/direct_notes").glob("*.json")) for r in json.loads(p.read_text())}
    assert len(notes) == len(prior) == 360
    rows = []
    for old in prior:
        n = notes[old["sample_id"]]
        m = meta_by_id[old["sample_id"]]
        old_type = old["bias_label"].split("::")[0]
        new_type = broad(n["bias_label"])
        change = old_type != new_type
        refined = old_type == "W" and new_type == "W"
        prefix = f"旧{old_type}→新{new_type}。" if change else (f"保留W，细分为{n['bias_label']}。" if refined else f"逐段复核后仍为{new_type}。")
        row = {k: old[k] for k in ["sample_id", "group_id", "batch_id", "territory", "territory_zh", "doc_lang", "doc_id"]}
        row.update({
            "bias_label": n["bias_label"],
            "claim_quote": n.get("claim_quote"),
            "attribution_quote": n.get("attribution_quote"),
            "reason_zh": n["reason_zh"],
            "previous_bias_label": old["bias_label"],
            "previous_bias_type": old_type,
            "new_bias_class": new_type,
            "class_changed": change,
            "W_subtype_refined": refined,
            "change_reason_zh": prefix + n["reason_zh"],
            "annotation_scope": "target_paragraph_only",
            "article_title": old["article_title"],
            "article_timestamp": old["article_timestamp"],
            "source_url": old["source_url"],
            "raw_file": old["raw_file"],
            "raw_field": old["raw_field"],
            "original_text_sha256": old["original_text_sha256"],
            "original_text": old["original_text"],
            "original_queries": m["original_queries"],
        })
        rows.append(row)
    (ROOT / "annotations.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    dump("labels.json", {r["sample_id"]: r["bias_label"] for r in rows})
    csvwrite("annotations.csv", rows)
    risk = [r for r in rows if r["bias_label"] not in {"NONE", "UNK"}]
    uncertain = [r for r in rows if r["bias_label"] == "UNK"]
    changes = [r for r in rows if r["class_changed"] or r["W_subtype_refined"]]
    csvwrite("risk_cases.csv", risk)
    csvwrite("uncertain_cases.csv", uncertain)
    csvwrite("changes.csv", changes)
    compare_fields = ["sample_id", "group_id", "territory_zh", "doc_lang", "doc_id", "previous_bias_label", "previous_bias_type", "bias_label", "new_bias_class", "class_changed", "W_subtype_refined", "change_reason_zh"]
    csvwrite("label_comparison.csv", rows, compare_fields)
    with (ROOT / "audit/retrieval_origins.csv").open(encoding="utf-8-sig", newline="") as f:
        origins = list(csv.DictReader(f))
    risk_by_id = {r["sample_id"]: r for r in risk}
    risk_origins = [dict(r, bias_label=risk_by_id[r["sample_id"]]["bias_label"]) for r in origins if r["sample_id"] in risk_by_id]
    csvwrite("risk_retrieval_ranks.csv", risk_origins)

    def aggregate(rs, key):
        c = collections.Counter(r["bias_label"] for r in rs)
        sub = collections.Counter(x for r in rs if r["bias_label"] not in {"NONE", "UNK"} for x in r["bias_label"].split("+"))
        return {key: rs[0][key] if rs else "TOTAL", "total": len(rs), "NONE": c["NONE"],
                "W": sum(any(x.startswith("W") for x in r["bias_label"].split("+")) for r in rs),
                **{k: sub[k] for k in ["W1", "W2", "W3", "W4", "W5", "G"]},
                "confirmed_risk": sum(r["bias_label"] not in {"NONE", "UNK"} for r in rs),
                "UNK": c["UNK"]}
    groups = [aggregate([r for r in rows if r["group_id"] == group], "group_id") for group in ["G1", "G2", "G3"]]
    total = aggregate(rows, "group_id")
    total["group_id"] = "TOTAL"
    csvwrite("group_summary.csv", groups + [total])
    territories = []
    for batch in sorted(set(r["batch_id"] for r in rows)):
        rs = [r for r in rows if r["batch_id"] == batch]
        territories.append(dict(aggregate(rs, "batch_id"), group_id=rs[0]["group_id"], territory=rs[0]["territory"], territory_zh=rs[0]["territory_zh"]))
    csvwrite("territory_summary.csv", territories)
    transitions = collections.Counter((r["previous_bias_type"], r["new_bias_class"]) for r in rows)
    transition_rows = [{"previous_type": a, "new_class": b, "count": n} for (a, b), n in sorted(transitions.items())]
    csvwrite("transitions.csv", transition_rows)
    old_counts = collections.Counter(r["bias_label"].split("::")[0] for r in prior)
    summary = {
        "annotation_version": "v4", "samples": 360, "territories": 30, "groups": 3,
        "unique_source_paragraphs": 352, "languages": len(set(r["doc_lang"] for r in rows)),
        "annotation_unit": "territory_doc", "context": "target paragraph only",
        "previous_v1_1": dict(old_counts), "new": total, "by_group": groups,
        "by_subtype": {k: total[k] for k in ["W1", "W2", "W3", "W4", "W5", "G"]},
        "broad_class_changes": sum(r["class_changed"] for r in rows),
        "retained_W_with_subtype_refinement": sum(r["W_subtype_refined"] for r in rows),
        "changes_csv_rows": len(changes), "transitions": transition_rows,
        "retrieval_origin_rows": len(origins), "risk_retrieval_origin_rows": len(risk_origins),
        "new_answer_direction_labels": 0, "claimant_direction_strings_removed_from_new_bias_label": True,
        "measured_accuracy_or_F1": None,
        "interpretation": "Label changes follow a changed protocol and paragraph-only scope; they are not measured accuracy improvements or proof of corpus neutrality."
    }
    dump("summary.json", summary)
    (ROOT / "RESULTS.md").write_text(make_results(rows, groups, total, risk, uncertain, changes, summary))
    (ROOT / "README.md").write_text(make_readme(summary))
    (ROOT / "index.html").write_text(make_viewer(rows, total))
    make_workbook(rows, risk, uncertain, changes, groups + [total])
    # An unchanged frozen audit input permits rebuilding without any model/API call.
    (ROOT / "SHA256SUMS").unlink(missing_ok=True)
    from verify import verify
    result = verify()
    result.pop("checksummed_files")
    result["checksum_check"] = "Run python verify.py to verify the packaged SHA256SUMS."
    dump("verification.json", result)
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and p.name != "SHA256SUMS" and "__pycache__" not in p.parts and p.suffix != ".pyc")
    (ROOT / "SHA256SUMS").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.relative_to(ROOT).as_posix() + "\n" for p in files))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def make_results(rows, groups, total, risk, uncertain, changes, summary):
    lines = ["# 三组360条：按v4重新标注", "",
             "所有360条均重新阅读完整目标原段落，未重新抽样，未读取相邻段落进行判断。未进行外部事实核验、RAG生成或答案方向标注。", "",
             "## 新结果", "",
             "|组|段落对象|NONE|W|G|已确认W/G风险|UNK|",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for r in groups + [total]:
        lines.append("|" + "|".join(str(r[k]) for k in ["group_id", "total", "NONE", "W", "G", "confirmed_risk", "UNK"]) + "|")
    lines += ["", "本批没有W/G组合标签，因此上表W与G可直接相加；其他批次允许组合时须按风险段落去重。",
              "", "W子类计数：" + "，".join(f"{k}={total[k]}" for k in ["W1", "W2", "W3", "W4", "W5"]) + "。没有为了填满类别而强行标注。",
              "", "## 与旧版比较", "",
              "|类别|旧v1.1|新v4|", "|---|---:|---:|",
              "|NONE|329|345|", "|W（各子类合计）|6|5|", "|G|4|3|", "|UNK|21|7|",
              "", "18条的主要类别发生变化，另5条保留W并细分为W子类；changes.csv共23行。其余337条也已重读，并各有新的理由。",
              "", "旧G→NONE 2条；旧UNK→NONE 14条；旧W→UNK 1条；旧UNK→G 1条。",
              "这主要反映G定义收窄及上下文范围改变，不能解释为文档内容变得更客观或标注准确率得到提高。",
              "", "## 8条已确认风险", ""]
    for r in risk:
        lines += [f"### {r['sample_id']} {r['territory_zh']}（{r['doc_lang']}，{r['doc_id']}）",
                  "", f"新：{r['bias_label']}；旧偏见类型：{r['previous_bias_type']}。", "",
                  "原文定位：", "", "> " + r["claim_quote"].replace("\n", "\n> "), "",
                  "判断：" + r["reason_zh"], ""]
    lines += ["## 7条UNK", "",
              "UNK表示本段不足以可靠判断措辞性质或来源边界，不是已确认偏见，也不只是尚未确定子类。", ""]
    for r in uncertain:
        lines += [f"- {r['sample_id']}（{r['territory_zh']}，{r['doc_lang']}）：{r['reason_zh']}"]
    lines += ["", "## 代表性变化", "",
              "- B01-D03：G→NONE。具名条约与结论已有联系；不复核条款、法律解释或履约。",
              "- B15-D11：G→NONE。只读本段的建筑起源和位置，不再用邻段争论判定该段G。",
              "- B08-D03：W→UNK。看似故意拉开边界标记的表述有语气限定，意图观察与归属仍不明确。",
              "- B22-D02：UNK→G。只定位目标段中未交代来源的公投合法性判断；不使用邻段或校准公投是否合法。",
              "- B10-D05：UNK→NONE。武装设站和争夺领土的段内情境不足以使wring一词本身成为W；没有RAG影响证据不是判断依据。",
              "", "## 阅读边界", "",
              "这些是当前助手依据操作规范给出的弱标注，尚无独立金标准或准确率/F1测量。NONE不能等同于事实正确、完全中立；W/G风险不能直接等同于会改变RAG输出。原文没有被修改，也未自动删除任何段落。",
              "30个领土、360个领土—段落对象包含352个不同原段落，8组重复原段的新版标签全部一致。标题、分类和无关背景仍在原抽样中；未把它们强行计为偏见，也未把本样本比例外推全库。", ""]
    return "\n".join(lines)


def make_readme(summary):
    return """# 三组段落偏见标注 v4

将最近三组共360条原样本全部重新标注，原文及旧版结果完整保留。

## 直接查看

1. 解压后双击 index.html：无需启动服务，按组、语言、标签、变更与关键词筛选，查看原文高亮及中文理由。
2. 用 Excel 打开 annotations.xlsx：包含全部、风险、疑难、变更和组汇总五张表。
3. annotations.csv 是带UTF-8 BOM的完整表；annotations.jsonl、labels.json 适合程序读取。
4. RESULTS.md 是中文结果说明；changes.csv 是23条类别改变或W子类细分记录，label_comparison.csv 比较全部360条。

## 本轮规则

核心判断字段只有 bias_label：NONE、UNK、W1—W5、G及已确认组合。

- W1：贬损、污名化称谓；W2：无充分限定的褒扬；W3：不当确定性或绝对化；W4：情绪化隐喻或戏剧化；W5：言说、呈现与预设造成的可信度倾斜。
- W必须结合完整目标段落的主体、引语、否定、条件及具体事实行为。词语命中不等于风险。历史军事事件、行政称谓、技术比喻和有明确主体的引述不自动属于W。
- G只检查来源或观点主体的归属。具名协议、报告、裁判或可识别主体已与该项判断关联时，不要求给条款、联网核验、证明来源真实或验证推理。普通事实缺少引文不自动属于G/UNK。
- 协议内容是否充分支持主权推论、内部逻辑冲突、范围扩大、历史真实性，不在本轮G中。不会把排除的G问题机械转为W。
- 单段中的争议判断若直接由叙述者断言、又没有相应观点主体，可构成G；若归属范围或措辞性质仍有真正歧义，则为UNK。
- G维度没有问题时，仍须独立检查W。NONE表示本段未确认W/G，不表示事实校准通过、法律解释正确或完全中立。
- 不读取邻段，不补全文，不联网核验，不标答案偏向性，不进行RAG生成或CS评价。

protocol/ 中保留本轮采用的v4原规范、提示词和构造示例。S02/S03等NONE仅针对G维度，不能跳过真实段落的W评估。

## 对象和溯源

沿用G1/G2/G3，每组120条、10个领土，每个领土12个段落对象。共360个对象、352个不同原段落、27种文档语言。G1为既有试标；G2/G3沿用原抽样，不重抽。样本资格和排除中国相关声索方等历史设置未改变。本样本不是全库随机偏见率调查。

本轮判断对象为完整段落。原查询、检索器、模式和排名只作溯源，不作为偏见证据；没有对同一段在不同查询下独立重复评判，也没有生成新的国家方向标签。

sample_id定位样本；doc_lang/doc_id及raw_file/raw_field定位冻结的维基百科原段。doc_id中的数字是该语言维基百科pageid，p后为article数组的零基下标；不是Wikidata Q编号。原文空白和字符保持原样。

previous_bias_label是旧版审计值，可能含旧方向后缀；它不是新版输出。新版bias_label不含Portugal等国家或NEUTRAL方向。旧版全文表另存于audit/previous_annotations_v1_1.jsonl，未覆盖。

## 自动化与质量检查

标注由当前会话助手直接逐条完成，未另行调用收费API。不是一个独立固定GPT-6 API运行，精确模型快照未单独记录；没有独立人工金标准，不能报告已验证准确率/F1。本轮未附加人工审核前置条件。

audit/review_inputs/保存30份仅含目标原段和定位元数据的输入，audit/direct_notes/保存对应的360条直接判断。历史会话已经讨论过部分案例，因此不宣称独立盲评。

python verify.py

以上命令检查360条齐全、三组计数、原文哈希、引用逐字存在、重复段标签一致、CSV/JSONL一致和SHA256SUMS。

python assemble.py

以上命令用冻结标注重新生成表格和浏览页，需要openpyxl；它只重建文件，不重新调用LLM或自动推导新标签。运行后可再执行python verify.py检查。

risk_retrieval_ranks.csv保留8条新版风险在原OpenAI/M3检索中的出现位置；未检索到或未入top-50的情况不补造排名。全部1435条检索溯源记录在audit/retrieval_origins.csv。排名不能证明偏见使检索概率升高。

没有修改仓库源码、requirements.txt或维基百科原文。不能仅凭W/G标签确认其对RAG答案的因果影响，也不自动删除或改写原段落。
"""


def make_workbook(rows, risk, uncertain, changes, groups):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook()
    wb.remove(wb.active)
    fields = ["sample_id", "group_id", "territory_zh", "doc_lang", "doc_id", "bias_label", "previous_bias_type",
              "class_changed", "reason_zh", "claim_quote", "attribution_quote", "change_reason_zh",
              "original_text", "source_url", "raw_file", "raw_field", "original_text_sha256"]
    for name, values in [("全部360条", rows), ("风险8条", risk), ("疑难7条", uncertain), ("变更23条", changes), ("组汇总", groups)]:
        ws = wb.create_sheet(name)
        headers = list(groups[0]) if name == "组汇总" else fields
        ws.append(headers)
        for r in values:
            ws.append([r.get(k) for k in headers])
        for cell in ws[1]:
            cell.fill = PatternFill("solid", fgColor="183B56")
            cell.font = Font(color="FFFFFF", bold=True)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if isinstance(cell.value, str):
                    cell.data_type = "s"
            ws.row_dimensions[row[0].row].height = 75 if name != "组汇总" else 23
        from openpyxl.utils import get_column_letter
        for i, h in enumerate(headers, 1):
            width = 100 if h == "original_text" else 65 if h in {"reason_zh", "change_reason_zh"} else 45 if h in {"claim_quote", "attribution_quote", "source_url"} else 24 if h in {"territory_zh", "doc_id", "raw_file", "original_text_sha256"} else 17
            ws.column_dimensions[get_column_letter(i)].width = width
        ws.freeze_panes = "D2" if name != "组汇总" else "B2"
        ws.auto_filter.ref = ws.dimensions
    wb.save(ROOT / "annotations.xlsx")


def make_viewer(rows, total):
    data = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")
    template = """<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>三组段落偏见标注 v4</title>
<style>
:root{font-family:system-ui,-apple-system,"Microsoft YaHei",sans-serif;color:#183046;background:#f1f5f9;line-height:1.65}
body{margin:0}main{max-width:1200px;margin:auto;padding:24px}h1{font-size:27px;margin:0 0 10px}h2{font-size:19px}a{color:#0757a6}header,.panel,article{background:white;border:1px solid #d5dfe9;border-radius:12px;padding:20px;margin-bottom:16px}.numbers{display:flex;flex-wrap:wrap;gap:12px}.numbers span{background:#eaf2f8;border-radius:8px;padding:8px 16px}.note{color:#44586a;font-size:14px}.filters{position:sticky;top:0;z-index:2;box-shadow:0 2px 8px #18304615}.controls{display:flex;flex-wrap:wrap;gap:10px}label{font-size:14px}select,input{font:inherit;padding:8px;border:1px solid #a8baca;border-radius:6px;background:white}input{min-width:230px}.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-weight:bold;background:#e5edf4;margin:0 8px}.risk{background:#fce5e5;color:#822424}.uncertain{background:#fff0ce;color:#765000}.none{background:#e8f2eb;color:#285a38}.original{white-space:pre-wrap;overflow-wrap:anywhere;font-size:16px;background:#f8fafc;padding:16px;border-radius:7px;border-inline-start:3px solid #a8bccd}mark.claim{background:#ffe0a0;color:inherit}mark.attribution{background:#ccebdc;color:inherit}.reason{border-left:3px solid #6a8ba7;padding-left:12px}summary{cursor:pointer}details p{margin:10px 0}.locator{color:#52677a;font-size:13px;overflow-wrap:anywhere}.change{color:#704512}.links{display:flex;gap:16px;flex-wrap:wrap}button{font:inherit;padding:7px 12px;cursor:pointer;border:1px solid #b0c1d0;border-radius:6px;background:#f7fafc}@media(max-width:600px){main{padding:12px}header,.panel,article{padding:14px}.filters{position:static}select,input{max-width:100%}}
</style>
<main><header><h1>三组段落偏见标注 v4</h1><p>按最新规则重读全部360条；保持原样本和原文。</p>
<div class="numbers"><span>30个领土 · 27种语言</span><span>确认W/G风险：8条</span><span>UNK：7条</span><span>NONE：345条</span></div>
<p class="note">W结合完整目标段落判断；G仅检查来源归属。未核验协议条款、事实真伪或法律解释，未读取相邻段。NONE不等于事实正确或完全中立；UNK不等于已确认偏见。本轮不标答案方向。</p>
<nav class="links"><a href="annotations.xlsx">Excel表格</a><a href="annotations.csv">CSV全文</a><a href="changes.csv">23条变更／细分</a><a href="RESULTS.md">中文结果说明</a><a href="README.md">范围与用法</a></nav></header>
<section class="panel filters"><div class="controls">
<label>分组<br><select id="group"><option value="">全部三组</option><option>G1</option><option>G2</option><option>G3</option></select></label>
<label>标签<br><select id="label"><option value="">全部标签</option><option value="RISK">已确认W/G风险</option><option>UNK</option><option>NONE</option><option>W1</option><option>W2</option><option>W3</option><option>W4</option><option>W5</option><option>G</option></select></label>
<label>语言<br><select id="lang"><option value="">全部语言</option></select></label>
<label>变更<br><select id="change"><option value="">全部</option><option value="class">主要类别变化（18）</option><option value="any">含W子类细分（23）</option></select></label>
<label>关键词<br><input id="search" placeholder="领土、ID、原文、中文理由"></label>
</div><p id="stats" aria-live="polite"></p><button id="expand">展开当前结果原文</button> <button id="collapse">折叠当前结果原文</button>
<p class="note">橙色：判定所引片段；绿色：相关归属文字。高亮是定位依据，不表示整句都要删除。</p></section>
<section id="results"></section><footer class="note">当前会话助手弱标注，无独立准确率/F1测量。352个不同原段落的重复样本标签一致。原文未作编辑。</footer></main>
<script id="dataset" type="application/json">__DATA__</script>
<script>
const rows=JSON.parse(document.getElementById('dataset').textContent);
const $=id=>document.getElementById(id);
const risk=r=>!['NONE','UNK'].includes(r.bias_label);
const langs=[...new Set(rows.map(r=>r.doc_lang))].sort();
langs.forEach(l=>{const o=document.createElement('option');o.value=l;o.textContent=l;$('lang').append(o)});
function el(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e}
function marked(r){
 const p=el('div',undefined,'original');p.dir='auto';const text=r.original_text;const spans=[];
 for(const [key,cls] of [['claim_quote','claim'],['attribution_quote','attribution']]){
  const q=r[key];if(!q)continue;let pos=0,index;while((index=text.indexOf(q,pos))>=0){spans.push({a:index,b:index+q.length,cls});pos=index+q.length}
 }
 const points=[...new Set([0,text.length,...spans.flatMap(s=>[s.a,s.b])])].sort((a,b)=>a-b);
 for(let i=0;i<points.length-1;i++){const a=points[i],b=points[i+1];const s=spans.find(s=>s.a<=a&&s.b>=b);p.append(s?el('mark',text.slice(a,b),s.cls):document.createTextNode(text.slice(a,b)))}
 return p
}
function render(){
 const key=$('search').value.trim().toLocaleLowerCase(),label=$('label').value;
 const filtered=rows.filter(r=>(!$('group').value||r.group_id===$('group').value)&&(!$('lang').value||r.doc_lang===$('lang').value)&&(!label||(label==='RISK'?risk(r):r.bias_label.split('+').includes(label)))&&(!$('change').value||($('change').value==='class'?r.class_changed:(r.class_changed||r.W_subtype_refined)))&&(!key||[r.sample_id,r.doc_id,r.territory,r.territory_zh,r.original_text,r.reason_zh].join(' ').toLocaleLowerCase().includes(key)));
 $('stats').textContent='显示 '+filtered.length+'/360 条；其中确认风险 '+filtered.filter(risk).length+' 条，UNK '+filtered.filter(r=>r.bias_label==='UNK').length+' 条。';
 const frag=document.createDocumentFragment();
 for(const r of filtered){
  const art=el('article');const head=el('h2',r.sample_id+' · '+r.territory_zh);head.append(el('span',r.bias_label,'badge '+(risk(r)?'risk':r.bias_label==='UNK'?'uncertain':'none')));art.append(head);
  art.append(el('p',r.group_id+' · '+r.doc_lang+' · '+r.doc_id+' · 旧偏见类型：'+r.previous_bias_type,'locator'));
  art.append(el('p',r.reason_zh,'reason'));
  const d=el('details');d.open=risk(r)||r.bias_label==='UNK';d.className='textdetail';d.append(el('summary','查看完整原文、定位和变更理由'));d.append(marked(r));
  d.append(el('p',r.change_reason_zh,r.class_changed?'change':'note'));
  const a=el('a','维基百科条目（当前网页可能与冻结版本不同）');a.href=r.source_url;a.target='_blank';a.rel='noopener';d.append(a);
  d.append(el('p',r.raw_file+' → '+r.raw_field+'；抓取时间：'+r.article_timestamp,'locator'));
  const q=el('details');q.append(el('summary','原查询链接（仅供溯源）'));for(const query of r.original_queries)q.append(el('p',query.query_id+' ['+query.language+'] '+query.query_text));d.append(q);
  art.append(d);frag.append(art)
 }
 $('results').replaceChildren(frag)
}
for(const id of ['group','label','lang','change'])$(id).addEventListener('change',render);
$('search').addEventListener('input',render);
$('expand').onclick=()=>document.querySelectorAll('.textdetail').forEach(d=>d.open=true);
$('collapse').onclick=()=>document.querySelectorAll('.textdetail').forEach(d=>d.open=false);
render();
</script></html>"""
    return template.replace("__DATA__", data)


if __name__ == "__main__":
    assemble()
