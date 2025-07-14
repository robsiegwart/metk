'''
Base classes for the package.
'''

import string
import random
from numbers import Number
from tabulate import tabulate
from metk.props import *


UUID_CHOICES = [ letter for letter in string.ascii_letters ] + list(range(0,10))


class metkObject:
    '''
    Base class for various classes in this package.
    
    References attributes ``_properties`` and ``_methods`` which can be
    overrided on child objects.
    '''
    _properties = []
    _methods = []
    
    @property
    def properties(self):
        '''
        Return as a string a table of the objects' properties and values if it
        has one.
        '''
        return tabulate(
            [ [prop, nformat(getattr(self, prop, None))] for prop in self._properties ],
            tablefmt='grid', numalign='left')
    
    @property
    def _prop_dict(self):
        return { k:getattr(self,k,None) for k in self._properties }

    @property
    def methods(self):
        return tabulate(
            [ [item, getattr(self, item).__doc__] for item in self._methods ],
            tablefmt='grid', numalign='left')


def simple_uuid(length=8):
    '''A simple short random identifier generator.'''
    return ''.join([str(random.choices(UUID_CHOICES)[0]) for i in range(length)])


def standardized(prop):
    '''Remove subscript from property lookup.'''
    return prop.replace('_','')


def prop_lookup(prop):
    '''Delegate a property lookup to a sub-object.'''
    prop = standardized(prop)
    if prop in shape_props:
        return 'shape'
    if prop in load_props:
        return 'loads'
    if prop in material_props:
        return 'material'
    return None


def nformat(number):
    '''
    Return a formatted representation of a number so that is has long decimals
    removed and commas inserted. ::

        3498234.20394   =>  3,498,234
        324.23235       =>  324
        49.494          =>  49.5
        4.494           =>  4.49
        0.549494        =>  0.549
    '''
    if not isinstance(number, Number):
        return number
    if isinstance(number, list):
        return [ nformat(each) for each in number ]
    if number == 0:
        return 0
    number = float(number)
    if abs(number) < 0.001:
        return '{:.6f}'.format(number)
    elif abs(number) < 1:
        return '{:.3f}'.format(number)
    elif abs(number) < 10:
        return '{:.2f}'.format(number)
    elif abs(number) < 100:
        return '{:.1f}'.format(number)
    elif abs(number) < 1000:
        return '{:.0f}'.format(number)
    else:
        return '{:,.0f}'.format(number)


def isNaN(num):
    return num != num


def round_to(number, multiple):
    '''Round ``number`` to values of multiple ``multiple``.'''
    return multiple*round(number/multiple)


def nearest_to(number, list):
    '''
    Return the number in ``list`` which is nearest to number ``number``,
    looking both directions.
    '''
    return min(list, key=lambda x: abs(x-number))