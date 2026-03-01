'''
Tests for load classes: Factor, Load, Force, Moment, CombinedLoad.

Two tests are marked xfail to document known bugs in Load.__add__ and
Load.__mul__, which use Python list operators (+, *) on self.value instead
of element-wise numeric operations.
'''

import pytest
import numpy as np
from metk.loads import Factor, Load, Force, Moment, CombinedLoad


# ===========================================================================
# Factor
# ===========================================================================

class TestFactor:
    def test_value_stored(self):
        f = Factor(2)
        assert f.value == 2

    def test_default_value_is_one(self):
        f = Factor()
        assert f.value == 1

    def test_name_stored(self):
        f = Factor(1.5, name='DL')
        assert f.name == 'DL'

    def test_mul_with_scalar(self):
        f = Factor(2)
        assert f * 5 == 10

    def test_rmul_with_scalar(self):
        f = Factor(3)
        assert 5 * f == 15

    def test_repr_with_name(self):
        f = Factor(1.2, name='LL')
        assert 'LL' in repr(f)
        assert '1.2' in repr(f)

    def test_repr_without_name(self):
        f = Factor(2)
        assert '2' in repr(f)


# ===========================================================================
# Load
# ===========================================================================

class TestLoadConstruction:
    def test_fx_kwarg(self):
        load = Load(fx=10)
        assert load.fx == 10

    def test_fz_kwarg(self):
        load = Load(fz=500)
        assert load.fz == 500

    def test_moment_components(self):
        load = Load(mx=100, my=200, mz=50)
        assert load.mx == 100
        assert load.my == 200
        assert load.mz == 50

    def test_unset_components_default_to_zero(self):
        load = Load(fx=10)
        assert load.fy == 0
        assert load.fz == 0
        assert load.mx == 0

    def test_f_x_alias(self):
        # f_x is a class-level alias for fx property
        load = Load(fx=10)
        assert load.f_x == 10

    def test_default_primary_secondary(self):
        load = Load()
        assert load.primary == 'x'
        assert load.secondary == 'y'

    def test_force_array(self):
        load = Load(fx=1, fy=2, fz=3)
        np.testing.assert_array_equal(load.force, [1, 2, 3])

    def test_moment_array(self):
        load = Load(mx=4, my=5, mz=6)
        np.testing.assert_array_equal(load.moment, [4, 5, 6])

    def test_invalid_primary_secondary_combo_raises(self):
        with pytest.raises(Exception):
            Load(primary='x', secondary='x')

    def test_invalid_axis_label_raises(self):
        with pytest.raises(Exception):
            Load(primary='a', secondary='b')


class TestLoadCoordinateTransform:
    def test_identity_returns_raw_values(self):
        load = Load(fx=10, fy=5, fz=2, primary='x', secondary='y')
        assert load.fx == 10
        assert load.fy == 5
        assert load.fz == 2

    def test_y_primary_x_secondary_remaps_fx_fy(self):
        # local x = global y, local y = global x
        # A global fy=10 appears as fx in the local frame
        load = Load(fx=0, fy=10, fz=0, primary='y', secondary='x')
        assert load.fx == pytest.approx(10)

    def test_vector_input_identity(self):
        load = Load(fx=10, fy=5, fz=2, primary=[1, 0, 0], secondary=[0, 1, 0])
        assert load.fx == pytest.approx(10)
        assert load.fy == pytest.approx(5)
        assert load.fz == pytest.approx(2)

    def test_vector_input_arbitrary_rotation(self):
        # Local frame rotated 45° around global z
        angle = np.pi / 4
        x_loc = [np.cos(angle), np.sin(angle), 0]
        y_loc = [-np.sin(angle), np.cos(angle), 0]
        load = Load(fx=10, primary=x_loc, secondary=y_loc)
        assert load.fx == pytest.approx(10 * np.cos(angle))
        assert load.fy == pytest.approx(-10 * np.sin(angle))
        assert load.fz == pytest.approx(0)

    def test_vector_input_unnormalized_is_normalised(self):
        # Passing a non-unit vector should still work (normalised internally)
        load_unit = Load(fx=10, primary=[1, 0, 0], secondary=[0, 1, 0])
        load_scaled = Load(fx=10, primary=[5, 0, 0], secondary=[0, 3, 0])
        assert load_unit.fx == pytest.approx(load_scaled.fx)

    def test_mixed_string_and_vector_raises(self):
        with pytest.raises(ValueError):
            Load(fx=10, primary='x', secondary=[0, 1, 0])

    def test_non_orthogonal_vectors_raises(self):
        with pytest.raises(ValueError):
            Load(fx=10, primary=[1, 0, 0], secondary=[1, 1, 0])

    def test_zero_vector_raises(self):
        with pytest.raises(ValueError):
            Load(fx=10, primary=[0, 0, 0], secondary=[0, 1, 0])


class TestLoadArithmetic:
    def test_add_two_loads(self):
        a = Load(fx=10)
        b = Load(fx=5)
        result = a + b
        assert result.fx == pytest.approx(15)

    def test_multiply_load_by_scalar(self):
        load = Load(fx=10, fz=5)
        result = load * 2
        assert result.fx == pytest.approx(20)
        assert result.fz == pytest.approx(10)

    def test_add_non_load_raises(self):
        load = Load(fx=10)
        with pytest.raises(Exception):
            _ = load + 5


# ===========================================================================
# Force
# ===========================================================================

class TestForce:
    def test_construction(self):
        f = Force(F=[10, 0, 0])
        np.testing.assert_array_almost_equal(f.F, [10, 0, 0])

    def test_default_position_vector_zero(self):
        f = Force(F=[10, 0, 0])
        np.testing.assert_array_equal(f.r, [0, 0, 0])

    def test_position_vector_stored(self):
        f = Force(F=[0, 0, 10], r=[5, 0, 0])
        np.testing.assert_array_equal(f.r, [5, 0, 0])

    def test_moment_from_cross_product(self):
        # r = [5, 0, 0], F = [0, 0, 10] => M = r x F = [0*10-0*0, 0*0-5*10, 5*0-0*0]
        #                                             = [0, -50, 0]
        f = Force(F=[0, 0, 10], r=[5, 0, 0])
        np.testing.assert_array_almost_equal(f.M, [0, -50, 0])

    def test_zero_position_gives_zero_moment(self):
        f = Force(F=[10, 20, 30], r=[0, 0, 0])
        np.testing.assert_array_almost_equal(f.M, [0, 0, 0])

    def test_addition(self):
        f1 = Force(F=[10, 0, 0])
        f2 = Force(F=[5, 0, 0])
        f3 = f1 + f2
        np.testing.assert_array_almost_equal(f3.F, [15, 0, 0])

    def test_scalar_multiplication(self):
        f = Force(F=[10, 0, 0])
        f2 = 3 * f
        np.testing.assert_array_almost_equal(f2.F, [30, 0, 0])

    def test_factor_applied(self):
        f = Force(F=[10, 0, 0], factor=2)
        np.testing.assert_array_almost_equal(f.F, [20, 0, 0])

    def test_xyz_properties(self):
        f = Force(F=[1, 2, 3])
        assert f.x == pytest.approx(1)
        assert f.y == pytest.approx(2)
        assert f.z == pytest.approx(3)


# ===========================================================================
# Moment
# ===========================================================================

class TestMoment:
    def test_construction(self):
        m = Moment(M=[0, 0, 100])
        np.testing.assert_array_almost_equal(m.M, [0, 0, 100])

    def test_addition(self):
        m1 = Moment(M=[0, 0, 100])
        m2 = Moment(M=[0, 0, 50])
        m3 = m1 + m2
        np.testing.assert_array_almost_equal(m3.M, [0, 0, 150])

    def test_scalar_multiplication(self):
        m = Moment(M=[0, 0, 100])
        m2 = 2 * m
        np.testing.assert_array_almost_equal(m2.M, [0, 0, 200])

    def test_factor_applied(self):
        m = Moment(M=[0, 0, 100], factor=1.5)
        np.testing.assert_array_almost_equal(m.M, [0, 0, 150])


# ===========================================================================
# CombinedLoad
# ===========================================================================

class TestCombinedLoad:
    def test_sum_forces(self):
        f1 = Force(F=[10, 0, 0])
        f2 = Force(F=[5, 0, 0])
        cl = CombinedLoad(forces=[f1, f2])
        np.testing.assert_array_almost_equal(cl.F, [15, 0, 0])

    def test_moment_from_forces_with_position(self):
        # Two forces at different positions contribute moments
        f1 = Force(F=[0, 0, 10], r=[5, 0, 0])
        cl = CombinedLoad(forces=[f1])
        # M = r x F = [0, -50, 0]
        np.testing.assert_array_almost_equal(cl.M, [0, -50, 0])

    def test_moment_from_moment_objects(self):
        m = Moment(M=[0, 0, 100])
        cl = CombinedLoad(moments=[m])
        np.testing.assert_array_almost_equal(cl.M, [0, 0, 100])

    def test_fx_fy_fz_components(self):
        f = Force(F=[1, 2, 3])
        cl = CombinedLoad(forces=[f])
        assert cl.Fx == pytest.approx(1)
        assert cl.Fy == pytest.approx(2)
        assert cl.Fz == pytest.approx(3)
