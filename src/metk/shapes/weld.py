'''
Weld Shape Classes
'''

from math import isnan
from metk.shapes.base import BaseShape


class BaseWeldShape(BaseShape):
    _properties = ['d','b','s','t','A','Ix','Iy','J','cx_max','cy_max']

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            if k == 't':
                continue
            setattr(self,k,v)
        
    @property
    def t(self):
        if self.weld_type == 'cjp':
            return self.s
        if self.weld_type == 'pjp':
            return self.s - 0.125
        if self.weld_type == 'fillet':
            return self.s*0.707
        elif self.weld_type in ['flare bevel', 'flare v-groove']:
            assert hasattr(self, 'radius')
            assert hasattr(self, 'flare_groove_factor')
            return self.flare_groove_factor*self.radius
    
    @property
    def dimensions(self):
        return {'d': self.d, 'b': self.b}
    
    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f'{self.label} weld shape (d={self.d}, b={self.b})'
    
    __str__ = __repr__


class LineWeld(BaseWeldShape):
    '''
    A single line weld. ::
    
              ________
           ┃        |
           y        |
           ┃        |
           o---x    d
          ∕┃        |
        z  ┃        |
           ┃  ______|_

    :param number d:        length of weld
    '''
    _name = 'Line weld shape'
    label = 'line'
    """Symmetric shape so only need one stress on each half."""
    b = None
    
    def __init__(self, d, weld_type='fillet', **kwargs):
        self.d = d
        self.weld_type = weld_type
        super().__init__(**kwargs)

    @property
    def A(self):
        return self.d*self.t
    
    @property
    def Ix(self):
        return 1/12*self.d**3*self.t

    @property
    def Iy(self):
        return 1/12*self.d*self.t**3
    
    @property
    def J(self):
        return 1/12*self.d**3*self.t
    
    @property
    def cx_left(self):
        return -self.t/2

    @property
    def cx_right(self):
        return self.t/2
    
    @property
    def cy_low(self):
        return -self.d/2
    
    @property
    def cy_high(self):
        return self.d/2


class BoxWeld(BaseWeldShape):
    '''
    A rectangular shaped weld. ::

        ┏━━━ y ━━━┓ ---/-
        ┃    |    ┃    |
        ┃    o--x ┃    d
        ┃   /     ┃    |
        ┗ z ━━━━━━┛ ---/-
        |         |
        /--- b ---/

    :param number d:        height dimension
    :param number b:        width dimension
    '''
    _name = 'Box weld shape'
    label = 'box'
    """Doubly symmetric shape so only need one stress on each side."""
        
    def __init__(self, d, b, weld_type='fillet', **kwargs):
        self.d = d
        self.b = b
        self.weld_type = weld_type
        super().__init__(**kwargs)
    
    @property
    def A(self):
        return 2*(self.b + self.d)*self.t

    @property
    def Ix(self):
        return self.d**2/6*(self.d + 3*self.b)

    @property
    def Iy(self):
        return self.b**2/6*(self.b + 3*self.d)

    @property
    def J(self):
        return (self.b + self.d)**3/6

    @property
    def cx_left(self):
        return -self.b/2

    @property
    def cx_right(self):
        return self.b/2

    @property
    def cy_low(self):
        return -self.d/2

    @property
    def cy_high(self):
        return self.d/2


class DoubleLineWeld(BaseWeldShape):
    '''
    A double line weld. ::
    
                   ______
        ┃   y   ┃      |
        ┃   |   ┃      |
        ┃   o---x      d
        ┃  /    ┃      |
        ┃z      ┃  ____|_
        |-- b --|
            
    '''
    _name = 'Double-line weld shape'
    label = 'double line'
    # _stress_locations = ['upper left', 'lower left']
    """Doubly symmetric shape so only need one stress on each side."""
    
    def __init__(self, d, b, weld_type='fillet', **kwargs):
        self.d = d
        self.b = b
        self.weld_type = weld_type
        super().__init__(**kwargs)
    
    @property
    def A(self):
        return 2*self.d*self.t

    @property
    def Ix(self):
        return self.d**3/6*self.t

    @property
    def Iy(self):
        return self.d*self.b**2/2*self.t

    @property
    def J(self):
        return self.d*(3*self.b**2 + self.d**2)/6*self.t

    @property
    def cx_left(self):
        return -self.b/2

    @property
    def cx_right(self):
        return self.b/2

    @property
    def cy_low(self):
        return -self.d/2
        
    @property
    def cy_high(self):
        return self.d/2


SHAPES = { shape.label: shape for shape in [LineWeld, BoxWeld, DoubleLineWeld] }


def get_weld_shape(name, d, b):
    if not is_weld_shape(name):
        raise Exception(f'Name "{name}" not a valid weld shape label.')
    if not b or isnan(b):
        return SHAPES[name.lower()](d)
    else:
        return SHAPES[name.lower()](d, b)


def is_weld_shape(name):
    return name.lower() in SHAPES.keys()