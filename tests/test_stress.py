'''
Tests for StressElement.

Principal stress values for simple states of stress have known closed-form
solutions that are used as ground truth here.
'''

import pytest
import numpy as np
from metk.stress.core import StressElement, SRSS


# ===========================================================================
# SRSS utility
# ===========================================================================

class TestSRSS:
    def test_single_value(self):
        assert SRSS(3) == pytest.approx(3)

    def test_two_values(self):
        # sqrt(3^2 + 4^2) = 5
        assert SRSS(3, 4) == pytest.approx(5)

    def test_three_values(self):
        assert SRSS(1, 1, 1) == pytest.approx(np.sqrt(3))

    def test_zero(self):
        assert SRSS(0, 0) == pytest.approx(0)


# ===========================================================================
# StressElement construction
# ===========================================================================

class TestStressElementConstruction:
    def test_construct_from_6_component_list(self):
        s = StressElement([100, 0, 0, 0, 0, 0])
        assert s.Sx == pytest.approx(100)
        assert s.Sy == pytest.approx(0)
        assert s.Sz == pytest.approx(0)

    def test_construct_from_6_component_array(self):
        s = StressElement(np.array([50, 30, 20, 10, 5, 2]))
        assert s.Sx == pytest.approx(50)
        assert s.Sy == pytest.approx(30)
        assert s.Sz == pytest.approx(20)

    def test_construct_from_3x3_matrix(self):
        S = np.array([[100, 0, 0],
                      [0,   0, 0],
                      [0,   0, 0]])
        s = StressElement(S)
        assert s.Sx == pytest.approx(100)
        assert s.Sy == pytest.approx(0)
        assert s.Sz == pytest.approx(0)

    def test_6_component_and_3x3_give_same_result(self):
        S_3x3 = np.array([[100, 20,  5],
                           [20,  50, 10],
                           [5,   10, 30]])
        S_6 = [100, 50, 30, 20, 5, 10]
        s1 = StressElement(S_6)
        s2 = StressElement(S_3x3)
        assert s1.Sx == pytest.approx(s2.Sx)
        assert s1.Sy == pytest.approx(s2.Sy)
        assert s1.Sz == pytest.approx(s2.Sz)
        assert s1.Sxy == pytest.approx(s2.Sxy)

    def test_name_stored(self):
        s = StressElement([0, 0, 0, 0, 0, 0], name='test')
        assert s.name == 'test'

    def test_shear_aliases(self):
        # Syx == Sxy, Szy == Syz, Sxz == Szx
        s = StressElement([0, 0, 0, 10, 20, 30])
        assert s.Syx == s.Sxy
        assert s.Szy == s.Syz
        assert s.Sxz == s.Szx


# ===========================================================================
# Uniaxial stress state — all answers known analytically
# ===========================================================================

class TestUniaxialStress:
    '''
    S = [[100, 0, 0], [0, 0, 0], [0, 0, 0]]
    Eigenvalues: 100, 0, 0
    P1=100, P2=0, P3=0
    von_mises = 100
    max_shear = tau1 = (P1-P3)/2 = 50
    intensity = max(|P1-P2|, |P2-P3|, |P3-P1|) = 100
    '''
    @pytest.fixture
    def uniaxial(self):
        return StressElement([100, 0, 0, 0, 0, 0])

    def test_p1(self, uniaxial):
        assert uniaxial.P1 == pytest.approx(100)

    def test_p2(self, uniaxial):
        assert uniaxial.P2 == pytest.approx(0, abs=1e-10)

    def test_p3(self, uniaxial):
        assert uniaxial.P3 == pytest.approx(0, abs=1e-10)

    def test_von_mises(self, uniaxial):
        assert uniaxial.von_mises == pytest.approx(100)

    def test_max_shear(self, uniaxial):
        # tau1 = (P1 - P3) / 2 = 50
        assert uniaxial.max_shear == pytest.approx(50)

    def test_intensity(self, uniaxial):
        assert uniaxial.intensity == pytest.approx(100)

    def test_principal_stresses_sorted_descending(self, uniaxial):
        p1, p2, p3 = uniaxial.principals
        assert p1 >= p2 >= p3


# ===========================================================================
# Hydrostatic stress state — all principals equal, no shear, zero von Mises
# ===========================================================================

class TestHydrostaticStress:
    '''
    S = 50*I (identity)
    P1 = P2 = P3 = 50
    von_mises = 0
    max_shear = 0
    intensity = 0
    '''
    @pytest.fixture
    def hydrostatic(self):
        return StressElement([50, 50, 50, 0, 0, 0])

    def test_all_principals_equal(self, hydrostatic):
        p1, p2, p3 = hydrostatic.principals
        assert p1 == pytest.approx(50)
        assert p2 == pytest.approx(50)
        assert p3 == pytest.approx(50)

    def test_von_mises_is_zero(self, hydrostatic):
        assert hydrostatic.von_mises == pytest.approx(0, abs=1e-10)

    def test_max_shear_is_zero(self, hydrostatic):
        assert hydrostatic.max_shear == pytest.approx(0, abs=1e-10)

    def test_intensity_is_zero(self, hydrostatic):
        assert hydrostatic.intensity == pytest.approx(0, abs=1e-10)


# ===========================================================================
# Pure shear stress state
# ===========================================================================

class TestPureShear:
    '''
    S = [[0, tau, 0], [tau, 0, 0], [0, 0, 0]]  with tau=100
    Eigenvalues: +100, -100, 0
    P1=100, P2=0, P3=-100
    von_mises = sqrt(0.5*(200^2 + 100^2 + 100^2)) = sqrt(0.5*60000) = sqrt(30000)
              = 100*sqrt(3) ≈ 173.2
    max_shear = (P1-P3)/2 = 100
    '''
    @pytest.fixture
    def pure_shear(self):
        # [Sx, Sy, Sz, Sxy, Szx, Syz] -> Sxy=tau=100, rest=0
        return StressElement([0, 0, 0, 100, 0, 0])

    def test_p1_positive(self, pure_shear):
        assert pure_shear.P1 == pytest.approx(100)

    def test_p3_negative(self, pure_shear):
        assert pure_shear.P3 == pytest.approx(-100)

    def test_von_mises(self, pure_shear):
        assert pure_shear.von_mises == pytest.approx(100 * np.sqrt(3))

    def test_max_shear(self, pure_shear):
        assert pure_shear.max_shear == pytest.approx(100)


# ===========================================================================
# Symmetric stress tensor (S matrix should be symmetric)
# ===========================================================================

class TestSymmetry:
    def test_s_matrix_is_symmetric(self):
        s = StressElement([10, 20, 30, 5, 3, 7])
        S = s.S
        np.testing.assert_array_almost_equal(S, S.T)

    def test_shear_components_symmetric(self):
        s = StressElement([0, 0, 0, 10, 20, 30])
        assert s.Sxy == s.Syx
        assert s.Syz == s.Szy
        assert s.Szx == s.Sxz
