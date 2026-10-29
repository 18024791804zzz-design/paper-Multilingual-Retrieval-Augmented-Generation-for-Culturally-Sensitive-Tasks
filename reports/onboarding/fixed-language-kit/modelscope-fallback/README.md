# Qwen 大权重持续超时时的替代下载

适用：固定的Qwen2.5-7B-Instruct模型在Hugging Face下载配置正常，但数GB权重文件长期停在0B或反复超时。

主脚本为 `download_qwen.py`，依赖独立下载环境中的 modelscope==1.22.3、setuptools==69.5.1。用新的下载venv安装这两个包，避免更改实验venv依赖。设置 EXP_ROOT 和 KIT 后运行脚本即可；它把权重保存到原先的 `$EXP_ROOT/models/Qwen2.5-7B-Instruct/`。

脚本保留并复用已验证文件，从固定HF revision补齐缺失的小配置/分词器文件，再从ModelScope同名仓库下载缺失的权重。所有请求保留现有代理和TLS验证，不向ModelScope发送HF token。该公共Qwen路线不适用于绕过Llama许可。

ModelScope请求master分支，但不把master视为固定版本的保证。下载完成后逐一检验11个必要文件：4个权重使用上游LFS SHA256，其余使用Git blob SHA1与文件长度。只有全部字节符合原定HF revision，才写入实验需要的模型身份标记，同时另存真实下载来源。校验失败时不要手动伪造标记或开始推理。

`qwen-pinned-manifest.json` 直接来自HF固定revision模型API的blobs元数据：a09a35458c702b33eeacc393d103063234e8bc28。不是根据目标服务器上尚未完成的下载文件自算出来的期望值。

已在当前CPU环境验证：ModelScope SDK最小安装与导入、SHA256/Git blob SHA1算法、构造文件上的成功标记、损坏文件拒绝与旧标记失效。未在当前环境下载15GB真实权重，未验证AutoDL到ModelScope的实际链路速度，未执行GPU推理。

运行前请停止原来的同目录HF下载任务，避免两个下载器并发修改文件。不要删除HF缓存；其未完成大文件不保证能跨下载器续传，但已完成并通过校验的文件可复用。

Llama-3.1-8B的独立流程见 [LLAMA.md](LLAMA.md)，其中会先验证HF文件访问权限，再请求镜像权重。
