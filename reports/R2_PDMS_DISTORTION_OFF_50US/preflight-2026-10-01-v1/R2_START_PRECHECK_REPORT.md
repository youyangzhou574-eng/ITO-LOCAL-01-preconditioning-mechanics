# R2 启动前核查（当前未启动native）

## 新任务范围

- 包：ITO_PDMS_DISTORTION_CONTROL_DIAGNOSTIC_V1
- case：R2_PDMS_DISTORTION_OFF_50US
- Pro decision：ITOL01-PRO-R2-DISTORTION-DIAGNOSTIC-20261001-01
- 直接基线R1，96层PDMS/CPE4R、50us、0→2%应变；仅PDMS distortion control关闭，其余冻结。
- 新正常DC/analysis/新ODB提取各1；DC与提取各1非物理技术恢复；已启动analysis不重跑；旧预算不结转。

## 实际已确认

R1输入SHA8e8405152be773653f956df64fafe06d80ba7b9c5b75fe83ec7e2c719215fdf3；PDMS Mooney-Rivlin、独立PDMS/ITO Solid Section，无显式section-controls/hourglass/distortion关键字。

当前授权服务器启动链是abaqus.bat→abq2021.bat→D:\SIMULIA\EstProducts\2021\win_b64\code\bin\ABQLauncher.exe，launcher版本6.423.0.20032；闭合原R1 DAT标题也标为Abaqus2021。这能确认版本身份，不能单独证明默认算法或省略参数的继承语义。

只读搜索安装目录后，精确目标simaelm-c-sectioncontrol.htm、simakey-r-sectioncontrols.htm、SectionControl.py未找到。发现readerSectioncontrols.pyc不能冒充官方算法说明。远端PowerShell Include未正确过滤而返回安装文件清单，已在本地对一次取得的清单做精确filename过滤；未重复扫描或运行solver。

## 当前缺项

2021版本匹配的PDMS默认hourglass/distortion组合、CPE4R可用性，以及指定DISTORTION CONTROL=NO而省略hourglass后的继承行为。2024/2025文档仅作线索。已将两个具体技术问题一次发送给原paired Pro，不重复请求已有总体R2授权。

## 准入顺序

版本/单因素证据→独立冻结输入/源及E路径绑定→fresh资源、许可、成本门→唯一DC闭合审计→唯一analysis→新ODB只读提取/运输/验证→R1比较与有效前缀诊断。

本阶段native_dispatches=0、ODB_calls=0。R1保持结案。预检不是新计算结果报告，也不称控制根因已被证明。

## 交付方式

完整Pro原文、SHA receipt、只读版本/文档搜索证据与输入预检在本文件夹。后续长报告使用摘要+文件清单+GitHub固定commit路径，不拆多段正文；Pro实际读取确认不是继续流程的前置门。
