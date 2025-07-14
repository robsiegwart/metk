'''
Base shape classes.
'''

from math import sqrt
from numbers import Number
from metk.core import metkObject


class BaseShape(metkObject):
    '''Base shape class for all shapes.'''
    _stress_locations = ['corners']
    _properties = ['A','height','width','Ix','Iy','J','cx_max','cy_max']
    label = None
    
    def compression_classification(self, w, t, E, Fy, lambda_p):
        if w/t <= lambda_p:
            return 'nonslender-element'
        else:
            return 'slender-element'
    
    def flexure_classification(self, w, t, E, Fy, lambda_p, lambda_r):
        if w/t <= lambda_p:
            return 'compact'
        elif w/t <= lambda_r:
            return 'noncompact'
        else:
            return 'slender-element'
        
    @property
    def dimensions(self):
        return {'Width': self.width, 'Height': self.height}
    
    @property
    def cy_max(self):
        return max(self.cy_high, abs(self.cy_low))
    
    @property
    def cx_max(self):
        return max(abs(self.cx_left), self.cx_right)


class DoublySymmetricShape(BaseShape):
    '''A shape with two planes of symmetry 90 degrees apart.'''
    @property
    def cx(self):
        return self.width/2
    
    @property
    def cy(self):
        return self.height/2
    
    @property
    def cr_max(self):
        return sqrt(self.cx**2 + self.cy**2)
    
    @property
    def cx_right(self):
        return self.cx

    @property
    def cx_left(self):
        return -self.cx

    @property
    def cy_high(self):
        return self.cy
        
    @property
    def cy_low(self):
        return -self.cy