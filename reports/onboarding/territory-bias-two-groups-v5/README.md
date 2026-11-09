# 两组原样本重新标注：W/G/U v5

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
