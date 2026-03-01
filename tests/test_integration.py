"""
Integration tests for StructuralObject / Member.

Uses only generic shapes and custom materials to avoid dependence on external
pickle/JSON databases, making these tests fully self-contained.

Stress formulas under pure axial load (no bending, shear, or torsion):
    Sa  = f_z / A
    Svx = Svy = 0
    Sbx = Sby = 0
    Txy = 0
    => All four corners have identical uniaxial state: [0, 0, Sa, 0, 0, 0]
    => von_mises = Sa  (uniaxial)
    => max_shear = Sa/2
"""

import pytest
from math import pi
from metk.structural.member import Member
from metk.shapes.generic import Circle, Rectangle
from metk.materials.materials import Material
from metk.loads import Load


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def circle_shape():
    return Circle(r=1)  # A = pi, Ix = Iy = J = pi/4


@pytest.fixture
def steel():
    return Material(
        **{"YS_min": 36000, "UTS_min": 58000, "modulus of elasticity": 29e6}
    )


@pytest.fixture
def axial_load():
    return Load(fz=1000)


@pytest.fixture
def axial_member(circle_shape, axial_load, steel):
    return Member(shape=circle_shape, loads=axial_load, material=steel)


# ===========================================================================
# Construction
# ===========================================================================


class TestMemberConstruction:
    def test_shape_assigned(self, axial_member, circle_shape):
        assert axial_member.shape is circle_shape

    def test_loads_assigned(self, axial_member, axial_load):
        assert axial_member.loads is axial_load

    def test_material_assigned(self, axial_member, steel):
        assert axial_member.material is steel

    def test_construct_with_shape_dict(self, axial_load, steel):
        m = Member(
            shape={
                "name": "test",
                "A": 5,
                "Ix": 10,
                "Iy": 10,
                "J": 5,
                "cx_right": 1,
                "cx_left": -1,
                "cy_high": 1,
                "cy_low": -1,
            },
            loads=axial_load,
            material=steel,
        )
        assert m.shape is not None

    def test_loads_created_from_kwargs(self, circle_shape, steel):
        m = Member(shape=circle_shape, material=steel, f_z=500)
        assert m.loads.fz == 500

    def test_default_name(self, axial_member):
        assert axial_member.name is not None


# ===========================================================================
# Pure axial stress
# ===========================================================================


class TestPureAxialStress:
    def test_sa_formula(self, axial_member):
        # Sa = f_z / A = 1000 / pi
        assert axial_member.Sa == pytest.approx(1000 / pi)

    def test_no_shear_stress(self, axial_member):
        # f_x = f_y = 0 => Svx = Svy = 0
        assert axial_member.Svx == pytest.approx(0)
        assert axial_member.Svy == pytest.approx(0)

    def test_no_bending_stress(self, axial_member):
        # m_x = m_y = 0 => Sbx = Sby = 0
        assert axial_member.Sbx == pytest.approx(0)
        assert axial_member.Sby == pytest.approx(0)

    def test_no_torsion(self, axial_member):
        # m_z = 0 => all Txy corner values = 0
        assert axial_member.Txy_ll == pytest.approx(0)
        assert axial_member.Txy_lr == pytest.approx(0)
        assert axial_member.Txy_ul == pytest.approx(0)
        assert axial_member.Txy_ur == pytest.approx(0)

    def test_von_mises_equals_sa_for_uniaxial(self, axial_member):
        # Pure axial => von Mises = |Sa|
        assert axial_member.von_mises == pytest.approx(abs(axial_member.Sa))

    def test_corner_elements_all_equal(self, axial_member):
        # All four corners have the same state under pure axial load
        vm_ll = axial_member.Sll.von_mises
        vm_lr = axial_member.Slr.von_mises
        vm_ul = axial_member.Sul.von_mises
        vm_ur = axial_member.Sur.von_mises
        assert vm_ll == pytest.approx(vm_lr)
        assert vm_ll == pytest.approx(vm_ul)
        assert vm_ll == pytest.approx(vm_ur)


# ===========================================================================
# Combined load: axial + bending
# ===========================================================================


class TestAxialPlusBending:
    def test_bending_adds_to_one_side_subtracts_from_other(self):
        shape = Rectangle(w=2, h=4)
        # mx bends about x-x: high side gets positive, low side negative
        load = Load(fz=0, mx=1000)
        m = Member(shape=shape, loads=load, material=Material(YS_min=36000))
        # cy_high = 2, cy_low = -2, Ix = (1/12)*2*4^3 = 128/12
        expected_high = 1000 * shape.cy_high / shape.Ix
        expected_low = 1000 * shape.cy_low / shape.Ix
        assert m.Sbx_high == pytest.approx(expected_high)
        assert m.Sbx_low == pytest.approx(expected_low)
        assert m.Sbx_high == pytest.approx(-m.Sbx_low)

    def test_max_stress_on_tension_side(self):
        shape = Rectangle(w=2, h=4)
        load = Load(fz=100, mx=1000)
        m = Member(shape=shape, loads=load, material=Material(YS_min=36000))
        # Tension side (high): Sa + Sbx_high
        # Compression side (low): Sa + Sbx_low (Sbx_low < 0)
        assert m.Sbx_high > abs(m.Sbx_low) or m.Sbx_high == pytest.approx(
            abs(m.Sbx_low)
        )


# ===========================================================================
# Output rendering
# ===========================================================================


class TestMemberOutput:
    def test_results_table_renders(self, axial_member):
        table = axial_member.results_table
        assert isinstance(table, str)
        assert len(table) > 0

    def test_series_contains_sa(self, axial_member):
        s = axial_member.series
        assert "Sa" in s.index

    def test_series_sa_value(self, axial_member):
        s = axial_member.series
        assert s["Sa"] == pytest.approx(1000 / pi)

    def test_get_delegates_to_shape(self, axial_member):
        # get() should delegate shape properties via prop_lookup
        A_via_get = axial_member.get("A")
        assert A_via_get == pytest.approx(pi)
