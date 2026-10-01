import copy, unittest
from pathlib import Path
try:
    import r2_offline_readiness as r2
except ImportError:
    r2 = None

DECK = b'*Heading\r\n** BASELINE\r\n*Part, name=STRIP\r\n*Solid Section, elset=PDMS, material=PDMS_METHOD_SEED\r\n1.\r\n*Solid Section, elset=ITO, material=ITO_BRITTLE_METHOD_SEED\r\n1.\r\n*End Part\r\n*Assembly, name=ASSEMBLY\r\n*End Assembly\r\n*Material, name=PDMS_METHOD_SEED\r\n*Hyperelastic, mooney-rivlin\r\n0.27, 0.0108, 0.036\r\n*Step, name=TENSION\r\n*Dynamic, Explicit\r\n, 5e-5\r\n*End Step\r\n'

class CandidateTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(r2, 'R2 offline implementation absent')
    def test_minimal_candidate_reverses_exactly_to_source(self):
        candidate = r2.make_candidate(DECK)
        audit = r2.audit_candidate(DECK, candidate)
        self.assertTrue(audit['all_other_bytes_identical'])
        self.assertTrue(audit['ITO_section_bytes_identical'])
        self.assertEqual(candidate.count(b'*SECTION CONTROLS'), 1)
        self.assertNotIn(b'HOURGLASS=', candidate)
        self.assertIn(b'NOT_RELEASED_FOR_NATIVE_EXECUTION', candidate)
    def test_ITO_rebinding_is_rejected(self):
        candidate=r2.make_candidate(DECK).replace(b'elset=ITO, material=',b'elset=ITO, CONTROLS=R2_PDMS_DC_OFF, material=')
        with self.assertRaises(ValueError):r2.audit_candidate(DECK,candidate)
    def test_material_or_mesh_change_is_rejected(self):
        candidate=r2.make_candidate(DECK).replace(b'0.27, 0.0108',b'0.28, 0.0108')
        with self.assertRaises(ValueError):r2.audit_candidate(DECK,candidate)
    def test_existing_controls_or_adaptive_mesh_is_rejected(self):
        for extra in [b'*SECTION CONTROLS, NAME=OLD\r\n',b'*ADAPTIVE MESH\r\n']:
            with self.assertRaises(ValueError):r2.make_candidate(DECK+extra)
    def test_duplicate_PDMS_section_is_rejected(self):
        with self.assertRaises(ValueError):r2.make_candidate(DECK+ b'*Solid Section, elset=PDMS, material=PDMS_METHOD_SEED\r\n1.\r\n')

class StorageTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(r2, 'R2 storage implementation absent')
    def test_R2_binding_is_distinct_and_actual_sizes_pending(self):
        binding=r2.make_binding(Path(__file__).parent)
        paths=r2.validate_binding(binding,Path(__file__).parent)
        self.assertIn('ITO_PDMS_DISTORTION_CONTROL_DIAGNOSTIC_V1',str(paths['archive']))
        self.assertIn('cases\\R2',str(paths['archive']))
        self.assertIsNone(binding['actual_archive_bytes'])
        self.assertFalse(binding['native_execution_released'])
    def test_R1_bulk_destination_is_rejected(self):
        binding=r2.make_binding(Path(__file__).parent)
        binding['paths']['archive']=binding['paths']['archive'].replace('DISTORTION_CONTROL_DIAGNOSTIC','FLAT_BILAYER_PDMS_DEPTH_REFINEMENT').replace('cases\\R2','cases\\R1')
        with self.assertRaises(ValueError):r2.validate_binding(binding,Path(__file__).parent)
    def test_wrong_metadata_and_traversal_are_rejected(self):
        binding=r2.make_binding(Path(__file__).parent)
        with self.assertRaises(ValueError):r2.validate_binding(binding,Path(__file__).parent/'other')
        binding['paths']['tmp']=str(Path(binding['bulk_root'])/'..'/'R1')
        with self.assertRaises(ValueError):r2.validate_binding(binding,Path(__file__).parent)

if __name__=='__main__': unittest.main(verbosity=2)
