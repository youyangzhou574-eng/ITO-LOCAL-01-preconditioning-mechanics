# NEW39 接口观测探针：离线交付与用途决定

## 已完成的交付

两个 CPE4T、八个稳态步骤的独立观测输入和新探针 UMAT 已生成，状态 **OFFLINE_BUILD_CLOSED_ONCE**。实际本地生成 PID30520，exit0；完成清单含12文件，另有 COMPLETION39.json。代码、输入、预测和审阅来源均有 SHA256 绑定。

- 输入：cases/B01_interface_probe/B01_P39/PROBE39.inp，6821 bytes，SHA256 `0c225a742eb6d40ac1550e15f3820c6baec25086625b43043fa5d33eff05f33f`。
- 探针：同目录 PROBE39_umat.for，2504 bytes，SHA256 `c6de88ec755aff601ecbbc8f5911a74061b1b56631609bbda412b8c25aaf3f9a`。
- 预期矩阵：同目录 EXPECTED39.json；参考几何及来源：GEOMETRY39.json、SOURCE_CLOSURE39.json、SOURCE_ADMISSION39.json。
- 完整设计：docs/B01_M02_PROBE_IMPLEMENTED_DESIGN39.md；它明确取代原草案的零温度基线和完整回调日志细节。

本包没有原生提交入口。**Fortran编译、datacheck、analysis均未执行，当前无活动仿真。** 原 P1 峰值、几何、相场失败和能量未资格结论保持。

## 实验能区分什么

S1–S4按真实 NPT 标签逐列施加单位 RPL，测四节点热反力；T1–T4施加节点温度基，测导热反力及接受态 TEMP/DTEMP/COORDS。两单元分别为单位方形和原5817参考几何，源矩阵、导热矩阵、温度采样均保留真实标签与符号。

单位方形标准 Gauss 源列第一列约为 `[0.155502117, 0.041666667, 0.011164550, 0.041666667]`，角点源列为 `[0.25,0,0,0]`；这是独立预测，不是已有原生结果，也未赋予 NPT 空间身份。第二几何面积为0.0002986766392777016 mm²。每单元只留 local node3 U1自由，离线诊断刚度分别45.83333333333333和40.103929340077606；不声称等于原生实际刚度。

温度采用常量1基线，使 NT/RFL 同行保留真实零反力；STATEV分块各含非零39标记，避免全零行被省略。该设计依据已读取的 [Abaqus 2025打印输出说明](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEOUTRefMap/simaout-c-printfile.htm)，其表格规则不代替2021实际输出资格。STATEV只记录接受态快照，不记录全部回调序列或回滚。结构化记录检查器不是DAT文本解析器；未来原生表头、接受态关联和RFL可用性仍须实际核对。

两个诊断几何可提供有限接口证据，不能单独证明 M02 整体矩阵、最后 H 状态、峰值根因或 P1 PASS。

## 测试和一次独立审阅

最终 **29项新测试通过，0.542s**。覆盖解析矩阵、常量零模、仿射场、重排、正自由刚度、温度/源基、完整真实标签、缺失/重复/非有限/拒绝态、精确打印区间、离线来源绑定及once/失败边界。Python测试不冒充Fortran编译或原生端到端验证。

一次独立审阅为 C0/I1/M0。唯一重要问题是旧审阅/测试凭据可能被换几何后的closure复用。现已强制两份凭据同时绑定完整几何metadata；3项定向方法在原实现产生5个真实失败，修复后最终29项GREEN。原始审阅、反例、修复前源码和RED日志均保留，没有第二次审阅或历史测试重跑。

源码closure SHA256 `20134175074e9111a518cf3cf6e96afee5ff1c35c78a0c3090368a33cdb82bfd`；offline admission SHA256 `9b41fb94532defc56c2ff8843b885fcd5a0560331a5c43aff4392ed0990f18d9`，其中 `native_pass=false`。

## 需要决定的用途与额度

当前账本 analysis7/32、P1used7/8、DC8/48、readonly8，最后1次P1用途是具体错误后的修复验证。NEW39是接口观测，现有用途门不能直接准入。需要1次新datacheck和1次analysis，CPU4，调度上限10分钟仅为计划上限；执行前仍须实际资源与来源/未知提交门。

| 选项 | 预算/用途变动 | 观测后P1剩余 |
|---|---|---|
| **A（推荐）** | 专加1次观测额度：P1limit=9、analysis总limit=33；P2/P3P4不变 | 1次修复验证 |
| B | 明确将现有最后1次P1额度改用于观测；总额度不变 | 0次 |

两项均未生效。当前没有预留、原生准入或提交；等待的是这一具体用途/额度决定，不是原始INP或泛泛继续许可。
