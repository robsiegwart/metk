'''
This module defines the `Bolt` class for representing structural bolts and the
`BoltGroup` class for managing collections of bolts. It includes properties for
calculating tensile and shear stresses based on AISC specifications.
'''

import os
from math import pi
from pandas import DataFrame, read_pickle
from metk.structural.structural_object import (
    StructuralObject,
    StructuralObjectGroup
)
from metk.shapes import Circle
from metk.core import nearest_to


local_dir = os.path.dirname(__file__)
open_dir = os.path.join(local_dir, 'data', 'bolt')


class Bolt(StructuralObject):
    '''
    A structural bolt element.

    :param number d:            Nominal bolt diameter in decimal form
    :param number r:            Nominal bolt radius in decimal form (if both
                                ``d`` and ``r`` are specified ``d`` is used)
    :param str number:          Number size such as '#6', '#10', '1/4', with or
                                without the pound sign.
    :param Load loads:          The loads on the bolt
    :param Material material:   The bolt material.    
    :param str thread_class:    UNF or UNC threads, choose from
                                ['coarse', 'fine']. Default is 'coarse'.
    '''
    _item_name = 'Bolt'

    def __init__(self,
                 d=None,
                 r=None,
                 number=None,
                 loads=None,
                 material=None,
                 thread_class='coarse',
                 **kwargs
            ):
        self.thread_class = thread_class.lower()
        self.loads = loads
        self.material = material
        
        # Load thread data for property lookups
        if self.thread_class not in ['coarse', 'fine']:
            raise Exception('thread_class must be either "coarse" or "fine"')
        thread_data = read_pickle(os.path.join(open_dir, f'{self.thread_class}.pkl'))

        # Get the value for nominal diameter from the available inputs
        if number:
            self.d = float(thread_data.query(f'`Size, Number or Inches` == {number.lstrip("#")}')['Basic Major Diameter (in)'])
        else:
            self.d = d if d else 2*r
        
        # Snap ``d`` to the nearest valid nominal bolt size.
        self.d = nearest_to(self.d, thread_data['Basic Major Diameter (in)'].infer_objects().to_list())
        
        # Get the TPI for the given bolt size
        self.tpi = int(thread_data.query(f'`Basic Major Diameter (in)` == {self.d}')['TPI'])

        # Get the diameter using the tensile area for calculation purposes
        self.A_t = pi/4*(self.d-0.9743/self.tpi)**2
        self.d_t = (4*self.A_t/pi)**0.5
        """Per Equation A-3-7 of AISC 360-16 specification"""

        super().__init__(Circle(d=self.d_t), loads, material, **kwargs)
        
    # AISC allowable stress calculations if nominal strengths supplied per
    # A360-16 Table J3.2
    @property
    def F_nt(self):
        if 'F_u' in self.kwargs:
            return self.kwargs['F_u']*0.75
        else:
            return self.kwargs.get('F_nt', None)
    
    @property
    def F_nv(self):
        if 'F_u' in self.kwargs and 'threads_excluded_from_shear_planes' in self.kwargs:
            if self.kwargs['threads_excluded_from_shear_planes']:
                return self.kwargs['F_u']*0.563
            else:
                return self.kwargs['F_u']*0.450
        else:
            return self.kwargs.get('F_nv', None)

    @property
    def allowable_tensile_stress(self):
        if self.F_nt:
            omega = 2
            """J3-1"""
            if abs(self.Svx) > 1 or abs(self.Svy) > 1:
                F_nt = self.F_nt
                return min(1.3*F_nt - omega*F_nt/self.F_nv*(self.Svx**2 + self.Svy**2)**0.5, F_nt)/omega
            else:
                return self.F_nt/omega
        return None

    @property
    def allowable_shear_stress(self):
        if self.F_nv:
            omega = 2
            """J3-1"""
            return self.F_nv/omega
        return None

    @property
    def r(self):
        return self.d/2

    def __repr__(self):
        return f'Bolt object'


class BoltGroup(StructuralObjectGroup):
    '''A group of ``Bolt`` objects.'''
    def __init__(self, bolts, **kwargs):
        if isinstance(bolts, DataFrame):
            bolts = [ Bolt(**row, **kwargs) for idx,row in bolts.iterrows() ]
        super().__init__(bolts)
    
    @property
    def bolts(self):
        return self._bolts

    def __repr__(self):
        return f'Bolt evaluation {self.name + " " if self.name else ""}containing {len(self.objects)} bolts'