# 实际验证记录 — skill 1.1.0

## 输入与执行边界

原skill固定commit：`ab3625b4a4fad3db242e1f2e8c63a27e2f998133`；物理计划固定commit：`3a906ee46ddd731b8e3c59073341862de1838615`。
本轮在隔离工作目录编写并执行普通Python测试；环境Python 3.13.5 / Linux。未运行Abaqus、Fortran编译、CAE/ODB或任何用户服务器命令；未执行原上游脚本。

## RED → GREEN（实际运行）

|批次|实际结果|含义|
|---|---|---|
|新增数学/元数据和文档结构测试，在实现前|45 tests，45 failures，exit1|函数/新结构尚不存在，失败已观察|
|新增包校验器测试，在实现前|9 tests，9 failures，exit1|校验器尚不存在，失败已观察|
|全部实现后|**54 tests，0 failure，0 error，exit0**|外部Python函数和静态规则通过|

其中38项是辅助函数测试、7项为文档/模板覆盖检查、9项为校验器普通文件测试。完整逐项结果见[TEST_RESULTS.json](TEST_RESULTS.json)。

这些RED记录针对新增实现缺失，**不是“原skill在54个真实场景全部失败”**。原skill的问题定位来自实际阅读，见[CHANGELOG](../CHANGELOG.md)。没有独立agent工具，本次未运行no-guidance/with-skill行为对照或压力评测；[12+压力场景](../tests/pressure_scenarios.md)状态保持NOT_RUN_INDEPENDENT_AGENT。

## 真实覆盖

标签11/22/12与缺失/重复；同job/step/inc时间量化和冲突/缺失；分支内LAST、回程隔离、非单调拒绝、禁止微小外推；三值有效前缀；标准HEX8刚体变换/翻转/尺度；按项目归一g的AT2均匀残量与ell敏感性；理想几何失配；包文件hash/破损链接/路径越界/非有限JSON和显式原生API导入检查。

## 不覆盖的能力

本机Abaqus2021解释器/编译器兼容性、有限变形UEL、ANS/EAS切线、DOF11真正收敛、native回滚/MPI、实际W0/W1导入、完整数据提取和实际材料标定均未测试。脚本AST的禁止导入检查只是有界结构检查，不是通用安全审计。

## 发布与安装核验

`FILE_MANIFEST.json`列出除清单自身外全部发布文件的原始UTF8字节大小与SHA256；清单不自哈希。`.gitattributes`在本目录禁用换行转换，避免Windows检出改变所校验字节；不修改全局Git配置。

安装端执行 `python scripts/validate_skill.py` 与 `python -m unittest discover -s tests -v`；校验器不访问外部链接，不安装、不运行solver。变更skill后应重新生成manifest和测试记录，不用“同名文件”代替来源确认。
