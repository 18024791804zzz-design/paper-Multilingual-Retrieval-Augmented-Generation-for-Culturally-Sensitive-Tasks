# 固定内容、改变证据语言：无卡准备操作包

- [下载操作包](fixed-content-language-kit-no-gpu.zip?raw=true)
- [无卡准备步骤](NO_GPU.md)
- [完整实验说明](FULL_GUIDE.md)
- [ZIP 校验值](SHA256SUMS)

ZIP 大小为 93,696 字节，包含环境/下载/离线检查/推理/评价脚本、既有30条查询与100段固定英文证据、200个待填写的翻译单元。不包含模型权重、HF token 或新的7B/8B实验结果。模型需要通过包内脚本另行从 Hugging Face 下载，Llama需账号许可。

解压后以 NO_GPU.md 为准，使用 `bash setup.sh --no-gpu` 准备环境。无卡时可安装CUDA版PyTorch、下载模型、验证文件结构和分词器；GPU/BF16检查和真实推理需等待挂载4090。译文仍需人工审核，不能把空翻译模板直接用于实验。

这些文件仅用于下载分发，不修改仓库源码或 requirements.txt。解压并运行时请放在服务器持久化数据盘、Git仓库之外。

SHA256：

```text
98b705f91cfdf31cf1f5d0146552ceae6f0bb10eb4913c46d12ed307477f4e46  fixed-content-language-kit-no-gpu.zip
```

## 大权重下载持续超时

可使用 [ModelScope替代下载与固定快照校验](modelscope-fallback/README.md)。下载器使用独立环境，实验依赖不变；实际传输速度需在目标服务器验证。
