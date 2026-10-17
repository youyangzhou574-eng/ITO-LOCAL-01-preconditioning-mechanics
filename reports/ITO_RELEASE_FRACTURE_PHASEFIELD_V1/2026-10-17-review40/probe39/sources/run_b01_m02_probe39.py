"""Build an offline review package only. No native dispatch exists in39."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import numpy as np
import b01_m02_probe39 as core

BASE=Path(__file__).resolve().parents[2]
OWNER='01a0d157-8547-7552-bb05-9a1c1c92698d'
INPUT_SHA='91b5fd771d9c9b7ea53147154a9d9c3161df647404933f3726da614a287d190e'
SOURCE_PATHS={'core':BASE/'src/python/b01_m02_probe39.py',
              'builder':Path(__file__).resolve(),
              'fortran':BASE/'src/fortran/b01_interface_probe39.for',
              'test_core':BASE/'tests/test_b01_m02_probe39.py',
              'test_builder':BASE/'tests/test_run_b01_m02_probe39.py'}
SOURCE_ROLES=tuple(SOURCE_PATHS)


def _geometry(g):
    if g.get('original_element')!=5817 or g.get('original_node_labels')!=[5907,5903,5902,5908] or g.get('source',{}).get('sha256')!=INPUT_SHA:raise ValueError('GEOMETRY_PROVENANCE')
    xy=np.asarray(g.get('coordinates_mm'),dtype=float);core.operators(xy)
    return {101:np.array([[0.,0.],[1.,0.],[1.,1.],[0.,1.]]),202:xy}


def render_deck(g):
    geoms=_geometry(g)
    lines=['*Heading','PROBE39 manufactured CPE4T interface observation; NOT a PF-CZM repair',
           '** OFFLINE ONLY: diagnostic purpose and budget not authorized','*Node']
    for e,xy in geoms.items():
        for n,(x,y) in zip(core.NODES[e],xy):lines.append('%d, %.17g, %.17g'%(n,x,y))
    lines+=['*Element, type=CPE4T, elset=EALL','101, 1, 2, 3, 4','202, 11, 12, 13, 14',
            '*Nset, nset=NALL','1, 2, 3, 4, 11, 12, 13, 14',
            '*Solid Section, elset=EALL, material=PROBE39','1.',
            '*Material, name=PROBE39','*Conductivity','1.','*Depvar','16',
            '*User Material, constants=2','100., 0.',
            '*Initial Conditions, type=TEMPERATURE','NALL, 1.']
    for step in range(1,9):
        lines+=['*Step, name=%s%d, nlgeom=NO, extrapolation=NO, inc=20, unsymm=NO'%('S' if step<=4 else 'T',step if step<=4 else step-4),
                '*Coupled Temperature-displacement, creep=NONE, steady state','1., 1., 1.e-6, 1.',
                '*Solution Technique, type=SEPARATED','*Boundary, op=NEW']
        for ns in core.NODES.values():
            for i,n in enumerate(ns):lines.append('%d, %d, 2, 0.'%(n,2 if i==2 else 1))
            for n,t in zip(ns,core.temperatures(step)):lines.append('%d, 11, 11, %.1f'%(n,t))
        lines+=['*Node Print, nset=NALL, frequency=1, summary=NO, totals=NO, global=YES','NT, RFL',
                '*El Print, elset=EALL, position=INTEGRATION POINTS, frequency=1, summary=NO',
                'SDV1, SDV2, SDV3, SDV4, SDV5, SDV6, SDV7, SDV8',
                'SDV1, SDV9, SDV10, SDV11, SDV12, SDV13, SDV14, SDV15, SDV16',
                '*Output, field, frequency=0','*Output, history, frequency=0',
                '*Restart, write, frequency=0','*End Step']
    return '\n'.join(lines)+'\n'


def _meta(p,b=None):
    if b is None:b=Path(p).read_bytes()
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


def _within(p,root):
    p=Path(p).resolve();root=Path(root).resolve()
    if not p.is_relative_to(root):raise ValueError('PATH_OUTSIDE_OFFLINE_ROOT')
    return p


def _read_ref(ref,root):
    p=_within(ref['path'],root);b=p.read_bytes()
    if len(b)!=ref['bytes'] or hashlib.sha256(b).hexdigest()!=ref['sha256']:raise ValueError('HASH_OR_SIZE')
    return b


def write_exclusive(path,data):
    with Path(path).open('xb') as f:f.write(data)


def _json(a):return (json.dumps(a,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')


def build_package(root,out,closure_path,admission_path):
    root=_within(root,BASE);out=_within(out,root)
    if out==root:raise ValueError('OUTPUT_MUST_BE_CHILD')
    if out.exists():raise FileExistsError('OFFLINE_ENTRY_ALREADY_EXISTS')
    cb=_within(closure_path,root).read_bytes();c=json.loads(cb)
    a=json.loads(_within(admission_path,root).read_bytes())
    if c.get('owner_thread')!=OWNER or a.get('offline_build_pass') is not True or a.get('native_pass') is not False or a.get('closure_sha256')!=hashlib.sha256(cb).hexdigest():raise ValueError('OFFLINE_ADMISSION')
    src=c['source_files']
    if set(src)!=set(SOURCE_ROLES):raise ValueError('SOURCE_SET')
    buffers={role:_read_ref(ref,root) for role,ref in src.items()}
    for role,buf in buffers.items():
        if hashlib.sha256(buf).hexdigest()!=hashlib.sha256(SOURCE_PATHS[role].read_bytes()).hexdigest():raise ValueError('EXECUTING_SOURCE_BINDING')
    for key in ['review','final_tests']:
        evidence=json.loads(_read_ref(a[key],root))
        if evidence.get('pass') is not True or evidence.get('source_files')!=src:raise ValueError('FINAL_'+key.upper()+'_BINDING')
        if not isinstance(c.get('geometry'),dict) or evidence.get('geometry')!=c['geometry']:raise ValueError('FINAL_'+key.upper()+'_GEOMETRY_BINDING')
    gb=_read_ref(c['geometry'],root);g=json.loads(gb);geoms=_geometry(g)
    deck=render_deck(g).encode('ascii');fortran=buffers['fortran'];fortran.decode('ascii')
    expected={'native_matrix_qualified':False,'source_column_sign':'raw RFL retained; sign convention not qualified',
              'point_order':'geometric CCW candidates only; no native NPT assignment','baseline_temperature':1,
              'native_compilation':'NOT_RUN','native_output_syntax':'DATACHECK_PENDING'}
    for e,xy in geoms.items():expected[str(e)]={k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in core.operators(xy).items()}
    out.mkdir()  # exclusive once boundary, including orphan/failed/partial directories
    try:
        write_exclusive(out/'INTENT39.json',_json(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),kind='OFFLINE_ONLY',closure_sha256=hashlib.sha256(cb).hexdigest(),native_admitted=False)))
        write_exclusive(out/'PROBE39.inp',deck);write_exclusive(out/'PROBE39_umat.for',fortran)
        write_exclusive(out/'EXPECTED39.json',_json(expected));write_exclusive(out/'GEOMETRY39.json',gb)
        write_exclusive(out/'SOURCE_CLOSURE39.json',cb);write_exclusive(out/'SOURCE_ADMISSION39.json',_json(a))
        (out/'sources').mkdir()
        for role,buf in buffers.items():write_exclusive(out/'sources'/SOURCE_PATHS[role].name,buf)
        files=[_meta(p) for p in sorted(out.rglob('*')) if p.is_file()]
        completion=dict(state='OFFLINE_BUILD_CLOSED_ONCE',native_admitted=False,compile_run=False,datacheck_run=False,
                        analysis_run=False,ODB_opened=False,scientific_pass=False,valid_prefix=None,files=files)
        write_exclusive(out/'COMPLETION39.json',_json(completion))
        if json.loads((out/'COMPLETION39.json').read_bytes())!=completion:raise ValueError('COMPLETION_READBACK')
        return completion
    except Exception as ex:
        write_exclusive(out/'FAILED_CLOSED39.json',_json(dict(state='OFFLINE_BUILD_FAILED_CLOSED',error_type=type(ex).__name__,error=str(ex))))
        raise


def main():
    ap=argparse.ArgumentParser(description='Offline39 package build only; no native actions implemented.')
    ap.add_argument('--build',action='store_true');args=ap.parse_args()
    if not args.build:ap.error('--build required')
    s=json.loads((BASE/'CONTINUATION.json').read_bytes());b=json.loads((BASE/'BUDGET_LEDGER.json').read_bytes())
    if s.get('owner_thread')!=OWNER or s.get('pause') or s.get('phase')!='P1_B01_M02_INTERFACE_PROBE_OFFLINE_DESIGN39' or any(s.get(k) is not None for k in ['active_attempt','native_job_id','readonly_job_id']):raise ValueError('CURRENT_OFFLINE_STATE')
    if b['analysis']!={'limit':32,'used':7,'P1_limit':8,'P2_limit':12,'P3_P4_limit':12,'P1_used':7} or b['unknown_submissions']:raise ValueError('FROZEN_BUDGET_STATE')
    parent=BASE/'cases/B01_interface_probe';parent.mkdir(exist_ok=True)
    r=build_package(BASE,parent/'B01_P39',BASE/'evidence/B01_M02_PROBE_SOURCE_CLOSURE39.json',BASE/'evidence/B01_M02_PROBE_SOURCE_ADMISSION39.json')
    print(json.dumps(dict(state=r['state'],native_admitted=False,files=len(r['files'])),ensure_ascii=True))


if __name__=='__main__':main()
