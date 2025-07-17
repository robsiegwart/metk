'''
Weld module for analyzing welds.
'''

from math import sqrt
from pandas import DataFrame
from metk.structural.structural_object import (
    StructuralObject,
    StructuralObjectGroup
)
from metk.shapes.weld import get_weld_shape
from metk.shapes.base import BaseShape


class Weld(StructuralObject):
    '''
    A structural weld element.

    Weld shapes use a Local coordinate system as follows:
        ``Z`` is normal to the profile, ``Y`` is vertical, and ``X`` horizontal.
        See the weld shapes file for illustrations of the shapes:

            metk/shapes/weld.py

    Weld orientations are specified by the ``primary`` and ``secondary``
    parameters. ``primary`` corresponds to the global axis that the local weld's
    ``+x`` axis points in; ``secondary`` corresponds to the global axis that the
    weld's local ``+y`` axis points in.

    If loads are output in the local weld coordinate system, then no
    adjustments are needed as the defaults for ``primary`` and ``secondary``
    are ``x`` and ``y``, respectively.
    '''
    _item_name = 'Weld'
    _info_props = ['weld_type','label']

    def __init__(self, shape, s, t=None, weld_type='fillet', material=None,
                 loads=None, **kwargs):
        self.weld_type = weld_type.lower()
        self.primary = kwargs.get('primary','x')
        self.secondary = kwargs.get('secondary','y')

        if not isinstance(shape, BaseShape):
            shape = get_weld_shape(shape, kwargs.get('d'), kwargs.get('b'))
            shape.weld_type = self.weld_type
            shape.radius = kwargs.get('radius')
            shape.flare_groove_factor = kwargs.get('flare_groove_factor')

        s = float(s)
        shape.s = s

        super().__init__(shape, loads, material, s=s, t=t, weld_type=weld_type,
                         **kwargs)

    def __repr__(self):
        return f'Weld {self.name}  ({repr(self.shape)}, {self.weld_type}, {self.s})'
    
    @property
    def t(self):
        return self.shape.t

    @property
    def s(self):
        return self.shape.s
    
    @s.setter
    def s(self, value):
        self.shape.s = value
    
    @t.setter
    def t(self, value):
        self.shape.t = value
    
    # ========================== Stress Properties =============================
    @property
    def Tx(self):
        return self.loads.m_z*self.shape.cy_max/self.shape.J

    @property
    def Ty(self):
        return self.loads.m_z*self.shape.cx_max/self.shape.J

    @property
    def S_normal(self):
        return abs(self.Sa) + abs(self.Sbx) + abs(self.Sby)

    @property
    def S_shear_x(self):
        return sqrt(self.Svx**2 + self.Tx**2)

    @property
    def S_shear_y(self):
        return sqrt(self.Svy**2 + self.Ty**2)

    @property
    def normal_stress_ratio(self):
        return self.S_normal/self.normal_allowable
        
    @property
    def shear_stress_ratio(self):
        return max(self.S_shear_x, self.S_shear_y)/self.allowable_shear_stress
    
    @property
    def tensile_ratio(self):
        try:
            return abs(self.max_tensile/self.allowable_tensile_stress)
        except TypeError:
            return None
    
    @property
    def shear_ratio(self):
        try:
            return abs(self.max_shear/self.allowable_shear_stress)
        except TypeError:
            return None


class WeldGroup(StructuralObjectGroup):
    '''
    A group of ``Weld`` objects.

    :param welds:   Either a DataFrame of welds as rows or a list of ``Weld``
                    objects.
    '''
    def __init__(self, welds, **kwargs):
        if isinstance(welds, DataFrame):
            welds = [ Weld(**row, **kwargs) for idx,row in welds.iterrows() ]
        super().__init__(welds)
    
    @property
    def welds(self):
        return self.objects

    def __repr__(self):
        return f'Weld evaluation {self.name or ""}containing {len(self.objects)} welds'