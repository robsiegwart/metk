'''
Base material classes.
'''

import os.path
import json
from tabulate import tabulate
from metk.core import metkObject, standardized
from metk.props import material_prop_aliases


local_dir = os.path.dirname(__file__)


def named_material_exists(name):
    return os.path.exists(os.path.join(local_dir, 'data', f'{name.strip()}.json'))


class BaseMaterial(metkObject):
    '''Base material class.'''
    
    def __getattr__(self, attr, subdict='properties'):
        '''Get a property -- default to the physical property sub-dict'''
        data_prop = material_prop_aliases.get(standardized(attr), None)
        if data_prop:
            try:
                return self._data[subdict][data_prop]
            except KeyError:
                for each in ['composition','meta']:
                    try:
                        return self._data[each][attr]
                    except KeyError:
                        continue
        return None
    
    @property
    def properties(self):
        return tabulate(self._data['properties'].items(), tablefmt='grid', disable_numparse=True)
    
    def __repr__(self):
        return self.name
    

class LibraryMaterial(BaseMaterial):
    '''
    Base class for standard materials included in this packages' "data/"
    folder.
    '''
    def __init__(self, src, grade=None):
        with open(os.path.join(local_dir, 'data', src)) as f:
            self._data = json.load(f)
    
    # property abbreviations/aliases
    @property
    def E(self):
        return self._data['properties'].get('modulus of elasticity', None)

    @property
    def Fy(self):
        return self._data['properties'].get('YS_min', None)
    
    @property
    def Fu(self):
        return self._data['properties'].get('UTS_min', None)
    
    @property
    def rho(self):
        return self._data['properties'].get('density', None)
    
    def __str__(self):
        return f'{self.name} (Library)'
    
    @property
    def name(self):
        return self._data['name']

    YS = Fy
    UTS = Fu