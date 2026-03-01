"""
Tests for metk.core: nformat, utility functions, and metkObject base class.
"""

from metk.core import (
    metkObject,
    nformat,
    round_to,
    nearest_to,
    isNaN,
    standardized,
    prop_lookup,
)


# ===========================================================================
# nformat
# ===========================================================================


class TestNformat:
    """Docstring examples are the primary specification."""

    def test_none_returns_empty_string(self):
        assert nformat(None) == ""

    def test_zero_int(self):
        assert nformat(0) == "0"

    def test_zero_float(self):
        assert nformat(0.0) == "0"

    def test_very_small_number_uses_scientific(self):
        assert nformat(0.0003) == "3.00e-04"

    def test_very_small_negative_uses_scientific(self):
        assert nformat(-0.0003) == "-3.00e-04"

    def test_sub_one_three_decimals(self):
        assert nformat(0.549494) == "0.549"

    def test_single_digit_two_decimals(self):
        assert nformat(4.494) == "4.49"

    def test_double_digit_one_decimal(self):
        assert nformat(49.494) == "49.5"

    def test_triple_digit_no_decimal(self):
        assert nformat(324.23235) == "324"

    def test_large_number_comma_separated(self):
        assert nformat(3498234.20394) == "3,498,234"

    def test_negative_double_digit(self):
        assert nformat(-49.494) == "-49.5"

    def test_boundary_999_no_comma(self):
        # Values < 1000 should not have a comma
        result = nformat(999)
        assert "," not in result
        assert result == "999"

    def test_boundary_1000_gets_comma(self):
        assert nformat(1000) == "1,000"

    def test_boundary_9_point_99(self):
        # Just under 10: two decimals
        assert nformat(9.99) == "9.99"

    def test_boundary_10(self):
        # At 10: one decimal
        assert nformat(10.0) == "10.0"

    def test_integer_input(self):
        # Integers (not just floats) should be handled
        assert nformat(500) == "500"

    def test_negative_large_number(self):
        assert nformat(-3498234) == "-3,498,234"


# ===========================================================================
# Utility functions
# ===========================================================================


class TestRoundTo:
    def test_rounds_down(self):
        assert round_to(7, 5) == 5

    def test_rounds_up(self):
        assert round_to(8, 5) == 10

    def test_exact_multiple(self):
        assert round_to(10, 5) == 10

    def test_non_standard_multiple(self):
        assert round_to(14, 3) == 15


class TestNearestTo:
    def test_finds_nearest(self):
        assert nearest_to(4.9, [1, 3, 5, 7]) == 5

    def test_finds_nearest_lower(self):
        assert nearest_to(2.1, [1, 3, 5, 7]) == 3

    def test_single_element_list(self):
        assert nearest_to(100, [42]) == 42

    def test_exact_match(self):
        assert nearest_to(3, [1, 3, 5, 7]) == 3


class TestIsNaN:
    def test_nan_is_nan(self):
        assert isNaN(float("nan")) is True

    def test_zero_is_not_nan(self):
        assert isNaN(0) is False

    def test_number_is_not_nan(self):
        assert isNaN(1.5) is False


class TestStandardized:
    def test_removes_underscore(self):
        assert standardized("f_x") == "fx"

    def test_no_underscore_unchanged(self):
        assert standardized("A") == "A"

    def test_multiple_underscores(self):
        assert standardized("m_x_y") == "mxy"


class TestPropLookup:
    def test_shape_property(self):
        assert prop_lookup("Ix") == "shape"

    def test_load_property(self):
        assert prop_lookup("fx") == "loads"

    def test_material_property(self):
        assert prop_lookup("Fy") == "material"

    def test_unknown_returns_none(self):
        assert prop_lookup("notaprop") is None


# ===========================================================================
# metkObject base class
# ===========================================================================


class DummyObj(metkObject):
    """Minimal concrete subclass for testing metkObject behaviour."""

    _properties = ("x", "y", "tags")
    x = 4.494
    y = 324.23235
    tags = ["a", "b"]


class EmptyObj(metkObject):
    """Subclass with no declared properties."""

    pass


class TestMetkObject:
    def test_prop_dict_returns_correct_values(self):
        obj = DummyObj()
        d = obj.prop_dict
        assert d == {"x": 4.494, "y": 324.23235, "tags": ["a", "b"]}

    def test_prop_dict_empty_properties(self):
        obj = EmptyObj()
        assert obj.prop_dict == {}

    def test_repr_format(self):
        obj = DummyObj()
        assert repr(obj) == "DummyObj(x=4.494, y=324.23235, tags=['a', 'b'])"

    def test_repr_empty_properties(self):
        obj = EmptyObj()
        assert repr(obj) == "EmptyObj()"

    def test_properties_table_contains_formatted_numbers(self):
        obj = DummyObj()
        table = obj.properties
        assert "4.49" in table
        assert "324" in table

    def test_properties_table_list_joined_with_comma(self):
        obj = DummyObj()
        table = obj.properties
        assert "a, b" in table

    def test_properties_table_none_value_displays_empty(self):
        class ObjWithNone(metkObject):
            _properties = ("val",)
            val = None

        table = ObjWithNone().properties
        # None should format as '' — no crash, and no literal 'None' in output
        assert "None" not in table
