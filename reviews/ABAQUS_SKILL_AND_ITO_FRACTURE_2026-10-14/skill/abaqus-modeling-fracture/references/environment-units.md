# 版本、解释器与单位

## 环境合同

记录实际 Abaqus 发行版、Standard/Explicit、操作系统、启动器、内置 Python、Fortran/C++ 编译器及并行方式。优先既有安装/成功日志和对应发行版手册；确需新探针时使用隔离小任务，不重新进入已关闭生产入口。

外部 Python 用于编排、文本、NumPy 和绘图；CAE/ODB API 运行在相应 Abaqus 内置环境中。不能用普通 pip 包或类型提示替代商业求解器/API。不要把外部 Python 3 的语法直接发送到 Abaqus 2021。

厂商的 Python 3.10.5 迁移公告对应 Abaqus 2024x GA。2021 端按其实际 Python 2.7 环境编写并验证：f-string、pathlib、typing 等不可假定可用。跨环境传递带单位与身份的 JSON/CSV/二进制数据，使用明确编码。Fortran 接口按版本核对，尤其 Explicit 接口参数曾发生变化。[O1][O2]

## 单位核对

Abaqus 不替用户指定一致单位。继承项目单位；仅在明确转换时更换整套单位，不混用几何、密度和断裂能。

若采用 N–mm–s：
- 应力/模量为 MPa；质量为 tonne；密度为 tonne/mm³。
- 1 Pa = 1e-6 MPa；1 kg/m³ = 1e-12 tonne/mm³。
- 1 J/m² = 1e-3 N/mm；Gc 的单位是能量/面积。
- 1 J/(kg·K) = 1e6 N·mm/(tonne·K)。
- 1 W/(m·K) = 1 N/(s·K)；1 W/(m²·K) = 1e-3 N/(mm·s·K)。
- 150 nm = 0.00015 mm；这些换算不代表任何材料实测值。

先做量纲与数量级复核，再考虑调整求解参数。密度对惯性、稳定步长与能量有影响；“准静态”不使密度和时间单位失效。文献值标记为方法假设，实测、拟合和估计分别记载。

## API 与资料

上游 `SKILL.md`、abqpy 类型提示、互联网示例仅提供候选符号。查目标版本的对象所属层级、参数、区域类型、输出位置及元素支持。小探针只验证实际调用，不证明科学模型。

Windows 命令通过参数数组/结构化接口传递。脚本、JSON 可 ASCII 转义；文件文本明确 UTF-8。已有可信 SSH/调度 helper 优先沿用。

来源：[O1/O2](source-provenance.md)，上游问题见 [C01/C02](conflicts.md)。

