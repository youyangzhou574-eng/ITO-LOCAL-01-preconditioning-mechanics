# UMAT、VUMAT、UEL 与状态

## 接口合同

| 接口 | 重点 |
|---|---|
| UMAT / Standard | 应力和 STATEV 更新、DDSDDE 的准确含义、工程剪应变、有限转动、混合元素/平面应力/壳条件 |
| VUMAT / Explicit | block 布局、tensor 分量与不同排列、共转基、Green–Naghdi 率、能量与稳定时间步信息、版本参数表 |
| UEL / Standard | RHS、AMATRX、SVARS、ENERGY、LFLAGS、NRHS、NDOFEL、自由度顺序、过程专属调用 |
| UELMAT | 仅在支持的元素/材料接口下访问材料库；能力不能由 UMAT 类推 |
| VUEL | 显式质量/内力/稳定步长与能量；不能把 UEL 原样更名 |
| 初值/外部数据库/输出子程序 | SIGINI、SDVINI、UEXTERNALDB、URDFIL/UVARM 等按真实阶段和并行约定核对 |

UMAT 的剪应变分量是 engineering shear；VUMAT 用 tensor shear。VUMAT 返回 stress tensor 并使用共转表示，不能普遍声称只传递偏应力、由 Abaqus 自动补全部压力；也不能无依据重复施加刚体转动修正。特定梁/管/壳的分量例外按手册另查。[O2/O3]

UEL 中 RHS 对多数非线性过程是外载减内力；AMATRX 与残量符号按目标过程定义。Riks 等 NRHS/载荷列例外必须实际支持。SVARS 一般以当前增量初态传入，输出用途的零增量调用不构成永久提交；依 LFLAGS/KINC 核查更新语义。[O4]

## 验证顺序

先检查接口签名、数组边界、固定/自由 Fortran 格式、隐式类型、精度和链接库。记录源码与输入摘要，编译通过之后仍需数值验证：
- 单元均匀应变、体积/剪切、零增量和刚体转动；
- 解析或内置材料对照，明确二者应力度量和 objective rate 差异；
- 有限差分切线：扰动步长扫描，比较方向导数，并控制状态回到同一接受态；
- 卸载、切回、重启、并行和输出映射；
- 近不可压缩、平面应力与壳厚度条件，不把三维代码默认用于任意元素。

全局 COMMON、SAVE、模块数组需要明确拥有者、索引、生命周期及同步。线程锁不能解决跨 MPI 进程的数据共享。状态传递不以数组暂时存在作为接受态证据。

仅复用已读、版本明确的作者代码。文件名带 official 或 README 写“verified”不替代厂商来源与测试记录；上游 VUMAT 弹性示例已列入 [隔离记录](conflicts.md)。

来源：[O2/O3/O4、S1/S5](source-provenance.md)。

