# 断裂选型、文献及来源范围

## 先确定要回答的破坏问题

|方法|适用任务|不可直接推出|
|---|---|---|
|K/J/CTOD、轮廓/域积分|已有裂纹驱动力；先检查材料/路径/约束假设|未知裂纹网络自行产生|
|VCCT|已有界面裂纹、预定义路径的能量释放率|任意膜内成核/分叉|
|界面CZM|牵引—分离、Mode I/II/混合模态脱粘|薄膜内部自动断裂；Tie自动失效|
|XFEM|版本/富集元素支持范围内的离散裂纹|任意多裂纹汇合、S4R直接富集、任意import兼容|
|弥散脆裂+删除|规定的起裂/软化/特征长度/失效机制|删除网格列就是真实裂缝宽度|
|AT1/AT2/PF-CZM|对应泛函下的裂纹带演化|三者只是命名差别；不用参数就能预测|
|相场疲劳/渐进损伤|有明确循环退化与标定的损伤模型|单调释放代码自动具有疲劳寿命能力|

MAXPS为最大主应力，MAXPE为最大主应变，QUADS为名义应力二次交互，不是“二次主应力”。起始、演化、可视裂纹、承载丧失、几何分离分别定义。[O5]

用户已选择方法时沿用，不重新作无尽选型。ITO V1已选有限变形AT2，见[项目配置](../profiles/ito-pdms.md)。AT2中任意正驱动可产生弥散损伤，旧265MPa不是独立强度输入；改变ell不是单纯加密网格。PF-CZM是膜内部本构选择，界面CZM是另一个几何界面模型。

## 固定文献清单

用户PDF固定版本：`5a5b0733965922929fc58f5559abc45670263c2a`，目录
[literature/fracture/2026-10-13](https://github.com/youyangzhou574-eng/ITO-LOCAL-01-preconditioning-mechanics/tree/5a5b0733965922929fc58f5559abc45670263c2a/literature/fracture/2026-10-13)。编号沿用用户文件。

|ID / 文件|文献与DOI|用于本项目的依据|迁移边界|
|---|---|---|---|
|S01 / 01_Chen_2002_ITO_Fracture.pdf|Chen、Cotterell、Wang，2002；10.1016/S0013-7944(01)00104-7|脆性透明膜拉伸通道裂纹与压缩下屈曲/脱粘/开裂|不是本工艺PDMS/ITO参数标定|
|S02 / 02_Zhang_2017_Main.pdf|Zhang等，2017；10.1021/acsami.7b15693|预拉伸基底上沉积硬膜，释放中横向恢复拉裂与屈曲脱粘竞争|材料主要Si/Au；不是现成ITO相场代码|
|S02-SI / 02_Zhang_2017_SI.pdf|同论文Supporting Information|实验和计算补充条件|执行端实施前实际读取；不能仅据主文补造SI参数|
|S03 / 03_Guillen_Hernandez_2019_Phase_Field.pdf|Guillén-Hernández等，2019；10.1016/j.ijpvp.2019.05.008|膜内相场与界面CZM的分工/竞争|完全粘接V1未实现该界面能力|
|S04 / 04_Reinoso_2017_Large_Deformation_Shell.pdf|Reinoso、Paggi、Linder，2017；10.1007/s00466-017-1386-3|大变形ANS/EAS实体壳相场的单元架构|项目Hencky能量是独立选择；必须逐方程核对，不称完全复现|
|S05 / 05_Kiendl_2016_Plates_Shells.pdf|Kiendl等，2016；10.1016/j.cma.2016.09.011|厚度位置先合并膜/弯曲应变，再拉压分裂|其所读小变形板壳内容不自动覆盖大变形|
|S06 / 06_Cotterell_Chen_2000_Buckling_Cracking.pdf|Cotterell、Chen，2000；10.1023/A:1007628800620|受压膜屈曲与开裂的机制/尺度|用于对照，不能代替相场材料参数|
|S07 / 07_Navidtehrani_2021_Abaqus_UMAT.pdf|Navidtehrani等，2021；10.3390/ma14081913|扩展UMAT热类比、AT1/AT2/PF-CZM作者基准|小应变；不把NLGEOM开关当有限变形UEL实现|

**本次skill修订阅读范围**：读取了原综合skill全部14个文件、当前计划关键正文和门控；沿用前轮实际读到的S02/S05/S07方法内容、S01/S03/S04/S06的已标注摘要/部分内容。本次没有重新逐页展开8个PDF，未新增声称S03/S04全文或作者源码已完整核验。P0必须记录真正读过的页/式号，之后才选择复现的方程和参数。用户已上传文件无需再次要求下载。

## 作者代码候选，不等于可直接生产使用

原综合skill提供的候选索引包括Pavan-asur/Fatigue-Solidshell、Oxford/empaneda、Molnar、Wu PF-CZM、AlexanderJFDR/Hyperelastic_phase_field等。其固定版本与许可观察保留在
[原source-provenance](https://github.com/youyangzhou574-eng/ITO-LOCAL-01-preconditioning-mechanics/blob/ab3625b4a4fad3db242e1f2e8c63a27e2f998133/reviews/ABAQUS_SKILL_AND_ITO_FRACTURE_2026-10-14/skill/abaqus-modeling-fracture/references/source-provenance.md)。

本次未下载/编译这些Fortran，不能把原清单中的推荐改称验证通过。复用时先查能量/退化函数、位移和d的DOF、裂纹变量方向、疲劳Gc退化、EAS/ANS、并行、输出覆盖及再分发许可。特别是Fatigue源码：单调基准仍须证明疲劳状态未暗中降低Gc；不能只改文件名或令循环数为1。

[Oxford代码入口](https://mechmat.web.ox.ac.uk/codes)供P1来源核对。无明确源码许可证时，不把源码捆绑进公开skill；记录链接和请求途径，不规避登录/版权。

## 本次核对的一手接口来源

- **P**：[项目固定计划](https://github.com/youyangzhou574-eng/ITO-LOCAL-01-preconditioning-mechanics/tree/3a906ee46ddd731b8e3c59073341862de1838615/plans/ITO_RELEASE_FRACTURE_PHASEFIELD_V1)。方案假设和项目数值门，不是实验事实。
- **O1**：[SIMULIA Python 3 update](https://3dswym.3dexperience.3ds.com/wiki/simulia-community/abaqus-python-3-update_Jh6mYnf4RwWRxe1OF4pxQw)。继承原审计的版本界线，本次未重做安装探针。
- **O2**：[Abaqus 2025 UEL](https://docs.software.vt.edu/abaqusv2025/English/SIMACAESUBRefMap/simasub-c-uel.htm)。本次读到SVARS/ENERGY、Static、Steady-State Fully Coupled Thermal-Stress、Linear Perturbation等条目；支持DOF11/接受态/能量槽位的接口警示，非2021现场验证。
- **O3**：[Abaqus 2025 UMAT](https://docs.software.vt.edu/abaqusv2025/English/SIMACAESUBRefMap/simasub-c-umat.htm)。本次读到分量、有限变形/混合单元注意事项；目标2021仍单独测试。
- **O4**：[Abaqus 2025 VUMAT](https://docs.software.vt.edu/abaqusv2025/English/SIMACAESUBRefMap/simasub-c-vumat.htm)。继承原综合审计的tensor/corotation纠错，本次未重新运行接口。
- **O5**：[Abaqus 2025 XFEM](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEANLRefMap/simaanl-c-enrichment.htm)。前轮已核对的功能边界，不把它当2021或所有XFEM理论的限制。
- **O6**：[OpenAI官方技能说明](https://developers.openai.com/codex/skills/)。本次实际打开后跳转官方Build skills，核对SKILL结构、本地.agents/skills、重复名称不合并及openai.yaml。安装路径仍按执行端实际版本确认。

## 原skill沿用与新设计界线

原上传位置固定在 `ab3625b4.../reviews/ABAQUS_SKILL_AND_ITO_FRACTURE_2026-10-14/skill/abaqus-modeling-fracture`，保留不修改。其environment/modeling/scripting合并为本版modeling-and-units；fracture/source/conflicts合并到本模块和CHANGELOG；其余核心主题保留并补充专项模块、模板与离线回归。

原作者声称九个上游仓库132份、121份去重文档是**原审计统计**，不是本次重新计数或121项可运行能力。新增加的流程、测试和小型解析/几何函数是本次独立编写，不包含商业手册、论文PDF或上游Fortran全文。数学见证与项目门明确分开。
