'''
Standard structural shape classes.
'''

import re
import os.path
from numpy import isreal, sqrt
from pandas import read_pickle
from metk.shapes.base import BaseShape
from metk.core import standardized


local_dir = os.path.dirname(__file__)


LABEL_RE = re.compile(r'(?P<type>HSS|W|L|WT|C|2L|HP|M|MC|MT|S|ST|PIPE)[0-9.\/xX]+')


def is_structural_shape_label(name):
    '''
    Test if a string name is a valid structural shape identifier.
    
    Note:   This function doesn't check if the shape actually exists but only
            checks if the format of the string is valid.
    '''
    return True if LABEL_RE.search(name) else False


def validate_structural_shape_name(name):
    '''
    Attempt to convert a user-supplied structural shape name to a valid name as
    contained in the ``aisc-shapes-database-v15.0.xlsx`` which is the source of
    data for this module.
    
    There are two naming conventions as defined by columns
    'EDI_Std_Nomenclature' and 'AISC_Manual_Label'. EDI naming is described in
    detail by this document:
        
        "Naming Convention for Structural Steel Products for Use in Electronic
        Data Interchange (EDI)", available at:
        
        "https://www.aisc.org/publications/steel-construction-manual-resources"

    NOTE:   This function is currently a placeholder as this logic has not been
            implemented yet.
    '''
    return name.strip().upper().replace(' ','')


def get_standard_shape(name):
    '''Return a named shape class by string lookup.'''
    try:
        type_ = LABEL_RE.search(name).group('type')
        return {
            'W':    W,
            'L':    L,
            'HSS':  HSS,            
        }[type_](name)
    except (AttributeError, KeyError):
        return None


class StandardShape(BaseShape):
    '''Base class for standard structural shapes.'''
    def __init__(self, name):
        name = name if name.startswith(self.label) else self.label + name
        self.name = validate_structural_shape_name(name)
        
        if not hasattr(self, 'src'):
            m = LABEL_RE.search(self.name)
            self.src = m.group('type') + '.pkl'

        self._db = read_pickle(os.path.join(local_dir, 'structural_shape_data', self.src)).set_index('EDI_Std_Nomenclature')
    
        try:
            data = self._db.loc[self.name]
            self._data = data[data.apply(isreal)]
            del self._db
            self._prop_adder = [ k for k,v in self._data.items() if v ]
        
        except (KeyError, RecursionError):
            print(f'Error: "{self.name}" not found in shapes database.')
            
    
    def __getattr__(self, attr):
        try:
            return self._data[standardized(attr)]
        except KeyError:
            return None

    def is_compact(self, E, Fy):
        '''
        A section is *compact* if its width-to-thickness ratio does not exceed
        ``lambda_p``.

        A section is *noncompact* if its width-to-thickness ratio exceeds
        ``lambda_p`` but does not exceed ``lambda_r``.

        Width-to-thickness is defined by ANSI/AISC 360-16 Tables 4.1a, 4.1b.

        :param num E:           value for Young's modulus
        :param num Fy:          value for yield strength
        '''
        return self.width_to_thickness <= self._lambda_p(E, Fy)
    
    def is_slender(self, E, Fy, load_type):
        '''
        A section is *slender* if its width-to-thickness ratio exceeds
        `lambda_r`. In addition to material properties Young's modulus and yield
        strength this property also depends on whether the member is in flexure
        or compression.

        Width-to-thickness is defined by ANSI/AISC 360-16 Tables 4.1a, 4.1b.

        :param num E:           value for Young's modulus
        :param num Fy:          value for yield strength
        :param str load_type:   one of 'compression' or 'flexure'
        :return bool:
        '''
        if load_type == 'compression':
            return self.width_to_thickness > self._lambda_r_comp(E, Fy)
        
        elif load_type == 'flexure':
            return self.width_to_thickness > self._lambda_r_flex(E, Fy)
        
    def __repr__(self):
        return f'Standard shape {self.name}'

    @property
    def cx_right(self):
        return self.width/2
    
    @property
    def cx_left(self):
        return -self.width/2
    
    @property
    def cy_high(self):
        return self.height/2
    
    @property
    def cy_low(self):
        return -self.height/2
    
    @property
    def cr_max(self):
        '''
        Max (vector) distance to outer fiber on both axes, used for torsion
        calculation.
        '''
        return sqrt(self.cx_left**2 + self.cy_high**2)
    
    @property
    def width(self):
        return getattr(self,self._width_prop)
    
    @property
    def height(self):
        return getattr(self,self._height_prop)


class W(StandardShape):
    '''
    Wide flange beam shape. ::

             y
        ┏━━━━|━━━━┓
        ┗━━━┓|┏━━━┛
            ┃|┃
            ┃o┃--- x
            ┃ ┃
        ┏━━━┛ ┗━━━┓
        ┗━━━━━━━━━┛
    
    :param str label:   Valid label shape identifier (e.g. W8X31)

    Specific properties for I (wide flange beam) shape in the AISC Structural
    Shapes Database:
        
    W
        weight per foot, lbs/ft
    A
        cross sectional area
    d
        overall depth of member (height)
    b_f
        flange width
    t_w
        thickness of web
    t_f
        thickness of flange
    '''
    label = 'W'
    src = 'W.pkl'
    _properties = StandardShape._properties + ['tf','tw']
    _width_prop = 'bf'
    _height_prop = 'd'
    
    def __repr__(self):
        return f'Wide Flange Beam ({self.name})'
    
    def _lambda_p(self,E,Fy):
        return 0.38*sqrt(E/Fy)

    def _lambda_r_comp(self,E,Fy):
        return 0.56*sqrt(E/Fy)

    def _lambda_r_flex(self,E,Fy):
        return sqrt(E/Fy)
    
    @property
    def width_to_thickness(self):
        '''Per AISC Table B4.1a'''
        return (self.bf/2)/self.tf


class L(StandardShape):
    '''
    L shape. Is oriented so that the long side is vertical and on the left: ::

         y
        ┏|┓
        ┃|┃
        ┃|┃
        ┃o┃--- x
        ┃ ┗━━━┓
        ┗━━━━━┛

    :param str label:   Valid label shape identifier (e.g. L6X6X1/2)

    Specific properties for L:



    '''
    _stress_locations = ['lower left', 'upper left', 'lower right']
    label = 'L'
    src = 'L.pkl'
    _properties = StandardShape._properties + ['t']
    _width_prop = 'b'
    _height_prop = 'd'
    
    @property
    def cx_right(self):
        return self.d - self.x
    
    @property
    def cx_left(self):
        return -self.x
    
    @property
    def cy_high(self):
        return self.b - self.y
    
    @property
    def cy_low(self):
        return -self.y
    
    @property
    def cr_max(self):
        '''
        Max (vector) distance to outer fiber on both axes, used for torsion
        calculation.
        '''
        return sqrt(self.cx_left**2 + self.cy_high**2)
    
    @property
    def width_to_thickness(self):
        return self.b/self.t
    
    def __repr__(self):
        return f'L section ({self.name})'
       
    def _lambda_p(self,E,Fy):
        return 0.54*sqrt(E/Fy)

    def _lambda_r_comp(self,E,Fy):
        return 0.45*sqrt(E/Fy)

    def _lambda_r_flex(self,E,Fy):
        return 0.91*sqrt(E/Fy)


class HSS(StandardShape):
    '''
    A standard hollow structural section (HSS) ::
    
        ┏━━━━━━━━━┓
        ┃ ┏━━━━━┓ ┃
        ┃ ┃  y  ┃ ┃
        ┃ ┃  |  ┃ ┃
        ┃ ┃  +--┃-┃-x
        ┃ ┃     ┃ ┃
        ┃ ┃     ┃ ┃
        ┃ ┗━━━━━┛ ┃
        ┗━━━━━━━━━┛
    
    :param str label:   Valid label shape identifier (e.g. HSS2X2X.125)

    Properties

    Ht
        Overall depth (height)
    h
        Depth of flat wall
    B
        Overall width
    b
        Width of flat wall
    t_nom
        Nominal wall thickness
    t_des
        Design wall thickness
    '''
    label = 'HSS'
    src = 'HSS.pkl'
    _properties = StandardShape._properties + ['tnom','tdes']
    _width_prop = 'B'
    _height_prop = 'Ht'
    
    @property
    def t(self):
        return self.tdes
    
    def _lambda_p(self,E,Fy):
        return 2.42*sqrt(E/Fy)

    def _lambda_r_comp(self,E,Fy):
        return 1.4*sqrt(E/Fy)

    def _lambda_r_flex(self,E,Fy):
        return 5.7*sqrt(E/Fy)
    
    @property
    def width_to_thickness(self):
        '''Per AISC Table B4.1a'''
        return max(self.b, self.h)/self.tnom
    
    @property
    def h_x(self):
        '''See AISC G4 ...'''
        return self.width - 3*self.t
    
    @property
    def h_y(self):
        '''See AISC G4 ...'''
        return self.height - 3*self.t


def StructuralShape(name):
    '''
    Return a structural shape class based on nane.

    :param str name:    A valid structural shape name (such as 'HSS6X10X.375' or 'L6X6X1/2') 
    '''
    if not is_structural_shape_label(name):
        raise Exception(f'Input "{name}" not a valid shape label.')
    return get_standard_shape(name)