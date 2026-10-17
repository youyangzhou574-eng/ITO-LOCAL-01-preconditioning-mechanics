"""New39 tests: manufactured interface predictions, not old native results."""
import importlib.util
import math
import sys
import unittest
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'src/python'))
SPEC = importlib.util.find_spec('b01_m02_probe39')
if SPEC:
    import b01_m02_probe39 as core


class Probe39Tests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(SPEC, 'new39 API not implemented; not a historical production defect')
        self.square = np.array([[0., 0.], [1., 0.], [1., 1.], [0., 1.]])

    def test_square_conduction_matches_analytic_matrix(self):
        expected = np.array([[4,-1,-2,-1],[-1,4,-1,-2],[-2,-1,4,-1],[-1,-2,-1,4]]) / 6
        np.testing.assert_allclose(core.operators(self.square)['K'], expected, atol=2e-15, rtol=0)

    def test_source_columns_distinguish_gauss_from_nodal(self):
        r = core.operators(self.square)
        np.testing.assert_allclose(r['source_corner'], np.eye(4)/4, atol=0, rtol=0)
        self.assertAlmostEqual(r['source_gauss'][0,0], (1+1/math.sqrt(3))**2/16, places=15)
        self.assertGreater(r['source_gauss'][1,0], 0)
        np.testing.assert_allclose(np.sum(r['source_gauss'],axis=0), [.25]*4, atol=2e-16, rtol=0)

    def test_constant_field_nullspace_and_affine_energy(self):
        x=np.array([[0.,0.],[2.,0.],[1.8,1.4],[-.2,.8]])
        r=core.operators(x)
        np.testing.assert_allclose(r['K']@np.ones(4), 0, atol=1e-15)
        self.assertAlmostEqual(float(x[:,0]@r['K']@x[:,0]), r['area'], places=13)
        self.assertAlmostEqual(float(x[:,1]@r['K']@x[:,1]), r['area'], places=13)

    def test_temperature_baseline_has_no_conductive_effect(self):
        r=core.operators(self.square)
        for i in range(4):
            target=core.temperatures(i+5)
            np.testing.assert_array_equal(target, np.ones(4)+np.eye(4)[i])
            np.testing.assert_allclose(r['K']@target, r['K'][:,i], atol=2e-16)
        for step in range(1,5):np.testing.assert_array_equal(core.temperatures(step),np.ones(4))

    def test_node_reordering_preserves_geometry_and_conduction(self):
        p=[1,2,3,0];a=core.operators(self.square);b=core.operators(self.square[p])
        np.testing.assert_allclose(b['K'],a['K'][np.ix_(p,p)],atol=2e-15,rtol=0)
        self.assertAlmostEqual(a['area'],b['area'])

    def test_one_free_mechanical_dof_has_positive_stiffness(self):
        for x in [self.square,[[0,0],[2,0],[1.8,1.4],[-.2,.8]]]:
            self.assertGreater(core.operators(x)['free_u1_node3_stiffness'],0)

    def test_invalid_geometry_is_not_repaired(self):
        for x in [self.square[::-1],self.square[[0,2,1,3]],np.zeros((4,2)),[[0,0],[1,0],[math.nan,1],[0,1]]]:
            with self.assertRaises(ValueError):core.operators(x)

    def test_step_domain_and_ip_basis(self):
        for step in range(1,9):
            values=[core.source_value(step,ip) for ip in range(1,5)]
            self.assertEqual(values,[int(step==j) for j in range(1,5)] if step<=4 else [0]*4)
        for step,ip in [(0,1),(9,1),(1,0),(1,5)]:
            with self.assertRaises(ValueError):core.source_value(step,ip)

    def test_decimal_intervals_preserve_sign_and_d_exponent(self):
        from fractions import Fraction as F
        self.assertEqual(core.print_interval('-3.524D-06'),(F('-0.0000035245'),F('-0.0000035235')))
        self.assertEqual(core.print_interval('0.000E+00'),(F('-0.0005'),F('0.0005')))
        for t in ['nan','inf','1E999999','x']:
            with self.assertRaises(ValueError):core.print_interval(t)

    def test_fortran_leading_decimal_prints(self):
        from fractions import Fraction as F
        self.assertEqual(core.print_interval('-.3524D-05'),(F('-0.0000035245'),F('-0.0000035235')))

    def test_snapshot_scientific_integer_prints(self):
        rows=fixture_snapshots()
        for r in rows:
            for k in ['schema','element','npt']:r[k]=format(float(r[k]),'.6E')
        self.assertEqual(core.validate_snapshots(rows,{s:1 for s in range(1,9)})['snapshot_count'],64)

    def test_coarsely_printed_snapshot_identity_is_ambiguous(self):
        rows=fixture_snapshots();rows[0]['schema']='4E+01'
        with self.assertRaises(ValueError):core.validate_snapshots(rows,{s:1 for s in range(1,9)})

    def test_complete_rows_and_real_labels_build_raw_columns(self):
        rows=fixture_rows();got=core.validate_node_rows(rows,{s:1 for s in range(1,9)})
        self.assertEqual(got['101']['source_RFL_tokens'][0],['-1.0101E+00']*4)
        self.assertEqual(got['202']['temperature_RFL_tokens'][3],['-2.0214E+00']*4)
        self.assertFalse(got['sign_convention_qualified'])

    def test_missing_duplicate_nonfinite_and_rejected_rows_rejected(self):
        rows=fixture_rows()
        for bad in [rows[:-1],rows+[dict(rows[0])],[dict(rows[0],RFL='nan')]+rows[1:],[dict(rows[0],accepted=False)]+rows[1:],[dict(rows[0],node=99)]+rows[1:],[dict(rows[0],increment=2)]+rows[1:]]:
            with self.assertRaises(ValueError):core.validate_node_rows(bad,{s:1 for s in range(1,9)})

    def test_nonzero_baseline_not_inferred_for_missing_data(self):
        rows=fixture_rows();rows[0]=dict(rows[0],NT='0.0000')
        with self.assertRaises(ValueError):core.validate_node_rows(rows,{s:1 for s in range(1,9)})

    def test_snapshot_matches_identity_and_stateless_source(self):
        got=core.validate_snapshots(fixture_snapshots(),{s:1 for s in range(1,9)})
        self.assertEqual(got['snapshot_count'],64)
        self.assertFalse(got['all_trial_history_observed'])

    def test_bad_snapshot_does_not_become_accepted_evidence(self):
        rows=fixture_snapshots()
        for key,val in [('schema','38'),('npt','5'),('element','999'),('RPL','7.000'),('end_step_time','.500')]:
            bad=[dict(rows[0],**{key:val})]+rows[1:]
            with self.assertRaises(ValueError):core.validate_snapshots(bad,{s:1 for s in range(1,9)})


def fixture_rows():
    rows=[]
    for step in range(1,9):
        for element,nodes in [(101,[1,2,3,4]),(202,[11,12,13,14])]:
            for j,node in enumerate(nodes):
                nt=2 if step==j+5 else 1
                rows.append(dict(step=step,increment=1,accepted=True,element=element,node=node,NT=str(nt)+'.000',RFL='-'+str(element/100+node/10000)+'E+00'))
    return rows


def fixture_snapshots():
    rows=[]
    for step in range(1,9):
        for element in [101,202]:
            for ip in range(1,5):
                rows.append(dict(step=step,increment=1,accepted=True,schema='39',element=str(element),npt=str(ip),TEMP='1.000000',DTEMP='0.000000',phi='1.000000',x='0.5000',y='0.5000',RPL=str(int(step==ip)),end_step_time='1.000000'))
    return rows


if __name__=='__main__':unittest.main()
