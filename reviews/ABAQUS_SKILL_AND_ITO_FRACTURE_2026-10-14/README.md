# Abaqus 综合 skill 与 ITO 新断裂方案审阅

当前需要审阅四项：综合 skill 的适用边界、新断裂方案的物理选择、新计划的数值验收定义，以及既有 V2 表面拉应力证据。建议按下表顺序阅读并集中回复。状态截至 2026-10-14。

| 顺序 | 审阅内容 | 需要给出的判断 | 材料 |
|---|---|---|---|
| 1 | 综合 Abaqus skill | 方法路由、官方纠错、版本限制及执行恢复规则是否充分；指出具体缺漏或错误 | [skill 入口](skill/abaqus-modeling-fracture/SKILL.md)、[冲突表](skill/abaqus-modeling-fracture/references/conflicts.md)、[来源](skill/abaqus-modeling-fracture/references/source-provenance.md) |
| 2 | Pro 新断裂方案 | 是否以有限变形 solid-shell AT2 作为新分支主路线；核对完全释放、无初始缺口和支撑选择 | [待判断事项](REVIEW_DECISIONS.md)、[Pro 固定版本方案](https://github.com/youyangzhou574-eng/ITO-LOCAL-01-preconditioning-mechanics/blob/3a906ee46ddd731b8e3c59073341862de1838615/plans/ITO_RELEASE_FRACTURE_PHASEFIELD_V1/EXECUTION_PLAN.md) |
| 3 | 数值验收 | 核对 Pro 已提出的阈值、分母、实际输出来源及阶段适用范围 | [验收审阅表](REVIEW_DECISIONS.md#验收定义和阈值) |
| 4 | 表面拉应力与后续验证 | 现有证据允许何种表述；独立表层深度验证能解决什么，仍缺什么 | [科学证据摘要与原图](evidence/SURFACE_STRESS_REVIEW.md) |

## 当前结论

综合 skill 已形成 14 个文件，来源为九个固定版本仓库。132 份 SKILL.md 去重为 121 份；包含部分非 Abaqus 文档，不等同于 121 项可运行能力。结构与链接检查 64 项通过；一次独立读者应用检查覆盖六个场景。没有进行 Abaqus 编译、求解或全部上游代码认证。[检查记录](checks/STRUCTURAL_VALIDATION.json)、[应用检查](checks/FORWARD_EVALUATION.json)、[覆盖范围澄清](checks/EVALUATION_SCOPE_CLARIFICATION.json)

**验收表述澄清：旧 V2 没有冻结的数值收敛容差；Pro 新方案已经提出具体数值门。**新方案阈值需要按其定义和实际授权范围使用，不能反向套到旧 V2，亦不能因通用 skill 不设固定百分比而忽略项目的明确标准。REVIEW_DECISIONS.md 对本次审阅具有优先解释作用；skill v1 的“D2 待定”应理解为待确认采用及适用性，不是 Pro 文档没有数字。

既有 V2 科学状态仍为 `UNRESOLVED / scientific_pass=false / validprefix=null`。上下表面的拉压差异和两网格峰值接近，不能证明断裂、脱粘或全局收敛。

## 审阅边界

- 请审阅新增资料与新方案的适用性。旧求解、源码审查和已关闭分析不在本次重复执行范围。
- Pro 原方案已在仓库内，本目录引用固定 commit，保留其版本身份。
- 本次用户授权为整理并上传待审阅资料；没有因此启动新模型、向 Pro 对话发消息或变更运行中的作业。
- 原始来源归档仍保留在本地。此处包含综合 skill、审阅说明、核验记录和选定科学证据；文件边界与 SHA 见 [清单](FILE_MANIFEST.json)。

## 建议回复格式

对 R1 综合 skill、R2 新分支路线、R3 验收定义、R4 科学证据分别写“接受 / 修改后接受 / 暂不接受”，附具体理由、修改位置和必要证据。新建模执行范围由用户另行明确，不从审阅文件的措辞自动派发。
