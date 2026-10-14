"""Package validator tests use temporary ordinary files only."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'scripts'/'validate_skill.py'
V=None
if PATH.exists():
    spec=importlib.util.spec_from_file_location('validate_skill',PATH)
    V=importlib.util.module_from_spec(spec); spec.loader.exec_module(V)

class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(V,'Package validator not implemented')
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'SKILL.md').write_text('---\nname: abaqus-modeling-fracture\ndescription: Use when reviewing Abaqus evidence.\n---\n# Test\n',encoding='utf-8')

    def manifest(self):
        records=[]
        for p in sorted(self.root.rglob('*')):
            if p.is_file() and p.name!='FILE_MANIFEST.json':
                b=p.read_bytes(); records.append(dict(path=p.relative_to(self.root).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
        (self.root/'FILE_MANIFEST.json').write_text(json.dumps({'files':records}),encoding='utf-8')

    def test_valid_manifest(self):
        self.manifest(); self.assertEqual(V.validate(self.root),[])

    def test_missing_manifest_fails(self):
        self.assertTrue(V.validate(self.root))

    def test_changed_file_detected(self):
        self.manifest(); p=self.root/'SKILL.md'; p.write_text(p.read_text()+'changed\n')
        self.assertTrue(any('hash/size' in e for e in V.validate(self.root)))

    def test_extra_file_detected(self):
        self.manifest(); (self.root/'extra.txt').write_text('x')
        self.assertTrue(any('inventory' in e for e in V.validate(self.root)))

    def test_broken_link_detected(self):
        p=self.root/'SKILL.md'; p.write_text(p.read_text()+'[missing](missing.md)\n'); self.manifest()
        self.assertTrue(any('Missing link' in e for e in V.validate(self.root)))

    def test_path_escape_detected(self):
        p=self.root/'SKILL.md'; p.write_text(p.read_text()+'[escape](../outside.md)\n'); self.manifest()
        self.assertTrue(any('Escaping link' in e for e in V.validate(self.root)))

    def test_native_import_detected(self):
        (self.root/'scripts').mkdir(); (self.root/'scripts'/'unsafe.py').write_text('import odbAccess\n'); self.manifest()
        self.assertTrue(any('Forbidden import' in e for e in V.validate(self.root)))

    def test_nonfinite_json_rejected(self):
        (self.root/'bad.json').write_text('{"v":NaN}'); self.manifest()
        self.assertTrue(any('Invalid JSON' in e for e in V.validate(self.root)))

    def test_invalid_frontmatter(self):
        (self.root/'SKILL.md').write_text('# no metadata\n'); self.manifest()
        self.assertTrue(any('frontmatter' in e for e in V.validate(self.root)))

if __name__=='__main__': unittest.main()
