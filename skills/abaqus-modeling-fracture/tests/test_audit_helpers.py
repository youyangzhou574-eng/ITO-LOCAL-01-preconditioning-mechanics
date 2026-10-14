"""Ordinary Python tests; no Abaqus/Fortran/ODB or network is exercised."""
import importlib.util
import math
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'scripts' / 'audit_helpers.py'
H = None
if PATH.exists():
    spec = importlib.util.spec_from_file_location('audit_helpers', PATH)
    H = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(H)


class AuditHelpers(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(H, 'Offline audit helpers have not been implemented')

    def test_label_selection_keeps_shear(self):
        self.assertEqual(H.select_components(['11','22','33','12','13','23'], [1,2,30,4,5,6], ['11','22','12']), (1.,2.,4.))

    def test_missing_component_is_not_zero(self):
        with self.assertRaises(ValueError):
            H.select_components(['11','22'], [1,2], ['11','22','12'])

    def test_duplicate_component_is_ambiguous(self):
        with self.assertRaises(ValueError):
            H.select_components(['11','11'], [1,2], ['11'])

    def test_component_shape_mismatch(self):
        with self.assertRaises(ValueError):
            H.select_components(['11'], [1,2], ['11'])

    def test_component_nonfinite(self):
        with self.assertRaises(ValueError):
            H.select_components(['11'], [math.nan], ['11'])

    def frame(self, inc=3, time=None):
        return dict(job='W1', step='BIRTH', increment=inc, time_basis='step', time_s=struct.unpack('f', struct.pack('f', .3))[0] if time is None else time)

    def rows(self):
        return [dict(job='W1', step='BIRTH', increment=3, time_basis='step', time_token='0.300', accepted=True)]

    def test_float32_printed_time_match(self):
        r = H.match_frame_to_sta(self.frame(), self.rows())
        self.assertTrue(r['matched'])
        self.assertEqual(r['time_storage_type'], 'NOT_INFERRED')

    def test_same_increment_wrong_time_rejected(self):
        self.assertFalse(H.match_frame_to_sta(self.frame(time=.31), self.rows())['matched'])

    def test_missing_native_increment_unresolved(self):
        r = H.match_frame_to_sta(self.frame(4), self.rows())
        self.assertIsNone(r['matched'])
        self.assertEqual(r['status'], 'ACCEPTANCE_UNRESOLVED')

    def test_wrong_job_not_matched(self):
        f=self.frame(); f['job']='OTHER'
        self.assertIsNone(H.match_frame_to_sta(f,self.rows())['matched'])

    def test_total_time_not_step_time(self):
        f=self.frame(); f['time_basis']='total'
        self.assertIsNone(H.match_frame_to_sta(f,self.rows())['matched'])

    def test_unaccepted_attempt_does_not_count(self):
        r=self.rows(); r[0]['accepted']=False
        self.assertIsNone(H.match_frame_to_sta(self.frame(),r)['matched'])

    def test_conflicting_sta_rows_unresolved(self):
        r=self.rows(); r.append(dict(r[0], time_token='0.310'))
        self.assertEqual(H.match_frame_to_sta(self.frame(),r)['status'], 'AMBIGUOUS_ACCEPTANCE')

    def test_initial_frame_needs_separate_evidence(self):
        self.assertIsNone(H.match_frame_to_sta(self.frame(0,0),[])['matched'])

    def test_nan_frame_rejected(self):
        with self.assertRaises(ValueError):
            H.match_frame_to_sta(self.frame(time=math.nan),self.rows())

    def test_fortran_decimal_token(self):
        r=self.rows(); r[0]['time_token']='3.000D-01'
        self.assertTrue(H.match_frame_to_sta(self.frame(),r)['matched'])

    def samples(self):
        return [dict(branch='release', strain=x, value=y, native_index=i) for i,x,y in [(0,0,0),(1,.1,1),(2,.1,2),(3,.2,4)]]

    def test_last_duplicate_within_branch(self):
        c=H.branch_curve(self.samples(),'release',1)
        self.assertEqual([r['native_index'] for r in c],[0,2,3])

    def test_reloading_not_merged_with_release(self):
        s=self.samples()+[dict(branch='reload',strain=.1,value=100,native_index=4)]
        self.assertEqual(H.branch_curve(s,'release',1)[1]['value'],2.)
        self.assertEqual(H.branch_curve(s,'reload',1)[0]['value'],100.)

    def test_decreasing_branch_supported(self):
        s=[dict(branch='release',strain=x,value=i,native_index=i) for i,x in enumerate([.2,.1,0])]
        self.assertEqual([r['strain'] for r in H.branch_curve(s,'release',-1)],[0.,.1,.2])

    def test_reversal_not_silently_sorted(self):
        s=self.samples()+[dict(branch='release',strain=.15,value=1,native_index=4)]
        with self.assertRaises(ValueError): H.branch_curve(s,'release',1)

    def test_near_duplicate_not_coalesced(self):
        s=self.samples(); s[2]['strain']=.1000000000001
        self.assertEqual(len(H.branch_curve(s,'release',1)),4)

    def test_missing_branch_rejected(self):
        with self.assertRaises(ValueError): H.branch_curve(self.samples(),'absent',1)

    def test_interpolation_has_source_bracket(self):
        c=H.branch_curve(self.samples(),'release',1); r=H.interpolate_bounded(c,.15)
        self.assertAlmostEqual(r['value'],3.)
        self.assertEqual(r['native_indices'],[2,3])

    def test_no_extrapolation_even_tiny(self):
        c=H.branch_curve(self.samples(),'release',1)
        with self.assertRaises(ValueError): H.interpolate_bounded(c,.200000000000001)

    def test_prefix_unknown_is_not_true(self):
        r=H.valid_prefix([True,None,True,False])
        self.assertEqual(r['last_proven_valid_index'],0)
        self.assertEqual(r['first_observed_invalid_index'],3)
        self.assertEqual(r['first_unproven_index'],1)

    def test_prefix_no_recovery_after_false(self):
        self.assertEqual(H.valid_prefix([True,False,True])['last_proven_valid_index'],0)

    def test_prefix_not_started(self):
        self.assertIsNone(H.valid_prefix([None,False])['last_proven_valid_index'])

    def test_integer_flags_not_booleans(self):
        with self.assertRaises(ValueError): H.valid_prefix([1])

    def test_at2_undeformed(self):
        r=H.at2_homogeneous(0.,.005,.00075,1e-7)
        self.assertEqual(r['d'],0.)
        self.assertEqual(r['g'],1.)

    def test_at2_stationary_equation(self):
        H0=2.3; gc=.005; ell=.00075; k=1e-7
        d=H.at2_homogeneous(H0,gc,ell,k)['d']
        self.assertAlmostEqual(-2*(1-k)*(1-d)*H0+gc*d/ell,0.,places=12)

    def test_at2_no_nonzero_initial_threshold(self):
        self.assertGreater(H.at2_homogeneous(1e-12,.005,.00075,0.)['d'],0.)

    def test_at2_ell_is_model_parameter(self):
        self.assertGreater(H.at2_homogeneous(1.,.005,.0015,0.)['d'],H.at2_homogeneous(1.,.005,.00075,0.)['d'])

    def test_at2_bad_inputs(self):
        for args in [(-1,.005,.00075,0),(1,0,.001,0),(1,.005,0,0),(1,.005,.001,1)]:
            with self.assertRaises(ValueError): H.at2_homogeneous(*args)

    def test_geometric_misfit_is_not_imposed_film_strain(self):
        x,y=H.ideal_free_misfit(.1)
        self.assertAlmostEqual(x,-.1/1.1)
        self.assertAlmostEqual(y,math.sqrt(1.1)-1)

    def cube(self):
        return [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]

    def test_hex_mapping_unit_cube(self):
        values=H.hex8_mapping_dets(self.cube())
        self.assertEqual(len(values),17)
        self.assertTrue(all(abs(v-.125)<1e-14 for v in values))

    def test_hex_rigid_rotation_translation(self):
        nodes=[(100-y,200+x,300+z) for x,y,z in self.cube()]
        self.assertTrue(all(abs(v-.125)<1e-14 for v in H.hex8_mapping_dets(nodes)))

    def test_hex_inversion_not_absolute_value(self):
        self.assertTrue(all(v<0 for v in H.hex8_mapping_dets([(-x,y,z) for x,y,z in self.cube()])))

    def test_hex_volume_units_scale_cubically(self):
        self.assertTrue(all(abs(v-1.)<1e-13 for v in H.hex8_mapping_dets([(2*x,2*y,2*z) for x,y,z in self.cube()])))

    def test_hex_nonfinite_rejected(self):
        n=self.cube(); n[0]=(math.nan,0,0)
        with self.assertRaises(ValueError): H.hex8_mapping_dets(n)


if __name__=='__main__': unittest.main()
