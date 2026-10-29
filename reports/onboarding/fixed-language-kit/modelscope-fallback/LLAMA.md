# Llama-3.1-8B-Instruct：无卡下载补齐

前置：已有NO_GPU操作包、Qwen替代下载脚本download_qwen.py、下载venv中的ModelScope1.22.3。此脚本复用download_qwen.py的逐字节校验函数。

在独立下载venv中增加huggingface-hub==0.29.3，下载download_llama.py和llama-pinned-manifest.json到同一modelscope-fallback目录，设置EXP_ROOT/KIT后运行download_llama.py。

脚本首先使用Hugging Face SDK和账号token检查固定Llama配置文件的访问权限。没有HF token、或账号没有Llama-3.1-8B-Instruct权限时，必须先完成账号申请/配置；不会继续请求镜像权重。HF_TOKEN只交给HF SDK，不传给ModelScope。

已授权后，从固定HF revision下载配置和分词器，从ModelScope的LLM-Research/Meta-Llama-3.1-8B-Instruct下载4个权重分片。ModelScope请求master，但只有10个必要文件全部匹配原定HF revision的文件长度与SHA256/Git blob SHA1，才写入experiment_download.json并另存真实下载来源。

原定HF revision：0e9e39f249a16976918f6564b8830bc894c89659。权重合计约14.96GiB。模型仍保存在models/Llama-3.1-8B-Instruct，Qwen目录不变，仓库源码和实验venv依赖不变。

已测试：固定SDK导入/所需参数、构造文件校验与损坏拒绝、旧完成标记失效，以及模拟HF拒绝访问时停止下载。真实账号授权、AutoDL到Llama镜像的传输、该镜像与HF权重是否匹配，需要在目标服务器执行后确认；当前没有下载/运行真实8B模型。若镜像不存在、不可访问或校验不一致，保留错误日志，不能伪造完成标记。

模型完成下载后，在实验venv执行verify_models_cpu.py --models llama。两个模型通过后，再准备忠实译文及冻结数据；GPU验证仍留到开卡后。
