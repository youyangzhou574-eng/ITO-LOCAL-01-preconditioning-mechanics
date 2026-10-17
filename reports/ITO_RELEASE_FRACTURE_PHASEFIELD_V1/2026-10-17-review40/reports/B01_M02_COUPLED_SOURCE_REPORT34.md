# NEW34 耦合单元来源核对

## 问题与边界

33已解释标准Q4与保存E的正应变表示差异，尚未解释32的角点g(d)对应和31的标量残量。此新来源路线仅询问CPE4T耦合单元的插值/材料计算位置。为避免重复，匹配读取B02_SOURCE_INTEGRATION_REPORT06.md；旧06已讨论非耦合传热角点通量文档，不复查该网页，不重跑旧来源入口。

两条官方限定查询、两页选定HTML各下载一次，均HTTP200；完成回执为evidence/B01_M02_coupled_source34/COMPLETION34.json。没有原生、调度或ODB调用。

## 所得与未得

[二维单元库](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEELMRefMap/simaelm-r-2delem.htm)将CPE4T列为四节点双线性位移/温度单元，角点自由度1/2/11；[分析类型说明](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEELMRefMap/simaelm-c-analysistype.htm)描述耦合单元温度线性插值及其他单元的例外。

这些一般插值说明没有明确给出本次2021 CPE4T的UMAT TEMP取样坐标/与机械IP的赋值关系，不能将其等同于材料点实际温度或RPL精确积分规则。2025资料不授予本次2021实现资格。检索出现的“一阶单元热膨胀使用常温度”只适用于thermal expansion叙述，不能移用为一般UMAT相场变量的规则。二维单元库IP编号图本轮未下载或查看，不据文字入口猜图。

## 下一动作

来源路线已闭合，不重复相同查询/下载。继续使用已闭合局部数据和33的独立Bbar算子，检验包含全部相邻单元的节点行中，保存S组装的内力与保存RF是否对应。它能进一步限制机械场解释，不能独自证明完整native矩阵或具体标量实现。未找到可证实单一修复，最后P1 analysis仍未预留。
