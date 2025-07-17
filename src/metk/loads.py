'''
Basic force and moment classes for generating and evaluating loads and load
combinations with factors.

User classes defined by this module:

  - Factor
  - Load
  - Force
  - Shear
  - Moment
  - CombinedLoad
'''

import re
import copy
import numpy as np
from metk.core import metkObject, nformat


class Factor:
    '''A generic load factor used for amplifying loads.'''
    def __init__(self, value=1, name=None):
        self.value = value
        self.name = name
 
    def __mul__(self, scalar):
        return self.value*scalar
    
    __rmul__ = __mul__
    
    def __repr__(self):
        return f'{self.name} = {self.value}' if self.name else f'Factor   {self.value}'
    
    def __str__(self):
        return f'Factor ({self.value})'


class Load(metkObject):
    '''
    A generic load containing force and moment components. Loads can be
    transformed to other coordinate systems at 90 degree rotations by specifying
    direction axes.
    '''
    _load_re = re.compile(r'^-?[xyz]$')
    """regex for load labels such as '-x','y','-z' ... """
    
    _properties = ['f_x','f_y','f_z','m_x','m_y','m_z','primary','secondary']
    
    # ``_load_map`` is used for transforming loads from the global coordinate
    # system to another coordinate system aligned with the global csys but
    # rotated by 90, 180, 270 degrees; this is done by specifying two axes:
    #   - the first is the axis which the local element's x-axis points in;
    #   - the second is the axis which the local element's y-axis points in
    _load_map = { 'x': {
                     'y': {'f_x': 'f_x', 'f_y': 'f_y', 'f_z': 'f_z',   'm_x': 'm_x', 'm_y': 'm_y', 'm_z': 'm_z'},
                    '-y': {'f_x': 'f_x', 'f_y':'-f_y', 'f_z':'-f_z',   'm_x': 'm_x', 'm_y':'-m_y', 'm_z':'-m_z'},
                     'z': {'f_x': 'f_x', 'f_y':'-f_z', 'f_z': 'f_y',   'm_x': 'm_x', 'm_y':'-m_z', 'm_z': 'm_y'},
                    '-z': {'f_x': 'f_x', 'f_y': 'f_z', 'f_z':'-f_y',   'm_x': 'm_x', 'm_y': 'm_z', 'm_z':'-m_y'} },
                  '-x': {
                     'y': {'f_x':'-f_x', 'f_y': 'f_y', 'f_z':'-f_z',   'm_x':'-m_x', 'm_y': 'm_y', 'm_z':'-m_z'},
                    '-y': {'f_x':'-f_x', 'f_y':'-f_y', 'f_z': 'f_z',   'm_x':'-m_x', 'm_y':'-m_y', 'm_z': 'm_z'},
                     'z': {'f_x':'-f_x', 'f_y':'-f_z', 'f_z': 'f_y',   'm_x':'-m_x', 'm_y':'-m_z', 'm_z': 'm_y'},
                    '-z': {'f_x':'-f_x', 'f_y': 'f_z', 'f_z':'-f_y',   'm_x':'-m_x', 'm_y': 'm_z', 'm_z':'-m_y'} },
                  'y': {
                     'x': {'f_x': 'f_y', 'f_y': 'f_x', 'f_z':'-f_z',   'm_x': 'm_y', 'm_y': 'm_x', 'm_z':'-m_z'},
                    '-x': {'f_x':'-f_y', 'f_y': 'f_x', 'f_z': 'f_z',   'm_x':'-m_y', 'm_y': 'm_x', 'm_z': 'm_z'},
                     'z': {'f_x': 'f_y', 'f_y': 'f_z', 'f_z': 'f_x',   'm_x': 'm_y', 'm_y': 'm_z', 'm_z': 'm_x'},
                    '-z': {'f_x':'-f_y', 'f_y': 'f_z', 'f_z':'-f_x',   'm_x':'-m_y', 'm_y': 'm_z', 'm_z':'-m_x'} },
                  '-y': {
                     'x': {'f_x': 'f_y', 'f_y': 'f_x', 'f_z': 'f_z',   'm_x': 'm_y', 'm_y': 'm_x', 'm_z': 'm_z'},
                    '-x': {'f_x':'-f_y', 'f_y': 'f_x', 'f_z':'-f_z',   'm_x':'-m_y', 'm_y': 'm_x', 'm_z':'-m_z'},
                     'z': {'f_x':'-f_y', 'f_y': 'f_z', 'f_z':'-f_x',   'm_x':'-m_y', 'm_y': 'm_z', 'm_z':'-m_x'},
                    '-z': {'f_x': 'f_y', 'f_y': 'f_z', 'f_z': 'f_x',   'm_x': 'm_y', 'm_y': 'm_z', 'm_z': 'm_x'} },
                  'z': {
                     'x': {'f_x': 'f_z', 'f_y': 'f_x', 'f_z': 'f_y',   'm_x': 'm_z', 'm_y': 'm_x', 'm_z': 'm_y'},
                    '-x': {'f_x':'-f_z', 'f_y':'-f_x', 'f_z': 'f_y',   'm_x':'-m_z', 'm_y':'-m_x', 'm_z': 'm_y'},
                     'y': {'f_x': 'f_z', 'f_y': 'f_y', 'f_z':'-f_x',   'm_x': 'm_z', 'm_y': 'm_y', 'm_z':'-m_x'},
                    '-y': {'f_x':'-f_z', 'f_y':'-f_y', 'f_z':'-f_x',   'm_x':'-m_z', 'm_y':'-m_y', 'm_z':'-m_x'} },
                  '-z': {
                     'x': {'f_x':'-f_z', 'f_y': 'f_x', 'f_z':'-f_y',   'm_x':'-m_z', 'm_y': 'm_x', 'm_z':'-m_y'},
                    '-x': {'f_x': 'f_z', 'f_y':'-f_x', 'f_z':'-f_y',   'm_x': 'm_z', 'm_y':'-m_x', 'm_z':'-m_y'},
                     'y': {'f_x':'-f_z', 'f_y': 'f_y', 'f_z': 'f_x',   'm_x':'-m_z', 'm_y': 'm_y', 'm_z': 'm_x'},
                    '-y': {'f_x': 'f_z', 'f_y':'-f_y', 'f_z': 'f_x',   'm_x': 'm_z', 'm_y':'-m_y', 'm_z': 'm_x'} }
        }
    
    _coords = {
        'f_x': 0, 'f_y': 1, 'f_z': 2, 'm_x': 3, 'm_y': 4, 'm_z': 5
    }

    def _to_local(self, primary, secondary, input_load):
        """Return a transformed load value"""
        mapping = self._load_map[primary][secondary]
        target = mapping[input_load]
        target_sign = -1 if len(target.split('-')) > 1 else 1
        target_stub = target.split('-')[-1]
        return target_sign*self._raw_value[self._coords[target_stub]]
    
    def _is_valid_combination(self, primary, secondary):
        """Check if a primary/secondary input pair is valid"""
        return primary.split('-')[-1] != secondary.split('-')[-1]

    def __init__(self, *args, **kwargs):
        kwargs = {k.lower().replace('_',''):v for k,v in kwargs.items()}
        self._fx, self._fy, self._fz, self._mx, self._my, self._mz = list(args) + [0]*(6-len(args))
        if not self._fx:
            self._fx = kwargs.get('fx',0)
        if not self._fy:
            self._fy = kwargs.get('fy',0)
        if not self._fz:
            self._fz = kwargs.get('fz',0)
        if not self._mx:
            self._mx = kwargs.get('mx',0)
        if not self._my:
            self._my = kwargs.get('my',0)
        if not self._mz:
            self._mz = kwargs.get('mz',0)
        
        self.primary = kwargs.get('primary','x')
        self.secondary = kwargs.get('secondary','y')
        self.name = kwargs.get('name','<unnamed>').capitalize()

        if not self._load_re.search(self.primary) or not self._load_re.search(self.secondary):
            raise Exception
        
        if not self._is_valid_combination(self.primary, self.secondary):
            raise Exception(f'Load orientations are not a valid combination (primary={self.primary}, secondary={self.secondary})')

        self.transformed = False if self.primary == 'x' and self.secondary == 'y' else True
    
    @property
    def _raw_value(self):
        return np.array([self._fx, self._fy, self._fz, self._mx, self._my, self._mz])
    
    @property
    def force(self):
        return self._raw_value[:3]
    
    @property
    def moment(self):
        return self._raw_value[3:]
    
    def rotate_on_axis(self, vector, axis, angle):
        angle = np.radians(angle)
        M = {
            'x': self._ROTX(angle),
            'y': self._ROTY(angle),
            'z': self._ROTZ(angle),
        }
        return np.matmul(np.linalg.inv(M[axis.lower()]), vector)

    def _ROTX(self, angle):
        return np.array([
            [ 1,               0,              0 ],
            [ 0,   np.cos(angle), -np.sin(angle) ],
            [ 0,   np.sin(angle),  np.cos(angle) ]
        ])

    def _ROTY(self, angle):
        return np.array([
            [  np.cos(angle),   0,  -np.sin(angle) ],
            [              0,   1,               0 ],
            [  np.sin(angle),   0,   np.cos(angle) ]
        ])

    def _ROTZ(self, angle):
        return np.array([
            [  np.cos(angle), -np.sin(angle),  0 ],
            [  np.sin(angle),  np.cos(angle),  0 ],
            [              0,              0,  1 ]
        ])

    @property
    def value(self):
        return [ self.fx, self.fy, self.fz, self.mx, self.my, self.mz ]
    
    @property
    def fx(self):
        if self.transformed:
            return self._to_local(self.primary, self.secondary, 'f_x')
        else:
            return self._fx
    
    @property
    def fy(self):
        if self.transformed:
            return self._to_local(self.primary, self.secondary, 'f_y')
        else:
            return self._fy
    
    @property
    def fz(self):
        if self.transformed:
            return self._to_local(self.primary, self.secondary, 'f_z')
        else:
            return self._fz
    
    @property
    def mx(self):
        if self.transformed:
            return self._to_local(self.primary, self.secondary, 'm_x')
        else:
            return self._mx
    
    @property
    def my(self):
        if self.transformed:
            return self._to_local(self.primary, self.secondary, 'm_y')
        else:
            return self._my
    
    @property
    def mz(self):
        if self.transformed:
            return self._to_local(self.primary, self.secondary, 'm_z')
        else:
            return self._mz
        
    f_x = fx
    f_y = fy
    f_z = fz
    m_x = mx
    m_y = my
    m_z = mz
    
    def __mul__(self, scalar):
        return Load(scalar*self.value)
    
    __rmul__ = __mul__

    def __add__(self, other):
        if not isinstance(other, Load):
            raise Exception
        return Load(self.value + other.value)
    
    def __str__(self):
        return '   '.join([ f'{label}={nformat(getattr(self,label))}' for label in self._coords.keys() if getattr(self,label) ])
    
    def __repr__(self):
        return f'Load({self.value})'
    

class VectorLoad(metkObject):
    '''
    Base class for 3-dimensional vector ``Force``, ``Shear``, and ``Moment``
    loads.
    '''    
    def __init__(self, name=None, description=None, factor=1):
        self.name = name
        self.description = description
        self._set_factor(factor)
    
    @property
    def factor(self):
        return self._factor
    
    @factor.setter
    def factor(self, factor):
        self._set_factor(factor)

    @property
    def evaluated(self):
        return self._raw_value*self.factor.value

    @property
    def x(self):
        return self.evaluated[0]
    
    @property
    def y(self):
        return self.evaluated[1]
    
    @property
    def z(self):
        return self.evaluated[2]
    
    def _set_factor(self, factor):
        if not isinstance(factor, Factor):
            self._factor = Factor(factor)
        else:
            self._factor = factor
    

class Force(VectorLoad):
    '''
    A 3-D force vector.

    Takes as input an array in 3 dimensions and a position vector in 3
    dimensions. The position vector is used for calculating a moment about a
    point and defaults to [0,0,0] so the moment is 0 by default.
    '''
    def __init__(self, F=[0,0,0], r=[0,0,0], **kwargs):
        super().__init__(**kwargs)
        self._raw_value = np.asarray(F)
        self._r = np.asarray(r)
    
    @property
    def F(self):
        return self.evaluated
    
    @F.setter
    def F(self, F):
        self._raw_value = np.asarray(F)
    
    @property
    def r(self):
        return self._r
    
    @r.setter
    def r(self, r):
        self._r = np.asarray(r)

    @property
    def M(self):
        return np.cross(self._r, self.F)
   
    def __add__(self, force, use_evaluated=False):
        '''
        Force addition.
        
        ``F3 = F1 + F2``
        '''
        if use_evaluated:
            return Force(F=self.F + force.F)
        else:
            return Force(F=self._raw_value + force._raw_value)
    
    def __rmul__(self, scalar):
        '''
        Force scaling. Existing factor and name attributes are preserved.
        
        ``F2 = 3 * F1``
        '''
        f = copy.deepcopy(self)
        f._raw_value *= scalar
        return f
    
    __mul__ = __rmul__

    def __repr__(self):
        return f'Force {self.name}   F={self._raw_value}, r={self._r}, factor: {self.factor}'


class Moment(VectorLoad):
    '''A Moment load.'''
    def __init__(self, M, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raw_value = np.asarray(M)

    @property
    def M(self):
        return self.evaluated
    
    @M.setter
    def M(self, val):
        self._raw_value = np.asarray(val)
    
    def __add__(self, other, use_evaluated=False):
        '''M3 = M1 + M2'''
        if use_evaluated:
            return Moment(M=self.M + other.M)
        else:
            return Moment(M=self._raw_value + other._raw_value)

    def __rmul__(self, scalar):
        '''M2 = n*M1'''
        m = copy.deepcopy(self)
        m._raw_value *= scalar
        return m
    
    __mul__ = __rmul__

    def __repr__(self):
        return f'Moment {self.name}  M={self._raw_value}, factor: {self.factor}'


class CombinedLoad:
    '''
    A container for one or more forces and/or moments acting at a common point
    for which force and moment summations may be performed.
    '''
    def __init__(self, forces=[], moments=[], name=''):
        self.forces = forces
        self.moments = moments
        self.name = name

    @property
    def F(self):
        return sum([ force.F for force in self.forces ])
    
    @property
    def M(self):
        return sum([ force.M for force in self.forces ] +
                   [ moment.M for moment in self.moments ])

    @property
    def Fx(self):
        return self.F[0]

    @property
    def Fy(self):
        return self.F[1]

    @property
    def Fz(self):
        return self.F[2]

    @property
    def Mx(self):
        return self.M[0]

    @property
    def My(self):
        return self.M[1]

    @property
    def Mz(self):
        return self.M[2]
    
    def __repr__(self):
        return f'Combined load {self.name}    F={self.F}  M={self.M}'