"""Static R2 readiness only. No native launch or ODB access."""
import datetime, hashlib, json, re
from pathlib import Path

PACKAGE='ITO_PDMS_DISTORTION_CONTROL_DIAGNOSTIC_V1'
DECISION='ITOL01-PRO-R2-VERSION-EVIDENCE-ACCESS-DISPOSITION-20261001-01'
BULK=Path(r'E:\open\ITO-LOCAL-01\ITO_PDMS_DISTORTION_CONTROL_DIAGNOSTIC_V1')
MARKER=b'** NOT_RELEASED_FOR_NATIVE_EXECUTION; VERSION_SEMANTICS_PENDING\r\n'
CONTROL=b'*SECTION CONTROLS, NAME=R2_PDMS_DC_OFF, DISTORTION CONTROL=NO\r\n'
ASSOCIATION=b', CONTROLS=R2_PDMS_DC_OFF'

def section_lines(data, elset):
    return [line for line in data.splitlines(keepends=True) if line.lower().startswith(b'*solid section,') and re.search(rb'\belset\s*=\s*'+elset+rb'(?:\s*[,\r\n]|\s*$)',line,re.I)]

def make_candidate(original):
    keys=[line.lower().strip() for line in original.splitlines() if line.startswith(b'*') and not line.startswith(b'**')]
    if any(line.startswith((b'*section controls',b'*adaptive mesh',b'*hourglass stiffness')) for line in keys):
        raise ValueError('Unexpected existing control or adaptive mesh exception')
    sections=section_lines(original,b'PDMS')
    if len(sections)!=1 or b'controls=' in sections[0].lower().replace(b' ',b''):
        raise ValueError('PDMS section must be unique and unbound')
    if len(section_lines(original,b'ITO'))!=1:raise ValueError('ITO section identity missing or duplicate')
    steps=[line for line in original.splitlines(keepends=True) if line.lower().startswith(b'*step,')]
    if len(steps)!=1:raise ValueError('Expected sole native TENSION step')
    line=sections[0]; ending=b'\r\n' if line.endswith(b'\r\n') else b'\n'
    changed=line[:-len(ending)]+ASSOCIATION+ending
    result=original.replace(line,changed,1).replace(steps[0],CONTROL+steps[0],1)
    return MARKER+result

def audit_candidate(original,candidate):
    expected=make_candidate(original)
    if candidate!=expected:raise ValueError('Candidate has changes outside the exact approved difference')
    if section_lines(original,b'ITO')!=section_lines(candidate,b'ITO'):raise ValueError('ITO keyword changed')
    restored=candidate[len(MARKER):].replace(CONTROL,b'',1).replace(ASSOCIATION,b'',1)
    if restored!=original:raise ValueError('Unrelated source bytes changed')
    return {'status':'STATIC_MINIMAL_DIFFERENCE_PASS_NOT_NATIVE_RELEASE','all_other_bytes_identical':True,'ITO_section_bytes_identical':True,'PDMS_only_control_association':True,'native_execution_released':False,'effective_2021_default_semantics':'UNRESOLVED','HOURGLASS_explicit_change':False,'adaptive_mesh_present':False,'baseline_sha256':hashlib.sha256(original).hexdigest(),'candidate_sha256':hashlib.sha256(candidate).hexdigest(),'allowed_changes':['one PDMS CONTROLS association','one DISTORTION CONTROL=NO definition','nonsemantic NOT_RELEASED comment']}

def make_binding(metadata):
    a=BULK/'cases'/'R2'/'extract_attempt01'
    p=dict(parts=a/'transport'/'parts',archive=a/'transport'/'export.tar',export=a/'export_R2',derived=a/'derived',figures=a/'figures',tmp=a/'tmp')
    return {'version':1,'package_id':PACKAGE,'decision_id':DECISION,'case':'R2','attempt_id':'extract_attempt01','metadata_root':str(Path(metadata).resolve()),'bulk_root':str(BULK),'paths':{k:str(v) for k,v in p.items()},'actual_archive_bytes':None,'actual_archive_sha256':None,'actual_source_ODB_sha256':None,'required_free_bytes_by_stage':{'copy':None,'assemble':None,'extract':None,'analysis':None},'space_gate_status':'MUST_COMPUTE_FROM_R2_ACTUAL_MANIFEST_BEFORE_TRANSPORT','derived_allowance_bytes':2*1024**3,'minimum_margin_bytes':20*1024**3,'native_execution_released':False}

def validate_binding(binding,metadata):
    expected=make_binding(metadata)
    for key in ['version','package_id','decision_id','case','attempt_id','metadata_root','bulk_root']:
        if binding.get(key)!=expected[key]:raise ValueError('R2 storage identity mismatch: '+key)
    result={}
    for key,want in expected['paths'].items():
        path=Path(binding.get('paths',{}).get(key,''))
        if str(path)!=want or '..' in path.parts:raise ValueError('R2 path mismatch: '+key)
        for ancestor in [path]+list(path.parents):
            if ancestor.exists() and (ancestor.is_symlink() or ancestor.is_junction()):raise ValueError('Storage reparse target refused')
        result[key]=path
    return result

def prepare(root,baseline):
    root=Path(root);baseline=Path(baseline)
    original=(baseline/'ITOL01_PDR1_V1.inp').read_bytes()
    if hashlib.sha256(original).hexdigest()!='8e8405152be773653f956df64fafe06d80ba7b9c5b75fe83ec7e2c719215fdf3':raise ValueError('Frozen baseline input changed')
    candidate=make_candidate(original);audit=audit_candidate(original,candidate)
    binding=make_binding(root);validate_binding(binding,root)
    with (root/'ITOL01_PDR2_V1_NOT_RELEASED.inp').open('xb') as f:f.write(candidate)
    records={'R2_CANDIDATE_INPUT_AUDIT.json':audit,'R2_LOCAL_STORAGE_BINDING.json':binding}
    records['BUDGET_LEDGER.json']={'package_id':PACKAGE,'decision_id':'ITOL01-PRO-R2-DISTORTION-DIAGNOSTIC-20261001-01','status':'STATIC_ONLY_NOT_RELEASED_VERSION_PENDING','datacheck':{'normal_max':1,'normal_used':0,'technical_recovery_max':1,'technical_recovery_used':0},'analysis':{'normal_max':1,'normal_used':0,'started_solver_reruns_max':0,'started_solver_reruns_used':0},'new_ODB_extraction':{'normal_max':1,'normal_used':0,'technical_recovery_max':1,'technical_recovery_used':0},'additional_cases':0,'old_ODB_opens':0,'old_budget_transfer':0,'attempt_events':[]}
    for name,obj in records.items():
        with (root/name).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)
    return audit

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);args=p.parse_args()
    print(json.dumps(prepare(Path(__file__).parent,args.baseline)))
