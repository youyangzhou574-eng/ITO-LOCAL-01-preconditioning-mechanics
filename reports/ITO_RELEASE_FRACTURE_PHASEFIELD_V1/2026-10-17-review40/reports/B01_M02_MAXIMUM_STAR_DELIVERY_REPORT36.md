# B01_M02 原生最大残量节点完整邻元交付36

## 结论与实际范围

node5904的全部邻元由完整input连接确定为5813、5814、5818、5820。原34只覆盖其中5818、5820，本次补齐5813、5814。固定Bbar面积平均算子和全局IP排列[1,2,4,3]，计算两个完整机械行；未重新优化排列或重复34的48候选扫描。

实际读取唯一一个已收集inc10 S NPZ（290712bytes），同buffer SHA/CRC后解码全部23280行，选中4单元/16应力行参与装配。另读取已绑定4个派生文件及父级/采集元数据。没有U/E/NT11/H新读取、ODB打开、远端查询或新native。verified36 PID27352 exit0；32file完成清单及ZIP CRC/逐成员SHA一次闭合。无新图像。

## 完整行与原生记录

| 行 | 完整内力减RF（N） | 存储表示传播区间（N） | 与RF=0的区间关系 |
| --- | ---: | --- | --- |
| 5904/DOF1 | 4.9988863153049845e-9 | [-1.503706194982864e-9, 1.150147881853847e-8] | 相交 |
| 5904/DOF2 | -3.521977704756818e-6 | [-3.532199440764102e-6, -3.5117559687649435e-6] | 分离 |

对应35已核对的step1/BEND/inc10/attempt1最终第46次平衡迭代，原生最大残余力打印为+3.524E-06 N（5904/DOF2，MSG10637），打印区间[3.5235e-6,3.5245e-6] N。

独立原始残量幅值不落在该打印区间内，保留raw_magnitude_in_print_interval=false；传播实际float32应力/RF半相邻存储区间后，幅值区间与原生打印区间相交，propagated_magnitude_intersects_print=true。两个原始符号相反，保持OPPOSITE_SIGNS_CONVENTION_UNQUALIFIED，不拟合或翻转数据。本次数值结果支持有限机械收敛残量的条件解释；不能把它叫零残量、native错误、全部矩阵资格或原生IP空间映射证明。

逐单元贡献和精确Fraction上下界在TABLES36.json及element_contributions36.csv中保留。输入域仍为NLGEOM=NO、稳态coupled、厚度1、原PIN/ROLLER/LOAD点BC，无额外机械荷载。表示区间只传播固定binary64系数和实际float32存储，不涵盖算子生成/native舍入或保存时序的全部不确定性。

## 实现与审阅

3个新源码、2个新tests，8个已闭合模块仅source-bound纯helper复用，共13文件。最终12core+17runner=29tests GREEN 0.480s，一次独立review C0/I0/M0；源码未改，直接绑定同次GREEN，没有复测/二次review。新API缺失RED与旧生产缺陷区分。首core测试的对称应力fixture不能区别错误IP排列，保留1failure后改为单IP剪切fixture；这是测试样例修正，不冒充生产bug或mutationRED。

审阅独立12个畸变双单元力最大差3.3306690738754696e-16 N，768个Fraction端点、12次行/分量重排、9项重新计算哈希后的语义失配检查通过。此为synthetic算术验证，不是新增物理门。审阅脚本自身np.cross弃用warning保留，不影响成功退出，不因此修改已闭合源码。

完整gateway synthetic为实际bootstrap+stubrunner，实际runner组合synthetic另mock状态/准入；真实完整执行以本次once回执为据，不夸大synthetic覆盖。源闭合SHA 9e5821dd26ea4e317b18a257e1596ac2607d3deef52ae54f315a2b67c5b325fe。

## 下一项与未解除的门

机械最大残量节点已补齐，停止这条机械节点扩展路线。接下来NEW37先核对标量接口的定义/量纲/归一/体积热源积分约定：只以现有作者UMAT、input、已缓存官方资料和31–36闭合报告为依据，分清能从公式确定的数值尺度与仍未资格的原生取样/组装规则。不能将31的mm伪标量残量直接当物理热流，也不能拟合比例或再扫描排列以消除差异。

原B01及M02 peak/geometry/phase FAIL全部保持。M02峰值0.20462124049663544 N、误差79.0802974%；P1false/valid_prefix=null、P2/P3false、物理能量UNRESOLVED。没有已证实的单一native技术错误和修复预测，最后1P1analysis未预留。analysis7/P1used7/DC8/readonly8，当前无activejob。
