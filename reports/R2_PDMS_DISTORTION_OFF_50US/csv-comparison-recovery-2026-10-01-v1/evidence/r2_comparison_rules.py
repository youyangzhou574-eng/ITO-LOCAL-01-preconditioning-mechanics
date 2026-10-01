"""R2/R1 same measured-strain scalar comparison and native-frame selection.

No case data is opened here. Exact duplicate strains keep LAST. Only scalar
quantities may be interpolated between two actual rows; U/V fields must be
loaded separately at native frames. Missing diagnostic coverage stays missing.
Prefix indices refer to rows of the supplied scalar axis, NOT an unrelated
history/field index. Callers must map audited frame/time prefixes explicitly.
Geometry/core prefix membership never implies global energy quality or physics.
"""
import numpy as np


def _axis(values):
    a=np.asarray(values,dtype=float)
    if a.ndim!=1 or not np.all(np.isfinite(a)) or np.any(np.diff(a)<0):
        raise ValueError('Nonfinite/decreasing measured strain axis')
    return a


def _last_unique(a):
    if not len(a):return np.array([],dtype=int)
    _,rev=np.unique(a[::-1],return_index=True)
    return np.sort(len(a)-1-rev)


def native_bracket(axis,target):
    a=_axis(axis);keep=_last_unique(a);u=a[keep]
    if not len(u) or not np.isfinite(target) or target<u[0] or target>u[-1]:
        raise ValueError('No extrapolation or fabricated native coverage')
    j=int(np.searchsorted(u,target));i=j if u[j]==target else j-1
    return dict(left_index=int(keep[i]),right_index=int(keep[j]),
        weight=0. if i==j else float((target-u[i])/(u[j]-u[i])))


def common_strain_grid(R2_axis,R1_axis):
    a=_axis(R2_axis);b=_axis(R1_axis)
    result=dict(available=False,grid=[],common_range=None,finite_strain_interval=False,
        exact_duplicates='LAST',extrapolation=False,smoothing=False,event_shift=False)
    if not len(a) or not len(b):
        result['unavailable_reason']='NO_NATIVE_MEASURED_STRAIN_ROWS';return result
    lo=max(float(a[0]),float(b[0]));hi=min(float(a[-1]),float(b[-1]))
    if lo>hi:
        result['unavailable_reason']='NO_COMMON_MEASURED_STRAIN';return result
    grid=np.unique(np.r_[a[(a>=lo)&(a<=hi)],b[(b>=lo)&(b<=hi)],lo,hi])
    result.update(available=True,grid=grid.tolist(),common_range=[lo,hi],
        finite_strain_interval=hi>lo,unavailable_reason=None)
    return result


def _prefix_index(value,length):
    if value is None:return
    if isinstance(value,bool) or not isinstance(value,(int,np.integer)) or not 0<=value<length:
        raise ValueError('Prefix first-invalid index must identify an actual supplied row')


def compare_scalar(R2_axis,R2_values,R1_axis,R1_values,
                   R2_first_invalid=None,R1_first_invalid=None):
    """Unnormalized signed scalar differences; no new force agreement gate.

Prefix arguments only apply when scalar rows and audited prefix rows are the
same inventory. Histories with different sampling require their own explicit
time/strain mapping by the comparator, never direct use of field indices.
"""
    a=_axis(R2_axis);b=_axis(R1_axis)
    av=np.asarray(R2_values,dtype=float);bv=np.asarray(R1_values,dtype=float)
    if av.shape!=a.shape or bv.shape!=b.shape:
        raise ValueError('Scalar/native strain row shape differs; no vector field interpolation')
    _prefix_index(R2_first_invalid,len(a));_prefix_index(R1_first_invalid,len(b))
    result=common_strain_grid(a,b)
    result.update(rows=[],max_abs_difference=None,rms_difference=None,
        scientific_validation_claim=False,force_acceptance_threshold=None,
        U_V_field_interpolation=False,global_energy_quality_inferred=False,
        prefix_scope='SUPPLIED_SCALAR_ROW_GEOMETRY_CORE_ONLY')
    if not result['available']:return result
    if not np.all(np.isfinite(av)) or not np.all(np.isfinite(bv)):
        result.update(available=False,unavailable_reason='NONFINITE_NATIVE_SCALAR_VALUES')
        return result
    for eps in result['grid']:
        ra=native_bracket(a,eps);rb=native_bracket(b,eps)
        def scalar(v,r):
            return float((1-r['weight'])*v[r['left_index']]+r['weight']*v[r['right_index']])
        va=scalar(av,ra);vb=scalar(bv,rb)
        eligible=((R2_first_invalid is None or ra['right_index']<R2_first_invalid)
                  and (R1_first_invalid is None or rb['right_index']<R1_first_invalid))
        result['rows'].append(dict(measured_macrostrain=eps,R2_bracket=ra,R1_bracket=rb,
            R2_value=va,R1_value=vb,difference_R2_minus_R1=va-vb,
            within_both_geometry_core_prefixes=eligible,raw_diagnostic_only=not eligible))
    diffs=np.array([r['difference_R2_minus_R1'] for r in result['rows']])
    result['max_abs_difference']=float(np.max(np.abs(diffs)))
    result['rms_difference']=float(np.sqrt(np.mean(diffs**2)))
    result['difference_summary_scope']='ALL_COMMON_RAW_SCALAR_ROWS_NOT_A_PHYSICAL_VALIDATION'
    return result


def select_native_frames(times,events,history_times,first_invalid=None):
    """Select actual endpoints, event brackets and actual quality-peak brackets.

Unavailable history times or times outside actual diagnostic coverage produce
an explicit missing selection. No extrapolation or substituted final time.
"""
    t=np.asarray(times,dtype=float)
    if t.ndim!=1 or not len(t) or not np.all(np.isfinite(t)) or np.any(np.diff(t)<=0):
        raise ValueError('Actual native frame time inventory invalid')
    _prefix_index(first_invalid,len(t))
    reasons={};missing={}
    def add(i,reason):
        _prefix_index(i,len(t));reasons.setdefault(int(i),[])
        if reason not in reasons[int(i)]:reasons[int(i)].append(reason)
    add(0,'FIRST_ACTUAL_FRAME');add(len(t)-1,'LAST_ACTUAL_FRAME')
    for label,event in events.items():
        for name in ('low_frame','high_frame'):
            idx=event.get(name)
            if idx is not None:add(idx,label)
    if first_invalid is not None:
        add(first_invalid,'FIRST_GEOMETRY_CORE_INVALID')
        if first_invalid>0:add(first_invalid-1,'LAST_GEOMETRY_CORE_VALID')
    for label,value in history_times.items():
        if value is None:
            missing[label]='NATIVE_HISTORY_TIME_UNAVAILABLE';continue
        if not np.isfinite(value):raise ValueError('Nonfinite native history selection time')
        if value<t[0] or value>t[-1]:
            missing[label]='OUTSIDE_ACTUAL_NATIVE_FRAME_COVERAGE';continue
        j=int(np.searchsorted(t,value))
        # Preserve the original R1 selection: at an exact saved-frame event,
        # retain previous/exact/next actual frames; otherwise the two brackets.
        indices=range(max(0,j-1),min(len(t),j+2)) if t[j]==value else (j-1,j)
        for i in indices:add(i,label)
    return dict(frames=sorted(reasons),reasons=reasons,unavailable_selections=missing,
        U_V_field_interpolation=False,extrapolation=False,scientific_validation_claim=False)
