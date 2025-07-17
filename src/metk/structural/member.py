'''
Definitions for a general structural member and a group of member objects.
'''

from pandas import DataFrame
from metk.structural.structural_object import (
    StructuralObject,
    StructuralObjectGroup
)


class Member(StructuralObject):
    '''
    A structural member under arbitrary loading defined by a cross-sectional
    shape, material, and loads.
    '''
    _item_name = 'Member'
    
    def __init__(self, shape=None, loads=None, material=None, **kwargs):
        super().__init__(shape, loads, material, **kwargs)

    def __repr__(self):
        return f'Member {self.name or ""}'
    

class MemberGroup(StructuralObjectGroup):
    '''A group of structural members to evaluate as a batch'''

    def __init__(self, objects, **kwargs):
        if isinstance(objects, DataFrame):
            objects = [ Member(**row) for idx,row in objects.iterrows() ]
        super().__init__(objects, **kwargs)
    
    def __repr__(self):
        return f'Group of {len(self.objects)} Member objects'