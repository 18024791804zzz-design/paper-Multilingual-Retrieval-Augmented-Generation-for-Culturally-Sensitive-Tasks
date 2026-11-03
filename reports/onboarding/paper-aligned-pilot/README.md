# 完整 MRS / top-10 小模型实验结果

这是子集比较实验，不代表论文完整主实验性能。三轮各10个领土、30条查询；保留所选领土全部声索方语言及英语。模型为 Llama-3.2-1B-Instruct、Qwen2.5-1.5B-Instruct；比较 no_ir / qlang / rel_langs。CPU float32、temperature=0、seed=4321，最多取10段预计算OpenAI检索文档，使用仓库原始候选打分实现及经过对照验证的KV-cache优化。

**540条回答完成、18组官方CS通过。** 累计推理约6.12小时；Llama进程峰值7.88 GiB、Qwen进程峰值9.11 GiB。三轮共19个已知控制方、11个未知；MRS大小组成近似原数据，但地域、语言频率与完整主实验不同。第三轮Ras_Doumeira_ti的qlang仅有7段，未补造到10段。

## 查看与下载

- [实验结果及配对分析](RESULTS.md)
- [汇总指标CSV](summary.csv)：包括分轮、合并重算及三轮算术平均，不能混淆Delta CS的合并值和比值均值。
- [逐条问题与答案CSV](questions_and_answers.csv)：540条，query_json/raw_response_json用JSON字符串保留精确原文与换行，含原始生成、打分选项、规范化国家、候选分数、文档ID与语言。
- [完整结果ZIP](paper-aligned-pilot-results.zip)：打开文件页后使用 **Download raw / 下载原始文件**；完整提示词、文档文本、各次官方CS、时长、完整性检查及原环境仓库外脚本均在包内。模型权重和凭据不包含在内。
- [多语言检索机制的证据与验证方案](MECHANISM_PLAN.md)：计划尚未开展新的模型推理；不是已经证实的因果结论。
- [现有检索集合的精确文档重叠审计](document_overlap_audit.json)：只读描述性分析；语言与精确文档ID不能替代观点或语义标注。
- [文件SHA-256清单](file_manifest.json)

ZIP保留原环境目录结构，脚本中的路径可能指向原/workspace及仓库外的官方评价脚本；它是结果/审计包，不是自动安装的独立软件发行版。原始打分选中的候选用于CS；原始生成文本作为诊断记录，二者可能不同。

本PR仅添加报告和实验数据，不修改项目源码或requirements.txt。运行前后检查的53个仓库文件与259个旧结果JSON保持不变；完整性记录在ZIP中。
