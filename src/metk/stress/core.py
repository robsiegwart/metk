'''
Defines ``StressElement`` which is a basic stress element having six stress
components (3 normals and 3 shears) and providing computed stress outputs
such as von Mises stress and stress intensity.
'''

from functools import cached_property
import numpy as np
from metk.core import metkObject
from pandas import Series


def SRSS(*args):
    '''Square root sum of squares of arbitrary arguments.'''
    return np.sqrt(sum(arg**2 for arg in args))


class StressElement(metkObject):
    """
    A stress element containing 3 normal stresses and 3 shear stresses.

    :param S:   Input stress values, either a 1x6 list/array or a 3x3 array.
    """
    def __init__(self, S, name=None):
        if isinstance(S, list):
            S = np.asarray(S)

        if S.shape == (6,):
            self._S11 = float(S[0])
            self._S22 = float(S[1])
            self._S33 = float(S[2])
            self._S12 = float(S[3])
            self._S13 = float(S[4])
            self._S23 = float(S[5])
        
        elif S.shape == (3,3):
            self._S11 = float(S[0][0])
            self._S22 = float(S[1][1])
            self._S33 = float(S[2][2])
            self._S12 = float(S[0][1])
            self._S13 = float(S[0][2])
            self._S23 = float(S[1][2])
        
        self.name = name

    @property
    def Sx(self):
        return self._S11
    
    @property
    def Sy(self):
        return self._S22
    
    @property
    def Sz(self):
        return self._S33
    
    @property
    def Sxy(self):
        return self._S12
    
    @property
    def Syz(self):
        return self._S23
    
    @property
    def Szx(self):
        return self._S13

    @property
    def S(self):
        return np.array([[ self._S11, self._S12, self._S13 ],
                         [ self._S12, self._S22, self._S23 ],
                         [ self._S13, self._S23, self._S33 ]])
    
    @cached_property
    def eig(self):
        '''
        Compute the eigenvalues of the stress tensor to use for calculating
        principal stresses and directions.
        '''
        evals,evecs = np.linalg.eig(self.S)
        p3,p2,p1 = np.sort(evals)
        e3 = evecs[np.where(evals==p3)]
        e2 = evecs[np.where(evals==p2)]
        e1 = evecs[np.where(evals==p1)]
        return (p1,p2,p3), (e1,e2,e3)

    @property
    def principals(self):
        '''The principal stress values as a list, P1 > P2 > P3'''
        return self.eig[0]
    
    @property
    def principal_dirs(self):
        '''The principal stress direction vectors, P1_e, P2_e, P3_e'''
        return self.eig[1]
    
    @property
    def von_mises(self):
        '''The von Mises stress'''
        p1,p2,p3 = self.principals
        return np.sqrt(0.5*( (p1 - p2)**2 + (p2 - p3)**2 + (p3 - p1)**2 ) )
    
    @property
    def P1(self):
        '''First (maximum) principal stress'''
        return self.principals[0]
    
    @property
    def P2(self):
        '''Middle principal stress'''
        return self.principals[1]
    
    @property
    def P3(self):
        '''Third (minimum) principal stress'''
        return self.principals[2]
    
    @property
    def intensity(self):
        '''The stress intensity quantity'''
        return max(
            abs(self.P1 - self.P2),
            abs(self.P2 - self.P3),
            abs(self.P3 - self.P1)
        )
    
    @property
    def tau1(self):
        '''The first principal shear stress'''
        return (self.P1 - self.P3)/2
    
    @property
    def tau2(self):
        '''The second principal shear stress'''
        return (self.P1 - self.P2)/2
    
    @property
    def tau3(self):
        '''The third principal shear stress'''
        return (self.P2 - self.P3)/2
    
    @property
    def series(self):
        '''Return a ``Series`` version containing the element stresses'''
        return Series(
            data=[self.Sx,self.Sy,self.Sz,self.Sxy,self.Syz,self.Sxz],
            index=['Sx','Sy','Sz','Sxy','Syz','Sxz']
        )
    
    def __str__(self):
        return 'StressElement [{},{},{},{},{},{}]'.format(
           format(self._S11, "=6.0f"),
           format(self._S12, "=6.0f"),
           format(self._S13, "=6.0f"),
           format(self._S22, "=6.0f"),
           format(self._S23, "=6.0f"),
           format(self._S33, "=6.0f")
       )
    
    def __repr__(self):
        return f'StressElement({self.series.to_list()})'
    
    # Aliases
    Syx = Sxy
    Szy = Syz
    Sxz = Szx
    max_shear = tau1