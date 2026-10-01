# -*- coding: utf-8 -*-
"""New-grid identity gates; original native coordinate representation tolerance."""
from __future__ import print_function
import numpy as np
def validate_mesh_instance(inst,reference):
    nn=len(reference['nodes']);ne=len(reference['elements'])
    nodes=list(inst.nodes);elems=list(inst.elements)
    if len(nodes)!=nn or len(elems)!=ne:raise ValueError('New R1 native mesh count mismatch')
    labels=[n.label for n in nodes];elabels=[e.label for e in elems]
    if len(set(labels))!=nn or set(labels)!=set(int(x) for x in reference['nodes']):raise ValueError('R1 native node label inventory mismatch')
    if len(set(elabels))!=ne or set(elabels)!=set(int(x) for x in reference['elements']):raise ValueError('R1 native element label inventory mismatch')
    expected=np.asarray([reference['nodes'][str(n.label)] for n in nodes],dtype=np.float64)
    native=np.asarray([n.coordinates[:2] for n in nodes],dtype=np.float64)
    if not np.all(np.isfinite(native)) or not np.allclose(native,expected,rtol=0.,atol=1e-9):raise ValueError('R1 native coordinate identity mismatch')
    if any(list(e.connectivity)!=reference['elements'][str(e.label)] for e in elems):raise ValueError('R1 native connectivity identity mismatch')
    return {'nodes':nn,'elements':ne,'max_native_coordinate_representation_error_mm':float(np.max(np.abs(native-expected))),'original_native_coordinate_tolerance_mm':1e-9,'connectivity_exact':True}
def validate_frame_arrays(arrays,nn):
    labels=np.arange(1,nn+1,dtype=np.int64)
    for field in ('U','V'):
        if field+'_labels' not in arrays or field+'_data' not in arrays:raise ValueError('R1 required nodal '+field+' unavailable')
        ids=arrays[field+'_labels'];data=arrays[field+'_data']
        if ids.shape!=(nn,) or not np.array_equal(np.sort(ids),labels) or data.ndim!=2 or data.shape[0]!=nn or data.shape[1]<2 or not np.all(np.isfinite(data)):raise ValueError('R1 nodal '+field+' label/count/finite gate failed')
