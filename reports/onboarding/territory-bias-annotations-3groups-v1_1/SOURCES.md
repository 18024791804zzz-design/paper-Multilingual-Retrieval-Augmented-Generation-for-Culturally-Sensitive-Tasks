# 数据与方法来源

原数据：https://huggingface.co/datasets/borderlines/bordirlines
项目：https://github.com/18024791804zzz-design/paper-Multilingual-Retrieval-Augmented-Generation-for-Culturally-Sensitive-Tasks
维基百科原始资料：项目公开WJ_data.zip；快照时间逐段保存在audit/manifest.json。原文未改写，目标段落不截断。来源页面为可变化的当前入口，复现实验应使用本包冻结文本和时间戳。

Wiki正文的适用许可及署名要求参见原页面历史；通常为CC BY-SA及适用的GFDL条款，不能将全文视为项目代码的MIT许可。保存页面标题、URL、快照时间、段落ID及原文哈希以供归因。

WNC：https://github.com/rpryzant/neutralizing-bias ，核对版本b7b42e71d211b4f9a757a5e8d9aa98236fb733ec。
BASIL指南/工具：https://github.com/marshallwhiteorg/emnlp19-media-bias ，核对版本4a8865347588648ae14e63344c9686d2b0a4930e。
Wikipedia NPOV：https://en.wikipedia.org/wiki/Wikipedia:Neutral_point_of_view 。

W/I/G是本研究借鉴上述来源拟定的操作性标签，不是原论文已经验证的统一量表。程序只检查材料完整性、标签格式与国家名，不证明标注准确。本包没有金标准答案、旧模型标签或Controller。
