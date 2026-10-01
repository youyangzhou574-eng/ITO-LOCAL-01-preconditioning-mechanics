# -*- coding: utf-8 -*-
"""One read-only NEW flat-bilayer ODB session. Abaqus Python2.7 / ordinary Python3 mock compatible."""
from __future__ import print_function
import datetime
import hashlib
import json
import os
import sys
import tarfile
import traceback
import numpy as np

PACKAGE="ITO_PDMS_DISTORTION_CONTROL_DIAGNOSTIC_V1"
BASE_FIELDS=("U","V","S","LE","CKE","CKLE","CKEMAG","CKLS","CKSTAT","STATUS")
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            b=f.read(4*1024*1024)
            if not b: break
            h.update(b)
    return h.hexdigest()
def utc():
    if hasattr(datetime,"timezone"):
        return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
    return datetime.datetime.utcnow().isoformat()+"Z"
def json_write(path,obj):
    tmp=path+".tmp"
    with open(tmp,"w") as f: json.dump(obj,f,indent=2,sort_keys=True)
    if os.path.exists(path): os.remove(path)
    os.rename(tmp,path)
def optional(obj,key,default=None):
    try: return getattr(obj,key)
    except Exception: return default
def raw(obj):
    try: return getattr(obj,"dataDouble"),"dataDouble"
    except Exception: return getattr(obj,"data"),"data"
def field_arrays(fo):
    labels=[];ips=[];datas=[];coords=[];meta={"components":[str(x) for x in fo.componentLabels],
          "positions":[],"instances":[],"data_access":[],"section_points":[]}
    try:
        blocks=list(fo.bulkDataBlocks)
        for b in blocks:
            nodal=optional(b,"nodeLabels",())
            elem=optional(b,"elementLabels",())
            if nodal is None: nodal=()
            if elem is None: elem=()
            labs=nodal if len(nodal) else elem
            if not len(labs): continue
            data,access=raw(b)
            arr=np.asarray(data,dtype=np.float64).reshape((len(labs),-1))
            ip=optional(b,"integrationPoints",())
            if ip is None or len(ip)!=len(labs): ip=[0]*len(labs)
            labels.append(np.asarray(labs,dtype=np.int64));ips.append(np.asarray(ip,dtype=np.int32));datas.append(arr)
            coord=optional(b,"localCoordSystem",())
            if coord is not None and len(coord): coords.append(np.asarray(coord,dtype=np.float64))
            else: coords.append(None)
            meta["data_access"].append(access)
            meta["positions"].append(str(b.position))
            inst=optional(b,"instance")
            meta["instances"].append(str(optional(inst,"name","UNKNOWN")))
            meta["section_points"].append(str(optional(b,"sectionPoint","NONE")))
        meta["access_mode"]="BULK_DATA_BLOCKS"
    except Exception as e:
        labels=[];ips=[];datas=[];coords=[]
        meta["bulk_fallback_reason"]=str(e)
        meta["data_access"]=[];meta["positions"]=[];meta["instances"]=[];meta["section_points"]=[]
        for v in fo.values:
            label=optional(v,"nodeLabel",None)
            if not label: label=optional(v,"elementLabel",None)
            if label is None: raise ValueError("native field value has no label")
            d,access=raw(v)
            d=np.asarray(d,dtype=np.float64).reshape(1,-1)
            labels.append(np.asarray([label],dtype=np.int64));ips.append(np.asarray([optional(v,"integrationPoint",0)],dtype=np.int32));datas.append(d)
            coord=optional(v,"localCoordSystemDouble",None)
            if coord is None: coord=optional(v,"localCoordSystem",None)
            coords.append(None if coord is None else np.asarray([coord],dtype=np.float64))
            meta["data_access"].append(access);meta["positions"].append(str(v.position))
            inst=optional(v,"instance")
            meta["instances"].append(str(optional(inst,"name","UNKNOWN")))
            meta["section_points"].append(str(optional(v,"sectionPoint","NONE")))
        meta["access_mode"]="FIELD_VALUES"
    for key in ("positions","instances","data_access","section_points"):
        meta[key]=sorted(set(meta[key]))
    n=sum(len(v) for v in labels)
    arrays={"labels":np.concatenate(labels) if n else np.empty((0,),dtype=np.int64),
            "ip":np.concatenate(ips) if n else np.empty((0,),dtype=np.int32),
            "data":np.concatenate(datas) if n else np.empty((0,max(1,len(meta["components"]))),dtype=np.float64)}
    if coords and any(c is not None for c in coords):
        shapes=set(c.shape[1:] for c in coords if c is not None)
        if len(shapes)!=1: raise ValueError("inconsistent native orientation shapes")
        shape=next(iter(shapes))
        filled=[];mask=[]
        for labs,c in zip(labels,coords):
            empty=np.empty((len(labs),)+shape,dtype=np.float64);empty.fill(np.nan)
            filled.append(empty if c is None else c)
            present=np.empty((len(labs),),dtype=np.uint8);present.fill(c is not None)
            mask.append(present)
        arrays["localcoords"]=np.concatenate(filled);arrays["localcoords_present"]=np.concatenate(mask)
        meta["localcoords_shape"]=list(shape)
    meta["value_count"]=int(n)
    meta["stored_numeric_type"]="float64 container; native data access precision is recorded, not upgraded"
    return arrays,meta

def record_file(root,name,extra=None):
    path=os.path.join(root,name)
    entry={"name":name,"bytes":os.path.getsize(path),"sha256":sha(path)}
    if extra:entry.update(extra)
    return entry
