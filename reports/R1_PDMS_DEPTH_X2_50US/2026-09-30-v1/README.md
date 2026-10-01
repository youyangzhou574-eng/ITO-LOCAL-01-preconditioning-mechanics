# R1 PDMS depth refinement — frozen diagnostic archive

## 状态与用途

- R1_PDMS_DEPTH_X2_50US；PDMS厚度层数48→96，其余物理设置冻结。
- 4001 native frames；提取、运输、几何/core-field审计完成。
- 科学资格未通过：AE/E*=10.325393327019%（限5%）；ETOTAL漂移1.102940038338%（限1%）；ITO:ALLDC未取得，不能填0。
- 分类：PDMS_DEPTH_SENSITIVITY_OBSERVED_NOT_RESOLVED；诊断收口，预算关闭，无新native work授权。
- 本报告19段已被原配对网页完整接收并最终裁定。此目录仅完整归档，不重新提交旧正文、不恢复科学计算。

## 阅读入口

- [完整Markdown报告](report/full_report.md) / [完整TXT原文](report/full_report.txt)
- [最终科学裁定原文](ruling/final_scientific_closeout.txt)
- [末帧真实双层变形和ITO状态](figures/R1_FINAL_MAX_CHILD_SHAPE.png)：frame4000、约50us、2%应变、X+U scale1；2044activecracked/4deleted。native CKSTAT/删除带不是实验裂纹宽度。
- [父/子单元非仿射](figures/R1_FINAL_PARENT_AND_CHILD_NONAFFINE.png)
- [能量与反力比较](figures/R1_FL1_ENERGY_AND_FORCE.png)
- [区域动能](figures/R1_FL1_REGIONAL_KE.png)
- [CSV分文件索引](data/CHUNK_INDEX.json)：大表按连续行区间分文件，重复表头，逐行解析值与完整原表核对一致。
- [完整原始CSV](data/original/)；超过网页显示容量时使用索引中的小文件或raw链接。
- [原native审计](evidence/R1_NATIVE_AND_PATH_AUDIT.json) / [按事件拆分](evidence/events/)；原审计原bytes保留。
- [审批原文](approvals/)；均为本项目历史批准，不构成新case授权。

## 原文和解释边界

完整报告SHA256：89943da677382d6edc698c9ec44e61b583c4ec82a4e9185eaa42eaf77544ea85，200174 UTF8 bytes。

final_scientific_closeout.txt原样保存网页裁定。裁定中的反力delta/Fref=1.258文字不得当作新R1的5%合格门；R1_FL1_COMPARISON_AUDIT.json保持描述性敏感性比较（NO_NEW_FORCE_5PCT_GATE）。旧FL1/FL2失败仍保留。图片为真实已审查输出，不能据两档一方向称网格收敛或物理验证。

## 证据和交付

本目录只含白名单报告、可读附件及审计，不包含ODB、NPZ、压缩包、LFS指针、连接脚本或凭据。原始大型求解证据仍在本地保护，原报告记录其SHA；未把本地路径宣称为网页附件。

见[文件清单与SHA](FILE_MANIFEST.json)。公开HTTP读取核对与网页对话实际读取是不同证据；未验证的网页访问不会标为已读。
