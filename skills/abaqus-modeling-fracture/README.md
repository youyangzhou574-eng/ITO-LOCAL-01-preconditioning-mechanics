# Abaqus skill：ITO释放断裂增强版 1.1.0

用途：让Codex在已有Abaqus通用技能基础上，正确执行**预拉伸PDMS→平坦新膜出生→释放诱导膜内相场断裂**的项目工作流。

**这是skill与离线审计工具，不是UEL求解器、仿真结果或新计算授权。**本次没有运行Abaqus/Fortran/ODB，没有更改正式物理方案，没有在用户电脑安装。

## 安装哪个目录

完整安装仓库中的 `skills/abaqus-modeling-fracture/`，不要只复制SKILL.md。原始上传在reviews中的副本保留作为历史，不和本版同时装成两个同名激活skill。

固定源：原skill `ab3625b4a4fad3db242e1f2e8c63a27e2f998133`；物理设计 `3a906ee46ddd731b8e3c59073341862de1838615`。本次改进来源/范围和限制见[CHANGELOG](CHANGELOG.md)，实际测试见[验证记录](checks/VALIDATION_REPORT.md)。

## Codex安装与回滚

按安装端真实版本的skill机制，优先使用其现有`$skill-installer`从明确固定commit安装本目录；或手动复制完整目录。

官方本地发现路径包括用户级 `$HOME/.agents/skills/abaqus-modeling-fracture` 和项目级 `<repo>/.agents/skills/abaqus-modeling-fracture`。本项目优先项目级；若用户要跨项目使用可选用户级。Windows由实际HOME解析，不写死用户名或E盘路径。安装端有旧版/自定义路径时先查看实际发现机制，不能假定复制成功等于被加载。[官方说明](https://developers.openai.com/codex/skills/)

安装顺序：
1. 拉取本次明确commit到隔离工作树或下载目录，先检查代码和`FILE_MANIFEST.json`。
2. 在外部Python3.10+运行下方校验与测试。不要用Abaqus2021 Python2.7执行这些辅助脚本。
3. 若有同名已安装版本，备份到**skill发现路径之外**，记下来源hash；发现其它来源的本地修改时合并或请求用户决定，不静默覆盖。
4. 复制完整目录到一个选定发现根。不要同时安装用户级和项目级同名副本；同名skill不会自动合并。
5. 明确调用 `$abaqus-modeling-fracture`，确认读到本版版本和`profiles/ito-pdms.md`。若发现列表未更新，按客户端机制重载/重启。回复实际加载路径，不仅回复“文件已复制”。
6. 回滚时恢复备份的完整目录；不修改任何模型/结果/监控状态。

本目录无安装钩子、MCP服务、网络/solver提交程序；不需修改VPN、许可证服务、全局执行策略或下载未知依赖。

## 安装前自测

从本skill根运行：
```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

离线辅助函数使用标准库，不依赖NumPy/Abaqus。源码只处理调用者传入的普通数值/元数据；不会自动访问ODB、联网或启动任务。示例调用在[测试文件](tests/test_audit_helpers.py)。**通过这些测试不代表相场UEL、Fortran、服务器或独立agent行为已经通过验证。**

## 本版主要改进

|问题|本版行为|
|---|---|
|新相场路线仍写成待选择，旧V2路径/禁写规则渗入新包|项目profile绑定已发布AT2设计；选择/实现/运行授权分开|
|只讲UMAT/UEL名称，没有落到接口测试|增加DOF11收敛、四切线块、ANS/EAS凝聚、trial回滚及MPI输出配方|
|平膜出生与基底预应力混淆|明确双参考构形、位移界面、d不跨基底、出生小增量切线验证|
|STA精度、前三列张量、跨分支去重、valid prefix误判|提供针对性普通Python函数和回归测试|
|断裂能误算人工能量，损伤带冒充裂宽|分项能量映射、AT2观测语义和厚度贯通定义|
|普通提取/网络错误导致重复审批或重复求解|基于实际授权的连续执行；未知状态只对账，技术修复不重算物理|

## Codex读入后第一件事

用户只要求安装时，提交安装/测试回执，不开服务器。用户另让按方案执行后，读取固定项目设计与当前case授权，创建公式—代码映射及P0来源核对，按P1/P2小型验证向前推进；不要继续旧fracture OFF的W1，也不要重新询问已经选定的方法。

建议安装提示：
```text
安装此固定版本中 skills/abaqus-modeling-fracture 的完整目录。
保留并备份已安装同名skill，避免重复激活；先在外部Python运行包校验和测试，确认实际发现/加载路径。
阅读SKILL.md与ITO profile；本次仅安装和检查，不启动Abaqus、不恢复旧监控、不改物理计划。
回复版本、路径、实际测试结果与未测项目。
```
