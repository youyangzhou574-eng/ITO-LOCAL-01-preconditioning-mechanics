---
name: abaqus-modeling-fracture
description: Use when working on Abaqus CAE or input-deck modeling, nonlinear mechanics, fracture or failure, XFEM, VCCT, cohesive zones, phase-field fracture, UMAT/VUMAT/UEL, solver diagnosis, or ODB-based verification. Applies to Abaqus 2021 and other explicitly identified releases; excludes unrelated simulation software and general phase-transition modeling.
---

# Abaqus 建模与断裂

依据实际版本、物理问题和可核查数据推进 Abaqus 工作。此 skill 提供方法选择与核验参考，不自带经过认证的断裂求解器。默认中文交流。

## 开始时确认

从现有上下文、输入文件、运行记录取得：研究问题与目标量、Abaqus/Standard 或 Explicit、版本与内置 Python、单位、几何/材料/边界、载荷与初始历史、当前阶段及既有授权。只询问真正缺失且影响结果的信息。

对已有任务先读当前计划、用户最新要求和活动运行记录。区分静态检查、建模/编译、原生求解、只读提取、科学验证；说明本次实际完成哪一层。已授权的工作继续推进，遇到实质冲突时完成独立部分，再给出冲突、证据、推荐和待决定事项。

## 按任务读取

| 当前任务 | 参考 |
|---|---|
| 环境、Python、API、单位 | [版本与单位](references/environment-units.md) |
| 参数化脚本、INP/INCLUDE、分阶段依赖 | [脚本与输入审计](references/scripting-input-audit.md) |
| 几何、材料、网格、边界、静态/动态/热/接触/疲劳 | [通用建模](references/modeling-analysis.md) |
| 裂纹/脱粘/失效方法选择 | [断裂选型](references/fracture-selection.md) |
| 相场、有限变形、薄膜 solid-shell | [相场与固体壳](references/phase-field-solid-shell.md) |
| UMAT/VUMAT/UEL、状态与并行 | [子程序](references/user-subroutines.md) |
| 作业、日志、SSH/调度器、导出错误 | [执行与恢复](references/execution-recovery.md) |
| ODB、应力位置、历史、原始数据、图表 | [提取与证据](references/evidence-postprocessing.md) |
| 算例、切线、收敛、敏感性、成本 | [验证与成本](references/verification-cost.md) |
| 上游建议互相矛盾或拟复用代码 | [冲突记录](references/conflicts.md)、[来源](references/source-provenance.md) |
| 明确是当前 ITO/PDMS 工作 | [ITO 项目分支](profiles/ito-pdms.md)，仍以项目最新记录为准 |

只加载相关参考。材料组织演化的 phase-field/CALPHAD、其他软件的 MCP 和通用 GCI 程序不自动成为 Abaqus 断裂能力。

## 交付结果的最小结构

1. **结论与当前状态**：可以确认什么，尚缺什么。
2. **本次动作**：模型/源码/数据具体变化，实际执行记录。
3. **验证证据**：用哪些数据、比较量、版本和判据，结果与适用范围。
4. **下一步或冲突**：最小必要动作；需要用户判断时给具体备选及后果。

技术成功不自动升级为科学通过。低动能、漂亮裂纹云图、单次求解成功或两个网格相似，都只能支持各自直接观测到的事实。

## 常见误用

- 把下载的 skill 当作许可、运行或模型正确性的证明。
- 把 UMAT、UEL、XFEM、CZM、PF-CZM 与 AT2 互换使用。
- 把示例参数、经验百分比或默认 CPU 数写成项目硬标准。
- 为排错自动改变材料、边界、稳定化、网格或重新提交未知作业。
- 把当前 ITO 的特殊执行规则扩展为所有未来项目必须执行的流程。

