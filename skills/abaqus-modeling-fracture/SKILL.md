---
name: abaqus-modeling-fracture
description: Use when building or reviewing Abaqus models, prestrain/deposition/release histories, thin-film fracture, phase-field solid-shell UEL, UMAT/VUMAT, XFEM/CZM, nonlinear solver failures, or ODB evidence. Not for phase-transition/CALPHAD models or unrelated solvers.
---

# Abaqus 建模与断裂

把物理问题、版本接口、原生执行和科学证据分开。提供可执行工作流与离线核查工具，**不自带已验证的 Abaqus 断裂求解器，不因安装获得计算权限**。默认中文，变量名保留原接口。

## 从实际任务接续

读取用户最新目标、当前项目计划和当前运行记录。优先复用已有输入与证据，不重复问已确定的相场/XFEM、二维/三维选型。只读取本次所需模块；旧报告是证据，不是永久运行指令。

形成一条可执行摘要：`项目/分支 → 当前阶段 → 已有证据 → 本次获准动作 → 完成条件 → 下一项`。安装、阅读、离线测试、原生提交、科学变体分别识别。若阶段已获准且前置条件成立，直接接续；未知作业状态只对账，不重新提交。

## 按需路由

|任务|读取|
|---|---|
|版本、单位、通用 CAE/INP、网格/接触/边界|[建模与单位](references/modeling-and-units.md)|
|方法选择与论文迁移|[断裂与文献](references/fracture-and-literature.md)|
|相场残量、有限变形、ANS/EAS、状态/并行|[UEL 实现](references/uel-implementation.md)|
|预拉伸、新膜出生、释放/重拉状态|[沉积参考态](references/deposition-and-release.md)|
|STA、分量标签、UEL 输出、能量、裂纹/图表|[ODB 与证据](references/odb-and-evidence.md)|
|提交、资源、连接、运输、失败恢复|[执行与恢复](references/execution-and-recovery.md)|
|基准、数值容差、验证优先级|[验证矩阵](references/validation-matrix.md)|
|明确是 ITO-LOCAL-01 新断裂分支|[ITO/PDMS 配置](profiles/ito-pdms.md)，再读其所指固定方案|
|交付格式、安装、测试范围|[交付模板](assets/handoff-template.md)、[安装入口](README.md)|

## 执行配方

1. **定义问题**：量纲、参考构形、真实/假设边界、方法与目标量；未知实验参数标为未知或候选。
2. **映射实现**：论文方程 → 应力/应变与自由度 → 源码 → 原生输出 → 对应测试。作者基准与本项目改造分开。
3. **先小后大**：力学/相场/回滚/输出/出生验证通过后才扩大模型；不能靠更大三维网格替代接口正确性。
4. **提交与取证**：同一输入绑定独立运行身份；成功退出、完整导出、几何有效、能量闭合、形态结论分别判断。
5. **交付并继续**：摘要给结论、变化、证据和下一步；完整报告/真实图/CSV用固定 GitHub commit。没有需用户决策的实质变化时，不把网页已读或普通解析修复变成新审批。

## 最容易误判的边界

- 小应变 UMAT + NLGEOM 不是有限变形实体壳相场；普通静力机械收敛不证明 DOF 11 相场收敛。
- 初始平膜与数值微扰分开；膜内 AT2、界面 CZM、裂后接触、电学是不同能力。
- 按实际标签选 11/22/12；不按前三列。缺失量为未知，不补零。
- 已接受增量与最后保存帧分开；时间量化误差不等于原生不收敛。
- `detJ` 几何映射与 `detF`、原生积分点与附加几何探针分开。负值经核对后不能用漂亮图或成功退出推翻。
- AT2 的 first d>0 不是一条裂纹；高损伤带宽不是裂缝开口；物理断裂能不是需压到5%以下的人工能量。
- 只在同一单调分支内比较同应变；不得合并释放与重拉。

离线工具运行方式及适用范围见 [ODB 与证据](references/odb-and-evidence.md)。不加载无关上游 skill 全集，不执行未知下载脚本。
