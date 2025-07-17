'''
This module defines the `StructuralObject` class, which serves as a base for
structural elements like `Weld`, `Member`, and `Bolt`.

'''

from functools import cached_property
from collections.abc import Collection
from pandas import DataFrame, Series
from metk.core import *
import metk.props
from metk.stress import StressElement
from metk.materials import Material, NamedMaterial
from metk.materials.base_materials import BaseMaterial, named_material_exists
from metk.loads import Load
from metk.shapes import Shape
from metk.shapes.structural_shapes import is_structural_shape_label, get_standard_shape
from metk.shapes.generic import is_generic_shape_label, get_generic_shape


class StructuralObject(metkObject):
    '''
    Base class for ``Weld``, ``Member``, and ``Bolt`` classes. Represents some
    geometry or a section combined with a material and some loads. Computes
    nominal stresses at up to 4 corners of the element (left/right, top/bottom).
    Generates various combined stresses based on component stresses
    (von Mises, intensity, max shear).
    '''
    _component_stresses = [
        'Sa',               # Direct axial stress
        'Svx',              # Direct shear stress in x-dir
        'Svy',              # Direct shear stress in y-dir
        'Txy_lr',           # Torsional stress at lower-right corner
        'Txy_ll',           # Torsional stress at lower-left corner
        'Txy_ur',           # Torsional stress at upper-right corner
        'Txy_ul',           # Torsional stress at upper-left corner
        'Sbx_low',          # Bending stress about x-x axis, lower max fiber
        'Sbx_high',         # Bending stress about x-x axis, upper max fiber
        'Sby_left',         # Bending stress about y-y axis, left-most max fiber
        'Sby_right'         # Bending stress about y-y axis, right-most max fiber
    ]
    _combined_stresses =  [
        'Sll',              # Lower-left corner point stress stress element
        'Slr',              # Lower-right corner point stress stress element
        'Sul',              # Upper-left corner point stress stress element
        'Sur'               # Upper-right corner point stress stress element
    ]
    _resultant_stresses = [
        'von_mises',
        'max_tensile',
        'max_shear',
        'max_bending',
        'membrane_plus_bending_min',
        'membrane_plus_bending_max'
    ]
    
    _info_props = []

    def __init__(self, shape, loads, material, **kwargs):
        # Parse shape input
        if isinstance(shape, str):
            if is_structural_shape_label(shape) and get_standard_shape(shape):
                shape = get_standard_shape(shape)
            elif is_generic_shape_label(shape):
                shape = get_generic_shape(shape, kwargs)
            else:
                raise FileNotFoundError(f'Cannot find source for shape "{shape}"')
        elif isinstance(shape, dict):
            shape = Shape(**shape)
        self.label = getattr(shape, 'label', None)

        # Parse material input
        if material:
            if isinstance(material, BaseMaterial):
                pass
            elif isinstance(material, dict):
                material = Material(**material)
            else:
                material = str(material)
                if named_material_exists(material):
                    material = NamedMaterial(material)
                else:
                    raise FileNotFoundError(f'Cannot find source for material "{material}"')

        # Parse loads input
        # TO DO:
        #    - need some provision if 'primary' and 'secondary' are left blank
        #      which pandas converts to nan
        if not loads:
            loads = Load(
                f_x=kwargs.get('f_x',0), f_y=kwargs.get('f_y',0), f_z=kwargs.get('f_z',0),
                m_x=kwargs.get('m_x',0), m_y=kwargs.get('m_y',0), m_z=kwargs.get('m_z',0),
                primary=kwargs.get('primary','x'), secondary=kwargs.get('secondary','y')
            )
        
        self.shape = shape
        self.loads = loads
        self.material = material
        self.description = kwargs.get('description', None)
        self.allowable = kwargs.get('allowable', None)

        self._doc_equations = {}

        self.kwargs = kwargs
        self.name = kwargs.get('name') or kwargs.get('Name') or '<unnamed>'
        
    def get(self, attribute, default=None):
        '''
        Try to get an arbitrary property on the object and delegate lookup to
        sub-objects as needed.
        '''
        sub_obj = prop_lookup(attribute)
        if sub_obj:       # property points to a sub-object
            rval = getattr(getattr(self, sub_obj), attribute, None)
        else:             # otherwise see if it is on the object itself
            rval = self.kwargs.get(attribute, None)
        return rval

    # ========================== Stress Components =============================
    @cached_property
    def Sa(self):
        '''Nominal axial stress ==> Sz, S33'''
        return self.loads.f_z/self.shape.A

    @cached_property
    def Svx(self):
        '''Nominal direct shear stress in X ==> Szx/Sxz, S31/S13'''
        return self.loads.f_x/self.shape.A
        
    @cached_property
    def Svy(self):
        '''Nominal direct shear stress in Y ==> Syz/Szy, S32/S23'''
        return self.loads.f_y/self.shape.A
        
    @cached_property
    def Txy_lr(self):
        '''Torsional stress, lower right ==> Sxy/Syx, S12/S21'''
        return self.loads.m_z*(self.shape.cy_low**2 + self.shape.cx_right**2)**0.5/self.shape.J

    @cached_property
    def Txy_ll(self):
        '''Torsional stress, lower left ==> Sxy/Syx, S12/S21'''
        return self.loads.m_z*(self.shape.cy_low**2 + self.shape.cx_left**2)**0.5/self.shape.J

    @cached_property
    def Txy_ur(self):
        '''Torsional stress, upper right ==> Sxy/Syx, S12/S21'''
        return self.loads.m_z*(self.shape.cy_high**2 + self.shape.cx_right**2)**0.5/self.shape.J

    @cached_property
    def Txy_ul(self):
        '''Torsional stress, upper left ==> Sxy/Syx, S12/S21'''
        return self.loads.m_z*(self.shape.cy_high**2 + self.shape.cx_left**2)**0.5/self.shape.J

    @cached_property
    def Sbx_low(self):
        '''Bending stress about X-X axis, low side ==> Sz, S33'''
        return self.loads.m_x*self.shape.cy_low/self.shape.Ix
        
    @cached_property
    def Sbx_high(self):
        '''Bending stress about X-X axis, high side ==> Sz, S33'''
        return self.loads.m_x*self.shape.cy_high/self.shape.Ix

    @cached_property
    def Sby_left(self):
        '''Bending stress about Y-Y axis, left side ==> Sz, S33'''
        return self.loads.m_y*self.shape.cx_left/self.shape.Iy

    @cached_property
    def Sby_right(self):
        '''Bending stress about Y-Y axis, right side ==> Sz, S33'''
        return self.loads.m_y*self.shape.cx_right/self.shape.Iy
    
    # ================= Corner point combined stress elements ==================
    @cached_property
    def Sll(self):
        return StressElement([
                    [ 0            , self.Txy_ll   , self.Svx                               ],
                    [ self.Txy_ll  , 0             , self.Svy                               ],
                    [ self.Svx     , self.Svy      , self.Sa + self.Sbx_low + self.Sby_left ]
                ],
                name='Sll'
            )

    @cached_property
    def Slr(self):
        return StressElement([
                    [ 0             , self.Txy_lr  , self.Svx                                ],
                    [ self.Txy_lr   , 0            , self.Svy                                ],
                    [ self.Svx      , self.Svy     , self.Sa + self.Sbx_low + self.Sby_right ]
                ],
                name='Slr'
            )

    @cached_property
    def Sul(self):
        return StressElement([
                    [ 0             , self.Txy_ul   , self.Svx                                ],
                    [ self.Txy_ul   , 0             , self.Svy                                ],
                    [ self.Svx      , self.Svy      , self.Sa + self.Sbx_high + self.Sby_left ]
                ],
                name='Sul'
            )

    @cached_property
    def Sur(self):
        return StressElement([
                    [ 0             ,  self.Txy_ur  ,  self.Svx                                 ],
                    [ self.Txy_ur   ,  0            ,  self.Svy                                 ],
                    [ self.Svx      ,  self.Svy     ,  self.Sa + self.Sbx_high + self.Sby_right ]
                ],
                name='Sur'
            )

    # ====================== Derived Stress Quantities =========================
    @property
    def von_mises(self):
        '''
        Maximum von Mises stress across all four corner points.
        
        TODO: Implement exclusion logic on corners that don't exist.
        '''
        return max([ stress.von_mises for stress in [self.Sll, self.Slr, self.Sul, self.Sur] ])
    
    @property
    def Sbx(self):
        '''Maximum bending stress, x-x'''
        return max(abs(self.Sbx_high), abs(self.Sbx_low))

    @property
    def Sby(self):
        '''Maximum bending stress, y-y'''
        return max(abs(self.Sby_right), abs(self.Sby_left))

    @property
    def max_tensile(self):
        return max(
            self.Sa,
            self.Sbx_high,
            self.Sbx_low,
            self.Sby_left,
            self.Sby_right
        )

    @property
    def max_shear(self):
        return max([abs(s) for s in [
            self.Svx,
            self.Svy,
            self.Txy_lr,
            self.Txy_ll,
            self.Txy_ur,
            self.Txy_ul
        ]])
    
    @property
    def max_bending(self):
        return max([abs(s) for s in [
            self.Sbx_low,
            self.Sbx_high,
            self.Sby_left,
            self.Sby_right
        ]])
    
    @property
    def membrane_plus_bending_max(self):
        return max(
            self.Sa + self.Sbx_high,
            self.Sa + self.Sbx_low,
            self.Sa + self.Sby_left,
            self.Sa + self.Sby_right
        )

    @property
    def membrane_plus_bending_min(self):
        return min(
            self.Sa + self.Sbx_high,
            self.Sa + self.Sbx_low,
            self.Sa + self.Sby_left,
            self.Sa + self.Sby_right
        )
    
    def evaluate_doc_equations(self):
        '''
        Update the equations in ``_equations`` so they may be printed with
        their values.
        '''
        # update equations with values for pretty printing
        for k,eq in self._equations.items():
            eq.evaluate()
        for k,eq in self._doc_equations.items():
            eq.evaluate()

    @property
    def series(self):
        '''Compute all derived properties and return as a Series.'''
        data = []
        index = []

        index.append('Name')
        data.append(getattr(self, 'name'))

        for prop in self._info_props:
            val = getattr(self, prop, None)
            if val:
                data.append(val)
                index.append(prop)
                
        for prop in self._component_stresses:
            if prop in index:
                continue
            data.append(getattr(self, prop))
            index.append(prop)
        
        for prop in self._resultant_stresses:
            if prop in index:
                continue
            data.append(getattr(self, prop, None))
            index.append(prop)
        
        for obj in [ self.shape, self.loads, self.material ]:
            if obj is not None:
                for k,v in obj._prop_dict.items():
                    if k in index:
                        continue
                    index.append(k)
                    data.append(v)

        return Series(data, index=index)
    
    @property
    def results_table(self):
        resdict = self.series.to_dict()
        formatted = { k:nformat(v) for k,v in resdict.items() }
        return tabulate(formatted.items())
    

class StructuralObjectGroup(Collection):
    '''
    A group of ``StructuralObject`` items which can all be evaluated at once.
    '''
    def __init__(self, objects, **kwargs):
        self.objects = objects
        for k,v in kwargs.items():
            try:
                setattr(self,k,v)
            except AttributeError:
                continue
        self.result = None
        self.name = kwargs.get('name') or kwargs.get('Name') or ''
        
    def __iter__(self):
        for obj in self.objects:
            yield obj
        
    def sort_cols(self, cols_list):
        cols = cols_list
        cols_new = []
        for c in  metk.props.shape_props \
                + metk.props.material_props \
                + metk.props.load_props \
                + StructuralObject._component_stresses \
                + StructuralObject._resultant_stresses:
            if c in cols_list:
                cols_new.append(c)
                cols.remove(c)
        return cols + cols_new

    def evaluate(self):
        '''
        Compute all properties and derived quantities and return as a DataFrame.
        '''
        result = DataFrame([item.series for item in self.objects])
        result.dropna(axis=1, how='all', inplace=True)
        new_cols = self.sort_cols(result.columns.to_list())
        result = result[self.sort_cols(result.columns.to_list())]
        self.result = result
        return result
    
    def __repr__(self):
        return f'Structural Group containing {len(self.objects)} objects'
    
    def __contains__(self, item):
        return item in self.objects

    def __iter__(self):
        for obj in self.objects:
            yield obj

    def __len__(self):
        return len(self.objects)
    
    def __getitem__(self, index):
        if type(index) != int:
            raise TypeError('Access by index only')
        return self.objects[index]