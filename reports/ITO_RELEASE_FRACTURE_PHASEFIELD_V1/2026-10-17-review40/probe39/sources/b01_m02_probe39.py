"""Offline CPE4T probe predictions and observation-contract checks.

No solver, scheduler, ODB, network, or historical entry is callable here.
Floating tolerances belong to synthetic arithmetic tests only.
"""
from fractions import Fraction
import math
import re
import numpy as np

NODES = {101: (1, 2, 3, 4), 202: (11, 12, 13, 14)}


def _shape(r, s):
    return (np.array([(1-r)*(1-s),(1+r)*(1-s),(1+r)*(1+s),(1-r)*(1+s)])/4,
            np.array([[-(1-s),-(1-r)],[(1-s),-(1+r)],[(1+s),(1+r)],[-(1+s),(1-r)]])/4)


def operators(coordinates):
    x=np.asarray(coordinates,dtype=float)
    if x.shape!=(4,2) or not np.isfinite(x).all():raise ValueError('Q4_COORDINATES')
    corners=[(-1,-1),(1,-1),(1,1),(-1,1)]
    a=1/math.sqrt(3);points=[(-a,-a),(a,-a),(a,a),(-a,a)]
    corner_j=[]
    for r,s in corners:
        _,dn=_shape(r,s);j=float(np.linalg.det(x.T@dn))
        if not math.isfinite(j) or j<=0:raise ValueError('NONPOSITIVE_REFERENCE_MAP')
        corner_j.append(j)
    shapes=[];weights=[];grads=[];bs=[]
    for r,s in points:
        n,dn=_shape(r,s);jac=x.T@dn;j=float(np.linalg.det(jac))
        if j<=0 or not math.isfinite(j):raise ValueError('NONPOSITIVE_REFERENCE_MAP')
        g=dn@np.linalg.inv(jac);b=np.zeros((3,8))
        b[0,::2]=g[:,0];b[1,1::2]=g[:,1];b[2,::2]=g[:,1];b[2,1::2]=g[:,0]
        shapes.append(n);weights.append(j);grads.append(g);bs.append(b)
    weights=np.array(weights);grads=np.array(grads);shapes=np.array(shapes);bs=np.array(bs)
    area=float(weights.sum());k=np.einsum('qia,qja,q->ij',grads,grads,weights)
    trace=bs[:,0,:]+bs[:,1,:];mean=np.einsum('qi,q->i',trace,weights)/area
    bbar=bs.copy();bbar[:,0,:]+=(mean-trace)/2;bbar[:,1,:]+=(mean-trace)/2
    c=np.diag([100.,100.,50.]);free=float(sum(weights[q]*(bbar[q,:,4]@c@bbar[q,:,4]) for q in range(4)))
    if free<=0:raise ValueError('NO_POSITIVE_FREE_MECHANICAL_DOF')
    return dict(area=area,K=k,source_gauss=shapes.T*weights,source_corner=np.diag(corner_j),
                temperature_gauss=shapes,temperature_corner=np.eye(4),gauss_coordinates=shapes@x,
                corner_coordinates=x.copy(),free_u1_node3_stiffness=free,
                column_order='geometric CCW quadrature order; NOT native NPT identity')


def source_value(step,npt):
    if type(step) is not int or type(npt) is not int or not 1<=step<=8 or not 1<=npt<=4:raise ValueError('PROBE_STEP_OR_IP')
    return int(step<=4 and step==npt)


def temperatures(step):
    if type(step) is not int or not 1<=step<=8:raise ValueError('PROBE_STEP')
    value=np.ones(4)
    if step>=5:value[step-5]+=1
    return value


def print_interval(token):
    if not isinstance(token,str) or len(token)>80:raise ValueError('PRINT_TOKEN')
    m=re.fullmatch(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+))(?:[eEdD]([+-]?\d{1,4}))?',token.strip())
    if not m:raise ValueError('PRINT_TOKEN')
    exponent=int(m[2] or 0)
    if abs(exponent)>400:raise ValueError('PRINT_EXPONENT')
    digits=len(m[1].split('.')[1]) if '.' in m[1] else 0
    value=Fraction(m[1])*Fraction(10)**exponent
    half=Fraction(10)**(exponent-digits)/2
    return value-half,value+half


def _integer(value):
    if isinstance(value,bool):raise ValueError('IDENTITY_INTEGER')
    if isinstance(value,int):return value
    if isinstance(value,str) and re.fullmatch(r'\d+',value):return int(value)
    raise ValueError('IDENTITY_INTEGER')


def _accepted(accepted):
    if set(accepted)!=set(range(1,9)) or any(type(v) is not int or v<1 for v in accepted.values()):raise ValueError('ACCEPTED_STEP_SET')


def _snapshot_integer(value):
    if isinstance(value,int) or isinstance(value,str) and re.fullmatch(r'\d+',value):return _integer(value)
    lo,hi=print_interval(value)
    if math.ceil(lo)!=math.floor(hi):raise ValueError('AMBIGUOUS_SNAPSHOT_IDENTITY')
    return math.ceil(lo)


def validate_node_rows(rows,accepted):
    """Check explicitly transcribed/decoded table records; not a native DAT parser."""
    _accepted(accepted);seen={}
    for row in rows:
        try:
            s=_integer(row['step']);inc=_integer(row['increment']);e=_integer(row['element']);n=_integer(row['node'])
            if row['accepted'] is not True or s not in accepted or inc!=accepted[s] or e not in NODES or n not in NODES[e]:raise ValueError('ROW_IDENTITY')
            key=(s,e,n)
            if key in seen:raise ValueError('DUPLICATE_ROW')
            lo,hi=print_interval(row['NT']);expected=1+int(s==NODES[e].index(n)+5)
            if not lo<=expected<=hi:raise ValueError('TEMPERATURE_BOUNDARY_MISMATCH')
            print_interval(row['RFL']);seen[key]=row['RFL']
        except (KeyError,TypeError) as ex:raise ValueError('MISSING_ROW_FIELD') from ex
    required={(s,e,n) for s in range(1,9) for e,ns in NODES.items() for n in ns}
    if set(seen)!=required:raise ValueError('INCOMPLETE_NODE_TABLE')
    result={'sign_convention_qualified':False,'unit':'native artificial thermal reaction; no fitted scaling'}
    for e,ns in NODES.items():
        result[str(e)]={'source_RFL_tokens':[[seen[s,e,n] for s in range(1,5)] for n in ns],
                        'temperature_RFL_tokens':[[seen[s,e,n] for s in range(5,9)] for n in ns]}
    return result


def validate_snapshots(rows,accepted):
    """Validate accepted STATEV snapshot identity, not all calls or trial rollback."""
    _accepted(accepted);seen=set()
    for row in rows:
        try:
            s=_integer(row['step']);i=_integer(row['increment']);e=_snapshot_integer(row['element']);p=_snapshot_integer(row['npt'])
            if row['accepted'] is not True or s not in accepted or i!=accepted[s] or e not in NODES or not 1<=p<=4 or _snapshot_integer(row['schema'])!=39:raise ValueError('SNAPSHOT_IDENTITY')
            key=s,e,p
            if key in seen:raise ValueError('DUPLICATE_SNAPSHOT')
            t=print_interval(row['TEMP']);dt=print_interval(row['DTEMP']);phi=print_interval(row['phi'])
            if phi[1]<t[0]+dt[0] or phi[0]>t[1]+dt[1]:raise ValueError('PHI_CALLBACK_IDENTITY')
            r=print_interval(row['RPL']);v=source_value(s,p)
            if not r[0]<=v<=r[1]:raise ValueError('RPL_BASIS')
            end=print_interval(row['end_step_time'])
            if not end[0]<=1<=end[1]:raise ValueError('NOT_FINAL_STEP_STATE')
            print_interval(row['x']);print_interval(row['y']);seen.add(key)
        except (KeyError,TypeError) as ex:raise ValueError('MISSING_SNAPSHOT_FIELD') from ex
    if seen!={(s,e,p) for s in range(1,9) for e in NODES for p in range(1,5)}:raise ValueError('INCOMPLETE_SNAPSHOTS')
    return dict(snapshot_count=len(seen),all_trial_history_observed=False,native_matrix_qualified=False)
