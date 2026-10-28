# 无卡模式：先完成环境、模型和数据准备

适用目标：先在平台的无 GPU 模式准备，后续同一实例切换到 RTX 4090。安装 CUDA 版 PyTorch 不需要当前存在 GPU；使用 GPU 时才需要 NVIDIA 驱动。当前阶段不要安装 CPU-only torch 再重复替换。

1. 确认无卡/GPU模式使用同一持久化数据盘，切换后保留相同镜像、Python版本和挂载路径。venv不是跨机器/跨镜像的独立安装包；若平台切换会重建系统，需要重新创建兼容环境，但无需重新下载模型。不要只把文件保存在临时容器或30GB系统盘。

2. 检查磁盘和Python，配置真实的数据盘路径：

```bash
df -hT
findmnt
python3 --version

export DATA_DISK=/替换为实际数据盘挂载目录
export EXP_ROOT="$DATA_DISK/fixed-language-rag"
mkdir -p "$EXP_ROOT"
df -h "$EXP_ROOT"
```

需要 Python 3.10–3.12，建议数据盘可用空间60–70GiB。两模型权重合计约29.14GiB，其他空间用于CUDA版Python环境、可选翻译模型和实验输出。无卡模式下 nvidia-smi 不存在、torch.cuda.is_available()为False通常属于预期。

3. 上传本次更新的ZIP并安装隔离环境：

```bash
python3 -m zipfile -e /替换为上传路径/fixed-content-language-kit-no-gpu.zip "$EXP_ROOT"
export KIT="$EXP_ROOT/fixed-content-language-kit"
source "$KIT/env.sh"
export PYTHON_BIN=python3
export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
bash "$KIT/setup.sh" --no-gpu
source "$EXP_ROOT/venv/bin/activate"
```

该模式安装 PyTorch2.6.0 cu124、Transformers4.49.0、NumPy1.26.4 等既定依赖，只执行 CPU 与依赖检查，并跳过GPU检查和nvidia-smi。无需在容器中安装NVIDIA驱动或完整CUDA toolkit。

请提前在平台规格中确认未来4090宿主驱动兼容CUDA12.4；默认cu124建议至少550.54.14。如果平台只支持较旧驱动、但支持CUDA11.8，可以在首次安装前设置 `export TORCH_INDEX_URL=https://download.pytorch.org/whl/cu118`，仍安装PyTorch2.6.0。无卡阶段无法实际验证未来GPU驱动。

4. 申请/确认Llama访问许可，然后下载固定快照：

```bash
read -r -s -p 'HF read token: ' HF_TOKEN
echo
export HF_TOKEN
python "$KIT/download_models.py" --models llama --workers 2
python "$KIT/download_models.py" --models qwen --workers 2
```

若平台已经注入HF_TOKEN可跳过read。当前聊天云环境里的token不会自动同步到新服务器。Llama需获批账号的read token。下载中断后重跑同一命令；下载与断点元数据保存在同一数据盘目录。不要用只下载config/tokenizer的目录冒充完整模型。

可选：提前下载独立翻译模型：

```bash
python "$KIT/download_models.py" --models translator --workers 2
```

5. 在不加载7B/8B权重的前提下做离线检查：

```bash
python -m pip check
python "$KIT/cpu_check.py" --require-cuda-build
HF_HUB_OFFLINE=1 python "$KIT/verify_models_cpu.py"
python "$KIT/selfcheck.py"
python "$KIT/audit.py"
du -sh "$EXP_ROOT/models/"*
df -h "$EXP_ROOT"
```

verify_models_cpu检查固定快照标记、配置、tokenizer、chat template、各权重分片的存在性以及Safetensors头部/索引是否匹配，并对已有查询构造提示词/分词；不把两个大模型实例化到CPU内存，不进行生成。结果保存 `$EXP_ROOT/models_cpu_verification.json`。这是结构检查，不是所有tensor数值的完整密码学校验，也不代表GPU推理已经通过。

selfcheck使用构造数据检查官方CS和配对分析格式，不代表模型实验结果。audit当前显示译文为空/未审核是预期；完成真实译文之前不要执行freeze。

6. 如果希望继续利用无卡时间，可以使用外部翻译/人工审核准备译文。也可选用已下载NLLB在CPU生成草稿：

```bash
python "$KIT/translate.py" --device cpu
```

该步骤只使用600M翻译模型，不使用两个7B/8B被测模型；CPU翻译会较慢。之后按照README逐条人工核对，未审核前不能作为等价证据。只准备环境与模型时可完全跳过这一步。

7. 若下载耗时较长，可后台执行（HF_TOKEN需要提前export）：

```bash
nohup "$EXP_ROOT/venv/bin/python" "$KIT/download_models.py" --models llama qwen --workers 2 > "$EXP_ROOT/logs/download-models.log" 2>&1 &
echo $! > "$EXP_ROOT/logs/download-models.pid"
tail -n 30 "$EXP_ROOT/logs/download-models.log"
```

nohup只应对终端断开，平台停机/实例回收会停止下载。切换到GPU前确认下载进程完成，避免重启中断；中断后仍可在相同目录恢复。

8. 下次重连或切换GPU模式后，重新设置环境变量并激活同一venv：

```bash
export EXP_ROOT=/替换为同一个数据盘路径/fixed-language-rag
export KIT="$EXP_ROOT/fixed-content-language-kit"
source "$KIT/env.sh"
source "$EXP_ROOT/venv/bin/activate"
nvidia-smi
python "$KIT/gpu_check.py"
```

不需要再运行setup.sh或重新下载模型。GPU/BF16检查通过，真实译文审核/冻结完成后，再执行README中的上下文检查、3条查询预运行以及正式实验。GPU检查不通过时不要开始主实验。

源码与原项目requirements.txt始终不变。本包所有环境/模型/实验文件保存在仓库外。
