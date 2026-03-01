"""
Base classes for the package.
"""

import string
import random
from tabulate import tabulate
from metk.props import *
from typing import Any, Dict, Tuple


UUID_CHOICES = [letter for letter in string.ascii_letters] + list(range(0, 10))


class metkObject:
    """
    Base class for the classes in this package.

    Provides standardized interfaces for inspecting properties and methods.
    """

    _properties: Tuple[str, ...] = ()

    @property
    def properties(self):
        """Return a table of the object's properties and values."""
        rows = []
        for prop in self._properties:
            v = getattr(self, prop, None)
            formatted = (
                ", ".join(str(x) for x in v) if isinstance(v, list) else nformat(v)
            )
            rows.append([prop, formatted])
        return tabulate(rows, tablefmt="grid", numalign="left")

    @property
    def prop_dict(self) -> Dict[str, Any]:
        """Return a dict of the object's properties and their values."""
        return {k: getattr(self, k, None) for k in self._properties}

    def __repr__(self) -> str:
        props = ", ".join(f"{k}={v!r}" for k, v in self.prop_dict.items())
        return f"{type(self).__name__}({props})"


def simple_uuid(length=8):
    """A simple short random identifier generator."""
    return "".join([str(random.choices(UUID_CHOICES)[0]) for i in range(length)])


def standardized(prop):
    """Remove subscript from property lookup."""
    return prop.replace("_", "")


def prop_lookup(prop):
    """Delegate a property lookup to a sub-object."""
    prop = standardized(prop)
    if prop in shape_props:
        return "shape"
    if prop in load_props:
        return "loads"
    if prop in material_props:
        return "material"
    return None


def nformat(number: int | float | None) -> str:
    """
    Return a formatted string representation of a number with adaptive
    precision and comma separators for large values. ::

        3498234.20394   =>  3,498,234
        324.23235       =>  324
        49.494          =>  49.5
        4.494           =>  4.49
        0.549494        =>  0.549
        0.000300        =>  3.00e-04
        None            =>  ''
    """
    if number is None:
        return ""

    if number == 0:
        return "0"

    if abs(number) < 0.001:
        return "{:.2e}".format(number)
    elif abs(number) < 1:
        return "{:.3f}".format(number)
    elif abs(number) < 10:
        return "{:.2f}".format(number)
    elif abs(number) < 100:
        return "{:.1f}".format(number)
    else:
        return "{:,.0f}".format(number)


def isNaN(num):
    return num != num


def round_to(number, multiple):
    """Round ``number`` to values of multiple ``multiple``."""
    return multiple * round(number / multiple)


def nearest_to(number, list):
    """
    Return the number in ``list`` which is nearest to number ``number``,
    looking both directions.
    """
    return min(list, key=lambda x: abs(x - number))
