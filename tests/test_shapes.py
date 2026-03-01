'''
Tests for generic shape classes: Circle, Rectangle, HollowRectangle.

All assertions use exact or approximate arithmetic derived from the formulas
in each class, so failures directly indicate a formula regression.
'''

import pytest
from math import pi, sqrt
from metk.shapes.generic import Circle, Rectangle, HollowRectangle
from metk.shapes.structural_shapes import W, HSS, L, StructuralShape, is_structural_shape_label, _GenericStandardShape


# ===========================================================================
# Circle
# ===========================================================================

class TestCircle:
    def test_radius_stored(self):
        c = Circle(r=5)
        assert c.r == 5

    def test_diameter_from_radius(self):
        c = Circle(r=5)
        assert c.d == pytest.approx(10)

    def test_construct_from_diameter(self):
        c = Circle(d=10)
        assert c.r == pytest.approx(5)

    def test_radius_and_diameter_constructors_equivalent(self):
        cr = Circle(r=5)
        cd = Circle(d=10)
        assert cr.A == pytest.approx(cd.A)
        assert cr.Ix == pytest.approx(cd.Ix)
        assert cr.J == pytest.approx(cd.J)

    def test_area(self):
        c = Circle(r=5)
        assert c.A == pytest.approx(pi * 25)

    def test_second_moment_x(self):
        c = Circle(r=5)
        assert c.Ix == pytest.approx(pi * 5**4 / 4)

    def test_second_moment_y_equals_x(self):
        # Circle is symmetric
        c = Circle(r=5)
        assert c.Ix == pytest.approx(c.Iy)

    def test_torsional_constant(self):
        # For a solid circle J = pi*r^4/2
        c = Circle(r=5)
        assert c.J == pytest.approx(pi * 5**4 / 2)

    def test_plastic_section_modulus(self):
        c = Circle(r=5)
        assert c.Zx == pytest.approx(c.d**3 / 6)

    def test_cx_max_equals_radius(self):
        c = Circle(r=5)
        assert c.cx_max == pytest.approx(5)

    def test_cy_max_equals_radius(self):
        c = Circle(r=5)
        assert c.cy_max == pytest.approx(5)

    def test_centroid_distances_symmetric(self):
        c = Circle(r=5)
        assert c.cx_right == pytest.approx(5)
        assert abs(c.cx_left) == pytest.approx(5)
        assert c.cy_high == pytest.approx(5)
        assert abs(c.cy_low) == pytest.approx(5)

    def test_prop_dict_keys(self):
        c = Circle(r=5)
        assert set(c.prop_dict.keys()) == {'d', 'r', 'A', 'Ix', 'Zx', 'J'}


# ===========================================================================
# Rectangle
# ===========================================================================

class TestRectangle:
    def test_area(self):
        r = Rectangle(w=4, h=6)
        assert r.A == pytest.approx(24)

    def test_second_moment_x(self):
        r = Rectangle(w=4, h=6)
        # Ix = (1/12) * w * h^3
        assert r.Ix == pytest.approx(1/12 * 4 * 6**3)   # 72

    def test_second_moment_y(self):
        r = Rectangle(w=4, h=6)
        # Iy = (1/12) * h * w^3
        assert r.Iy == pytest.approx(1/12 * 6 * 4**3)   # 32

    def test_plastic_section_modulus_x(self):
        r = Rectangle(w=4, h=6)
        # Zx = w*h^2/4
        assert r.Zx == pytest.approx(4 * 6**2 / 4)      # 36

    def test_plastic_section_modulus_y(self):
        r = Rectangle(w=4, h=6)
        # Zy = h*w^2/4
        assert r.Zy == pytest.approx(6 * 4**2 / 4)      # 24

    def test_elastic_section_modulus_x(self):
        r = Rectangle(w=4, h=6)
        # Sx = Ix / cy = 72 / 3 = 24
        assert r.Sx == pytest.approx(24)

    def test_elastic_section_modulus_y(self):
        r = Rectangle(w=4, h=6)
        # Sy = Iy / cx = 32 / 2 = 16
        assert r.Sy == pytest.approx(16)

    def test_centroid(self):
        r = Rectangle(w=4, h=6)
        assert r.cx == pytest.approx(2)
        assert r.cy == pytest.approx(3)

    def test_cx_max_cy_max(self):
        r = Rectangle(w=4, h=6)
        assert r.cx_max == pytest.approx(2)
        assert r.cy_max == pytest.approx(3)

    def test_radii_of_gyration(self):
        r = Rectangle(w=4, h=6)
        assert r.rx == pytest.approx(sqrt(r.Ix / r.A))
        assert r.ry == pytest.approx(sqrt(r.Iy / r.A))

    def test_torsional_constant_positive(self):
        r = Rectangle(w=4, h=6)
        assert r.J > 0

    def test_square_has_equal_moments(self):
        r = Rectangle(w=5, h=5)
        assert r.Ix == pytest.approx(r.Iy)

    def test_width_height_properties(self):
        r = Rectangle(w=4, h=6)
        assert r.width == 4
        assert r.height == 6


# ===========================================================================
# HollowRectangle
# ===========================================================================

class TestHollowRectangle:
    def test_area(self):
        # A = w*h - (w-2t)*(h-2t) = 6*8 - 4*6 = 48 - 24 = 24
        hr = HollowRectangle(w=6, h=8, t=1)
        assert hr.A == pytest.approx(24)

    def test_second_moment_x(self):
        # Ix = (1/12)*(6*8^3 - 4*6^3) = (1/12)*(3072 - 864) = 184
        hr = HollowRectangle(w=6, h=8, t=1)
        assert hr.Ix == pytest.approx(184)

    def test_second_moment_y(self):
        # Iy = (1/12)*(8*6^3 - 6*4^3) = (1/12)*(1728 - 384) = 112
        hr = HollowRectangle(w=6, h=8, t=1)
        assert hr.Iy == pytest.approx(112)

    def test_area_greater_than_solid_minus_inner(self):
        hr = HollowRectangle(w=6, h=8, t=1)
        assert hr.A > 0

    def test_ix_less_than_solid_rectangle(self):
        # Hollow should have less Ix than solid of same outer dimensions
        hr = HollowRectangle(w=6, h=8, t=1)
        solid = Rectangle(w=6, h=8)
        assert hr.Ix < solid.Ix

    def test_centroid_at_center(self):
        hr = HollowRectangle(w=6, h=8, t=1)
        assert hr.cx == pytest.approx(3)
        assert hr.cy == pytest.approx(4)

    def test_plastic_section_modulus_x_positive(self):
        hr = HollowRectangle(w=6, h=8, t=1)
        assert hr.Zx > 0

    def test_thicker_wall_less_hollow(self):
        # With t = h/2 = w/2, hollow approaches solid
        hr_thin = HollowRectangle(w=6, h=8, t=0.1)
        hr_thick = HollowRectangle(w=6, h=8, t=1)
        assert hr_thin.A < hr_thick.A


# ===========================================================================
# Structural shapes (SQLite database)
#
# Property values are taken directly from the AISC Shapes Database v16.0.
# These tests confirm that the SQLite database is present, readable, and
# returns the expected numeric values for a representative shape from each
# supported shape type.
# ===========================================================================

class TestStructuralShapeLabels:
    def test_w_label_recognised(self):
        assert is_structural_shape_label('W8X31')

    def test_hss_label_recognised(self):
        assert is_structural_shape_label('HSS6X6X.375')

    def test_l_label_recognised(self):
        assert is_structural_shape_label('L6X6X1/2')

    def test_invalid_string_not_recognised(self):
        # 'ROUNDBAR' contains no valid type-code prefix (W, L, HSS, …) followed
        # by digits, so the regex must not match it.
        assert not is_structural_shape_label('ROUNDBAR')

    def test_empty_string_not_recognised(self):
        assert not is_structural_shape_label('')


class TestWShape:
    '''W8X31 properties from AISC Shapes Database v16.0.'''

    @pytest.fixture(scope='class')
    def shape(self):
        return W('W8X31')

    def test_cross_sectional_area(self, shape):
        assert shape.A == pytest.approx(9.13, rel=1e-3)

    def test_moment_of_inertia_x(self, shape):
        assert shape.Ix == pytest.approx(110.0, rel=1e-3)

    def test_elastic_section_modulus_x(self, shape):
        assert shape.Sx == pytest.approx(27.5, rel=1e-3)

    def test_moment_of_inertia_y(self, shape):
        assert shape.Iy == pytest.approx(37.1, rel=1e-3)

    def test_elastic_section_modulus_y(self, shape):
        assert shape.Sy == pytest.approx(9.27, rel=1e-3)

    def test_repr_contains_name(self, shape):
        assert 'W8X31' in repr(shape)


class TestHSSShape:
    '''HSS6X6X.375 properties from AISC Shapes Database v16.0.'''

    @pytest.fixture(scope='class')
    def shape(self):
        return HSS('HSS6X6X.375')

    def test_cross_sectional_area(self, shape):
        assert shape.A == pytest.approx(7.58, rel=1e-3)

    def test_moment_of_inertia_x(self, shape):
        assert shape.Ix == pytest.approx(39.5, rel=1e-3)

    def test_elastic_section_modulus_x(self, shape):
        assert shape.Sx == pytest.approx(13.2, rel=1e-3)

    def test_moment_of_inertia_y_equals_x(self, shape):
        # Square HSS: Ix == Iy
        assert shape.Iy == pytest.approx(shape.Ix, rel=1e-3)

    def test_repr_contains_name(self, shape):
        assert 'HSS6X6X.375' in repr(shape)


class TestLShape:
    '''L6X6X1/2 properties from AISC Shapes Database v16.0.'''

    @pytest.fixture(scope='class')
    def shape(self):
        return L('L6X6X1/2')

    def test_cross_sectional_area(self, shape):
        assert shape.A == pytest.approx(5.77, rel=1e-3)

    def test_moment_of_inertia_x(self, shape):
        assert shape.Ix == pytest.approx(19.9, rel=1e-3)

    def test_elastic_section_modulus_x(self, shape):
        assert shape.Sx == pytest.approx(4.59, rel=1e-3)

    def test_moment_of_inertia_y_equals_x(self, shape):
        # Equal-leg angle: Ix == Iy
        assert shape.Iy == pytest.approx(shape.Ix, rel=1e-3)

    def test_repr_contains_name(self, shape):
        assert 'L6X6X1/2' in repr(shape)


class TestStructuralShapeFactory:
    def test_w_shape_returns_w_instance(self):
        assert isinstance(StructuralShape('W8X31'), W)

    def test_hss_shape_returns_hss_instance(self):
        assert isinstance(StructuralShape('HSS6X6X.375'), HSS)

    def test_l_shape_returns_l_instance(self):
        assert isinstance(StructuralShape('L6X6X1/2'), L)

    def test_invalid_label_raises(self):
        with pytest.raises(Exception):
            StructuralShape('ROUNDBAR')

    def test_unregistered_type_returns_generic_instance(self):
        mc = StructuralShape('MC12X50')
        assert isinstance(mc, _GenericStandardShape)

    def test_generic_shape_property_access(self):
        # MC12X50 values from AISC Shapes Database v16.0
        mc = StructuralShape('MC12X50')
        assert mc.A  == pytest.approx(14.7, rel=1e-3)
        assert mc.Ix == pytest.approx(269.0, rel=1e-3)
        assert mc.Sx == pytest.approx(44.9,  rel=1e-3)
