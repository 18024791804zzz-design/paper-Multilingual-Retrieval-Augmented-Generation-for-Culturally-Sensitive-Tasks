# 固定内容、只改变证据语言：4090 单卡实验操作包

这是待在你的 Linux / RTX 4090 服务器执行的方案与脚本。当前聊天环境没有验证该服务器 GPU，也没有运行 Llama-3.1-8B / Qwen2.5-7B 的新实验。本包没有附带它们的实验结果。

**先以无卡模式准备时，请优先按照 [NO_GPU.md](NO_GPU.md) 执行，安装命令使用 `bash setup.sh --no-gpu`。** CUDA版PyTorch和模型可以提前安装/下载，GPU执行检查留到切换4090后。

## 1. 实验到底改变什么

主比较固定每一条查询的原文、选项及顺序、系统提示、证据所表达的事实、段落数量及顺序、文档编号、生成与选择规则。唯一计划改变的是这些段落的语言呈现：英文 `en`、简体中文 `zh`、俄文 `ru`。另有 `no_ir` 无文档参考条件。

不能直接使用三个语言的原生维基页面：它们的事实、篇幅、观点和更新时间不相同。应从同一份英文原段落生成忠实译文，再逐段人工审核。即便通过审核，更严谨的表述仍是“在翻译忠实控制条件下，证据语言呈现的影响”，不要声称数学意义上的完全相同信息、也不要把结果自动解释为国家立场偏好。

本包先采用已经固定的第一轮小实验样本：10 个领土、30 条查询、完整的可用 MRS；6 个已知 Controller、4 个 Unknown。每个领土固定其**英文查询在 OpenAI.qlang 下的前 10 段英文命中**；这个领土所有查询语言都使用同一组有序证据。合计 100 个源段落、7,714 个英文词、200 个中/俄翻译单元。源文本和原始 ID/排名已在 `data/base.json` 中，不用重新向 OpenAI 发检索请求。

每条查询分别跑 en / zh / ru / no_ir，2 模型共 `30 × 4 × 2 = 240` 次回答。MRS 中不同查询的语言可以不同，但每条查询跨条件时自身保持原样。这样可以在每个证据条件内继续计算原有的跨查询语言 CS。

这是新增的机制实验。`en/zh/ru` 是证据呈现条件，不是原论文 `qlang/rel_langs` 三个检索模式；冻结英文检索结果也不等于复现多语言检索过程。不要与此前小模型结果合并为同一套设置。

模型逐个加载，batch size 1；BF16 权重，SDPA，最多 8192 输入 token，seed 4321，贪心，无量化。答案选择沿用项目的特殊实现：在自由生成的同一条 50-token 前缀上累计各候选的逐位置 log probability；保留候选原生文本和字面 `<|eot_id|>` 规则，无长度归一化。**它不是 teacher forcing；也不能用 raw_generated 替代最终候选选择。** KV cache 加速先做本机对照；log_softmax 使用 FP32。GPU/BF16 与此前 CPU/FP32 不保证逐位相同。

## 2. 确认硬件、挂载点和空间

```bash
nvidia-smi
python3 --version
df -hT
findmnt
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
```

这款 ComfyUI 镜像可以使用，但请先在平台页面停止 ComfyUI 的 GPU 工作流/释放其模型占用。不要停止不认识的进程。目标是在正式运行前尽量只保留必要的显示开销。

识别平台的**持久化数据盘**挂载位置。不要把下面的占位路径原样执行，不要把模型放到 30GB 系统盘。

```bash
export DATA_DISK=/替换为真实的数据盘挂载目录
export EXP_ROOT="$DATA_DISK/fixed-language-rag"
mkdir -p "$EXP_ROOT"
df -h "$EXP_ROOT"
```

两模型 safetensors 权重约 14.96 + 14.19 = 29.14 GiB；环境、CUDA 运行库、可选翻译模型、临时文件与输出另占空间。建议数据盘可用空间至少 60–70 GiB。若“免费 50GB + 付费 50GB”确实合计 100GB，通常足够；以 `df -h` 实际可用量为准。磁盘更紧时依次下载/运行模型，但两模型须读取同一份冻结输入。

## 3. 上传操作包并创建隔离环境

把 ZIP 从聊天下载到本地，再上传到服务器数据盘。例如：

```bash
python3 -m zipfile -e /替换为上传后的路径/fixed-content-language-kit.zip "$EXP_ROOT"
export KIT="$EXP_ROOT/fixed-content-language-kit"
source "$KIT/env.sh"
```

选 Python 3.10、3.11 或 3.12；推荐已有的 3.11/3.12。这个方案不要求更换镜像系统 Python，不会修改 ComfyUI 的现有环境。若平台当前 Python 合适：

```bash
export PYTHON_BIN=python3
# 如 PyPI 访问慢，可选国内镜像；不是 apt 镜像。
export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
bash "$KIT/setup.sh"
source "$EXP_ROOT/venv/bin/activate"
```

脚本新建**不带 `--system-site-packages`** 的 venv，安装 PyTorch 2.6.0 cu124 与本包独立的版本清单。不会执行原仓库的 requirements.txt。PyTorch 安装使用其独立的 CUDA wheel 索引，后续依赖受 `torch==2.6.0 / numpy==1.26.4` 约束。

默认 cu124 建议 NVIDIA Linux 驱动至少 550.54.14。`nvidia-smi` 显示的是驱动支持的 CUDA 上限；镜像里的 NVCC 版本不要求与 wheel 一致。若驱动不足以运行 cu124，但可运行 CUDA 11.8，可在首次安装前设置：

```bash
export TORCH_INDEX_URL=https://download.pytorch.org/whl/cu118
bash "$KIT/setup.sh"
```

不要在容器里自行更换宿主 GPU 驱动；驱动异常应在平台选择兼容实例/联系平台。4090 本身支持 BF16。脚本末尾运行 CUDA/BF16 矩阵乘、tensor↔numpy 检查、pip check，保存 `environment.freeze.txt` 和 `nvidia-smi.txt`。无需安装 FlashAttention、xformers 或完整 CUDA toolkit。

如果 `venv` 组件缺失，先确认系统版本和 Python 路径，再安装与所选解释器对应的 venv 包。例如系统默认 Python 时可使用 `apt-get update`、`apt-get install -y python3-venv`。自装 3.12 解释器不要误用其他版本的 venv 包。

## 4. 获取 Llama 权限并下载固定模型版本

在 Hugging Face 登录账号，到以下模型页面接受许可、完成 Llama 访问申请：

- https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
- https://huggingface.co/Qwen/Qwen2.5-7B-Instruct

Llama 需要**同一个获批账号**的读取 token；创建 token 本身不会自动授予 gated 模型权限。Qwen 无需 Llama 的许可。使用隐藏输入将 token 仅放入当前 shell 环境，不写入仓库、命令历史或报告：

```bash
read -r -s -p 'HF read token: ' HF_TOKEN
echo
export HF_TOKEN
python "$KIT/download_models.py" --models llama qwen --workers 2
df -h "$EXP_ROOT"
du -sh "$EXP_ROOT/models/"*
```

若平台已经通过环境变量提供 HF_TOKEN，可跳过 read。403/401 时先检查账号许可、token 权限与实际下载错误；不要把 token 发进聊天。国内下载慢可先降低 workers 到 1、利用同一目录重新执行实现续传，或在可联网机器下载相同 revision 后完整上传。不要混用不同快照的 config/tokenizer/权重。

`models.json` 固定了经 API 查到的快照提交：

| 模型 | revision |
|---|---|
| Llama | 0e9e39f249a16976918f6564b8830bc894c89659 |
| Qwen | a09a35458c702b33eeacc393d103063234e8bc28 |
| 可选 NLLB | f8d333a098d19b4fd9a8b18f94170487ad3f821d |

下载只保存一套 HF Transformers 所需权重及 tokenizer/config，避免再复制 original/consolidated 或其他格式。目录是 `$EXP_ROOT/models/Llama-3.1-8B-Instruct` 与 `Qwen2.5-7B-Instruct`。如果采用完整本地上传方式，确认确实是这些 revision 后，按 models.json 为各目录保存对应的 `experiment_download.json`，脚本才允许推理。

## 5. 制作、审核、冻结等价译文

建议使用与受测模型独立的翻译系统/人工译者。可选的本地草稿方案是 NLLB-200-distilled-600M：

```bash
python "$KIT/download_models.py" --models translator
python "$KIT/translate.py"
python "$KIT/audit.py"
```

它只生成草稿，不勾选人工审核。源段超过 512 个 NLLB token、生成未正常结束的段落会留空并写入 `data/translation_errors.json`，需要人工/外部系统按句子对应补齐。禁止为通过检查直接截断段落；不要用受测 Qwen 作为唯一翻译器、再把它与 Llama 的差异当成无混杂的语言效应。

人工逐条编辑 `data/translations.jsonl`，保留 doc_key/source_text/source_sha256：

```json
{"doc_key":"en/21312_p5","source_sha256":"保持原值","source_text":"保持原文","target_language":"zh","translation":"审核后的完整译文","reviewed":true,"reviewed_by":"实际审核者","review_notes":"核对控制/声索/时点、否定与限定词"}
```

审核重点：

1. “实际控制/管理”“声索”“国际承认”“法律归属”不能互换；不把 claimed by 翻成 belongs to。
2. 保留各方名称、争议关系、否定/不确定/据某方称等限定词、时间、数字；不补充新的事实或结论。
3. 保持 10 个段落的边界与顺序，不重新组织成摘要。正文中的标题、列表、引文也应对应处理。
4. 领土别名应能指向同一实体。不能给一个语言额外加入解释性别名，而其他语言没有。
5. 不给目标模型提供源语言、国家来源、翻译器身份等额外标签。原始页面 ID 只在报告元数据中保存。

回译和相似度可辅助发现问题，但不能证明语义等价。最好由双语审核者完成，并在一部分样本上加入第二份独立译文作稳健性检查。保持英文原文也会带来源语言/翻译腔的不对称；结果解释时写清楚。

确认 200 个单元全部通过后：

```bash
python "$KIT/audit.py" --freeze
sha256sum "$KIT/data/frozen.json"
python "$KIT/selfcheck.py"
```

freeze 会拒绝缺失译文、未审核、被改动源文本/哈希、重复或多余条目。它验证的是人工审核记录与结构，不会自动证明翻译忠实。冻结后修改译文或脚本必须使用新的实验输出目录。

## 6. 先检查完整上下文，再做两模型小样本预运行

```bash
python "$KIT/run.py" --model llama --out "$EXP_ROOT/results/preflight/llama" --preflight-only
python "$KIT/run.py" --model qwen --out "$EXP_ROOT/results/preflight/qwen" --preflight-only

python "$KIT/run.py" --model llama --out "$EXP_ROOT/results/smoke/llama" --limit-queries 3 --validate-cache
python "$KIT/run.py" --model qwen --out "$EXP_ROOT/results/smoke/qwen" --limit-queries 3 --validate-cache
```

每个模型用**自己的** apply_chat_template；语义消息相同，模型内部特殊 token 可以不同。两模型逐个运行，不同时驻留显存。检查各 `preflight.json`、`cache_validation.json`、`answers.jsonl` 与 `run_report.json`。生成后的评分选择、自由输出、输入 token、时间、GPU allocated/reserved 和 Linux 进程峰值 RSS 都保存。

超长输入立即报错，绝不静默截断；若有一组超长，不能只裁这个语言。应预先统一选择较小的文档子集，重新翻译审核、冻结，并把它记作不同设置。翻译后 token 数不同是语言呈现的一部分，不能靠填充重复文字伪装“等长”。最多 8192 是本实验的预算上限，并非声称模型原生只有 8192 context。

KV cache 对照使用同一模型/精度的全前缀与缓存计算。BF16 允许数值差，但必须相同生成序列/最终选项，累计候选分数误差阈值 0.1 会明确记录。若未通过，先停止检查；可用 `--reference-no-cache` 在**全新输出目录**运行原始的无缓存流程，两个模型全部条件一致。不能隐瞒失败或直接放宽阈值继续。

## 7. 后台运行正式实验与监控

```bash
nohup bash "$KIT/run_all.sh" > "$EXP_ROOT/logs/main.log" 2>&1 &
echo $! > "$EXP_ROOT/logs/main.pid"
```

```bash
tail -n 30 "$EXP_ROOT/logs/main.log"
nvidia-smi
df -h "$EXP_ROOT"
wc -l "$EXP_ROOT/results/main/llama/answers.jsonl" "$EXP_ROOT/results/main/qwen/answers.jsonl"
ps -p "$(cat "$EXP_ROOT/logs/main.pid")" -o pid,etime,%cpu,%mem,args
```

每模型期望 120 行，两个模型 240 行。每条答案落盘并 fsync；同一配置重跑跳过已完成的 `(qid, evidence_language)`。若进程异常退出不会补造答案，完整性检查会阻止不完整结果参与评价。nohup 只防终端断开；平台停机/回收后仍需依赖数据盘和检查点恢复。若最后一条 JSONL 因硬停机破损，应先备份、检查修复尾行，再恢复，勿把损坏文件当作完成结果。

正式运行脚本在模型下载完成后启用 HF 离线模式。计时建议以 smoke 实测估算：每模型预计生成总时长约 `120 × 该模型单次平均秒数`，另加加载/验证/预填充开销；全 720 查询每模型 2880 次。不要把此前 CPU 小模型耗时外推到 4090。多次完全相同的贪心运行不是独立随机重复，不能靠多次运行虚增样本量。

## 8. 评价与如何回答研究问题

run_all.sh 结束会自动评价，也可单独执行：

```bash
python "$KIT/score.py" --results "$EXP_ROOT/results/main"
```

主要文件：

- `main/analysis.json`：三种证据语言两两答案翻转率、以领土为单位的配对 bootstrap 区间、各条件官方 CS、C/N/D/M/U/V/G 等辅助值。
- `main/all_questions_answers.csv`：原问题、查询语言、Controller、两模型每个条件的答案与输入 token。
- `main/<model>/answers.jsonl`：完整问题与提示词、原文档标识、自由生成、候选分数、最终答案、时间与内存。
- `main/<model>/response_table_<condition>.csv`、`cs_<condition>.json/.log`：直接交给未改动上游脚本的表格、官方结果或具体失败。
- `data/base.json`、`translations.jsonl`、`frozen.json/.lock.json`：原文来源、逐段翻译审核及冻结输入。

主指标不是 ΔCS，而是对同一个查询、同一组证据事实：

\[
Flip(\ell_1,\ell_2)=\frac1n\sum_i\mathbf1[a_i(D_i^{\ell_1})\ne a_i(D_i^{\ell_2})].
\]

同时报告按查询和按领土加权的翻转率。`no_ir` 配对是“加入证据”的参考，不算纯语言对比。置信区间按领土聚类，避免把同领土不同语言的查询当成独立样本；10 个领土很小，区间只是探索性描述。

官方 CS 仍在每个证据条件内沿查询语言计算：KB CS 的 en 是**英文查询**，不是英文证据；CST 是声索方查询语言间答案相等的程度；C/N 是相对数据集 Controller 的匹配情况；ΔCS=(C-N)/N。它们回答的问题与跨证据语言 Flip 不同，可能完全不变但仍存在很多配对答案变化。Unknown 不参与 KB/C/N；若 N=0，ΔCS 未定义；不补零、不丢弃样本来让脚本通过。

辅助指标 D=C-N，M=(C+N)/2；对有完整控制/非控制组的已知领土，U=mean[c(1-n)]，V=mean[(1-c)n]，G=U+V。它们用于区分两组同时改善、两组都差以及方向抵消。完整720中官方 C 与 N 可能来自不同可用组；辅助配对指标会另外报告共同完整子集，不能冒充官方全体分母。

如果出现翻转：先审核具体译文、跨语言实体名、候选分数边际与长度；再检查是否系统地朝证据语言相关声索方移动。单纯“答案不同”只能支持语言敏感，不能自动支持民族立场偏好、偏见或正确性提高。若不翻转，也只说明这批条件没有观察到最终选项变化，可继续看候选分数变化并扩大领土覆盖。

## 9. 通过后扩展到原始 720 查询

先确认这240次闭环通过。正式720是 `720 × (3+1) × 2 = 5760` 次回答，仍是一条4090顺序跑。为避免覆盖小试，复制一份 kit；模型目录可以共用，结果必须另存。

准备原始 `borderlines.zip`（注意项目中历史文件可能拼写为 bordirlines.zip，以内部 `data/queries.tsv` 为准）。固定 native 查询数据集快照：

```bash
cp -a "$KIT" "$EXP_ROOT/fixed-content-language-kit-720"
export KIT720="$EXP_ROOT/fixed-content-language-kit-720"
# 只删新复制目录中的小试冻结文件；原小试及结果保留。
rm -f "$KIT720/data/frozen.json" "$KIT720/data/frozen.lock.json"
export NATIVE_REVISION="$(python -c 'from huggingface_hub import HfApi; print(HfApi().dataset_info("manestay/borderlines").sha)')"
python "$KIT720/prepare_full.py" --zip /替换为原始压缩包路径/borderlines.zip --native-revision "$NATIVE_REVISION" --replace-pilot
```

然后对新目录重新执行第5–6步；用 `$KIT720` 替代 `$KIT`，预运行输出也使用新目录。两模型的完整720上下文检查通过后运行：

```bash
nohup bash "$KIT720/run_full.sh" > "$EXP_ROOT/logs/full720.log" 2>&1 &
echo $! > "$EXP_ROOT/logs/full720.pid"
```

这个脚本使用 `results/full720/<model>`，评价指向 results/full720。不要直接运行新副本的 run_all.sh，因为其中默认目录 main 会与小试冲突。

预计算英文命中并非每个领土都有10段：250个领土可取10，Vereker Banks / Q246 只有1段。忠实保留1段且在全部语言中一致，不能重复填充到10。本项目原始720也不是每个领土都有所有国家语言；mfe/to/dz 等缺查询或某些声索方共享语言。保留原始组成并报告有效分母，不额外编造问题。本包的全量准备脚本会读取原始720和原生候选信息，下载数据 Arrow 文件，不运行远程数据集加载代码；全量路径需要在服务器额外进行完整性/上下文验证，当前本地只验证了30条小试路径。

## 10. 仓库完整性和备份

本包独立于原 Git 仓库，不修改源码或 requirements.txt。如需服务器上保留原项目作对照：

```bash
git clone https://github.com/18024791804zzz-design/paper-Multilingual-Retrieval-Augmented-Generation-for-Culturally-Sensitive-Tasks.git "$EXP_ROOT/project"
git -C "$EXP_ROOT/project" checkout --detach c22df814be7cca8c4b4271f1adb4af621934a01e
git -C "$EXP_ROOT/project" status --porcelain
```

实验脚本、venv、数据、模型、结果均在 project/ 外。CS 来源和 commit 在 vendor/SOURCE.md，上游 calculate_CS.py 未修改。完成后备份冻结数据、models.json、环境版本、全部答案和评价，不必打包权重：

```bash
tar -czf "$EXP_ROOT/fixed-language-results.tar.gz" -C "$EXP_ROOT" fixed-content-language-kit results/main environment.freeze.txt nvidia-smi.txt
git -C "$EXP_ROOT/project" status --porcelain
df -h "$EXP_ROOT"
```

保留原始快照的 Controller 标签及文档时点，勿把它当作2026年实时主权事实。这个实验验证生成阶段的证据语言影响，不单独验证检索召回，也不代表完整论文性能。
