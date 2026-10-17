# NEW39 一次独立离线审阅

审阅结论：**修复后方可关闭离线包审阅项**。Critical 0 / Important 1 / Minor 0。该结论只针对离线实现可审查性，不批准 native，不授予 P1 PASS，不消耗观测额度。

## 审阅身份与范围

审阅了 REVIEW_PENDING39.json、DESIGN_RULINGS39.json、GEOMETRY_SELECTION39.json、原始 DRAFT39，以及本次审阅期间补充的 B01_M02_PROBE_IMPLEMENTED_DESIGN39.md。后者明确取代旧草案的零温度基线与完整回调追加日志描述；因此旧草案的差异不再列为未解决问题。

五份受审源码为 src/python/b01_m02_probe39.py、src/python/run_b01_m02_probe39.py、src/fortran/b01_interface_probe39.for、tests/test_b01_m02_probe39.py、tests/test_run_b01_m02_probe39.py。本次实际读入字节的 SHA256 全部与 REVIEW_PENDING39 一致，详见 REVIEW_SYNTHETIC39.json。既有 FULL_GREEN27_39.log 的散列也与 pending 一致，日志记录 27 tests / OK；本审阅没有重跑完整测试集。

## Important：R39-I1 — 审阅/测试凭据未绑定被审阅的几何

位置：src/python/run_b01_m02_probe39.py:91–94；相关来源检查在 :21–24；tests/test_run_b01_m02_probe39.py:26–36、:88–93。

builder 在检查 review/final_tests 时只要求 pass=true 与 source_files 相同，随后从 closure.geometry 读取几何。两份凭据均未要求绑定 geometry 或完整 closure 的摘要。_geometry 只检查原元素/节点标签与一个 source.sha256 字符串；它不会证明当前坐标正是该来源中的坐标。因此同一版源码的旧审阅/测试凭据可以支持一个不同的几何包，尽管几何是本实验的重要独立身份。

已复现的独立反例：在 BASE/evidence/B01_M02_probe39 下建立自动清理的临时目录，复制五份未改动源码作为来源；review 和 final_tests 都显式记录原5817几何的 metadata；closure 改指向节点坐标 [[2,0],[3,0],[3,1],[2,1]]，保留原5817、节点5907/5903/5902/5908及原source SHA；更新 closure 的 admission 摘要。builder 返回 OFFLINE_BUILD_CLOSED_ONCE，把 element202 面积从 0.0002986766392777016 改为 0.9999999999999999。两份凭据中明确记录的旧 geometry 字段被忽略。原始工程、真实39入口和原模型未被修改；临时目录已由 context 清理。

反例不是要求 native 分布式授权网关，也不是要求防止持有者故意伪造全部凭据；它展示了正常重建 closure/admission 后，旧 review/tests 被意外复用的缺口。

建议修复：让 review 与 final_tests 都包含并强制核对同一个完整 closure SHA256，或至少强制核对 closure.geometry 的 path/bytes/sha256（包括缺字段拒绝），同时保留现有 source_files 绑定。几何选择收据是经审阅的输入身份，不能只凭嵌入的旧来源SHA字符串认可任意坐标。添加定向测试：保留原review/tests，改变几何并重算几何、closure及admission摘要，要求在 out.mkdir 之前拒绝；另分别覆盖review缺/错几何与tests缺/错几何。保留真实 RED-GREEN，不需要第二次独立审阅。

## 已完成的独立核查及证据边界

- Q4 的连接顺序、参考形函数、Jacobian与梯度链式法则、2×2权重以及厚度/热导率为1时的源和导热量纲一致。候选列明确采用几何顺序，没有把顺序当作原生NPT；原始反力符号未翻转或拟合。
- 对单位方形和5817参考几何，独立鞋带面积与源列总和一致到浮点舍入量级；K对称且常量零模残量至多1.12e-16；仿射温度2x−3y+7的离散能量分别为12.999999999999995和0.003882796310613612，与独立13×面积一致到浮点舍入量级。这是合成算术核查，不引入原生物理容差。
- 代码生成8个稳态步骤，每步重设全部边界；每个元素只有local node3 U1自由，程序给出的正刚度诊断值分别45.83333333333333和40.103929340077606。这里只证明本离线诊断算子为正，不把这些数值称为Abaqus实际机械刚度。
- UMAT静态检查未发现共享SAVE、文件追加或可变全局状态；STRESS、切线、热耦合输出、能量和STATEV均按本过程初始化；源按KSTEP/NPT激活；STATEV是当前调用快照，代码和新版说明不将它解释为完整trial/rollback历史。固定格式非注释语句没有超过72列。
- 输出计划在每个NODE表同列NT/RFL，在每个SDV分块保留非零schema39且每行最多9变量；默认field/history请求设frequency=0。尚未证明实际Abaqus版本接受这些输出标识或产生预期表布局。
- print_interval对 -.3524D-05 返回精确有理端点 -7049/2000000000 与 -7047/2000000000。结构化合同保留原数字token，检查记录完整性、重复、标签、拒绝态和非有限值。它不读取DAT，也不能凭外部填入accepted=True独立证明求解器接受态；新版说明已经明确这一限制。
- 输出目录的独占创建、已有partial/orphan/failed目录拒绝重入以及普通写异常关闭逻辑与此离线包范围一致。没有要求分布式native gateway。

## Declined to judge

未运行 Fortran 编译、Abaqus datacheck/analysis、SSH、scheduler、ODB/NPZ读取、网络查询或下载；未启动真实39包入口，未修改源码/测试/历史审阅/入口、预算或Git。未验证ABA_PARAM.INC/编译器ABI、当前安装版本的RFL可用性、实际SDV分块/表头、原生积分点定位、真实接受态与回滚、实际机械方程计数、无场输出时ODB文件是否仍由求解器创建，亦未判定任何真实M02结论。

本次独立审阅到此结束。R39-I1由主执行者做真实定向RED-GREEN并记录最终源码身份；不进行第二次审阅。最后1次P1额度仍为修复验证用途，不能用于该观测。
