# -*- coding: utf-8 -*-
from __future__ import print_function
import os,json,time,sys,zipfile,io,contextlib
from r1_time_rule_27 import time_audit,finite
import numpy as np
from native_field_helpers import sha
WAITS=(.1,.2,.5,1.,2.)
class ArrayDict(dict):
    @property
    def files(self):return list(self.keys())
@contextlib.contextmanager
def open_npz(path):
    # SMA Python2.7 np.load fails its file-handle ZIP probe; named ZIP reads work.
    with zipfile.ZipFile(path,"r") as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or any(not n.endswith(".npy") for n in names):raise ValueError("invalid NPZ member inventory")
        arrays=ArrayDict()
        for name in names:arrays[name[:-4]]=np.lib.format.read_array(io.BytesIO(z.read(name)),allow_pickle=False)
        yield arrays
def publish_temp(temp,target,rename=None,sleep=None):
    if os.path.exists(target):raise ValueError("immutable destination exists: "+target)
    rename=rename or os.rename;sleep=sleep or time.sleep
    for attempt in range(6):
        try:
            if os.path.exists(target):raise ValueError("immutable destination appeared: "+target)
            rename(temp,target);return
        except OSError as e:
            number=getattr(e,"winerror",None)
            print("PUBLICATION_ERROR",target,"winerror",number,"attempt",attempt+1);sys.stdout.flush()
            if number not in (32,33) or attempt==5:raise
            sleep(WAITS[attempt])
def publish_json(path,obj,rename=None,sleep=None):
    if os.path.exists(path):raise ValueError("immutable destination exists")
    temp=path+".writing"
    if os.path.exists(temp):raise ValueError("temporary destination exists")
    with open(temp,"w") as f:json.dump(obj,f,indent=2,sort_keys=True)
    publish_temp(temp,path,rename,sleep)
def publish_npz(path,**arrays):
    temp=path+".writing.npz"
    if os.path.exists(path) or os.path.exists(temp):raise ValueError("block destination exists")
    # Native NumPy1.15/Python2.7 writer retains its filename-based behavior.
    np.savez_compressed(temp,**arrays)
    publish_temp(temp,path)
def snapshot(root,m,stage):
    sequence=m.get("progress_sequence",0)+1;m["progress_sequence"]=sequence
    snap={k:m.get(k) for k in ("package_id","job","attempt_id","extractor_sha256","source_sha256_before","source_bytes_before","odb_open_calls","readonly_requested","frame_count","last_frame","last_time_s")}
    snap.update(status="RUNNING",phase=stage,progress_sequence=sequence,completed_frame_blocks=len([x for x in m["files"] if x["name"].startswith("frame_")]))
    publish_json(os.path.join(root,"progress_%06d.json"%sequence),snap)
def validate_dataset(root,m):
    entries=m["files"];names=[x["name"] for x in entries]
    if len(names)!=len(set(names)):raise ValueError("duplicate export blocks")
    expected=m["native_frame_inventory"]
    validate_native_inventory(m)
    indices=[x["frame_index"] for x in expected]
    if indices!=list(range(len(expected))) or len(expected)!=m["frame_count"]:raise ValueError("native frame inventory invalid")
    frames=[x for x in entries if x["name"].startswith("frame_")]
    if len(frames)!=len(expected) or [x["frame_index"] for x in frames]!=indices:raise ValueError("missing or duplicate frame")
    if not set(("MESH_NATIVE.npz","HISTORY_NATIVE.npz","HISTORY_INDEX.json")).issubset(set(names)):raise ValueError("mesh/history missing")
    for x in entries:
        p=os.path.join(root,x["name"])
        if os.path.getsize(p)!=x["bytes"] or sha(p)!=x["sha256"]:raise ValueError("block hash or size mismatch")
        if x["name"].endswith(".npz"):
            with open_npz(p) as a:
                for key in a.files:a[key] # forces zip CRC/decompression
    for native,block in zip(expected,frames):
        if native["frame_index"]!=block["frame_index"] or native["increment_number"]!=block["increment_number"] or native["time_s"]!=block["time_s"]:raise ValueError("actual frame coverage mismatch")
        with open_npz(os.path.join(root,block["name"])) as a:
            raw=a["meta_utf8"]
            meta=json.loads((raw.tobytes() if hasattr(raw,"tobytes") else raw.tostring()).decode("utf-8"))
            if any(meta[k]!=native[k] for k in ("frame_index","increment_number","time_s")):raise ValueError("frame metadata mismatch")
    with open(os.path.join(root,"HISTORY_INDEX.json")) as f:history=json.load(f)
    if not history:raise ValueError("empty history index")
    with open_npz(os.path.join(root,"HISTORY_NATIVE.npz")) as a:
        if set(a.files)!=set(x["key"] for x in history):raise ValueError("history inventory mismatch")
        for x in history:
            if a[x["key"]].shape!=(x["samples"],2):raise ValueError("history samples mismatch")
            v=a[x["key"]]
            if v.dtype!=np.dtype("float64") or len(v)<2 or not np.all(np.isfinite(v)) or v[0,0]!=0 or np.any(np.diff(v[:,0])<=0) or not time_audit(v[-1,0],m["native_expectation"]["duration_s"])["pass"]:raise ValueError("native history finite/order/full-time coverage fails")
    if not m.get("extraction_data_complete"):raise ValueError("data completion missing")

def validate_native_inventory(m):
    if m.get("package_id")!="ITO_PDMS_DISTORTION_CONTROL_DIAGNOSTIC_V1":raise ValueError("R2 package identity differs")
    e=m.get("native_expectation",{});frames=m.get("native_frame_inventory",[])
    if m.get("job")!="ITOL01_PDR2_V1" or e.get("job")!=m.get("job") or e.get("duration_s")!=5e-5:raise ValueError("Frozen R2 job/duration identity differs")
    if len(frames)!=e.get("expected_frame_count") or len(frames)!=m.get("frame_count") or not frames:raise ValueError("Native frame count identity differs")
    if [f["frame_index"] for f in frames]!=list(range(len(frames))) or m.get("last_frame")!=len(frames)-1:raise ValueError("Native frame indices differ")
    times=[f["time_s"] for f in frames];inc=[f["increment_number"] for f in frames]
    if any(not finite(float(t)) for t in times) or times[0]!=0 or any(times[k]>=times[k+1] for k in range(len(times)-1)):raise ValueError("Native time chronology differs")
    if inc[0]!=0 or any(v!=int(v) or v<0 for v in inc) or any(inc[k]>=inc[k+1] for k in range(len(inc)-1)) or inc[-1]!=e.get("final_increment"):raise ValueError("Audited native final increment differs")
    audit=time_audit(times[-1],e["duration_s"])
    if not audit["pass"] or m.get("last_time_s")!=times[-1]:raise ValueError("Pro endpoint representation rule fails")
    return audit
