import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src/python'))
SPEC=importlib.util.find_spec('run_b01_m02_probe39')
if SPEC:import run_b01_m02_probe39 as runner


class Builder39Tests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(SPEC,'new offline39 builder API missing, not historical production failure')
        self.temp=tempfile.TemporaryDirectory(dir=BASE/'evidence/B01_M02_probe39')
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.geometry={'original_element':5817,'original_node_labels':[5907,5903,5902,5908],
            'source':{'sha256':'91b5fd771d9c9b7ea53147154a9d9c3161df647404933f3726da614a287d190e'},
            'coordinates_mm':[[2,0],[3,0],[3,1],[2,1]]}

    def fixture(self):
        def put(name,buf):
            p=self.root/name;p.write_bytes(buf);return {'path':str(p),'bytes':len(buf),'sha256':hashlib.sha256(buf).hexdigest()}
        g=put('geometry.json',json.dumps(self.geometry).encode())
        src={r:put(r+'.txt',runner.SOURCE_PATHS[r].read_bytes()) for r in runner.SOURCE_ROLES}
        closure={'source_files':src,'geometry':g,'owner_thread':'01a0d157-8547-7552-bb05-9a1c1c92698d'}
        c=put('closure.json',json.dumps(closure).encode())
        review=put('review.json',json.dumps({'pass':True,'source_files':src,'geometry':g}).encode())
        tests=put('tests.json',json.dumps({'pass':True,'source_files':src,'geometry':g}).encode())
        a=put('admission.json',json.dumps({'offline_build_pass':True,'native_pass':False,'closure_sha256':c['sha256'],'review':review,'final_tests':tests}).encode())
        return Path(c['path']),Path(a['path'])

    def test_generated_8_steps_reset_all_boundaries_and_keep_rows_visible(self):
        deck=runner.render_deck(self.geometry)
        parts=deck.split('*Step, name=')[1:];self.assertEqual(len(parts),8)
        for j,p in enumerate(parts):
            rows=p.split('*Boundary, op=NEW\n')[1].split('*Node Print')[0].strip().splitlines()
            thermo={};mechan=set()
            for row in rows:
                n,a,b,v=row.split(',');n=int(n);a=int(a);b=int(b)
                if a==11:thermo[n]=float(v)
                else:mechan.update((n,d) for d in range(a,b+1))
            self.assertEqual(set(thermo),{1,2,3,4,11,12,13,14})
            for ns in [[1,2,3,4],[11,12,13,14]]:
                self.assertEqual([thermo[n] for n in ns],[1+int(j==i+4) for i in range(4)])
                self.assertEqual({(n,d) for n in ns for d in [1,2]}-mechan,{(ns[2],1)})
            self.assertIn('\nNT, RFL\n',p)
            lines=p.split('*El Print')[1].split('*Output')[0].splitlines()[1:]
            for line in lines:
                fields=[s.strip() for s in line.split(',')]
                self.assertLessEqual(len(fields),9);self.assertEqual(fields[0],'SDV1')

    def test_actual_geometry_provenance_mismatch_rejected(self):
        for g in [dict(self.geometry,original_element=1),dict(self.geometry,original_node_labels=[1,2,3,4]),dict(self.geometry,source={'sha256':'0'*64})]:
            with self.assertRaises(ValueError):runner.render_deck(g)

    def test_build_once_creates_local_reviewable_package_only(self):
        c,a=self.fixture();out=self.root/'out';r=runner.build_package(self.root,out,c,a)
        self.assertFalse(r['native_admitted']);self.assertEqual(r['state'],'OFFLINE_BUILD_CLOSED_ONCE')
        self.assertTrue((out/'PROBE39.inp').exists());self.assertTrue((out/'EXPECTED39.json').exists())
        expected=json.loads((out/'EXPECTED39.json').read_text())
        self.assertAlmostEqual(expected['101']['area'],1)
        self.assertFalse(expected['native_matrix_qualified'])
        with self.assertRaises(FileExistsError):runner.build_package(self.root,out,c,a)

    def test_orphan_partial_and_failure_directories_are_not_reentered(self):
        c,a=self.fixture()
        for label in ['INTENT39.json','COMPLETION39.json','COMPLETION39.PARTIAL','FAILED_CLOSED39.json']:
            out=self.root/label.replace('.','_');out.mkdir();(out/label).write_text('{}')
            with self.assertRaises(FileExistsError):runner.build_package(self.root,out,c,a)

    def test_changed_source_rejected_before_output(self):
        c,a=self.fixture();obj=json.loads(c.read_text());Path(obj['source_files']['core']['path']).write_text('changed')
        out=self.root/'out'
        with self.assertRaises(ValueError):runner.build_package(self.root,out,c,a)
        self.assertFalse(out.exists())

    def test_review_source_or_admission_mismatch_rejected(self):
        c,a=self.fixture();ad=json.loads(a.read_text());ad['native_pass']=True;a.write_text(json.dumps(ad))
        with self.assertRaises(ValueError):runner.build_package(self.root,self.root/'out',c,a)
        self.assertFalse((self.root/'out').exists())

    def test_rehashed_review_with_wrong_source_binding_rejected(self):
        c,a=self.fixture();ad=json.loads(a.read_text());p=Path(ad['review']['path']);review=json.loads(p.read_text())
        review['source_files']['core']['sha256']='0'*64
        buf=json.dumps(review).encode();p.write_bytes(buf);ad['review'].update(bytes=len(buf),sha256=hashlib.sha256(buf).hexdigest());a.write_text(json.dumps(ad))
        with self.assertRaises(ValueError):runner.build_package(self.root,self.root/'out',c,a)
        self.assertFalse((self.root/'out').exists())

    def test_post_intent_write_failure_is_closed_without_retry(self):
        c,a=self.fixture();out=self.root/'out';real=runner.write_exclusive
        def failed_disk(path,data):
            if Path(path).name=='PROBE39.inp':raise OSError('synthetic write failure')
            return real(path,data)
        with patch.object(runner,'write_exclusive',failed_disk):
            with self.assertRaises(OSError):runner.build_package(self.root,out,c,a)
        self.assertEqual(json.loads((out/'FAILED_CLOSED39.json').read_text())['state'],'OFFLINE_BUILD_FAILED_CLOSED')
        with self.assertRaises(FileExistsError):runner.build_package(self.root,out,c,a)

    def test_rehashed_changed_geometry_rejects_stale_review_and_tests(self):
        c,a=self.fixture();closure=json.loads(c.read_text());ad=json.loads(a.read_text())
        p=Path(closure['geometry']['path']);g=json.loads(p.read_text());g['coordinates_mm']=[[4,0],[5,0],[5,1],[4,1]]
        buf=json.dumps(g).encode();p.write_bytes(buf);closure['geometry'].update(bytes=len(buf),sha256=hashlib.sha256(buf).hexdigest())
        cb=json.dumps(closure).encode();c.write_bytes(cb);ad['closure_sha256']=hashlib.sha256(cb).hexdigest();a.write_text(json.dumps(ad))
        out=self.root/'changed_geometry'
        with self.assertRaises(ValueError):runner.build_package(self.root,out,c,a)
        self.assertFalse(out.exists())

    def test_each_final_binding_requires_exact_geometry(self):
        for kind in ['review','final_tests']:
            for change in ['missing','wrong']:
                with self.subTest(kind=kind,change=change):
                    c,a=self.fixture();ad=json.loads(a.read_text());p=Path(ad[kind]['path']);evidence=json.loads(p.read_text())
                    if change=='missing':del evidence['geometry']
                    else:evidence['geometry']['sha256']='0'*64
                    buf=json.dumps(evidence).encode();p.write_bytes(buf);ad[kind].update(bytes=len(buf),sha256=hashlib.sha256(buf).hexdigest());a.write_text(json.dumps(ad))
                    out=self.root/(kind+'_'+change)
                    with self.assertRaises(ValueError):runner.build_package(self.root,out,c,a)
                    self.assertFalse(out.exists())

    def test_path_scope_escape_rejected_before_write(self):
        c,a=self.fixture()
        with self.assertRaises(ValueError):runner.build_package(self.root,self.root.parent/'OUTSIDE_PROBE39',c,a)

    def test_cli_cannot_submit_or_connect(self):
        p=subprocess.run([sys.executable,'-B',str(BASE/'src/python/run_b01_m02_probe39.py'),'--submit'],capture_output=True,text=True,cwd=BASE)
        self.assertEqual(p.returncode,2)


if __name__=='__main__':unittest.main()
