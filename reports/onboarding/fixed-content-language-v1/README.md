# 固定内容、改变证据语言：可直接运行输入 v1

100段英文原文的中文与俄文译文，共200条；30条问题、10个领土、每个领土10段证据，三种证据语言en/zh/ru，加no_ir。两模型为此前已下载的Llama-3.1-8B-Instruct、Qwen2.5-7B-Instruct，共240次回答。

译文由助手直接生成并逐段检查控制/声索/行政管理、否定限定、时间和数量等内容，未使用NLLB。translation_method记录来源。按用户指示不设人工审核前置条件，没有reviewed/reviewed_by字段，已生成可直接运行的data/frozen.json及SHA256锁文件。

本包包含完整实验脚本与输入，不含模型权重或HF token。保持EXP_ROOT指向原数据盘实验目录，只将KIT改成本包解压目录，即可复用原venv和models，无须覆盖旧操作包。

```bash
export EXP_ROOT=/root/autodl-tmp/fixed-language-rag
export KIT="$EXP_ROOT/fixed-content-ready-v1"
source "$KIT/env.sh"
"$EXP_ROOT/venv/bin/python" "$KIT/audit.py"
"$EXP_ROOT/venv/bin/python" "$KIT/selfcheck.py"
"$EXP_ROOT/venv/bin/python" "$KIT/run.py" --model llama --out "$EXP_ROOT/results/fixed-language-v1-preflight/llama" --preflight-only
"$EXP_ROOT/venv/bin/python" "$KIT/run.py" --model qwen --out "$EXP_ROOT/results/fixed-language-v1-preflight/qwen" --preflight-only
```

preflight-only已支持无卡，仅加载分词器检查全部120个提示词/模型，不加载大模型。两者通过后切换4090，保持数据盘和环境路径不变，然后：

```bash
export EXP_ROOT=/root/autodl-tmp/fixed-language-rag
export KIT="$EXP_ROOT/fixed-content-ready-v1"
source "$KIT/env.sh"
"$EXP_ROOT/venv/bin/python" "$KIT/gpu_check.py"
"$EXP_ROOT/venv/bin/python" "$KIT/run.py" --model llama --out "$EXP_ROOT/results/fixed-language-v1-smoke/llama" --limit-queries 3 --validate-cache
"$EXP_ROOT/venv/bin/python" "$KIT/run.py" --model qwen --out "$EXP_ROOT/results/fixed-language-v1-smoke/qwen" --limit-queries 3 --validate-cache
nohup bash "$KIT/run_all.sh" > "$EXP_ROOT/logs/fixed-language-v1.log" 2>&1 &
```

正式结果写入results/fixed-language-v1，脚本自动运行官方CS及跨证据语言的配对分析。先确认smoke与cache验证通过，再运行nohup。无卡模式不执行GPU步骤。

## 文件与检查范围

- parallel.csv / parallel.json：原文、中文、俄文三列对照。
- data/translations.jsonl：200条可直接回填的译文，保留源文SHA256。
- data/frozen.json / frozen.lock.json：冻结问题与三语证据。
- content_notes.json：原文缺失数值、截断句子、异常列表及历史叙述等内容说明，说明不进入提示词。
- numeric_screen.json：数值字面匹配异常及世纪罗马数字/年代/单位换算的解释。
- glossary.json：关键关系词和术语。
- verification.json：结构、源文一致性和离线流程检查结果。

英文原文中已有的缺失数值、空括号和不完整引注未补全；声索、实际控制、国际承认及作者评价按原有归因翻译；没有根据Controller标签修改证据，也未更新原文历史时点。翻译自查和结构检查不是数学意义上的语义等价证明。当前本地没有运行目标7B/8B模型或4090推理，真实上下文检查和推理以服务器输出为准。

源码仓库与原requirements.txt保持不变。此包为30查询机制小试，不是720查询完整论文复现。数据冻结后变更译文或实现时使用新结果目录，避免混合不同实验版本。
