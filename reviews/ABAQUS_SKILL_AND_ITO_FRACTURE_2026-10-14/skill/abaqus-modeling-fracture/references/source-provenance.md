# 来源、版本与覆盖边界

编写日期：2026-10-14。以下仓库固定到明确 commit；正文是独立整理的方法说明，未直接拼接上游模板或 Fortran。下载的源文件不等于已验证的求解能力。

## Skill 来源

| ID | 固定源 | SKILL.md 数 | 主要借鉴与边界 | 根许可观察 |
|---|---|---:|---|---|
| S1 | [jasonanewcoder/abaqus_skills](https://github.com/jasonanewcoder/abaqus_skills/tree/4737c0ab8d0548e0aa26345c5f7d5ac1a2e5dbc9) | 7 | 静态、复合材料、疲劳、热、XFEM、子程序。版本及 VUMAT/XFEM 错误见冲突记录 | MIT |
| S2 | [Cai-aa/CAE-Agent-Hub](https://github.com/Cai-aa/CAE-Agent-Hub/tree/194ef498e6efb1984cd65325e21e71087588a581/Skill/abaqus) | 44 | Abaqus 建模、分析、固化、优化；FEniCS 只作方法参考。逐模块保留 UPSTREAM 声明 | MIT，模块另有声明 |
| S3 | [jaimecernuda/abaqus-scripting](https://github.com/jaimecernuda/abaqus-scripting/tree/431b28138e34541aa8eb027be55a5eb0488f0738/.claude/skills) | 15 | CAE 分模块流程、Tosca/优化边界；11 份与 S2 字节相同 | 未发现根 LICENSE |
| S4 | [1348109517/abaqus-agent-skills](https://github.com/1348109517/abaqus-agent-skills/tree/a8295b90acfe71ad0c088898fbc2da878b46303a) | 19 | 输入依赖、命名、载荷映射、分阶段激活、脚本排错；隧道专用流程不设为默认 | Apache-2.0 + NOTICE |
| S5 | [svd-ai-lab/sim-plugin-abaqus](https://github.com/svd-ai-lab/sim-plugin-abaqus/tree/4118f73841245dc7890f9d526da8d7415e455d98) | 1 | 自动化、运行与结果接口；插件未安装，执行代码未运行 | Apache-2.0 + LICENSE-NOTICE |
| S6 | [shaokun-chen/Agent4Abaqus](https://github.com/shaokun-chen/Agent4Abaqus/tree/b5c9f4077d07ed1aae051fe1d7df2d1aded0b56b) | 1 | 建模流程索引；该 SKILL 是无 YAML 的索引，自动重试策略未继承 | MIT |
| S7 | [test1card/femis-skill](https://github.com/test1card/femis-skill/tree/ceff46782f8379425162f7de42a46312f07704a5) | 1 | FEM/力学验证与方法索引；多软件示例不当作 Abaqus API | Apache-2.0 + NOTICE |
| S8 | [HeshamFS/materials-simulation-skills](https://github.com/HeshamFS/materials-simulation-skills/tree/fa1ce8de76b2ab7a856f81891525cfa227fadfe9) | 24 | 数值方法、验证、HPC、数据与性能；通用阈值、MD/ontology 流程不作为 Abaqus 标准 | Apache-2.0 |
| S9 | [axscience/matsci-skills](https://github.com/axscience/matsci-skills/tree/ac652c4de983c8fe74c8e6f191e492ad6acf53d9) | 20 | 有限元、材料证据和结果表达；CALPHAD/组织演化相场不是断裂相场 | MIT |

总计 132 份，按源字节 SHA 去重后 121 份。数量包括相关仓库的非 Abaqus 文档，不代表 121 项可运行 Abaqus 能力。全部九个仓库下载为固定版本归档；大仓库 S2/S3 仅解出相关 skill 树、引用文件及许可证，其余小仓库解出完整内容。原始资料的脚本没有自动执行。

### 综合模块与来源对应

- 环境与脚本：S1–S6 + O1；按 O1 修正版本边界。
- 几何、材料、网格、工况、接触、热与分阶段分析：S1–S4/S6/S9 + O7。
- 断裂方法：S1/S7 + O5 + R1–R8；具体方法保留并列选择。
- 子程序、有限变形相场与固体壳：S1/S5 + O2–O4 + 作者代码索引；附加状态、切线、厚度、并行验证要求。
- 运行恢复、数据身份与图表：S4–S9；已有任务的 once/资源合同按任务加载。
- 收敛与成本：S7–S9；区分方法约定、模型验证和项目科学接受。
- ITO 项目说明：当前用户要求与项目计划，不能向一般 Abaqus 项目外推。

本包不附上游执行器、编译库和材料参数库。按路由读取对应模块，具体实施时再取目标版本手册或作者代码，逐项检查。原始归档是审计材料，不需要加入 Codex 的自动 skill 搜索路径。

## 厂商一手资料

公开网页主要为 2025 文档；它们用于纠正接口含义，**不证明所有 API/功能在 Abaqus 2021 可用**。实际安装的对应版手册与最小测试决定可用性。

- **O1**：[SIMULIA Python 3 update](https://3dswym.3dexperience.3ds.com/wiki/simulia-community/abaqus-python-3-update_Jh6mYnf4RwWRxe1OF4pxQw)：2024x GA 迁移到 Python 3.10.5。
- **O2**：[VUMAT](https://docs.software.vt.edu/abaqusv2025/English/SIMACAESUBRefMap/simasub-c-vumat.htm)：应力、剪分量、共转局部基、objective rate 及元素例外。
- **O3**：[UMAT](https://docs.software.vt.edu/abaqusv2025/English/SIMACAESUBRefMap/simasub-c-umat.htm)：STATEV、DDSDDE、工程剪应变及单元验证。
- **O4**：[UEL](https://docs.software.vt.edu/abaqusv2025/English/SIMACAESUBRefMap/simasub-c-uel.htm)：RHS、AMATRX、SVARS、LFLAGS、NRHS 和零增量调用。
- **O5**：[XFEM cohesive behavior](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEANLRefMap/simaanl-c-enrichment-xfem-based-cohesive-behavior.htm)：起裂与演化准则。
- **O6**：[Conventions](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEMODRefMap/simamod-c-conventions.htm)、[Solid element library](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEELMRefMap/simaelm-r-3delem.htm)：单位、分量、坐标和元素输出。
- **O7**：[Sequentially coupled thermal-stress analysis](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEANLRefMap/simaanl-c-thermstressanal.htm)：温度映射与结构响应。

## 作者算法实现索引

这些是算法候选/基准参考，**不是本轮解包的 skill 或已通过本地求解验证的实现**。先查原论文、源码、许可、版本和方法映射。

| ID | 一手入口 | 可用价值与边界 |
|---|---|---|
| R1 | [Pavan-asur/Fatigue-Solidshell](https://github.com/Pavan-asur/Fatigue-Solidshell/tree/fc393929b08362d72ad2793f942fe47b56435274) | solid-shell、ANS/EAS、四自由度节点；2020/2022 作者说明不能代替 2021/并行/目标能量验证，许可待确认 |
| R2 | [Oxford MechMat codes](https://mechmat.web.ox.ac.uk/codes)、[E. Martínez-Pañeda codes](https://www.empaneda.com/codes/) | 相场 UMAT、UEL、UELMAT 等作者实现；各下载包形式与许可分别核查 |
| R3 | [Molnar phase-field tutorials](https://molnar-research.com/tutorials_PH.html) | 分阶段作者教学与算例，用于基准复现 |
| R4 | [jianyingwu/pfczm-abaqus](https://github.com/jianyingwu/pfczm-abaqus/tree/9cdc19ef3ba41e3dc2ddbbdb63be4f533f87769e) | PF-CZM/BFGS；作者标明串行与研究使用，不当作 AT2 并行实现 |
| R5 | [AlexanderJFDR/Hyperelastic_phase_field](https://github.com/AlexanderJFDR/Hyperelastic_phase_field/tree/afb36a139062a9e83eb45ffd4376e7ee69e1d408) | MIT；断裂示例二维，有限变形应力度量值得对照；非现成 3D solid-shell |
| R6 | [Datta Abaqus-UEL-Hyperelasticity](https://github.com/bibekanandadatta/Abaqus-UEL-Hyperelasticity) | PK1/PK2 与 2D/3D 超弹 UEL 参考；不包含完整目标相场断裂 |
| R7 | [Fang phase-field dataset v2](https://data.mendeley.com/datasets/9n6rhvmjjn/2) | 版本化作者数据/实现；DOI 10.17632/9n6rhvmjjn.2 |
| R8 | [Bilinear-CZM-UMAT](https://github.com/harshaa765/Bilinear-CZM-UMAT)、[NASA CompDam_DGD](https://github.com/nasa/CompDam_DGD) | CZM 验证及复合材料渐进损伤参考；材料机制、许可与 Abaqus 版本各有边界 |

## 审计位置

本机原始档案保存在 E: bulk 下的 `abaqus_skill_synthesis_20261014`：
`archives/`、`unpacked/`、`receipts/`、`DOWNLOAD_COMPLETION.json`、`SKILL_CONTENT_INVENTORY.json`。
`SOURCE_COVERAGE.json` 记录逐份来源与覆盖类别。此可安装 skill 的实际使用不依赖该缓存路径；移动本 skill 时保留本来源文件即可。

