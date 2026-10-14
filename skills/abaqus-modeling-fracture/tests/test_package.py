"""Structural coverage assertions, not independent agent behavior testing."""
import json
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]

class PackageCoverage(unittest.TestCase):
    def read(self,path):
        p=ROOT/path
        self.assertTrue(p.is_file(), 'Missing packaged file: '+path)
        return p.read_text(encoding='utf-8')

    def test_metadata_and_router(self):
        text=self.read('SKILL.md')
        self.assertTrue(text.startswith('---\nname: abaqus-modeling-fracture\n'))
        self.assertLess(len(text),5000)
        self.assertIn('profiles/ito-pdms.md',text)

    def test_ito_design_not_reopened(self):
        text=self.read('profiles/ito-pdms.md')
        self.assertIn('DESIGN_SELECTED_IMPLEMENTATION_PENDING',text)
        self.assertNotIn('no Git 写入',text)
        self.assertNotIn('no Pro 新消息',text)
        self.assertNotIn('E:\\open',text)

    def test_uel_phase_residual_and_energy_slot_limits(self):
        text=self.read('references/uel-implementation.md')
        for s in ['DOF 11','ENERGY(6)','KINC=0','ANS','EAS','MPI']:
            self.assertIn(s,text)

    def test_observation_not_fracture_width(self):
        text=self.read('references/odb-and-evidence.md')
        for s in ['first d>0','detF','detJ','PK2','Cauchy','0.90/0.95/0.99','branch']:
            self.assertIn(s,text)

    def test_no_native_authorization_in_example(self):
        c=json.loads(self.read('assets/case-contract.example.json'))
        self.assertFalse(c['authorization']['native_execution'])
        self.assertEqual(c['authorization']['approved_stages'],[])
        self.assertIsNone(c['runtime']['scheduler_job_id'])

    def test_test_limits_disclosed(self):
        text=self.read('tests/pressure_scenarios.md')
        self.assertIn('NOT_RUN_INDEPENDENT_AGENT',text)
        self.assertIn('SSH',text)

    def test_relative_markdown_links_resolve(self):
        docs=list(ROOT.rglob('*.md')); self.assertGreater(len(docs),8)
        for p in docs:
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if '://' in link or link.startswith('#'): continue
                target=(p.parent/link.split('#')[0]).resolve()
                self.assertTrue(target.is_relative_to(ROOT.resolve()),str(target))
                self.assertTrue(target.exists(),str(target))

if __name__=='__main__': unittest.main()
