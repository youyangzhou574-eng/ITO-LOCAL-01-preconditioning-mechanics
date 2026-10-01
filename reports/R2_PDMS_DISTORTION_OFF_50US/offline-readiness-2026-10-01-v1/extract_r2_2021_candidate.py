# -*- coding: utf-8 -*-
"""Frozen arrays/fields; immutable publication v2. One readonly ODB handle."""
from __future__ import print_function
import os,sys,json,traceback,tarfile
import numpy as np
from pdms_native_gates_27 import validate_mesh_instance,validate_frame_arrays
from native_field_helpers import PACKAGE,BASE_FIELDS,field_arrays,sha,utc,record_file
from extraction_protocol_R2 import publish_json,publish_npz,snapshot,validate_dataset,validate_native_inventory

def export(odb,root,manifest,source,expected_hash):
    steps=list(odb.steps.keys())
    if steps!=["TENSION"]:raise ValueError("unexpected native step identity")
    instances=list(odb.rootAssembly.instances.keys())
    if instances!=["STRIP-1"]:raise ValueError("unexpected native instance identity")
    inst=odb.rootAssembly.instances["STRIP-1"]
    manifest["native_mesh_identity"]=validate_mesh_instance(inst,manifest["mesh_reference"])
    publish_npz(os.path.join(root,"MESH_NATIVE.npz"),
        node_labels=np.asarray([n.label for n in inst.nodes],dtype=np.int64),
        node_coordinates=np.asarray([n.coordinates for n in inst.nodes],dtype=np.float64),
        element_labels=np.asarray([e.label for e in inst.elements],dtype=np.int64),
        element_connectivity=np.asarray([e.connectivity for e in inst.elements],dtype=np.int64))
    manifest["files"].append(record_file(root,"MESH_NATIVE.npz"))
    step=odb.steps["TENSION"]
    manifest["frame_count"]=len(step.frames)
    manifest["native_frame_inventory"]=[{"frame_index":i,"increment_number":f.incrementNumber,"time_s":float(f.frameValue)} for i,f in enumerate(step.frames)]
    for index,frame in enumerate(step.frames):
        arrays={}
        meta={"frame_index":index,"increment_number":frame.incrementNumber,
              "time_s":float(frame.frameValue),"native_present_fields":sorted(list(frame.fieldOutputs.keys())),
              "fields":{}}
        names=sorted(set(BASE_FIELDS)|set(x for x in frame.fieldOutputs.keys() if x.startswith("CKSTAT")))
        for name in names:
            if name not in frame.fieldOutputs:
                meta["fields"][name]={"availability":"UNAVAILABLE_IN_THIS_FRAME"}
                continue
            values,fmeta=field_arrays(frame.fieldOutputs[name])
            meta["fields"][name]=fmeta
            for key,val in values.items():arrays[name+"_"+key]=val
        validate_frame_arrays(arrays,len(manifest["mesh_reference"]["nodes"]))
        # Metadata is kept as UTF8 bytes, never pickle or object arrays.
        meta_bytes=json.dumps(meta,sort_keys=True).encode("utf-8")
        arrays["meta_utf8"]=np.frombuffer(meta_bytes,dtype=np.uint8)
        name="frame_%05d.npz"%index
        publish_npz(os.path.join(root,name),**arrays)
        manifest["files"].append(record_file(root,name,{"frame_index":index,"time_s":meta["time_s"],"increment_number":frame.incrementNumber}))
        manifest["last_frame"]=index;manifest["last_time_s"]=meta["time_s"]
        if index%100==0 or index==len(step.frames)-1:snapshot(root,manifest,"FRAMES")
        if index%100==0:
            print("EXPORTED_FRAME",index,"TIME",meta["time_s"]);sys.stdout.flush()
    histories={};history_index=[]
    for rname in sorted(step.historyRegions.keys()):
        region=step.historyRegions[rname]
        for hname in sorted(region.historyOutputs.keys()):
            key="h%05d"%len(history_index)
            hout=region.historyOutputs[hname]
            histories[key]=np.asarray(list(hout.data),dtype=np.float64)
            history_index.append({"key":key,"region":rname,"region_description":str(region.description),
                                  "variable":hname,"description":str(hout.description),
                                  "samples":len(hout.data)})
    publish_npz(os.path.join(root,"HISTORY_NATIVE.npz"),**histories)
    publish_json(os.path.join(root,"HISTORY_INDEX.json"),history_index)
    manifest["files"] += [record_file(root,"HISTORY_NATIVE.npz"),record_file(root,"HISTORY_INDEX.json")]
    manifest["extraction_data_complete"]=True
    snapshot(root,manifest,"HISTORY_EXPORTED")



def main():
    raise RuntimeError("NOT_RELEASED_FOR_NATIVE_EXECUTION; VERSION_SEMANTICS_PENDING")

if __name__=="__main__":main()
