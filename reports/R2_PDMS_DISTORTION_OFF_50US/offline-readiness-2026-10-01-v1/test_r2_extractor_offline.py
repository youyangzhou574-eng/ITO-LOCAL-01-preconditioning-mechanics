import unittest,sys,json
from pathlib import Path
import numpy as np
try:
    import extract_r2_2021_candidate as extract
    import extraction_protocol_R2 as protocol
except ImportError: extract=protocol=None
class Obj:
    def __init__(self,**kw): self.__dict__.update(kw)
class Checks(unittest.TestCase):
    def test_01_native_entry_blocked_before_odb(self):
        self.assertIsNotNone(extract,'R2 candidate missing')
        calls=[];previous=sys.modules.get('odbAccess');sys.modules['odbAccess']=Obj(openOdb=lambda **kw:calls.append(kw))
        try:
            with self.assertRaisesRegex(RuntimeError,'NOT_RELEASED'): extract.main()
            self.assertEqual(calls,[])
        finally:
            if previous is None: sys.modules.pop('odbAccess',None)
            else: sys.modules['odbAccess']=previous
    def test_02_full_mesh_two_fake_frames_r2_namespace(self):
        self.assertIsNotNone(extract,'R2 candidate missing')
        from r1_time_rule_27 import q32
        root=Path(__file__).parent
        binding=json.loads((root/'R2_LOCAL_STORAGE_BINDING.json').read_text())
        out=Path(binding['bulk_root'])/'offline_checks'/'fake_export_attempt01'
        out.mkdir(parents=True,exist_ok=False)
        m=json.loads((root/'REFERENCE_MESH.json').read_text())
        inst=Obj(nodes=[Obj(label=int(k),coordinates=tuple(v)) for k,v in sorted(m['nodes'].items(),key=lambda x:int(x[0]))],elements=[Obj(label=int(k),connectivity=tuple(v)) for k,v in sorted(m['elements'].items(),key=lambda x:int(x[0]))])
        labs=np.arange(51813,0,-1,dtype=np.int64)
        b=Obj(nodeLabels=labs,elementLabels=(),integrationPoints=(),dataDouble=np.zeros((51813,2)),position='NODAL',instance=Obj(name='STRIP-1'),sectionPoint=None,localCoordSystem=())
        uv=Obj(componentLabels=('1','2'),bulkDataBlocks=(b,),values=())
        frames=[Obj(incrementNumber=i*12,frameValue=t,fieldOutputs={'U':uv,'V':uv}) for i,t in enumerate((0.,q32(5e-5)))]
        h=Obj(description='FAKE_ONLY',data=((0.,0.),(q32(5e-5),0.)))
        odb=Obj(rootAssembly=Obj(instances={'STRIP-1':inst}),steps={'TENSION':Obj(frames=frames,historyRegions={'Assembly ASSEMBLY':Obj(description='FAKE_ONLY',historyOutputs={'ETOTAL':h})})})
        manifest={'package_id':'ITO_PDMS_DISTORTION_CONTROL_DIAGNOSTIC_V1','job':'ITOL01_PDR2_V1','files':[],'native_expectation':{'job':'ITOL01_PDR2_V1','duration_s':5e-5,'expected_frame_count':2,'final_increment':12},'mesh_reference':m}
        extract.export(odb,str(out),manifest,None,None);protocol.validate_dataset(str(out),manifest)
        arrays=0
        for p in out.glob('*.npz'):
            with protocol.open_npz(str(p)) as a: arrays+=len(a.files)
        with protocol.open_npz(str(out/'frame_00001.npz')) as a:
            self.assertEqual(a['U_data'].shape,(51813,2));self.assertEqual(int(a['U_labels'][0]),51813)
        receipt={'status':'R2_MOCK_ONLY_EXPORT_DECODE_PASS','native_dispatches':0,'real_ODB_calls':0,'fake_frames':2,'nodes':51813,'elements':51200,'decoded_arrays':arrays,'mock_directory':str(out),'science_qualification':False,'native_execution_released':False}
        (root/'R2_EXTRACTOR_OFFLINE_MOCK_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    def test_03_r1_identity_rejected(self):
        self.assertIsNotNone(protocol,'R2 protocol missing')
        with self.assertRaisesRegex(ValueError,'identity'):
            protocol.validate_native_inventory({'job':'ITOL01_PDR1_V1','native_expectation':{'job':'ITOL01_PDR1_V1','duration_s':5e-5}})
if __name__=='__main__': unittest.main(verbosity=2)
