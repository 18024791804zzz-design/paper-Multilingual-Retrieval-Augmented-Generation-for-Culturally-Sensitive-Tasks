# 107个对象的抽样排除原因与纳入说明

这些对象仅被排除于上一次“两方、不同语言代码、双方各top-3、恰好六条记录”的20对象抽样，并非被原论文251对象实验剔除，也未根据有无偏见排除。

## 数量与优先顺序

251 → 排除68个多方对象 → 183 → 排除37个同语言代码对象 → 146 → 排除2个缺指定查询对象 → 144。

三个类别按规则先后分配主要原因、互不重复。68个多方对象中另有21个也缺查询，故整个251对象不是只有2个缺查询。68=60个三方、7个四方、1个六方；其中11个还存在声索方共用语言。37同语对象按语言为ar15、sw9、en4、fr3、ru3、es2、ko1。

CSV中的“至少两种可用声索语言”等字段只是根据现有问题和标签判断的覆盖条件，不是新的模型实验结果，也不保证官方聚合脚本的所有分组都非空。

## 两个主要原因是缺查询的对象

- Minerva Reefs：Fiji=en、Tonga=to，只有en查询；Controller标签为Tonga，因此控制语缺失。上传WJ原始汤加语文章存在，但没有汤加语问题或预计算OpenAI结果。
- Tromelin Island：Mauritius=mfe、France=fr，只有en/fr；Controller标签为France。en在此不是声索语言，实际只有fr；缺非控制语mfe。原始mfe文章目录也不存在，metadata为空。

## 纳入时的处理

- 多方对象：按不同语言取top-3会使文档数量变化；保持所有声索方与答案选项，记录国家数、不同语言数和缺失覆盖。不要为统一六段随意删除第三方。
- 同语言对象：可研究文档措辞偏见、改写、事实保留与RAG回答变化，但同一语言不能被复制为两个独立的国家立场。原CS按语言存储，只有一个声索语言时没有跨语言CST配对；不会自动计为一致性100%。
- 缺查询对象：可纳入已有文本，但标明缺失。补译问题、重新检索属于扩展数据；把另一语言文档翻译过来不等于补到了该语言维基百科的原生观点。
- 汇总原CS时报告每项实际参与对象数，C与N尽量同时另报完整同领土覆盖的配对结果；空组或零分母不伪装为0分，不更改原官方公式。
- 按领土/争端家族和源段落分组划分训练测试；多方派生配对、重复段落及译文留在同一组。

若排除任何PRC/ROC声索方：107中58个被剔除，余49=10多方+37同语+2缺查询。与此前121个符合两方六段条件的非中国对象合计170。

## 全部107对象


### 多于两个声索方，不满足两方六段格式（68）

| 领土原名 | 声索方与语言 | 已有查询 | 另缺语言 |
|---|---|---|---|
| Abagaitu Islet | People's Republic of China [zhs]；Russia [ru]；Republic of China [zht] | en;ru;zhs;zht | 无 |
| Aksai Chin | India [hi]；Republic of China [zht]；People's Republic of China [zhs] | en;hi;zhs;zht | 无 |
| Arunachal Pradesh | India [hi]；Republic of China [zht]；People's Republic of China [zhs] | en;hi;zhs;zht | 无 |
| Baekdu Mountain | North Korea [ko]；Republic of China [zht]；People's Republic of China [zhs]；South Korea [ko] | en;ko;zhs;zht | 无 |
| Bajo Nuevo Bank | United States [en]；Nicaragua [es]；Jamaica [en]；Colombia [es] | en;es | 无 |
| Banc du Geyser | Madagascar [mg]；France [fr]；Comoros [ar] | ar;en;fr;mg | 无 |
| Barahoti | Republic of China [zht]；People's Republic of China [zhs]；India [hi] | en;hi;zhs;zht | 无 |
| Bedel pass | People's Republic of China [zhs]；Republic of China [zht]；Kyrgyzstan [ky] | en;ky;zhs;zht | 无 |
| Beyul Khenpajong | Bhutan [dz]；Republic of China [zht]；People's Republic of China [zhs] | en;zhs;zht | dz |
| Bhutanese exclaves | Republic of China [zht]；Bhutan [dz]；People's Republic of China [zhs] | en;zhs;zht | dz |
| Bolshoy Ussuriysky Island | Republic of China [zht]；Russia [ru]；People's Republic of China [zhs] | en;ru;zhs;zht | 无 |
| Boz-Tik | Kyrgyzstan [ky]；People's Republic of China [zhs]；Republic of China [zht] | en;ky;zhs;zht | 无 |
| Chagdzom | Republic of China [zht]；People's Republic of China [zhs]；Bhutan [dz] | en;zhs;zht | dz |
| Chagos Archipelago | United Kingdom [en]；Mauritius [mfe]；Maldives [en]；Seychelles [fr] | en;fr | mfe |
| Cherkip Gompa | Bhutan [dz]；People's Republic of China [zhs]；Republic of China [zht] | en;zhs;zht | dz |
| Chumar | Republic of China [zht]；People's Republic of China [zhs]；India [hi] | en;hi;zhs;zht | 无 |
| Darchen | People's Republic of China [zhs]；Bhutan [dz]；Republic of China [zht] | en;zhs;zht | dz |
| Demchok sector / Parigas region | People's Republic of China [zhs]；India [hi]；Republic of China [zht] | en;hi;zhs;zht | 无 |
| Depsang Plains | Republic of China [zht]；India [hi]；People's Republic of China [zhs] | en;hi;zhs;zht | 无 |
| Dokdo/Takeshima | North Korea [ko]；South Korea [ko]；Japan [ja] | en;ja;ko | 无 |
| Doklam | Bhutan [dz]；People's Republic of China [zhs]；Republic of China [zht] | en;zhs;zht | dz |
| Dungmar | People's Republic of China [zhs]；Republic of China [zht]；Bhutan [dz] | en;zhs;zht | dz |
| Erkeshtam | Republic of China [zht]；Kyrgyzstan [ky]；People's Republic of China [zhs] | en;ky;zhs;zht | 无 |
| Fergana Valley | Tajikistan [tg]；Uzbekistan [uz]；Kyrgyzstan [ky] | en;ky;tg;uz | 无 |
| Gesur | Bhutan [dz]；Republic of China [zht]；People's Republic of China [zhs] | en;zhs;zht | dz |
| Gezon | Republic of China [zht]；Bhutan [dz]；People's Republic of China [zhs] | en;zhs;zht | dz |
| Gilgit-Baltistan | Pakistan [ur]；India [hi]；Republic of China [zht] | en;hi;ur;zht | 无 |
| Glorioso Islands | Madagascar [mg]；France [fr]；Comoros [ar] | ar;en;fr;mg | 无 |
| Gue | Republic of China [zht]；People's Republic of China [zhs]；India [hi] | en;hi;zhs;zht | 无 |
| Haa District | Bhutan [dz]；People's Republic of China [zhs]；Republic of China [zht] | en;zhs;zht | dz |
| Heixiazi | Russia [ru]；Republic of China [zht]；People's Republic of China [zhs] | en;ru;zhs;zht | 无 |
| Itse Gompa | People's Republic of China [zhs]；Bhutan [dz]；Republic of China [zht] | en;zhs;zht | dz |
| Jadhang | India [hi]；Republic of China [zht]；People's Republic of China [zhs] | en;hi;zhs;zht | 无 |
| James Shoal | Republic of China [zht]；Malaysia [ms]；People's Republic of China [zhs] | en;ms;zhs;zht | 无 |
| Kaurik | India [hi]；Republic of China [zht]；People's Republic of China [zhs] | en;hi;zhs;zht | 无 |
| Khan Tengri | People's Republic of China [zhs]；Kyrgyzstan [ky]；Republic of China [zht] | en;ky;zhs;zht | 无 |
| Khochar | People's Republic of China [zhs]；Republic of China [zht]；Bhutan [dz] | en;zhs;zht | dz |
| Kula Kangri | Republic of China [zht]；Bhutan [dz]；People's Republic of China [zhs] | en;zhs;zht | dz |
| Lapthal | People's Republic of China [zhs]；India [hi]；Republic of China [zht] | en;hi;zhs;zht | 无 |
| Macclesfield Bank | Philippines [tl]；Republic of China [zht]；People's Republic of China [zhs] | en;tl;zhs;zht | 无 |
| Matthew Island and Hunter Island | New Caledonia [fr]；Vanuatu [en]；France [fr] | en;fr | 无 |
| Menchuma Valley | People's Republic of China [zhs]；Bhutan [dz]；Republic of China [zht] | en;zhs;zht | dz |
| Nelang | India [hi]；Republic of China [zht]；People's Republic of China [zhs] | en;hi;zhs;zht | 无 |
| Nyanri | Bhutan [dz]；Republic of China [zht]；People's Republic of China [zhs] | en;zhs;zht | dz |
| Pamir Mountains | Republic of China [zht]；Tajikistan [tg]；People's Republic of China [zhs] | en;tg;zhs;zht | 无 |
| Paracel Islands | Vietnam [vi]；Republic of China [zht]；People's Republic of China [zhs] | en;vi;zhs;zht | 无 |
| Parangcho | South Korea [ko]；Republic of China [zht]；People's Republic of China [zhs] | en;ko;zhs;zht | 无 |
| Pulam Sumda | India [hi]；People's Republic of China [zhs]；Republic of China [zht] | en;hi;zhs;zht | 无 |
| Ringung | Republic of China [zht]；Bhutan [dz]；People's Republic of China [zhs] | en;zhs;zht | dz |
| Rockall | Denmark [da]；Iceland [is]；Ireland [en]；United Kingdom [en] | da;en;is | 无 |
| Sakteng Wildlife Sanctuary | Bhutan [dz]；People's Republic of China [zhs]；Republic of China [zht] | en;zhs;zht | dz |
| Sang | Republic of China [zht]；People's Republic of China [zhs]；India [hi] | en;hi;zhs;zht | 无 |
| Sanmar | Republic of China [zht]；Bhutan [dz]；People's Republic of China [zhs] | en;zhs;zht | dz |
| Sapodilla Cayes | Honduras [es]；Belize [en]；Guatemala [es] | en;es | 无 |
| Scarborough Shoal | Republic of China [zht]；People's Republic of China [zhs]；Philippines [tl] | en;tl;zhs;zht | 无 |
| Senkaku Islands | Republic of China [zht]；People's Republic of China [zhs]；Japan [ja] | en;ja;zhs;zht | 无 |
| Serranilla Bank | Nicaragua [es]；United States [en]；Honduras [es]；Colombia [es] | en;es | 无 |
| Shaksgam Valley | India [hi]；People's Republic of China [zhs]；Republic of China [zht] | en;hi;zhs;zht | 无 |
| Shipki La | Republic of China [zht]；People's Republic of China [zhs]；India [hi] | en;hi;zhs;zht | 无 |
| Siachen Glacier | India [hi]；Pakistan [ur]；Republic of China [zht] | en;hi;ur;zht | 无 |
| Spratly Islands | Vietnam [vi]；Malaysia [ms]；Republic of China [zht]；People's Republic of China [zhs]；Brunei [ms]；Philippines [tl] | en;ms;tl;vi;zhs;zht | 无 |
| Tashigang | Republic of China [zht]；People's Republic of China [zhs]；India [hi] | en;hi;zhs;zht | 无 |
| Tibet | Bhutan [dz]；Republic of China [zht]；People's Republic of China [zhs] | en;zhs;zht | dz |
| Trans-Karakoram Tracts | Republic of China [zht]；People's Republic of China [zhs]；India [hi] | en;hi;zhs;zht | 无 |
| Tumen River | South Korea [ko]；Republic of China [zht]；People's Republic of China [zhs]；North Korea [ko] | en;ko;zhs;zht | 无 |
| Uzongu-Kuush | Republic of China [zht]；People's Republic of China [zhs]；Kyrgyzstan [ky] | en;ky;zhs;zht | 无 |
| Yalu River | Republic of China [zht]；South Korea [ko]；People's Republic of China [zhs]；North Korea [ko] | en;ko;zhs;zht | 无 |
| Zuthulphuk | People's Republic of China [zhs]；Bhutan [dz]；Republic of China [zht] | en;zhs;zht | dz |

### 两个声索方对应相同语言代码（37）

| 领土原名 | 声索方与语言 | 已有查询 | 另缺语言 |
|---|---|---|---|
| Aarsal | Syria [ar]；Lebanon [ar] | ar;en | 无 |
| Conejo Island | El Salvador [es]；Honduras [es] | en;es | 无 |
| Deir El Aachayer | Syria [ar]；Lebanon [ar] | ar;en | 无 |
| Fasht ad Dibal | Qatar [ar]；Bahrain [ar] | ar;en | 无 |
| Hala'ib Triangle | Egypt [ar]；Sudan [ar] | ar;en | 无 |
| Ingwavuma | South Africa [en]；Eswatini [en] | en | 无 |
| KaNgwane | Eswatini [en]；South Africa [en] | en | 无 |
| Kfar Qouq | Syria [ar]；Lebanon [ar] | ar;en | 无 |
| Khuriya Muriya Islands | Yemen [ar]；Oman [ar] | ar;en | 无 |
| Koalou | Burkina Faso [fr]；Benin [fr] | en;fr | 无 |
| Korean Peninsula | South Korea [ko]；North Korea [ko] | en;ko | 无 |
| Kpéaba | Guinea [fr]；Ivory Coast [fr] | en;fr | 无 |
| Lake Victoria | Uganda [sw]；Kenya [sw] | en;sw | 无 |
| Lolwe | Kenya [sw]；Uganda [sw] | en;sw | 无 |
| Malyy Zhemchuzhnyy | Kazakhstan [ru]；Russia [ru] | en;ru | 无 |
| Mazraat Deir al-Ashayer | Syria [ar]；Lebanon [ar] | ar;en | 无 |
| Migingo Island | Uganda [sw]；Kenya [sw] | en;sw | 无 |
| Oued Tourndo | Libya [ar]；Algeria [ar] | ar;en | 无 |
| Oyasi | Uganda [sw]；Kenya [sw] | en;sw | 无 |
| Qaa | Lebanon [ar]；Syria [ar] | ar;en | 无 |
| Qaruh | Saudi Arabia [ar]；Kuwait [ar] | ar;en | 无 |
| Qasr | Syria [ar]；Lebanon [ar] | ar;en | 无 |
| Qit'at Jaradah | Bahrain [ar]；Qatar [ar] | ar;en | 无 |
| Remba | Kenya [sw]；Uganda [sw] | en;sw | 无 |
| Ringiti | Uganda [sw]；Kenya [sw] | en;sw | 无 |
| Rukwanzi Island | Uganda [sw]；Democratic Republic of Congo [sw] | en;sw | 无 |
| Semliki River | Uganda [sw]；Democratic Republic of Congo [sw] | en;sw | 无 |
| Sigulu | Uganda [sw]；Kenya [sw] | en;sw | 无 |
| Sipilou | Guinea [fr]；Ivory Coast [fr] | en;fr | 无 |
| Southern Patagonian Ice Field | Chile [es]；Argentina [es] | en;es | 无 |
| Swains Island | United States [en]；Tokelau [en] | en | 无 |
| Tuffah | Syria [ar]；Lebanon [ar] | ar;en | 无 |
| Ukatnyy | Kazakhstan [ru]；Russia [ru] | en;ru | 无 |
| Umm al Maradim | Kuwait [ar]；Saudi Arabia [ar] | ar;en | 无 |
| Wadi Halfa Salient | Sudan [ar]；Egypt [ar] | ar;en | 无 |
| Wake Island | Marshall Islands [en]；United States [en] | en | 无 |
| Zhestky | Russia [ru]；Kazakhstan [ru] | en;ru | 无 |

### 恰好两方且语言不同，但缺指定语言查询（2）

| 领土原名 | 声索方与语言 | 已有查询 | 另缺语言 |
|---|---|---|---|
| Minerva Reefs | Fiji [en]；Tonga [to] | en | to |
| Tromelin Island | Mauritius [mfe]；France [fr] | en;fr | mfe |
