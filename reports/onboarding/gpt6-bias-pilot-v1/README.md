# GPT-6 领土争端偏见试标包 v1

120段原文，10个领土，10批，每批12段。目标是试用标注规则和检查模型输出，不估计原数据总体偏见比例，不代表论文性能。

## 本轮设置

- 声索方包含People's Republic of China或Republic of China的争端排除。
- 候选来自OpenAI/M3、qlang/rel_langs预计算top-50的并集；没有重新检索。
- 60段沿用此前双方语言各top-3，另60段按检索来源和排名补入；{'candidate_with_rank_11_25': 20, 'm3_only_candidate_for_query': 20, 'previous_openai_qlang_top3': 60, 'candidate_with_rank_26_50': 20}。
- 共14个文档语言代码：ar, en, es, fr, hr, it, iw, pt, ru, so, sr, sw, ti, uk。同一领土的相同语言/段落只出现一次；同段出现在不同领土时保留不同判断对象。
- direction_basis固定为**明确的主权/领土归属主张方向**。实际管理本身不自动当作合法主权支持。它与旧数据的viewpoint可能不同，不应混用标准。
- 每段一个标签：`W+G::Italy`等。W措辞/预设；I信息呈现；G归因；NONE当前范围未发现明确问题；UNK证据不足。方向用规范声索方名或NEUTRAL/MIXED/UNKNOWN。
- 原文目标段完整；第一轮上下文为同文相邻±1段，单上下文截取前1200字符并标记；不是整篇文章。复杂I/G可能需要UNK。
- 模型上传材料没有Controller、原观点/相关性标签、检索器名称、rank、score或作者此前判断。审计来源另存audit目录。

## 操作步骤

1. 解压整个ZIP。**不要把ZIP或整个audit目录直接上传给GPT-6。**
2. 新建干净的聊天会话，选择你可用的GPT-6与高推理；各批保持相同设置，不启用联网搜索。
3. 上传`UPLOAD_ONLY/01_INSTRUCTIONS.txt`和第一批`UPLOAD_ONLY/B01_Olivenza.txt`。
4. 粘贴`02_START_MESSAGE.txt`的全部内容发送。
5. 下载模型给出的`B01_labels.json`，保存到本包`results`目录。不能生成下载文件时，复制完整JSON到UTF-8文本文件并命名为`B01_labels.json`。
6. B02至B10每批使用一个新会话，都上传同一份01_INSTRUCTIONS.txt与对应批次，发送同一段启动消息。不要把上一批标签作为下一批参考。
7. 简单记录`run_metadata_template.csv`里的界面模型名、推理设置和时间；界面未提供精确模型版本就写未知，不推测。
8. 可将十份结果文件直接交回当前会话；若本机有Python3，执行下面的离线检查。

| 批次 | 领土 | 段数 | 上传数据文件 |
|---|---|---:|---|
| B01 | 奥利文萨 | 12 | `B01_Olivenza.txt` |
| B02 | 马尔维纳斯／福克兰群岛 | 12 | `B02_Falkland_Islands.txt` |
| B03 | 拉斯杜梅拉 | 12 | `B03_Ras_Doumeira.txt` |
| B04 | 武科瓦尔岛 | 12 | `B04_Vukovar.txt` |
| B05 | 巴西岛 | 12 | `B05_Isla_Brasilera.txt` |
| B06 | 西班牙北非主权地 | 12 | `B06_Plazas_de_Soberania.txt` |
| B07 | 塞瓦斯托波尔 | 12 | `B07_Sevastopol.txt` |
| B08 | 勃朗峰峰顶争端 | 12 | `B08_Mont_Blanc.txt` |
| B09 | 约旦河西岸 | 12 | `B09_West_Bank.txt` |
| B10 | 奇恩吉 | 12 | `B10_Chiengi.txt` |

## 离线检查（可选，本机有Python3即可，无第三方依赖）

在解压目录打开PowerShell或终端，工作目录应能看到check_results.py。

```shell
python check_results.py --selfcheck
python check_results.py --results results --out validated
```

Windows若`python`不可用而已安装Python启动器，可把`python`换为`py`。尚未做完十批时可查看进度：

```shell
python check_results.py --results results --out validated --allow-incomplete
```

生成`validated/labels.json`、`labels_table.csv`、`summary.json`和`unk_list.csv`。校验会拒绝缺失/重复ID、非法国家名、非法类型和损坏JSON；不判断标签语义准确。

## UNK复判

第一轮结束后自动准备更广的本地上下文，不调用任何API：

```shell
python make_recheck.py --labels validated/labels.json --out recheck_upload
```

仅为UNK样本生成R_Bxx文件，提供相邻±3段、每段最多4000字符并标记截断。每个R文件与原01_INSTRUCTIONS.txt一起上传新会话；不要上传旧标签来诱导模型。输出放到新的`recheck_results`目录。

```shell
python check_results.py --base validated/labels.json --results recheck_results --out validated_final
```

该命令仅允许替换原来UNK的样本。仍不能判断时可以继续UNK，不强制清零。没有UNK时无需复判，make_recheck会生成零个文件。

## 查看与提交

给GPT-6的只有UPLOAD_ONLY中的说明与单批文件。`audit/samples.csv`供你查看完整原文及来源；`retrieval_origins.csv`保留实际检索器/模式/查询/排名/分数；`manifest.json`和`expanded_contexts.json`支持复现与复判。不要将这些审计文件当作预测标签上传。

结果可提交十份Bxx_labels.json，或离线检查后的labels.json及summary.json。自动标签是弱监督数据；重复/不同模型一致不能代替独立准确率。此次没有运行LLM或修改项目源码。
