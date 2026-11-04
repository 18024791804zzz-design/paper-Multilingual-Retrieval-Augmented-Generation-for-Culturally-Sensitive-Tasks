# 偏见试标的方法核查与局部修订 v1.1

日期：2026-11-04。任务：核查段落独立性、两条强迫表述的不一致、原始query–doc字段如何关联标注、后续方法调整。没有新运行RAG，没有按旧风格扩标240条。

## 主要发现

- 数据中的doc是程序文本块，不保证每块语义完整。wiki_lib.py按section处理，保留标题、删除ref/table，再按双换行切分；ir_lib.py将article[i]直接作为一个doc。
- 物理相邻属于同篇文章，但未必属于同一论证单元；不应机械把±1/±3都当所需证据。上下文有时有用，但不能由本轮I=0推出I不存在，或上下文在所有情况下都无效。
- 上一轮I的定义混合了段落内呈现与文章/检索集合的选择问题，没有足够操作性锚点；I=0不构成有效性证明。
- 仅有W措辞风险不证明RAG输出会改变；强烈词语也可能是准确描述。未通过任何新模型生成实验验证W对回答的因果作用。
- 旧标注实际采用territory–doc单元，使用统一英文annotation_question；没有逐个提供原始语言query_text。120个该单元映射到495条检索记录、201个唯一query–doc对；映射不等于这些查询分别独立标注。

## 原文结构的实际反例

1. B01-D04，pt/Q14491.json article[43]，只含标题“Olivença na atualidade”（奥利文萨现状）。
2. B10-D04，sw/Q2173.json article[29]，“Leo hii ni Jamhuri ya Kidemokrasia ya Kongo.”（如今是刚果民主共和国）；article[28]说明1971—1997年国名为Zaire。孤立看会误以为在断言奇恩吉属于刚果，实际在承接国家更名。
3. B09-D10，ar/Q3587.json article[13]末尾引出阿隆方案条目；article[14]才列出沿约旦河设置以色列主权带等方案内容。分块边界切开了说明和列表。

这些只证明并非每个doc语义独立，不用于估计全语料非独立块比例。

代码证据：
https://github.com/18024791804zzz-design/paper-Multilingual-Retrieval-Augmented-Generation-for-Culturally-Sensitive-Tasks/blob/69d31eec1429863977866d11ff41177590c295de/wiki_lib.py#L533
https://github.com/18024791804zzz-design/paper-Multilingual-Retrieval-Augmented-Generation-for-Culturally-Sensitive-Tasks/blob/69d31eec1429863977866d11ff41177590c295de/information_retrieval/ir_lib.py#L104

## 两条强迫表述

- B02-D02，es/3929221_p13：forzar, mediante una acción militar...；旧标签UNK::NEUTRAL。
- B10-D05，en/10842948_p2：wring a treaty out of Msiri；旧标签W::NEUTRAL。

forzar是明确的施加军事强制，wring是带形象性的强迫习语，但两者都描述行动目的。语体差异可作候选，不足以单独证明第二条是不当偏见。原来对证据门槛处理不一致，因此撤回B10-D05的确定W，改UNK::NEUTRAL，与第一条同级。没有将二者统一强行标W。

B10-D05对应Q10/OpenAI/qlang/rank3，原人工relevance为False、原few-shot relevance亦为False。这些是严格相关性参考，不证明它没有任何潜在影响，但说明该段被标出的修辞与当前归属问答的关联性尚未建立。

## v1.1的精确修改范围

仅修改B10-D05；其余119条不变，不代表已经通过v2新标准复核。新计数：NONE106、W4、G2、UNK8。旧版v1继续保留，不能在论文中把v1.1写成一次独立重复标注或新模型实验。

- labels_v1_1.json：120条标签，含这一次局部修订。
- annotations_v1_1.csv：原文、旧标签、修订标签与理由。
- paired_case_review.json：两条比较材料原文及修订说明。
- example_query_doc_row.json：真实Q10检索行如何添加外部标注。
- joined_retrieval_annotations.csv：495条实际检索记录与120个领土–段落标签的关联，明确query_specific_judgment=False。
- ablation_candidates.json：两条保留强制/意图的同义改写候选。未验证语义完全等价，也未运行RAG；不是已经验证的中立化文本。
- protocol_v2_proposal.md：后续修订提案。

## 验证影响的最小实验

固定同一问题、同一模型与参数、原top-10的其余9段及顺序，仅替换目标段中的候选措辞。保留“试图通过军事/压力促成协议”的事实，不能改成自愿或删去军事成分。另设同义改写对照，检查差异是否只是措辞扰动。

报告原文/改写的最终选择及FlipRate；同时沿用现有候选评分实现报告分数差变化，避免只有选项未翻转就判断完全无影响。模型输出变化只表示敏感性，需结合证据支持和原任务指标判断是否改善。

本轮没有实测上述因果效应。原文和项目源码没有修改。
