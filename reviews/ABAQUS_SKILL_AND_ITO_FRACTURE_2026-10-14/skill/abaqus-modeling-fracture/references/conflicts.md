# 合并冲突与处理

## 已可按证据澄清的冲突

| ID | 上游内容 | 综合 skill 的处理 | 依据 |
|---|---|---|---|
| C01 | jason README/ERRATA 把 2023+ 与 Python3 并列 | 按实际安装和厂商 2024x GA 迁移说明；2021 端独立适配 | O1 |
| C02 | jason VUMAT 弹性文档称 stressOld/New 只存偏应力，并额外恢复压力/旋转 | 该示例整体隔离，未复制或运行；使用目标版本 VUMAT stress tensor、共转基及 objective rate 合同 | O2，原文 L71、L129–149 |
| C03 | XFEM 文档将 QUADS 写为 quadratic principal stress；MAXPE 简化成延性材料 | QUADS 为名义应力/牵引二次交互，MAXPE 为最大主应变准则 | O5；原文 reference/crack_initiation.md L32–33 |
| C04 | 通用 dynamic 用 10ms/100ms 固定分界，并把小步长错误导向 mass scaling | 依时间尺度/惯性/非线性/资源判断；先定位首错，物理变更单独论证 | S2 dynamic 原文；本综合方法范围限定 |
| C05 | 热耦合 troubleshooting 暗示结构元素 C3D8 无法产生热膨胀 | 区分顺序温度映射与同时热位移耦合；选择对应元素 | O7 |
| C06 | 多份材料/网格/ODB/job 文档内容相同 | 按源字节摘要去重；不把多个目录收录当成多重证据 | SKILL_CONTENT_INVENTORY.json 的 11 组相同文件 |
| C07 | Agent4Abaqus 自动重新生成/执行可重试 5 次；项目存在 once 与未知状态约束 | 已有用户执行合同优先；区分只读检查、脚本修复、新求解与重复提交 | S6 + 项目用户要求 |
| C08 | 部分库要求每次问全部参数/审批，其他库直接默认执行 | 先继承实际上下文和既有授权，只问缺失且关键的信息 | 用户授权 + 本 skill 范围 |
| C09 | 上游通用百分比/GCI 布尔值用于 PASS | 保留为方法参考，不变成模型科学硬门槛 | S1 XFEM checklist、S8 convergence-study |

C02 是普通 VUMAT 接口和该示例的实际冲突；特定元素/特殊接口的压力例外不改变须逐模型核对的结论。这里没有对整库所有 Fortran 作完整验证。

## 不是可简单合并的物理路线

AT1、AT2、PF-CZM、XFEM、CZM、VCCT 以及不同张压分裂/应力度量各自有假设。以方法路由并列；任务已选方法时保持选择，替换要提出证据与具体差异。小应变与有限变形、2D 与 3D、串行与并行、裂纹算法与可视化层也不能按同名参数拼接。

## 等待项目决定

D1/D2 见 [ITO 项目说明](../profiles/ito-pdms.md)。其共同内容已整理可用，尚未决定的物理选择与数值验收保留待定；不影响静态检查、资料核对和已授权的既有任务。

## 许可和引用

Jaime 上游未发现根 LICENSE；CAI 有主 LICENSE 和模块 UPSTREAM_LICENSE，但不能反推其他仓库的许可。本综合正文独立编写，未复制这些模板或 Fortran。下载归档保留原许可证与上游声明；未来复制、修改或分发具体实现前逐包确认许可。Pavan 等算法仓库本轮只作为链接/候选，不包装成已许可并验证的 solver。

