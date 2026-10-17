# B01_M02 完整局部节点内力—反力诊断34

## 结果

NEW34 已通过冻结源码入口实际执行一次并闭合。采用增量10保存的六单元应力，完整 input 连接确定11个候选节点，其中6个具有完整邻接单元：5898、5901、5902、5903、5907、5908。另5个节点明确为 INCOMPLETE_STAR，仅报告局部贡献和缺失单元，不比较完整平衡。

| 独立候选 | 共同IP排列 | 12自由度差值L2/N | 最大绝对差/N | 表示区间分离 |
|---|---|---:|---:|---:|
| 标准Gauss Q4 | [1,2,4,3] | 0.0295089759603102 | 0.0208001029568817 | 12/12 |
| 面积平均B-bar | [1,2,4,3] | 3.02038621138191e-06 | 2.40203231725161e-06 | 11/12 |

B-bar下 LOAD5903/DOF2 内力 -0.1986481296365627 N，对保存RF -0.1986481249332428 N，差 -4.7033199002122217e-09 N；两个传播/存储表示区间相交。最大差在自由node5902/DOF2，为 -2.4020323172516123e-06 N。其余自由行与保存RF=0的半相邻区间分离，不能把这些有限小残差直接称作native错误。B-bar的L2/(内力L2+RFL2)为 7.60235259322501e-06，仅描述，不增加科学门。

本次对参考坐标采用厚度1与工程剪切B；S12没有额外乘2。input检查确认NLGEOM=NO、稳态coupled、原位移边界及无显式机械载荷/惯性/稳定化关键词。精确Fraction只传播固定binary64(B*detJ*t)系数与float32 S/RF半相邻区间，不涵盖算子生成误差、native内部算术、有限求解收敛残量或作者原始节点精度。

结果支持33平均体积应变解释的机械虚功一致性；受测完整局部行不代表全部native assembled matrix。不能据此授予空间IP映射、UMAT TEMP取样规则、RPL积分或P1通过资格。原峰值误差79.0802974%、几何/相场FAIL、physical energy UNRESOLVED保持，scientific_pass=false、valid_prefix=null、P2/P3=false。

## 实现与证据

- 3新源码、2新tests、5旧pure helpers按不变字节新绑定；没有旧入口或闭合测试重入。
- 最终30tests GREEN（1.251s），一次独立review C0/I0/M1；Minor仅runner头注释/错误标识残留33，改为34后绑定最终测试。无实际生产功能缺陷，未以mutation冒充RED。缺失新API的RED及首完整测试bootstrap import命名失败保留。
- reviewer额外12畸变Q4、两算子能量梯度/转动协变性及3072 Fraction端点检查完成；无真实payload读取。
- 实际verified34 PID47128 exit0；精确5派生文件、其中2CSV，同bufferSHA后解码；32file完成清单。PACKAGE34.zip由runner一次CRC/eachSHA核验后闭合，此交付未重复ZIP全量验证。
- 完整gateway synthetic为真实bootstrap+stub runner；实际runner的synthetic组合验证独立运行且mock状态/准入。真实一次执行仅由本次实际回执证明，不夸大synthetic覆盖。
- 本次无新图片，无视觉通过声明。0NPZ/0ODB/0scheduler/0native，analysis仍7/P1used7/DC8/readonly8。

SOURCE_CLOSURE34 SHA `5969a06ac013cc9d6a40b53dc3f04c8bacf0e950afacd50b78a00069a11013de`；COMPLETION34 SHA `c4d8496d14d72876d8f7f29ad1bc8df107bf5d09b2ed203934b87bd72043b555`；RESULT34 SHA `4238d85f49c423864377360198391d918ea4f9f5bf32760bf523d360420e0c9d`；PACKAGE34 SHA `30a45e4e0274dbbde65d6a357ac5fe6dae8e83231b587d725689499f0e4a24a4`。

## 下一项：35收敛证据匹配

机械B-bar仍有最大2.402e-6 N自由行残差，需要匹配闭合native MSG在同一接受增量10、最终平衡迭代的打印残量/节点/DOF。标量31使用全部5820单元装配，不是六单元截断；不能把本次INCOMPLETE_STAR边界误套到31全局残量。下一步只复用已闭合31候选/局部残量CSV与34节点力CSV、以及匹配闭合MSG/STA，以判断有限收敛残量是否解释机械差值并定位标量候选的剩余不相容。不得重算旧31候选或34力、重开ODB，不能仅据打印相容授权最后一次原生分析。
