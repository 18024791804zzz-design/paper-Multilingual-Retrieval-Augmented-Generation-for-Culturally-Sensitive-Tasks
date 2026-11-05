# 来源

- 原论文与附录：https://arxiv.org/abs/2410.01171 ，用户上传ACL2025 Findings版本。
- 原代码：https://github.com/manestay/bordirlines ，本轮检查公开main树，未找到独立观点F1评测脚本。
- WNC：https://github.com/rpryzant/neutralizing-bias ，Pryzant等 Automatically Neutralizing Subjective Bias in Text。
- BABE：https://aclanthology.org/2021.findings-emnlp.101/ ；公开标注手册：https://github.com/Media-Bias-Group/Neural-Media-Bias-Detection-Using-Distant-Supervision-With-BABE/blob/main/annotation_guidelines_BABE.pdf 。
- BASIL：https://github.com/launchnlp/BASIL ；原指南：https://github.com/marshallwhiteorg/emnlp19-media-bias 。本轮只保留段内语义约束，不把跨文章信息选择当成已被WG覆盖。
- 宣传片段/技巧分类：https://aclanthology.org/2020.semeval-1.186/ 。
- MPQA3：https://aclanthology.org/N15-1146/ 。
- SemEval stance：https://aclanthology.org/S16-1003/ 。
- WiCE：https://aclanthology.org/2023.emnlp-main.470/ 。
- FEVER：https://aclanthology.org/N18-1074/ 。
- 统一立场与事实核查：https://aclanthology.org/N18-2004/ 。
- VAST：https://aclanthology.org/2020.emnlp-main.717/ 。
- X-Stance代码：https://github.com/ZurichNLP/xstance ，论文：http://ceur-ws.org/Vol-2624/paper9.pdf 。

来源核对方式：原论文使用本地上传PDF的文本；新增论文标题/摘要核对ACL官方GitHub元数据，X-Stance核对原项目README。本轮未声称逐篇阅读所有新论文全文。

扫描原文来自项目WJ_data.zip与冻结bordirlines.zip。每个例子保存标题、语言、页面入口、快照与raw_file/article索引。网页可能更新，实验请用冻结文本。维基百科文本通常适用CC BY-SA及页面历史中的其他许可要求，不应视为代码MIT许可；请保留归因。种子词表为当前助手提出的检索词，不是上述论文给出的经验证51语言量表。
