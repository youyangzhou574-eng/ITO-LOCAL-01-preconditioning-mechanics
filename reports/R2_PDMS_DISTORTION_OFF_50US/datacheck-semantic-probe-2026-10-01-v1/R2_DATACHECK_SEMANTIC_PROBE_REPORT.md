# R2 Abaqus 2021原生datacheck语义探针报告
## 身份与唯一执行
decision ITOL01-PRO-R2-2021-DATACHECK-SEMANTIC-PROBE-20261001-01，reply677b5067全文已保存并消费。两个既有摘要仅CRLF/LF不同，不补发。
R2 frozen input SHA6421953d8c038f80046f30b8619c7359ee7c148fed8f8f73325a07ecc122c267。唯一正常DC 1/1已使用；analysis0/1、extract0/1、technical recovery0、solverrerun0、oldODB0、预算转移0。
原生2021 DC exit0/finishedtrue/process0；12闭合文件逐bytes/SHA核对。51813nodes/51200CPE4R；49152PDMS/2048ITO material+property+literal connectivity表完全匹配R1。dt5.99496e-12，T/dt8340339.218276687<30000000；double both/four domains/no mass scaling保持。
## 实际阻塞：B尚未闭合，未启动analysis
Abaqus接受关键词并成功结束，无native ERROR；但本地旧两警告白名单审计为FAIL，因为新增第三条Section Controls solid-applicability警告。它完整原文随附件，不把“warning CAN BE IGNORED if solid only”误报为“solver忽略了本关键词”。局部检查均为solid CPE4R。
R1 PDMS property1是DEFAULT HOURGLASS CONTROL/HOURGLASS CONTROL PARAMETER1.0000；R2 PDMS property1只引用R2_PDMS_DC_OFF，独立SECTION CONTROLS块明确DISTORTION CONTROL IS NOT USED、ENHANCED HOURGLASS CONTROL IS USED以及THERE ARE NO HOURGLASS CONTROL PARAMETERS WITH ENHANCED HOURGLASS CONTROL。
因此没有声称R1实际hourglass算法已证明等价，也不能把参数消失解释成物理系数改变。R2 ITO property2仍default+1.0000，完整块相同。A/B/C/D保守审计false/false/true/false：A是复合资格门false，不代表parser拒绝；D是未能闭合额外默认/表述等价，非确认发生额外物理改变。没有修改审计白名单放行，没有改input/HOURGLASS/再DC/开旧ODB。
2021_MANUAL_BODY_NOT_OBTAINED保持。原科学/资源/停止门全部保持。请依据完整native块裁定B是否可接受闭合；若不能，请给有界补证路径而非再搜同一批网页或猜控制配置。
## 用户明确要求：下一正常报告申请更大有界工作预算
本节是用户通过嘟嘟新增要求，非执行端自行增额，也没有单独追加报告。
建议批准24小时壁钟自主工作窗口：用于原R2语义门闭合后的唯一analysis、只读监控、唯一new-ODB extract、唯一运输/验证及一次科学/R1同应变比较/图像审查/完整GitHub报告。24小时是工作安排窗口，不是自动杀进程期限，也不扩模型平台额度。
计算使用原4CPU/4domains、24GiB规划及fresh可用48GiB/commit32GiB/D312GiB/至少6cores门；不申请增加并行CPU或内存。原analysis1/1与extract1/1剩余预算继续，既有technical recover上限各1但仅真实技术失败可用，analysis started rerun0。
如果确实需要额外版本语义实验，请批准最多1次datacheck-only补证，不运行analysis或ODB，不改变科学R2冻结候选；必须由Pro明确探针输入/目的/停止门及是否改变原additionalcases0边界。未获这种明确新授权之前额外datacheck0/新增case0，不把正常DC1/1重置。
普通实现细节、代码核对和健康进度本地累计；仅科学决策、实际阻塞、资源或预算范围变化和必需验收集中提交。科学STOP/invalid-prefix/能量门失败不能用预算批准覆盖。当前等这一真实B阻塞裁定，不重复申请同义analysis许可。
## 可读文件与证据
R1/R2相关完整native control块（原DAT行号）、3条完整warning、原native/text/SHA/audit及完整最新裁定文本；不附凭据/私有端点/其他项目文件/ODB/PRT二进制。完整冻结候选与mesh已有offline-readiness-2026-10-01-v1固定commit6b464a4b927c8efedb4a5af56993b7c5c3dd10c2。此报告file-manifest说明全部文件SHA及原DAT来源SHA。公开可读不等于Pro实际读取。
