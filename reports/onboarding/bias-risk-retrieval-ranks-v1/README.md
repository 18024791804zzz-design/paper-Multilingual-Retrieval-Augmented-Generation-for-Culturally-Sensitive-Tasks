# 三组偏见风险段落的原检索排名

2026-11-05。沿用三组合并v1.1的10条明确标记风险对象（W6、G4），不包含21条UNK，不修改任何标签或原文。

- risk_document_rank_by_query.csv：10个领土—段落对象×双方语言查询，共20行；每行列OpenAI/M3×qlang/rel_langs四个排名。空白表示该查询、检索器及模式的预计算top-50没有该段，不表示全语料库不存在。文档语言与查询语言不同的qlang空白通常源于候选语言限制。
- risk_document_all_47_retrieval_records.csv：实际出现的47条检索记录，保留原始排名、分数、查询ID、文档ID、风险标签、中文理由及完整原文。

这只覆盖试标所用的双方语言查询，不是10段在全部720查询、所有其他检索模式中的搜索。同段的多个检索记录不是独立偏见标注。

每个排名和空白共80个单元格均与冻结bordirlines.zip的对应TSV重新核对。原ZIP SHA256：75cbda5ef44f6e7fbfa65a09e5f10d37cf0938a0f7b4cd58074cf6e01df88263。没有重新执行检索、重排或RAG生成。直接按原排名取top10时，对应的已标记风险记录数为：OpenAI qlang 8、OpenAI rel_langs 7、M3 qlang 7、M3 rel_langs 6；按不同风险对象去重分别为8、7、7、4。上述数字不是总体偏见率。

三组有OpenAI qlang top3锚点、M3独有候选和排名分层，不能直接据此比较两检索器的总体公允性。风险标签为当前助手的弱标注，没有独立准确率或RAG效应测量。

UNK表示偏见是否成立不能可靠判断，不等于已确认存在偏见但类型未知。UNKNOWN位于方向字段，含义不同。立场字段范围是explicit_sovereignty_claim，不等同于答案支持方向，更不等同于偏见受益方。

原三组材料及许可/来源：../territory-bias-annotations-3groups-v1_1/ 。
