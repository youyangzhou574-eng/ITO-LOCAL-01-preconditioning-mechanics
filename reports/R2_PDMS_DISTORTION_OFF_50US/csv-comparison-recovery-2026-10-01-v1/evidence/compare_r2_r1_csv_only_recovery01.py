"""One explicitly authorized CSV-only recovery. Closed audits are context only."""
import csv, datetime, hashlib, io, json, shutil, sys, traceback
from pathlib import Path
import numpy as np
from r2_comparison_rules import common_strain_grid, compare_scalar

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'ITO_FLAT_BILAYER_PDMS_DEPTH_REFINEMENT_V1'
AUTH = 'b325fe40a2e4b8dce92df0607d9dea9a1f44aa648e5e65324d6564b9a6cbe915'
EXPECTED = {
 'R2_HISTORY_CURVES.csv':'0c7ea4506d0d7fb13f5c81f008d00ac023c79d0be9a57d131f59e92ed30ed03e',
 'R2_SPATIAL_PATH.csv':'e3310025d5d178b14fec2d3a8b20d7a23fd4c32863a5a0b68822fef8cbe570f2',
 'R1_HISTORY_CURVES.csv':'6f321607799e9ec2f36b6f96143c83f2ec8d5352a74f51c2839864438c55bd84',
 'R1_SPATIAL_PATH.csv':'cfd420b93246d44270d06bdf718191aa50858193bf5807e3234b5ca2390cb76e'}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 with Path(p).open('x',encoding='utf-8',newline='\n') as f: json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def textfile(p,s):
 with Path(p).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
def csvdata(stream):
 r=csv.DictReader(stream);names=r.fieldnames
 if not names or len(set(names))!=len(names):raise ValueError('Absent/duplicate CSV headers')
 rows=list(r)
 return {k:np.array([v[k] for v in rows],dtype=object) if k=='raw_geometry_operation_error' else np.array([float(v[k]) for v in rows],dtype=float) for k in names}
def bracket(axis,grid):
 a=np.asarray(axis,dtype=float)
 if a.ndim!=1 or not len(a) or not np.isfinite(a).all() or np.any(np.diff(a)<0):raise ValueError('Invalid measured strain axis')
 _,rev=np.unique(a[::-1],return_index=True);keep=np.sort(len(a)-1-rev);u=a[keep]
 if np.any(grid<u[0]) or np.any(grid>u[-1]):raise ValueError('Extrapolation prohibited')
 j=np.searchsorted(u,grid);i=np.where(u[j]==grid,j,j-1);w=np.zeros(len(grid));mask=i!=j;w[mask]=(grid[mask]-u[i[mask]])/(u[j[mask]]-u[i[mask]])
 return keep[i],keep[j],w
def values(v,b):
 i,j,w=b;return (1-w)*v[i]+w*v[j]
def fixture():
 a=np.array([0.,1.,1.,3.]);b=np.array([.5,1.,2.]);av=np.array([-2.,9.,4.,-3.]);bv=np.array([3.,-1.,5.])
 old=compare_scalar(a,av,b,bv);g=np.array(old['grid']);diff=values(av,bracket(a,g))-values(bv,bracket(b,g))
 if not np.array_equal(diff,np.array([v['difference_R2_minus_R1'] for v in old['rows']])):raise AssertionError('Original scalar rule differs')
 if bracket(a,np.array([1.]))[0][0]!=2:raise AssertionError('Duplicate LAST differs')
 try:bracket(a,np.array([4.]));raise AssertionError('Extrapolation accepted')
 except ValueError:pass
 v=csvdata(io.StringIO('macro_strain,raw_geometry_operation_error\n0,\n1,diagnostic text\n'))
 if list(v['raw_geometry_operation_error'])!=['','diagnostic text']:raise AssertionError('Text preservation failed')
 try:csvdata(io.StringIO('macro_strain\n""\n'));raise AssertionError('Missing numeric accepted')
 except ValueError:pass
 return dict(status='PASS',original_rule_signed_scalar_equivalence=True,duplicate_LAST=True,no_extrapolation=True,text_column_preserved=True,missing_numeric_rejected=True)
def inputs():
 paths={};bindings={}
 for c,root,h in [('R2',ROOT,'f79545ade6741624bf3d4ac45010832cf4999c1e29a7593be29452b3f768df35'),('R1',BASE,'faba594e5507874877ec09fab56e12d13075195514a3e2efcc8e318529cf69fa')]:
  p=root/(c+'_LOCAL_STORAGE_BINDING.json')
  if sha(p)!=h:raise ValueError('Storage binding changed')
  bindings[c]=read(p)
  for kind in ['HISTORY_CURVES','SPATIAL_PATH']:
   n=c+'_'+kind+'.csv';paths[n]=Path(bindings[c]['paths']['derived'])/n
  p=root/(c+'_NATIVE_AND_PATH_AUDIT.json');paths[p.name]=p
 paths['authority']=ROOT/'USER_R2_LOCAL_CSV_COMPARISON_RECOVERY01_AUTHORIZATION.txt'
 paths['rules']=ROOT/'r2_comparison_rules.py';paths['source']=Path(__file__)
 hashes={n:sha(p) for n,p in paths.items()}
 for n,h in EXPECTED.items():
  if hashes[n]!=h:raise ValueError('Closed CSV identity differs: '+n)
 for n,h in [('R2_NATIVE_AND_PATH_AUDIT.json','575c2d95e3d16967eea2d15f70914a5ed19531983f7f488e52dea6f6ad39b774'),('R1_NATIVE_AND_PATH_AUDIT.json','0dacc01916a282a7a6212df978d74961bb71b00ab1a8452c985a72f2871422c5'),('authority',AUTH),('rules','97cf28c3e200b5401111abf4d64bbf16fcaf2d93c0900c2c0987deef8c2c5e59')]:
  if hashes[n]!=h:raise ValueError('Retained context/authority identity differs: '+n)
 return paths,bindings,hashes
def prepare():
 paths,bindings,hashes=inputs();out=Path(bindings['R2']['paths']['derived'])/'csv_comparison_recovery01'
 if out.exists():raise ValueError('Recovery output already exists')
 result=dict(status='CSV_ONLY_RECOVERY01_SOURCE_ADMISSION_PASS',utc=now(),source_hashes=hashes,input_paths={n:str(p) for n,p in paths.items()},output=str(out),targeted_fixture=fixture(),native_calls=0,ODB_calls=0,NPZ_reads=0,science_audit_reruns=0)
 write(ROOT/'R2_CSV_COMPARISON_RECOVERY01_SOURCE_ADMISSION.json',result)
 print(json.dumps({'status':result['status'],'fixture':result['targeted_fixture']},ensure_ascii=True))
def prefix(a,t):
 p=a['valid_prefix_audit']
 if p['first_invalid_frame'] is None:return np.ones(len(t),dtype=bool)
 limit=p.get('native_time_bracket_s',[None])[0]
 return np.zeros(len(t),dtype=bool) if limit is None else t<=float(limit)
def save_table(p,cols):
 with Path(p).open('x',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(cols);w.writerows(zip(*cols.values()))
def run():
 paths,bindings,hashes=inputs();admission=read(ROOT/'R2_CSV_COMPARISON_RECOVERY01_SOURCE_ADMISSION.json');parent=read(ROOT/'R2_CSV_COMPARISON_RECOVERY01_EXEC_RESERVATION.json')
 if hashes!=admission['source_hashes'] or parent['source_admission_sha256']!=sha(ROOT/'R2_CSV_COMPARISON_RECOVERY01_SOURCE_ADMISSION.json'):raise ValueError('Source admission/reservation changed')
 if read(ROOT/'BUDGET_LEDGER.json')['local_csv_comparison_recovery']['technical_recovery_used']!=1:raise ValueError('Budget must be reserved first')
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat('2026-10-02T11:42:38.303801+00:00'):raise ValueError('Window expired')
 out=Path(admission['output']);free=shutil.disk_usage(out.parent).free
 if free<23622320128:raise ValueError('E derived allowance plus margin gate failed')
 write(ROOT/'R2_CSV_COMPARISON_RECOVERY01_RESERVATION.json',dict(utc=now(),source_hashes=hashes,free_bytes=free,required_free_bytes=23622320128,next_check_automation='ito-r2-pro',next_check_minutes=5,automatic_retry_allowed=False,ODB_calls=0,NPZ_reads=0,science_audit_reruns=0))
 out.mkdir()
 write(out/'INPUT_IDENTITIES.json',dict(utc=now(),hashes=hashes,paths=admission['input_paths']))
 data={};audits={};context={}
 for c,root in [('R2',ROOT),('R1',BASE)]:
  audits[c]=read(paths[c+'_NATIVE_AND_PATH_AUDIT.json']);a=audits[c];e=a['energy']
  if a[c+'_scientific_gate'] is not False:raise ValueError('Expected retained scientific failure differs')
  context[c]={k:a.get(k) for k in ['case','status',c+'_scientific_gate','observed_mode','geometry_and_core_field_checks','valid_prefix_audit','frame_count','scientific_limits']}
  context[c]['energy_retained']={k:e.get(k) for k in ['Estar_N_mm','ratios_dimensionless','checks','missing_auxiliary_histories','precrack_engaged_KE_ratio_max','full_path_KE_ratio_max','two_end_BC_normalized_residual','region_energy_native']}
  context[c]['events_retained']={label:{k:v for k,v in event.items() if k!='points'} for label,event in a.get('events',{}).items()}
  data[c]={}
  for kind in ['HISTORY_CURVES','SPATIAL_PATH']:
   with paths[c+'_'+kind+'.csv'].open(encoding='utf-8-sig',newline='') as f:data[c][kind]=csvdata(f)
  s=data[c]['SPATIAL_PATH']
  if len(s['frame'])!=a['frame_count'] or not np.array_equal(s['frame'],np.arange(a['frame_count'])):raise ValueError('Closed CSV frame inventory differs')
 write(out/'RETAINED_CLOSED_AUDIT_CONTEXT.json',context)
 metrics=[];unavailable=[];grids={}
 for kind in ['HISTORY_CURVES','SPATIAL_PATH']:
  d2=data['R2'][kind];d1=data['R1'][kind];rule=common_strain_grid(d2['macro_strain'],d1['macro_strain']);g=np.array(rule['grid'])
  if not rule['available']:raise ValueError('No common measured strain')
  grids[kind]={k:v for k,v in rule.items() if k!='grid'};grids[kind]['rows']=len(g)
  b2=bracket(d2['macro_strain'],g);b1=bracket(d1['macro_strain'],g)
  cols={'actual_macro_strain':g};eligible=np.ones(len(g),dtype=bool)
  for c,d,b in [('R2',d2,b2),('R1',d1,b1)]:
   i,j,w=b
   for n,v in [('left_row',i),('right_row',j),('weight',w),('left_time_s',d['time_s'][i]),('right_time_s',d['time_s'][j])]:cols[c+'_'+n]=v
   eligible &= prefix(audits[c],d['time_s'][i]) & prefix(audits[c],d['time_s'][j])
  cols['within_both_geometry_core_prefixes']=eligible;cols['raw_diagnostic_only']=~eligible;cols['physical_path_qualified']=np.zeros(len(g),dtype=bool)
  spatial=['cumulative_cracked_reference_fraction','native_crack_observed_reference_fraction','deleted_reference_fraction','active_cracked_reference_fraction','min_active_Jacobian_mm2','overlap_area_mm2','ITO_active_max_principal_MPa','ITO_active_CKLE_max_abs']
  variables=sorted((set(d2)|set(d1))-{'time_s','macro_strain','raw_geometry_operation_error','frame'}) if kind=='HISTORY_CURVES' else spatial
  for var in variables:
   absent=[c for c,d in [('R2',d2),('R1',d1)] if var not in d]
   if absent:unavailable.append(dict(inventory=kind,variable=var,absent_cases=absent,availability='UNAVAILABLE_NOT_ZERO'));continue
   if not np.isfinite(d2[var]).all() or not np.isfinite(d1[var]).all():unavailable.append(dict(inventory=kind,variable=var,availability='NONFINITE_NATIVE_SCALAR_VALUES'));continue
   v2=values(d2[var],b2);v1=values(d1[var],b1);diff=v2-v1;peak=int(np.argmax(np.abs(diff)))
   cols['R2:'+var]=v2;cols['R1:'+var]=v1;cols['R2_minus_R1:'+var]=diff
   metrics.append(dict(inventory=kind,variable=var,common_rows=len(g),max_abs_difference=float(abs(diff[peak])),rms_difference=float(np.sqrt(np.mean(diff**2))),actual_strain_at_max=float(g[peak]),R2_signed_at_max=float(v2[peak]),R1_signed_at_max=float(v1[peak]),R2_minus_R1_signed_at_max=float(diff[peak]),physical_validation=False))
  save_table(out/('R2_R1_'+kind+'_SAME_ACTUAL_STRAIN.csv'),cols)
 save_table(out/'SCALAR_DIFFERENCE_SUMMARY.csv',{k:[m[k] for m in metrics] for k in metrics[0]})
 result=dict(status='CSV_COMPARISON_COMPLETED_SCIENTIFIC_FAILURE_RETAINED',utc=now(),scope='EXISTING_LOCAL_CSV_ONLY',common_grids=grids,metrics=metrics,unavailable=unavailable,missing_native_ALLDC={'R2':['global:ALLDC','ITO:ALLDC','PDMS:ALLDC'],'R1':['ITO:ALLDC']},science_gate={'R2':False,'R1':False},physical_path_qualified=False,geometry_prefix_is_not_energy_or_physics_qualification=True,spatial_field_maps='NOT_GENERATED_CSV_ONLY_SCOPE',ODB_calls=0,NPZ_reads=0,solver_calls=0,extraction_calls=0,transport_calls=0,science_audit_reruns=0,source_hashes_before=hashes)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 for filename,kind,variables,labels in [('FORCE_ENERGY_CSV.png','HISTORY_CURVES',['force_N_per_1mm_b','ALLAE','ALLVD','ALLKE'],['Signed force (N / 1 mm b)','Native ALLAE (N mm)','Native ALLVD (N mm)','Native ALLKE (N mm)']),('ITO_DAMAGE_CSV.png','SPATIAL_PATH',['cumulative_cracked_reference_fraction','deleted_reference_fraction','ITO_active_max_principal_MPa','ITO_active_CKLE_max_abs'],['Cumulative cracked reference fraction','Deleted reference fraction','Active ITO max principal stress (MPa)','Active ITO |CKLE| max'])]:
  fig,axs=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
  for ax,var,label in zip(axs.flat,variables,labels):
   for c,color in [('R1','#235789'),('R2','#c73e1d')]:
    d=data[c][kind];valid=prefix(audits[c],d['time_s']);ax.plot(100*d['macro_strain'][valid],d[var][valid],color=color,label=c,lw=1)
    if (~valid).any():ax.plot(100*d['macro_strain'][~valid],d[var][~valid],color=color,ls='--',label=c+' raw after invalidity')
   ax.set(xlabel='Native measured macrostrain (%)',ylabel=label);ax.grid(alpha=.25);ax.legend()
  fig.suptitle('Existing CSV diagnostic comparison; BOTH scientific gates FAIL',fontsize=12)
  fig.savefig(out/filename,dpi=180);plt.close(fig)
 result['source_hashes_after']={n:sha(p) for n,p in paths.items()}
 if result['source_hashes_after']!=hashes:raise ValueError('Input/source changed during local CSV recovery')
 write(out/'COMPARISON_RESULT.json',result)
 lines=['# R1/R2：已有本地 CSV 比较恢复报告','', '## 范围与结论','', '本次仅恢复本地 CSV 标量比较。原正常比较因文本列中的空字符串被转换为 float 而失败；原失败记录与源码保留。新入口保留 raw_geometry_operation_error 文本，缺失数值不补零。未重新求解、提取、运输、科学审计，未打开 ODB 或 NPZ。','', '**R1、R2 科学门均仍失败；本报告不构成物理路径验证、机制证明或收敛结论。**','', 'R2 原生 global/ITO/PDMS ALLDC 均缺失；R1 ITO ALLDC 缺失。缺失项保持 UNAVAILABLE_NOT_ZERO，不能把关闭控制推定成原生零值。','', '## 原闭合科学审计结论（原样保留，未重算）','', '| 指标（各自 E* 归一化） | R1 | R2 | 原阈值 |','|---|---:|---:|---:|']
 for k,limit in [('ALLAE','5%'),('ALLVD','5%'),('ETOTAL_drift','1%'),('boundary_work_vs_ALLWK','1%'),('ALLDC','5%')]:
  def ratio(c):
   v=audits[c]['energy']['ratios_dimensionless'].get(k);return '原生缺失' if v is None else ('%.9g%%'%(100*v))
  lines.append('| '+k+' | '+ratio('R1')+' | '+ratio('R2')+' | '+limit+' |')
 lines+=['', 'R1：ALLAE 和 ETOTAL 漂移超限。R2：ALLVD 和 ETOTAL 漂移超限，ALLDC 证据不完整。BC、功一致性及 precrack KE 的原判定保留。几何/核心字段有效前缀两案均至 frame 4000，first_invalid 为 null；这并不解除能量门失败。','', '## 比较规则与数据覆盖','', '实际应变取已有 CSV macro_strain；精确重复应变保留最后一行。使用两案共同区间内原应变值的并集；仅标量按原左右行线性插值。保留左右行号、原时间括号和权重，不外推、不平滑、不移动事件。差值为有符号 R2−R1，最大绝对差及 RMS 只描述共同原始标量路径，未设新力一致性门。原生图直接使用各案 CSV 行，未插值场。','']
 for kind in grids:lines.append('- '+kind+': '+str(grids[kind]['rows'])+' 共同应变行；范围 '+str(grids[kind]['common_range']))
 lines+=['','## 标量差异摘要','','| 量 | 最大绝对差 | RMS 差 | 最大差处实际应变 |','|---|---:|---:|---:|']
 for m in metrics:lines.append('| '+m['inventory']+'/'+m['variable']+' | %.9g | %.9g | %.9g |'%(m['max_abs_difference'],m['rms_difference'],m['actual_strain_at_max']))
 lines+=['', '完整逐应变记录见两个 SAME_ACTUAL_STRAIN.csv；单位沿用原 CSV，力 N/1mm b，能量 N mm，应力 MPa，面积/Jacobian mm²，比例与应变无量纲。各案能量以各自 E* 归一化，不把比值下降等同于绝对能量改善。','', '## 事件与图','', '原裂纹/删除事件括号保留于 RETAINED_CLOSED_AUDIT_CONTEXT.json，不从插值结果移动事件。FORCE_ENERGY_CSV.png 和 ITO_DAMAGE_CSV.png 使用真实已有 CSV，标题明确两案科学门失败。图像解码/查看回执由后续本地验收另行记录。','', '**四幅末帧空间场图/ITO 空间图未生成**：本次仅批准 CSV，CSV 不含完整 U/V/坐标场，不生成或推测空间图。','', '## 证据与复现','', 'INPUT_IDENTITIES.json 和 COMPARISON_RESULT.json 记录四份原 CSV、闭合审计、授权和源码的 SHA256，前后哈希一致。新一次恢复入口、预算及退出回执保存于原 metadata 根。原科学审计/失败记录未修改。本报告的科学内容输入仅为四份既有 CSV；闭合 JSON 仅提供保留的结论与前缀上下文。','', '没有新的科学算例、控制参数、材料或网格变更。完成本地比较不表示整个原计划的空间场比较已经完成。','']
 report='\n'.join(lines);textfile(out/'REPORT.md',report);textfile(out/'REPORT.txt',report)
 manifest={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.iterdir() if p.is_file()};write(out/'ARTIFACT_MANIFEST.json',manifest)
 write(ROOT/'R2_CSV_COMPARISON_RECOVERY01_COMPLETION_RECEIPT.json',dict(status=result['status'],utc=now(),output=str(out),result_sha256=sha(out/'COMPARISON_RESULT.json'),artifact_manifest_sha256=sha(out/'ARTIFACT_MANIFEST.json'),input_hashes_unchanged=True,ODB_calls=0,NPZ_reads=0,science_audit_reruns=0,actual_entry_calls=1,next_check_automation='ito-r2-pro',next_check_minutes=5,automatic_retry_allowed=False))
 print(json.dumps({'status':result['status'],'output':str(out),'metrics':len(metrics),'common_grids':grids},ensure_ascii=True))
if __name__=='__main__':
 if sys.argv[1:] == ['--prepare']:prepare()
 elif sys.argv[1:] == ['--run']:run()
 else:raise ValueError('Explicit --prepare or reserved --run required')
