"""Offline witnesses only: no solver, ODB API, filesystem writes, or network.

Python 3.10+ standard library. These functions do not certify an FE solution.
Tensor labels/bases, native accepted rows, branches and node order are inputs
whose provenance must be established independently. See references/odb-and-evidence.md.
"""
import bisect
from decimal import Decimal, InvalidOperation
import itertools
import math
import struct


def _finite(value, name):
    if isinstance(value, bool):
        raise ValueError(name + ' must be a finite number, not bool')
    try:
        v = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name + ' must be a finite number') from exc
    if not math.isfinite(v):
        raise ValueError(name + ' must be finite')
    return v


def select_components(labels, values, requested):
    """Exact labels; never assume the third tensor column is shear 12."""
    labels, values, requested = list(labels), list(values), list(requested)
    if len(labels) != len(values) or len(set(labels)) != len(labels):
        raise ValueError('Component shape mismatch or duplicate labels')
    if not requested or len(set(requested)) != len(requested):
        raise ValueError('Requested labels must be nonempty and unique')
    data = dict(zip(labels, (_finite(v, 'component') for v in values)))
    missing = [key for key in requested if key not in data]
    if missing:
        raise ValueError('Missing components; do not zero-fill: ' + repr(missing))
    return tuple(data[key] for key in requested)


def _half_ulp32(value):
    """Representation allowance, NOT proof of the actual ODB storage dtype."""
    try:
        b = struct.pack('!f', abs(value))
    except (OverflowError, struct.error) as exc:
        raise ValueError('Time outside supported binary32 range') from exc
    bits = struct.unpack('!I', b)[0]
    if bits >= 0x7f7fffff:
        raise ValueError('Time outside supported binary32 range')
    q = struct.unpack('!f', b)[0]
    next_q = struct.unpack('!f', struct.pack('!I', bits + 1))[0]
    return (next_q - q) / 2.


def match_frame_to_sta(frame, accepted_rows):
    """Match a saved frame to already-parsed accepted STA rows.

    Required frame keys: job, step, increment, time_basis, time_s.
    Required row keys: same identity, accepted (literal bool), time_token
    (the untouched printed decimal token). Does NOT parse an arbitrary STA.
    Half the printed decimal quantum plus a binary32 representation allowance
    is used only AFTER exact native identity matches. No physical gate changes.
    """
    keys = ('job', 'step', 'increment', 'time_basis')
    if any(key not in frame for key in keys):
        raise ValueError('Missing frame identity')
    if type(frame['increment']) is not int or frame['increment'] < 0:
        raise ValueError('Invalid native increment')
    if frame['time_basis'] not in ('step', 'total'):
        raise ValueError('Specify step or total time')
    observed = _finite(frame['time_s'], 'native time')
    if observed < 0:
        raise ValueError('Negative native time')
    base = {'matched': None, 'status': 'ACCEPTANCE_UNRESOLVED',
            'time_storage_type': 'NOT_INFERRED'}
    if frame['increment'] == 0:
        return dict(base, status='INITIAL_FRAME_NEEDS_STEP_START_PROOF')
    rows = [r for r in accepted_rows if r.get('accepted') is True
            and all(r.get(k) == frame[k] for k in keys)]
    if not rows:
        return base
    tokens = {r.get('time_token') for r in rows}
    if len(tokens) != 1:
        return dict(base, status='AMBIGUOUS_ACCEPTANCE')
    token = tokens.pop()
    if not isinstance(token, str):
        raise ValueError('Preserve original printed time token, not float(token)')
    try:
        decimal = Decimal(token.replace('D', 'E').replace('d', 'e'))
    except InvalidOperation as exc:
        raise ValueError('Invalid printed time token') from exc
    if not decimal.is_finite() or decimal < 0:
        raise ValueError('Invalid printed time')
    expected = _finite(decimal, 'printed time')
    quantum = _finite(Decimal(1).scaleb(decimal.as_tuple().exponent), 'printed quantum')
    limit = .5 * quantum + _half_ulp32(observed) + 8 * max(math.ulp(observed), math.ulp(expected))
    delta = abs(observed - expected)
    matched = delta <= limit
    return dict(base, matched=matched,
                status='ACCEPTED_IDENTITY_TIME_COMPATIBLE' if matched else 'TIME_INCONSISTENT',
                observed_s=observed, printed_token=token,
                absolute_difference_s=delta, representation_bound_s=limit,
                duplicate_identical_rows=len(rows))


def branch_curve(samples, branch, direction):
    """Exact duplicate strain -> LAST sample within ONE chronological branch.

    No near-duplicate clustering, sorting over reversals, or branch merging.
    Returned strain axis is increasing, even for a decreasing native branch.
    """
    if direction not in (-1, 1):
        raise ValueError('direction must be +1 or -1')
    records, previous = [], None
    for s in samples:
        if s.get('branch') != branch:
            continue
        i = s.get('native_index')
        if type(i) is not int or i < 0:
            raise ValueError('native_index must be a nonnegative integer')
        current = {'branch': branch, 'native_index': i,
                   'strain': _finite(s['strain'], 'strain'),
                   'value': _finite(s['value'], 'value')}
        if previous is not None:
            if i <= previous['native_index']:
                raise ValueError('Native samples must retain chronological identity')
            if direction * (current['strain'] - previous['strain']) < 0:
                raise ValueError('Branch reverses; split at the physical reversal')
        if records and current['strain'] == records[-1]['strain']:
            records[-1] = current
        else:
            records.append(current)
        previous = current
    if not records:
        raise ValueError('Requested branch absent')
    return records if direction == 1 else records[::-1]


def interpolate_bounded(curve, target):
    """Scalar interpolation only, with native indices; never nodal FE fields."""
    x = [_finite(r['strain'], 'strain') for r in curve]
    target = _finite(target, 'target strain')
    if not x or any(b <= a for a, b in zip(x, x[1:])):
        raise ValueError('Expected strictly increasing unique scalar axis')
    if target < x[0] or target > x[-1]:
        raise ValueError('Outside observed coverage; extrapolation forbidden')
    j = bisect.bisect_left(x, target)
    if x[j] == target:
        value = _finite(curve[j]['value'], 'value')
        return {'value': value, 'native_indices': [curve[j]['native_index']]*2,
                'weight_right': 0., 'method': 'EXACT_NATIVE_SCALAR'}
    left, right = curve[j-1], curve[j]
    weight = (target-x[j-1])/(x[j]-x[j-1])
    a, b = _finite(left['value'], 'value'), _finite(right['value'], 'value')
    return {'value': a+(b-a)*weight,
            'native_indices': [left['native_index'], right['native_index']],
            'weight_right': weight, 'method': 'BOUNDED_SCALAR_INTERPOLATION'}


def valid_prefix(flags):
    """Unknown breaks a proven prefix; later True never repairs earlier failure."""
    flags = list(flags)
    if any(v is not None and type(v) is not bool for v in flags):
        raise ValueError('Use literal True, False or None')
    first_unproven = next((i for i, v in enumerate(flags) if v is not True), None)
    first_invalid = next((i for i, v in enumerate(flags) if v is False), None)
    last = len(flags)-1 if first_unproven is None else first_unproven-1
    return {'last_proven_valid_index': last if last >= 0 else None,
            'first_unproven_index': first_unproven,
            'first_observed_invalid_index': first_invalid,
            'coverage_count': len(flags)}


def at2_homogeneous(history, gc, ell, kappa):
    """1D homogeneous diagnostic of the PLAN'S NORMALIZED g, not a solver.

    g=(1-kappa)*(1-d)^2+kappa, psi_plus/history per reference volume.
    No gradient term in this homogeneous witness; no shell strength calibration.
    It checks the local stationary equation, not full-field irreversibility.
    """
    history, gc, ell, kappa = [_finite(v, n) for v,n in
                             zip((history,gc,ell,kappa), ('H','Gc','ell','kappa'))]
    if history < 0 or gc <= 0 or ell <= 0 or not 0 <= kappa < 1:
        raise ValueError('Require H>=0, Gc>0, ell>0, 0<=kappa<1')
    drive = 2*(1-kappa)*history
    d = drive/(gc/ell+drive)
    return {'d': d, 'g': (1-kappa)*(1-d)**2+kappa,
            'fracture_density': gc*d*d/(2*ell)}


def ideal_free_misfit(prestrain):
    """Bare incompressible substrate geometry ONLY; NOT imposed ITO strain."""
    p = _finite(prestrain, 'prestrain')
    if p < 0:
        raise ValueError('This witness assumes a nonnegative tensile prestrain')
    return (-p/(1+p), math.sqrt(1+p)-1)


def _det3(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def hex8_mapping_dets(nodes):
    """Standard trilinear HEX8 geometry probes, signed detJ in length^3.

    Eight +/-1/sqrt(3) probes, center, eight corners, in that order.
    These are NOT claimed to be the native integration rule of C3D8RH or UEL.
    Not an EAS/ANS constitutive F calculator or an overlap certificate.
    """
    if len(nodes) != 8 or any(len(n) != 3 for n in nodes):
        raise ValueError('Expected eight native HEX8 nodes in validated order')
    xyz = [tuple(_finite(v, 'coordinate') for v in n) for n in nodes]
    xyz = [tuple(v-xyz[0][j] for j,v in enumerate(n)) for n in xyz]
    signs = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
             (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
    a = 1/math.sqrt(3)
    points = list(itertools.product((-a,a), repeat=3))+[(0,0,0)]+signs
    result=[]
    for q in points:
        dn=[]
        for s in signs:
            row=[]
            for j in range(3):
                other=[k for k in range(3) if k != j]
                row.append(s[j]*(1+s[other[0]]*q[other[0]])*(1+s[other[1]]*q[other[1]])/8)
            dn.append(row)
        jac=[[sum(xyz[n][i]*dn[n][j] for n in range(8)) for j in range(3)] for i in range(3)]
        result.append(_det3(jac))
    return tuple(result)
