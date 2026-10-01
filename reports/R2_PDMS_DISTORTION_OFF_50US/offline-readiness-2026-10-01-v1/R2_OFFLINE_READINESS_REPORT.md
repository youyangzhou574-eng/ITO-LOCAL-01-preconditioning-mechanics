# R2 离线准备完成记录

**OFFLINE_READINESS_COMPLETE / NOT_RELEASED_FOR_NATIVE_EXECUTION / VERSION_SEMANTICS_PENDING**

依据 Pro reply 6990c24e-ee5d-444c-b93b-a5e2881dee75，decision ITOL01-PRO-R2-VERSION-EVIDENCE-ACCESS-DISPOSITION-20261001-01，已一次完成允许的离线准备。条件性 R2 授权保留；真实 DC、analysis、新 ODB 提取均 0。未修改或重跑 R1。

## 已完成

- 实际 R1 冻结输入 SHA 8e8405152be773653f956df64fafe06d80ba7b9c5b75fe83ec7e2c719215fdf3。R2 候选 SHA 6421953d8c038f80046f30b8619c7359ee7c148fed8f8f73325a07ecc122c267。
- 唯一 PDMS controls 关联、唯一 DISTORTION CONTROL=NO 定义，另加未放行注释。移除这三项后逐字节还原冻结输入；ITO 截面、数据行及全部其他输入字节保持一致，无 adaptive mesh。
- 8 项新输入/存储身份检查 RED8→GREEN8。
- R2 独立 E bulk binding，无 reparse 祖先；实际 NTFS/Healthy/用户可写探针留存。容量是快照，运输峰值门仍必须按 R2 实际 manifest 计算，未借用 R1 尺寸。
- 冻结6源文件复制/适配前后 SHA 保存。新提取候选仅允许 fake export，native main 无条件抛出未放行异常。
- 3 项新 mock 检查 RED3→GREEN3：native entry 在打开 ODB 前拒绝；51813节点/51200单元完整网格、2个 fake frame 的 R2 NPZ CRC/无pickle解码；拒绝旧R1身份。没有真实 ODB，fake 数组不是科学结果。
- 本地 source compile 和安全 import PASS，不冒充服务器 Python2/native admission。
- 正式补证请求四问题已准备，尚未向任何支持联系人发送。

## 剩余启动前证据

2021 省略 HOURGLASS 的默认方法；新增 distortion=no 且仍省略 HOURGLASS 是否保持该默认及条件/例外；Explicit CPE4R 组合适用性；仅 PDMS Solid Section 关联是否保持 ITO 设置。接受版本对应官方短摘录或明确适用于2021的SIMULIA书面答复。较新版本、未标版本镜像、安装身份或DC关键词解析成功均不替代。

剩余属于正式版本说明获取，非原生失败，不消耗技术恢复。不存在已授权支持收件人，因此仅准备请求文本。停止重复已耗尽的网页/安装目录搜索。

## 后续顺序与科学界限

正式证据支持单一变量后：证据绑定→最小差异复核→唯一正常DC→资源/成本门→唯一analysis。生产启动器尚未准备/放行。若正式说明冲突则报告，不能自行加 HOURGLASS=ENHANCED 或另一个控制配置。

R1 仍 science gate=false：AE/E*=10.325393327019%>5%；ETOTAL漂移1.102940038338%>1%；ITO:ALLDC未取得。R1分类PDMS_DEPTH_SENSITIVITY_OBSERVED_NOT_RESOLVED。本包仅是R2离线软件/身份准备，不能作为物理有效性证据。

## 文件导航

R2_CANDIDATE_CONTROL_DIFF.txt 为小型可读输入差异；完整候选ITOL01_PDR2_V1_NOT_RELEASED.inp可下载。R2_CANDIDATE_INPUT_AUDIT.json、R2_LOCAL_STORAGE_BINDING.json、R2_SOURCE_PRESERVATION_RECEIPT.json、R2_EXTRACTOR_OFFLINE_MOCK_RECEIPT.json、R2_STORAGE_OFFLINE_PROBE_RECEIPT.json、R2_OFFLINE_SOURCE_COMPILE_RECEIPT.json和R2_OFFLINE_READINESS_RECEIPT.json为检查证据。

R2_2021_FORMAL_EVIDENCE_REQUEST.txt是可直接转交的请求。R2_VERSION_EVIDENCE_TABLE.csv列四项缺口。PRO_R2_*为完整已获裁定及SHA回执。FILE_MANIFEST.json逐文件bytes/SHA索引；未上传商业整本手册、凭据、其他项目或fake NPZ。
