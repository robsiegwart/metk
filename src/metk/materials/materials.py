'''
Basic, custom material classes.
'''

from .base_materials import BaseMaterial, LibraryMaterial


class Material(BaseMaterial):
    '''Custom user-defined material
    
        TODO:
            Standardize which names are used as the default OR put in some more
            logic to retrieve the right property. For example, if a user creates
            a custom material, if he wishes to enter the yield strength, which
            of 'Fy', 'F_y', 'YS', 'Yield_strength', or 'yield' should he enter?
    '''
    def __init__(self, **kwargs):
        self._data = {}
        
        data_dict = {}
        for k,v in kwargs.items():
            data_dict.update({k:v})
        
        self._data['properties'] = data_dict
        
        self._prop_adder = list(self._data.keys())
        self.name = kwargs.get('name', 'User-defined material')


class NamedMaterial(LibraryMaterial):
    def __init__(self, name, grade=None):
        try:
            super().__init__(f'{name.strip()}.json', grade)
        except FileNotFoundError:
            print(f'Material "{name}" not found in database')