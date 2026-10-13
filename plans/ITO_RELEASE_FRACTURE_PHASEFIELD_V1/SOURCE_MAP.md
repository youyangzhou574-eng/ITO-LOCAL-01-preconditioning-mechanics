# 文献、历史输入与本方案的证据边界

方案：ITO_RELEASE_FRACTURE_PHASEFIELD_V1  
日期：2026-10-13  
唯一所属：ITO_PRECONDITIONING_LOCAL_MECHANICS / ITO-LOCAL-01

## 1. 固定文献快照

本方案以仓库提交 `5a5b0733965922929fc58f5559abc45670263c2a` 为文献快照。8 个 PDF 位于 `literature/fracture/2026-10-13/`；原字节清单为该目录的 `DOWNLOAD_MANIFEST02.json`。不改 PDF，不重新上传商业手册或不明许可代码。

本次规划已通过 GitHub 连接读取当前分支、目录及完整下载清单。GitHub 的 PDF 正文接口及规划环境的二进制下载未能可靠取得全部 PDF；不能据此声称规划端逐页核验了 03/04 全文。本次另外实际读取了 07 的公开预印本正文、作者代码页、04 的出版社页面和相关有限变形方法综述。执行端已有用户下载的 PDF，应从本地/仓库文件提取完整方法，无需再次要求用户代查或重复注册下载。

下面的“作用”不是称论文已经验证本工艺 ITO/PDMS；EXECUTION_PLAN 中明确标为“本方案规定”的部分属于待验证工程设计。

## 2. 来源表

|编号|仓库文件与 DOI|用于本任务的依据|不能由该来源直接推出|
|---|---|---|---|
|S01|`01_Chen_2002_ITO_Fracture.pdf`；10.1016/S0013-7944(01)00104-7|脆性薄膜/透明导电膜在柔性基底上的拉裂与压缩失稳破坏问题|本工艺 ITO 强度、断裂能或 PDMS 界面参数已经标定|
|S02|`02_Zhang_2017_Main.pdf`；10.1021/acsami.7b15693|预拉伸弹性体上沉积硬膜后释放的物理路径；纵向压缩、横向恢复、屈曲/脱粘/开裂需区分|Si/Au 参数可直接用于 ITO，或论文提供本项目的相场程序|
|S02-SI|`02_Zhang_2017_SI.pdf`；10.1021/acsami.7b15693.s001|执行时核对释放方向、实验图和计算边界的补充依据|本方案作者已经在本轮逐页独立检查 SI|
|S03|`03_Guillen_Hernandez_2019_Phase_Field.pdf`；10.1016/j.ijpvp.2019.05.008|薄膜内部相场与预先存在界面的 CZM 分工；裂纹穿透、偏转、脱粘竞争|首版必须任意加入未知界面参数，或已经有本工艺无缺口多裂纹验证|
|S04|`04_Reinoso_2017_Large_Deformation_Shell.pdf`；10.1007/s00466-017-1386-3|有限变形 solid-shell、EAS/ANS、防锁死与 Abaqus/FEAP 用户单元实现的主要参考|普通 S4R+任意 UMAT 等价于文中用户单元，或打开 NLGEOM 就完成有限变形相场|
|S05|`05_Kiendl_2016_Plates_Shells.pdf`；10.1016/j.cma.2016.09.011|膜/弯曲应变组合后按厚度积分点作拉压分解|仅中面平均应变足够；其小变形算例可无修改作为大变形验证|
|S06|`06_Cotterell_Chen_2000_Buckling_Cracking.pdf`；10.1023/A:1007628800620|压缩薄膜屈曲开裂的机制背景|均匀压缩损伤即可称实际压碎|
|S07|`07_Navidtehrani_2021_Abaqus_UMAT.pdf`；10.3390/ma14081913|公开 UMAT/热传导类比相场、AT1/AT2/PF-CZM、小应变基准|将小应变源码接到大转动薄膜就已验证；AT2 有严格非零损伤起始阈值|

S04 出版页明确介绍 mixed EAS、ANS、solid-shell 和 fully coupled monolithic formulation。本方案的正式 UEL 采用整体耦合路线；不把 S07 的某一个单次交错更新当作完整有限变形收敛算法。

## 3. 已核实的公开阅读入口

- S07 正文公开预印本：https://arxiv.org/pdf/2104.04152 （预印本与仓库出版版页码不同，执行报告分别标页码）
- S07 作者代码页：https://mechmat.web.ox.ac.uk/codes ，选择标题为 ABAQUS UMAT subroutine for phase field fracture、对应 2021 年上述论文的条目。原始代码尚未由规划端编译运行；执行端须记录实际下载来源、文件哈希、许可及版本。
- S04 出版页面：https://link.springer.com/article/10.1007/s00466-017-1386-3
- S03 出版页面：https://www.sciencedirect.com/science/article/abs/pii/S0308016118304423
- S02 主文开放入口：https://par.nsf.gov/servlets/purl/10066605
- 补充有限变形背景，不属于用户上传八篇之一：Recent advancements on the phase field approach to brittle fracture for heterogeneous materials and structures，https://link.springer.com/article/10.1186/s40323-018-0102-y

## 4. 哪些是本方案规定，而不是文献原值

以下均为新的、需要验证的工程规定：首版采用 AT2 而非直接开发有限变形 PF-CZM；ITO 采用客观有限应变弹性能的谱分裂；首版完全粘接；候选几何/材料/长度尺度；后处理阈值；各阶段验收容差和预算。它们不冒充 S04 的逐式原样复制。

具体有限应变能量、正则化测度、残余刚度、相场变量方向和不可逆实现必须按 EXECUTION_PLAN 第 4 节统一。复现原文算例时使用原文参数；迁移到本项目时另列差异，不混用材料卡。

## 5. 历史事实与新目标

用户当前目标来自其与老师讨论后的明确需求：在预拉伸 PDMS 上沉积平坦 ITO，释放中研究断裂，而非只证明无损伤周期皱纹。

旧二维脆性开裂/删除算例和旧三维无断裂 W0/W1 不转化成新相场模型的有效验证。其 FAIL、原文件和资源账本保持不变。旧输入 E=103200 MPa、nu=0.27、Gc=0.005 N/mm 等只可用作候选数值参数，不能称本工艺实验标定。旧强度 265 MPa 不再是 AT2 的独立输入或硬起裂验收值。

## 6. 首次实现必须补齐的逐式映射

执行端在 `work_packages/ITO_RELEASE_FRACTURE_PHASEFIELD_V1/docs/equation_to_code_map.md` 中填写：PDF 文件、PDF 实际页号、公式/章节、源码函数/行号、变量方向、单位、与原文是否相同。至少覆盖位移/相场形函数、EAS 静态凝聚、ANS 采样、膜厚积分、有限应变能与切线、AT2 裂纹能、不可逆约束、积分点状态回滚和 UEL 能量输出。

存在原文未给出的实现细节时，标记 ORIGINAL_IMPLEMENTATION_DESIGN 并写相应验证；不伪造作者代码或论文结论。没有作者 UEL 源码不等于方法无法实施，但意味着需要按方程开发并通过小算例，不能跳过该工作直接跑完整薄膜。

END_ITO_PHASEFIELD_SOURCE_MAP
