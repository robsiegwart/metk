'''
Tests for material classes: Material (custom) and NamedMaterial/A36 (library).

A36.json values (USCS units):
    YS_min  = 36000 psi
    UTS_min = 58000 psi
    E       = 29e6  psi
    density = 0.284 lb/in^3
'''

import pytest
from metk.materials.materials import Material, NamedMaterial
from metk.materials.common import A36, A500_GrB, E60XX
from metk.materials.base_materials import named_material_exists


# ===========================================================================
# named_material_exists helper
# ===========================================================================

class TestNamedMaterialExists:
    def test_a36_exists(self):
        assert named_material_exists('A36') is True

    def test_nonexistent_material(self):
        assert named_material_exists('NotAMaterial') is False


# ===========================================================================
# Material (custom)
# ===========================================================================

class TestCustomMaterial:
    def test_name_defaults(self):
        m = Material()
        assert m.name == 'User-defined material'

    def test_custom_name(self):
        m = Material(name='My Steel')
        assert m.name == 'My Steel'

    def test_fy_alias_resolves_ys_min(self):
        # Fy is an alias for YS_min in material_prop_aliases
        m = Material(YS_min=36000)
        assert m.Fy == 36000

    def test_ys_alias_resolves_ys_min(self):
        m = Material(YS_min=36000)
        assert m.YS == 36000

    def test_fu_alias_resolves_uts_min(self):
        m = Material(UTS_min=58000)
        assert m.Fu == 58000

    def test_e_alias_resolves_modulus(self):
        m = Material(**{'modulus of elasticity': 29e6})
        assert m.E == pytest.approx(29e6)

    def test_multiple_properties(self):
        m = Material(YS_min=50000, UTS_min=65000)
        assert m.Fy == 50000
        assert m.Fu == 65000

    def test_repr_is_name(self):
        m = Material(name='TestMat')
        assert repr(m) == 'TestMat'


# ===========================================================================
# NamedMaterial / library materials
# ===========================================================================

class TestNamedMaterial:
    def test_construct_a36(self):
        m = NamedMaterial('A36')
        assert m is not None

    def test_name(self):
        m = NamedMaterial('A36')
        assert m.name == 'A36'

    def test_fy(self):
        m = NamedMaterial('A36')
        assert m.Fy == pytest.approx(36000)

    def test_fu(self):
        m = NamedMaterial('A36')
        assert m.Fu == pytest.approx(58000)

    def test_modulus_of_elasticity(self):
        m = NamedMaterial('A36')
        assert m.E == pytest.approx(29e6)

    def test_density(self):
        m = NamedMaterial('A36')
        assert m.rho == pytest.approx(0.284)

    def test_ys_alias(self):
        m = NamedMaterial('A36')
        assert m.YS == m.Fy

    def test_uts_alias(self):
        m = NamedMaterial('A36')
        assert m.UTS == m.Fu


# ===========================================================================
# Pre-instantiated common materials
# ===========================================================================

class TestCommonMaterials:
    def test_a36_fy(self):
        assert A36.Fy == pytest.approx(36000)

    def test_a36_fu(self):
        assert A36.Fu == pytest.approx(58000)

    def test_a36_e(self):
        assert A36.E == pytest.approx(29e6)

    def test_a500_grb_exists_and_has_fy(self):
        assert A500_GrB.Fy is not None
        assert A500_GrB.Fy > 0

    def test_e60xx_exists_and_has_fu(self):
        assert E60XX.Fu is not None
        assert E60XX.Fu > 0

    def test_properties_table_renders(self):
        # properties is overridden in BaseMaterial to use _data directly
        table = A36.properties
        assert isinstance(table, str)
        assert len(table) > 0
