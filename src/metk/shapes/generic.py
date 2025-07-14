'''
Generic shape classes.
'''

from math import pi, sqrt
from metk.shapes.base import BaseShape, DoublySymmetricShape


class Shape(BaseShape):
    '''
    Generic user-defined shape. Has no predefined property attributes so you can
    assign anything to it.
    '''
    def __init__(self, name=None, **kwargs):
        self._data = {}
        self.name = name
        
        for k,v in kwargs.items():
            if k.startswith('_') or k == 'label':
                setattr(self,k,v)
            else:
                self._data.update({k:v})

        # @property
        # def r(self):
        #     return min(self.rx, self.ry)
    
    def __repr__(self):
        return f'{self.name + " " or ""}(Custom shape)'


class Circle(DoublySymmetricShape):
    '''
    A solid circle defined by radius ``r`` or diameter ``d``. Radius ``r`` takes
    precedence.

    :param num r:   radius
    :param num d:   diameter
    '''
    _properties = ['d','r','A','Ix','Zx','J']
    label = 'Circle'

    def __init__(self, r=None, d=None):
        self.r = r if r else d/2

    @property
    def d(self):
        return 2*self.r
    
    @property
    def A(self):
        return pi*self.r**2
    
    @property
    def I(self):
        return pi*self.r**4/4
    
    @property
    def Z(self):
        return self.d**3/6
    
    @property
    def S(self):
        return self.I/self.r
    
    @property
    def J(self):
        return pi*self.r**4/4
    
    @property
    def c(self):
        return self.r
    
    def __repr__(self):
        return f'Circle (d={round(self.d,3)})'

    def __str__(self):
        return f'Circle shape (r={self.r})'
    
    width = d
    height = d
    Ix = I
    Iy = I
    Zx = Z
    Zy = Z
    Sx = S
    Sy = S


class Rectangle(DoublySymmetricShape):
    '''
    A solid rectangular section defined by width ``w`` and height ``h``.

    :param num w:   width
    :param num h:   height
    '''
    label = 'Rectangle'
    name = 'Rectangle'

    def __init__(self, w, h):
        self.w = w
        self.h = h

    @property
    def A(self):
        return self.w*self.h
    
    @property
    def Ix(self):
        return 1/12*self.w*self.h**3
    
    @property
    def Iy(self):
        return 1/12*self.h*self.w**3
    
    @property
    def Zx(self):
        return self.w*self.h**2/4
    
    @property
    def Zy(self):
        return self.h*self.w**2/4
    
    @property
    def cx(self):
        return self.w/2
    
    @property
    def cy(self):
        return self.h/2
    
    @property
    def Sx(self):
        return self.Ix/self.cy
    
    @property
    def Sy(self):
        return self.Iy/self.cx
    
    @property
    def J(self):
        # From Collins, J. Mechanical Design of Machine Elements and Machines. 2nd Ed.
        # page 155, Table 4.5
        a = max(self.w, self.h)/2
        b = min(self.w, self.h)/2
        return a*b**3*( 16/3 - 3.36*b/a*(1 - b**4/(12*a**4)) )
    
    @property
    def rx(self):
        return sqrt(self.Ix/self.A)
    
    @property
    def ry(self):
        return sqrt(self.Iy/self.A)
    
    @property
    def height(self):
        return self.h
    
    @property
    def width(self):
        return self.w

    @property
    def c_r(self):
        return sqrt(self.cx_max**2 + self.cy_max**2)
    
    # Aliases for structural
    @property
    def t(self):
        return self.w
    
    def __repr__(self):
        return f'Rectangle(w={self.w}, h={self.h})'
    
    def __str__(self):
        return f'Rectangle shape ({self.w}x{self.h})'
    
    c_y = cy
    c_x = cx
    Z_x = Zx
    Z_y = Zy
    S_x = Sx
    S_y = Sy
    r_x = rx
    r_y = ry
    t_t = t


class HollowRectangle(DoublySymmetricShape):
    '''
    A hollow rectangular section defined by outside width ``w``, outside height
    ``h``, and thickness ``t``. ::

        ┏━━━━━━━━━┓
        ┃ ┏━━━━━┓ ┃
        ┃ ┃  y  ┃ ┃
        ┃ ┃  |  ┃ ┃
        ┃ ┃  +--┃-┃-x
        ┃ ┃     ┃ ┃
        ┃ ┃     ┃ ┃
        ┃ ┗━━━━━┛ ┃
        ┗━━━━━━━━━┛


    :param num w:       width
    :param num h:       height
    :param num t:       thickness
    '''
    label = 'Hollow Rectangle'

    def __init__(self,w,h,t):
        self.w = w
        self.h = h
        self.t = t
        self.width = w
        self.height = h

    @property
    def A(self):
        return self.h*self.w - (self.h-2*self.t)*(self.w-2*self.t)
    
    @property
    def cx(self):
        return self.w/2

    @property
    def cy(self):
        return self.h/2  

    @property
    def Ix(self):
        return 1/12*(self.w*self.h**3 - (self.w-2*self.t)*(self.h-2*self.t)**3)

    @property
    def Iy(self):
        return 1/12*(self.h*self.w**3 - (self.h-2*self.t)*(self.w-2*self.t)**3)

    @property
    def Zx(self):
        return self.w*self.h**2/4-(self.w-2*self.t)*(self.h/2-self.t)**2
    
    @property
    def Zy(self):
        return self.h*self.w**2/4-(self.h-2*self.t)*(self.w/2-self.t)**2
    
    def __repr__(self):
        return f'HollowRectangle({self.w},{self.h},{self.t})'
    
    def __str__(self):
        return f'Hollow rectangular section ({self.w}x{self.h}x{self.t})'
    
    c_y = cy
    c_x = cx
    Z_x = Zx
    Z_y = Zy
    

SHAPES = {
    'rectangle': (Rectangle, ['w','h']),
    'circle': (Circle, ['r','d']),
    'hollow rectangle': (HollowRectangle, ['w','h','t'])
}


def is_generic_shape_label(label):
    '''Return the shape object from an input label.'''
    return label.lower() in ['rectangle','circle','hollow rectangle']


def get_generic_shape(label, kwargs):
    '''
    Test if a string name corresponds to a generic shape class defined here.
    '''
    if not is_generic_shape_label(label):
        raise Exception(f'Name "{label}"" not a valid generic shape class.')
    shape, args = SHAPES[label.lower()]
    return shape(**{ k:kwargs.get(k, None) for k in args })