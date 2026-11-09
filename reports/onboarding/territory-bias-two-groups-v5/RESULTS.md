# 两组240条：W/G/U v5重新标注

沿用既有G1、G2各120条，20个领土；全部重新阅读完整目标原段落，未重新抽样。原文未编辑，不使用邻段或外部事实搜索，也未运行RAG或CS。

|组|对象|确认W/G风险|待判断|U结构问题|NONE|
|---|---:|---:|---:|---:|---:|
|G1|120|4|4|1|111|
|G2|120|2|3|3|112|
|TOTAL|240|6|7|4|223|

统计分别按段落对象去重，允许不同维度重叠；本批各对象未出现多标签，所以四列可相加。U不是确认偏见，W3和G/uncertain也不是确认偏见。

新版W1为褒贬与情绪修辞，W2为确定性与可信度预设，W3为语义／修辞疑难。它们不能与v4的同编号直接比较。G保留来源归属标准并区分confirmed/uncertain。U仅为文本结构问题。

## 与v4的关系

- 原4条W和2条G仍为确认风险，W只按新版机制合并；不是因为改名就改变风险数量。
- 原7条UNK全部重读后分流为2条W3/uncertain、5条G/uncertain，仍是待判断。
- 原NONE中新增4条U：关系对象缺失、指代无法唯一恢复或被引述命题缺失；不计入偏见数量。
- 223条保持NONE；15条标签字符串变化包含重新分组，不能解释为15条旧判断错误。

## 已确认W/G风险（6条）

### B03-D02｜拉斯杜梅拉｜so｜2407_p4

v4：W2；v5：W1。

W1 / confirmed：作者把厄立特里亚政策直接褒扬为建立在和平及热爱索马里统一之上，没有限定为该国自述。

> Siyaasadda Ereteriya waa mid ku dhisan hab nabadeed taasoo ah dad jecel midnimada soomaaliya

### B06-D04｜西班牙北非主权地｜es｜45549_p8

v4：G；v5：G。

G / confirmed：段落在说明摩洛哥声索后直接以西班牙领土不可分割部分作为拒绝谈判的理由，却未限定这一归属判断的主体或来源。

> puesto que son parte integrante del territorio español

### B08-D05｜勃朗峰峰顶争端｜it｜19908_p26

v4：W5；v5：W2。

W2 / confirmed：作者先以擅自或任意纳入预设法国制图缺乏正当依据，后面的图书作者归因只明确引出另一项伪造评价，未将前项限定为其观点。

> che arbitrariamente inglobava la vetta in territorio francese

> Secondo gli autori di un libro

### B09-D08｜约旦河西岸｜ar｜1569_p13

v4：W4；v5：W1。

W1 / confirmed：作者把战争结果写成以军不可战胜神话的破灭，在转述军方自述之外添加戏剧化的胜负评价。

> تحطم أسطورة أن جيش إسرائيل لا يقهر

### B14-D07｜圣盖拉山／特尔迪纳峰｜sl｜534_p12

v4：W2；v5：W1。

W1 / confirmed：作者把地下景观直接誉为欧洲最壮丽的地下长廊，属于未限定为特定主体意见的审美褒扬。

> Njen podzemeljski svet skriva najveličastnejše podzemne galerije v Evropi.

### B18-D08｜休达｜ar｜30703_p0

v4：G；v5：G。

G / confirmed：开头直接以摩洛哥城市定义休达，后文虽将被占领判断归于摩方，却没有明确把前项身份定义也限定为该方主张。

> سبتة هي مدينة مغربية تحت السيادة الإسبانية

> ويعتبرها المغرب مدينة محتلة ولا يزال يطالب باسترجاعها

## 待判断（7条）

不是已检测出偏见但不知子类；它们尚未达到确认W/G问题的条件。

### B06-D03｜西班牙北非主权地｜es｜4718_p77

v4：UNK；v5：G。

G / uncertain：国际劳工组织明确批评的是法律，但相邻的企业规避劳动保护指控是否也属于该来源，段内覆盖范围不清。

> las empresas del sector multiplican los subterfugios para eludir las disposiciones favorables a los trabajadores

> La legislación marroquí ha sido criticada por la Organización Internacional del Trabajo.

### B08-D03｜勃朗峰峰顶争端｜it｜19908_p27

v4：UNK；v5：W3。

W3 / uncertain：看似故意拉开边界标记可读为制图安排的观察，也可读为暗示制图者刻意模糊边界，段内不足以确认不当意图预设。

> le crocette che segnano i confini appaiono volutamente distanziate

### B09-D06｜约旦河西岸｜iw｜320304_p30

v4：UNK；v5：G。

G / uncertain：封锁构成开战事由与预防性进攻的表述，未明确是在转述以方的理由还是作者的法律解释，相关判断的主体边界不清。

> שהיוותה עילת מלחמה (casus belli), פתחה ישראל ב־5 ביוני במתקפת מנע נגד צבאות מדינות ערב

### B10-D12｜奇恩吉｜en｜10842948_p4

v4：UNK；v5：W3。

W3 / uncertain：mad可作实际精神健康事件或戏剧化的孤独后果来理解，本段不能区分，因此不直接确认不当修辞。

> a lonely posting which sent more than one colonial officer mad

### B17-D12｜奥克帕拉河｜en｜21383_p3

v4：UNK；v5：G。

G / uncertain：世界银行明确对应新兴市场、HDI对应发展排名，但最腐败国家之一是否来自某项指标或作者概括，来源范围仍不清。

> remains one of the most corrupt nations in the world

> is considered to be an emerging market by the World Bank

> the country ranks very low in the Human Development Index

### B20-D07｜白礁｜ms｜105701_p30

v4：UNK；v5：G。

G / uncertain：以柔佛海峡反问反驳新加坡的帝国继承依据，但目标段未交代该论证属于马方诉讼意见、其他来源还是作者自身评论。

> Secara analogi, jika Selat Tebrau pernah ditadbir oleh British, apakah Selat Tebrau juga milik Singapura.

### B20-D12｜白礁｜ms｜105701_p3

v4：UNK；v5：G。

G / uncertain：新加坡的无异议主张已明确归属，但马方沉默出于邻国友谊这一解释未交代由谁提出，不能用后文法院结果为该动机解释补归因。

> Singapura pula mengemukakan dakwaan bahawa mereka telah menguasai pulau tersebut semenjak tahun 1840-an tanpa sebarang tentangan dan halangan oleh pihak Malaysia.

> Sikap berdiam diri serta mengelak dari menggunakan pendekatan konfrontasi oleh Malaysia berdasarkan semangat setiakawan dua negara yang berjiran itu

## U结构问题（4条）

不是所有缺日期、缺数字、标题或列表都标U。以下问题影响关系对象、指称或被引述命题的辨认。

### B10-D04｜奇恩吉｜sw｜2173_p29

v4：NONE；v5：U。

U / confirmed：只说如今是刚果民主共和国，却省略了被改称或转变的原指称对象，目标段内无法确定这一身份变化断言的主体。

> Leo hii ni Jamhuri ya Kidemokrasia ya Kongo.

### B11-D01｜科兰太因河｜en｜1993351_p0

v4：NONE；v5：U。

U / confirmed：先并列苏里南和圭亚那，随后只称该国最长河流，单数the country缺少唯一可辨认的指称对象。

> in Suriname and Guyana

> It is the longest river in the country

### B15-D10｜大卫·加雷贾修道院群｜ka｜10605_p17

v4：NONE；v5：U。

U / confirmed：段落引出Mose Janashvili对修道院的具体描述，却在冒号后完全没有被引述内容，目标段无法辨认该描述命题。

> მოსე ჯანაშვილი თავის თხზულებაში დავითგარეჯას აღწერს შემდეგნაირად:

### B18-D01｜休达｜en｜6443_p73

v4：NONE；v5：U。

U / confirmed：结对关系句停在with后的冒号，完全缺失关系另一方，目标段无法形成完整的城市结对命题。

> Ceuta is twinned with:

## 使用边界

240个领土—段落对象含237个不同原文，22种文档语言；重复原文没有不一致标签。981条检索来源记录保留查询、模型、模式、排名和分数，仅作溯源。

这是本会话助手直接依据规范完成的弱标注，无独立金标准或已测准确率/F1，也未证实任何标签会改变RAG输出。NONE不代表事实正确或完全中立；U不代表政治偏见。已有样本的取样方式与六组随机样本不同，不将本批比例外推全库。

后续可分别测试W编辑、G来源处理和U处理；本包只提供标注，不自动更改或删除原段落。
