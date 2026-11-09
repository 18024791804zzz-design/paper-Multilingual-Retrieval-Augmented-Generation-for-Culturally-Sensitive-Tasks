"""Assemble files from frozen direct annotations; no model calls or classification."""
from pathlib import Path
import collections
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def dump(path, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def csvwrite(path, rows, fields=None):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with p.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def jsonl(path, rows):
    (ROOT / path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def aggregate(rows, group):
    sub = collections.Counter(x for r in rows if r["bias_label"] not in {"NONE", "UNK"} for x in r["bias_label"].split("+"))
    return {
        "group_id": group, "total": len(rows),
        "territories": len(set(r["territory"] for r in rows)),
        "W": sum(any(x.startswith("W") for x in r["bias_label"].split("+")) for r in rows),
        **{k: sub[k] for k in ["W1", "W2", "W3", "W4", "W5", "G"]},
        "confirmed_risk": sum(r["bias_label"] not in {"NONE", "UNK"} for r in rows),
        "UNK": sum(r["bias_label"] == "UNK" for r in rows),
        "NONE": sum(r["bias_label"] == "NONE" for r in rows),
    }


def main():
    manifest = json.loads((ROOT / "audit/sampling_manifest.json").read_text())
    notes = {}
    for p in sorted((ROOT / "audit/direct_notes").glob("*.json")):
        for n in json.loads(p.read_text()):
            sid, label, reason, *quotes = n
            assert sid not in notes
            notes[sid] = {"bias_label": label, "reason_zh": reason,
                          "claim_quote": quotes[0] if quotes else None,
                          "attribution_quote": quotes[1] if len(quotes) > 1 else None}
    rows, origin_rows, sampling_rows = [], [], []
    for src in manifest["samples"]:
        anchor = src["selection"]["selected_origin"]
        r = {k: src[k] for k in ["sample_id", "group_id", "batch_id", "territory", "territory_zh", "doc_lang", "doc_id"]}
        r.update(notes[src["sample_id"]])
        r.update({
            "annotation_scope": "target_paragraph_only",
            "selected_query_id": anchor["query_id"],
            "selected_retriever": anchor["retriever"],
            "selected_mode": anchor["mode"],
            "selected_rank": anchor["rank"],
            "selection_stratum": src["selection"]["stratum"],
            "selection_description_zh": f"按{src['selection']['stratum']}分层随机选取，来源{anchor['query_id']} / {anchor['retriever']} / {anchor['mode']} / rank{anchor['rank']}；该领土所有适用列表中的最小排名为{min(h['rank'] for h in src['retrieval_origins'])}。",
            **{k: src[k] for k in ["article_title", "article_timestamp", "source_url", "raw_file", "raw_field", "original_text_sha256", "original_text", "original_queries"]},
        })
        rows.append(r)
        for h in src["retrieval_origins"]:
            origin_rows.append({**{k: src[k] for k in ["sample_id", "group_id", "territory", "doc_lang", "doc_id"]}, "bias_label": r["bias_label"], **h})
        sampling_rows.append({k: r[k] for k in ["sample_id", "group_id", "batch_id", "territory", "territory_zh", "doc_lang", "doc_id", "selected_query_id", "selected_retriever", "selected_mode", "selected_rank", "selection_stratum"]} |
                             {"minimum_rank_in_all_applicable_lists": min(h["rank"] for h in src["retrieval_origins"]), "previous_exact_text_overlap": False})
    assert len(rows) == len(notes) == 720
    jsonl("annotations.jsonl", rows)
    csvwrite("annotations.csv", rows)
    dump("labels.json", {r["sample_id"]: r["bias_label"] for r in rows})
    risk = [r for r in rows if r["bias_label"] not in {"NONE", "UNK"}]
    uncertain = [r for r in rows if r["bias_label"] == "UNK"]
    csvwrite("risk_cases.csv", risk)
    csvwrite("uncertain_cases.csv", uncertain)
    csvwrite("retrieval_origins.csv", origin_rows)
    csvwrite("risk_retrieval_ranks.csv", [r for r in origin_rows if r["bias_label"] not in {"NONE", "UNK"}])
    csvwrite("sampling_audit.csv", sampling_rows)
    groups = [aggregate([r for r in rows if r["group_id"] == g], g) for g in ["G4", "G5", "G6", "G7", "G8", "G9"]]
    total = aggregate(rows, "NEW_TOTAL")
    csvwrite("group_summary.csv", groups + [total])
    territory_rows = []
    for bid in sorted({r["batch_id"] for r in rows}):
        rs = [r for r in rows if r["batch_id"] == bid]
        territory_rows.append({"batch_id": bid, "territory": rs[0]["territory"], "territory_zh": rs[0]["territory_zh"], **aggregate(rs, rs[0]["group_id"])})
    csvwrite("territory_summary.csv", territory_rows)
    rank_summary = {
        "selected_rank_bands": dict(collections.Counter("4-10" if r["selected_rank"] <= 10 else "11-25" if r["selected_rank"] <= 25 else "26-50" for r in rows)),
        "selected_retriever": dict(collections.Counter(r["selected_retriever"] for r in rows)),
        "selected_mode": dict(collections.Counter(r["selected_mode"] for r in rows)),
        "selected_rank_min": min(r["selected_rank"] for r in rows),
        "selected_rank_max": max(r["selected_rank"] for r in rows),
        "selected_rank_mean": sum(r["selected_rank"] for r in rows) / len(rows),
        "all_original_hit_rows": len(origin_rows),
        "any_applicable_top3_occurrences": sum(r["rank"] <= 3 for r in origin_rows),
        "native_queries": len({q["query_id"] for r in rows for q in r["original_queries"]}),
        "paragraph_languages": dict(sorted(collections.Counter(r["doc_lang"] for r in rows).items())),
    }
    dump("rank_summary.json", rank_summary)
    common = ["sample_id", "group_id", "batch_id", "territory", "territory_zh", "doc_lang", "doc_id", "bias_label", "reason_zh",
              "claim_quote", "attribution_quote", "annotation_scope", "source_url", "raw_file", "raw_field", "original_text_sha256", "original_text"]
    previous = [json.loads(x) for x in (ROOT / "audit/previous_360_v4.jsonl").read_text().splitlines()]
    combined = [{k: r.get(k) for k in common} for r in previous + rows]
    jsonl("combined_9groups/annotations.jsonl", combined)
    csvwrite("combined_9groups/annotations.csv", combined, common)
    dump("combined_9groups/labels.json", {r["sample_id"]: r["bias_label"] for r in combined})
    all_groups = [aggregate([r for r in combined if r["group_id"] == f"G{g}"], f"G{g}") for g in range(1, 10)]
    combined_total = aggregate(combined, "ALL_TOTAL")
    csvwrite("combined_9groups/group_summary.csv", all_groups + [combined_total])
    summary = {
        "version": "six-random-v4", "seed": 20261109, "new_samples": 720, "new_territories": 60,
        "new_unique_texts": 720, "new_languages": len({r["doc_lang"] for r in rows}),
        "previous_exact_text_overlap": 0, "previous_territory_overlap": 0,
        "new_by_group": groups, "new_total": total,
        "cumulative_samples": 1080, "cumulative_unique_texts": len({r["original_text_sha256"] for r in combined}),
        "cumulative_total": combined_total, "cumulative_by_group": all_groups,
        "rank_summary": rank_summary,
        "self_review_changes": 2, "human_gold_standard": False, "measured_accuracy_or_F1": None,
        "note": "New groups are rank-stratified random samples excluding any applicable top3; older groups used another sampling design. Label counts are descriptive, not causal comparisons or corpus prevalence estimates."
    }
    dump("summary.json", summary)
    dump("combined_9groups/summary.json", {"groups": all_groups, "total": combined_total, "unique_texts": summary["cumulative_unique_texts"]})
    (ROOT / "RESULTS.md").write_text(results_md(groups, total, all_groups, combined_total, risk, uncertain, rank_summary))
    (ROOT / "README.md").write_text(readme())
    (ROOT / "combined_9groups/README.md").write_text("本目录为已发布v4前三组360条与本次新增六组720条的合并导出，共1080个对象、1072个不同精确原文。旧360条的标签和原文均原样保留。两批标注规范同为v4，但抽样设计不同；不能将组间标签比例差异当成检索模式效果。完整抽样与原文在上级目录。合并文件不新增答案方向标签。\n")
    template = (ROOT / "viewer_template.html").read_text()
    for token, value in {"__N__": len(rows), "__TERRITORIES__": 60, "__LANGUAGES__": summary["new_languages"], "__RISK__": len(risk),
                         "__UNK__": len(uncertain), "__NONE__": total["NONE"],
                         "__GROUP_OPTIONS__": "".join(f"<option>G{g}</option>" for g in range(4, 10))}.items():
        template = template.replace(token, str(value))
    # Replace dataset last, so template substitutions cannot mutate original paragraphs.
    (ROOT / "index.html").write_text(template.replace("__DATA__", json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")))
    workbook(rows, risk, uncertain, groups + [total], all_groups + [combined_total])
    (ROOT / "SHA256SUMS").unlink(missing_ok=True)
    from verify import verify
    verification = verify()
    verification.pop("checksummed_files")
    verification["checksum_check"] = "Run python verify.py to validate SHA256SUMS."
    dump("verification.json", verification)
    checksum()
    print(json.dumps({"new_total": total, "combined_total": combined_total, "rank_summary": rank_summary}, ensure_ascii=False, indent=2))


def checksum():
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and p.name != "SHA256SUMS" and "__pycache__" not in p.parts)
    (ROOT / "SHA256SUMS").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.relative_to(ROOT).as_posix() + "\n" for p in files))


def table(groups):
    lines = ["|组|对象数|W|G|确认风险|UNK|NONE|", "|---|---:|---:|---:|---:|---:|---:|"]
    for r in groups:
        lines.append("|" + "|".join(str(r[k]) for k in ["group_id", "total", "W", "G", "confirmed_risk", "UNK", "NONE"]) + "|")
    return "\n".join(lines)


def results_md(groups, total, all_groups, combined_total, risk, uncertain, ranks):
    lines = [
        "# 新增六组随机标注结果 v4", "",
        "本次720条全部直接阅读完整目标原段落，来自60个新领土与120个双方语言查询。每组120条、10个领土；每个领土12条。没有抽取列表最前面的720项，也没有保留此前的top-3锚点。",
        "", "## 新增六组", "", table(groups + [total]), "",
        "本批没有W/G组合标签，确认风险数等于W+G。W子类：" + "，".join(f"{k}={total[k]}" for k in ["W1", "W2", "W3", "W4", "W5"]) + "。",
        "", "## 随机抽样的具体做法", "",
        "种子20261109。沿用原资格框架：两声索方语言不同、两条本地语言查询可用，排除PRC/ROC声索方及已标30个领土，剩91个候选领土。将排序后的91个领土随机排列，取满足配额的60个；本次没有因配额不足跳过领土。",
        "每个领土先合并双方查询在OpenAI/M3、qlang/rel_langs下的候选，按原文精确去重；移除此前352段和本轮已选段。只要某段出现在该领土任一适用列表的前3名，即排除。",
        "再按两条查询 × 两检索器 × 三排名段（4–10、11–25、26–50）各随机选1条，共12条。模式在qlang/rel_langs候选中选择。六组按抽样顺序分组，并非六种实验干预。",
        "", f"选取来源排名：最小{ranks['selected_rank_min']}，最大{ranks['selected_rank_max']}，平均{ranks['selected_rank_mean']:.2f}。三排名段各240条；选取来源OpenAI和M3各360条。注意这是选取来源排名，全部出现位置另外保存。",
        "全样本720段精确文本互不重复，与旧352段没有精确重叠。不同语言译文和近似复述仍可存在；不宣称完成语义去重。没有按偏见词、预计标签或段落长度筛选，标题、列表和代码片段仍按原段保留。",
        "", "## 与既有三组累计", "", table(all_groups + [combined_total]), "",
        "累计1080个领土—段落对象来自90个领土，包含1072个不同精确原文。旧三组v4标签和原文完全不变。旧抽样含top-3锚点，本次排除top-3，不能用上述比例直接证明哪种检索更易检出偏见，也不能外推251个领土或全语料偏见率。",
        "", "## 已确认风险原文定位", "",
    ]
    for r in risk:
        lines += [f"### {r['sample_id']} {r['territory_zh']} · {r['doc_lang']} · {r['bias_label']}",
                  "", "> " + r["claim_quote"].replace("\n", "\n> "), "", r["reason_zh"], ""]
    lines += ["## UNK", "", "UNK为措辞解释或来源归属仍不清楚，不计为已确认风险，也不等于已经检测出偏见但没选定子类。", ""]
    for r in uncertain:
        lines += [f"- {r['sample_id']}（{r['territory_zh']}，{r['doc_lang']}）：{r['reason_zh']}"]
    lines += ["", "同段边界复核中B45-D07和B67-D05从初次W5改为UNK：前者可能为具名代表论证的转述，后者的历史意图用词存在中性与贬义解读。变化详见audit/final_review_log.json，未引入外部网页或相邻段。",
              "", "W/G只覆盖本轮已定义的表达与来源问题。部分W涉及文化、产业等背景，并非直接回答领土归属；有明确归因的强烈政治引语也可能不构成本轮W/G。NONE不能解释为没有政治方向、事实真实或不会影响RAG；本轮没有评估答案方向或RAG因果效应。",
              "这些是当前助手按规范给出的弱标注，尚无独立金标准或准确率/F1。没有新增强制人工审核步骤，也没有自动删除或改写原文。", ""]
    return "\n".join(lines)


def readme():
    return """# 新增六组随机段落标注 v4

本次新增720条（G4—G9，每组120条），并附累计九组1080条导出。这里的720是段落标注对象数，来自120条双方语言查询；不是对基准全部720条查询逐条标注其top-50。

## 查看方法

- 解压后双击 index.html：离线按组、语言、标签或关键词查看完整原文、高亮、中文理由及选取排名。
- annotations.xlsx 包含新增720条、28条风险、11条疑难、新增组汇总、累计九组汇总。
- annotations.csv（UTF-8 BOM）/annotations.jsonl 为新增720条；labels.json 仅保存sample_id与bias_label。
- risk_cases.csv、uncertain_cases.csv 是两个子表；RESULTS.md 提供中文汇总与每条风险定位。
- combined_9groups/ 为已发布前三组360条与新增720条的合并；旧版v4标签和原文保持不变。

## 标注规则

核心判断字段只有bias_label：NONE、UNK、W1—W5、G及已确认组合。

W1贬损或污名化称谓；W2无充分限定的褒扬；W3不当确定性或绝对化；W4情绪化隐喻或戏剧化；W5言说或叙述预设导致的可信度倾斜。结合完整原段判断主体、引语、否定、条件、文化用法和具体行为，不按词表命中即判。

G只检查来源/观点主体的归属。具名条约、裁判、报告或可识别主体与说法已有联系时，不要求展示条款、联网核验或证明推论。普通历史地理事实未附引用不自动判G。条款支持是否充分、内容扩大、法律解释、事实与内部逻辑校准不在本轮G中，也不机械转为W。

对于段内直接出现的争议法律/政治定性，需要区分作者判断和各方判断。清楚的来源问题标G；措辞或归属仍有真正歧义为UNK。已确认W/G存在时，不能因另一个维度不确定就整段改为UNK。

本轮只用目标原段，不读邻段或全文，不联网核验，不标答案偏向性，不运行RAG/CS，不改写或删除原文。NONE仅表示未确认本轮W/G，不能当作事实通过校验或完全中立。

protocol/保留原v4规范和构造示例。G示例中的NONE仅针对G维度，真实标注还须独立评估W。

## 随机性与来源

种子20261109。60个领土从剩余91个合资格对象中随机抽取，沿用排除PRC/ROC声索方的范围；原文中仍可能提及中国，未进行删词处理。60个新领土与旧30个没有重叠。

双方本地语言查询的OpenAI/M3 × qlang/rel_langs候选合并后精确去重。若某段在该领土任一适用列表排名1—3，整段排除。每个领土按两查询 × 两检索器 × 三排名段4–10/11–25/26–50各随机选1段。三排名段各240条，两检索器各360条；没有按内容、风险词或预计标签选取。

sampling_audit.csv记录每条选取来源和全部适用列表中的最小排名；retrieval_origins.csv记录全部真实出现位置；risk_retrieval_ranks.csv为风险子集。分层抽样中的来源配额不等于两个检索器各自检索了不同文档；同段可同时出现在二者结果中。

audit/sampling.json保留随机排列、分组、种子和排除规则，audit/sampling_manifest.json保留完整查询和原文映射。audit/sample_six.py是冻结样本的算法；运行需原始bordirlines.zip、解压WJ原文和历史排除表，按文件顶部修改路径，并将OUT指向一个新目录。territory_names_zh.json仅用于显示名，不参与抽样或偏见判断。

720段只做精确文本去重，没有语义去重；不同语言译文或近重复可能存在。六组是随机分组，不是干预条件。新增抽样排除top-3，与旧组含top-3锚点的设计不同，标签比例只作描述。

doc_id数字为该语言维基百科pageid，p后为article数组零基下标，不是Wikidata Q编号。raw_file/raw_field和原文SHA256可定位冻结原段。当前网页链接内容可能已经更新。

## 标注与验证

当前会话助手逐条阅读全部720条，未另行调用收费模型API。未单独记录精确模型快照，不将本次称为独立固定GPT-6 API运行。无独立金标准或测得准确率/F1；本次不设置人工审核前置门槛。

audit/review_inputs/只含目标原段及定位信息，无排名、旧标签、Controller或相邻段。audit/direct_notes/保留逐条判断；格式为sample_id、标签、中文理由、可选精确引用、可选来源引用。final_review_log.json记录2项同段复核调整。

python verify.py

检查720条齐全、六组计数、标签格式、原文哈希、引用存在、去重与旧文排除、排名下限、抽样配额、CSV/JSONL/浏览页内嵌数据一致、合并1080条及文件校验和。它验证文件与抽样完整性，不测偏见判断准确率。

python assemble.py

以上从冻结判断重建导出，需openpyxl；不会重新标注或调用LLM。重建后可再运行python verify.py。

仓库源码、requirements.txt及原始维基百科语料未修改。
"""


def workbook(rows, risk, uncertain, groups, cumulative):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    wb.remove(wb.active)
    fields = ["sample_id", "group_id", "territory_zh", "doc_lang", "doc_id", "bias_label", "reason_zh", "claim_quote", "attribution_quote",
              "selected_query_id", "selected_retriever", "selected_mode", "selected_rank", "original_text", "source_url", "raw_file", "raw_field", "original_text_sha256"]
    for name, values, headers in [("新增720条", rows, fields), ("风险28条", risk, fields), ("疑难11条", uncertain, fields),
                                  ("新增六组汇总", groups, list(groups[0])), ("累计九组汇总", cumulative, list(cumulative[0]))]:
        ws = wb.create_sheet(name)
        ws.append(headers)
        for r in values:
            ws.append([r.get(k) for k in headers])
        for cell in ws[1]:
            cell.fill = PatternFill("solid", fgColor="183B56")
            cell.font = Font(color="FFFFFF", bold=True)
        for line in ws.iter_rows(min_row=2):
            for cell in line:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                if isinstance(cell.value, str):
                    cell.data_type = "s"
            ws.row_dimensions[line[0].row].height = 75 if headers == fields else 23
        for i, key in enumerate(headers, 1):
            width = 100 if key == "original_text" else 65 if key == "reason_zh" else 45 if key in {"claim_quote", "attribution_quote", "source_url"} else 25 if key in {"territory_zh", "doc_id", "raw_file"} else 17
            ws.column_dimensions[get_column_letter(i)].width = width
        ws.freeze_panes = "D2" if headers == fields else "B2"
        ws.auto_filter.ref = ws.dimensions
    wb.save(ROOT / "annotations.xlsx")


if __name__ == "__main__":
    main()
