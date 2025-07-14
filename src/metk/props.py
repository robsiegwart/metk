'''
Standard names for various properties used in the package.

- Shape
- Material
- Load

The first purpose is to categorize so if a property is looked up on a 'Member'
it may be delegated to the appropriate object. Secondly, aliases are provided so
when various properties are queried the all point to the correct one that is
stored on the object.
'''

# Aliases
# =======
material_prop_aliases = {
    'Fy': 'YS_min',
    'YS': 'YS_min',
    'Fu': 'UTS_min',
    'Futs': 'UTS_min',
    'UTS': 'UTS_min',
    'rho': 'density',
    'E': 'modulus of elasticity'
}


# Categorization
# ==============
shape_props = [ 'A', 'w', 'h', 'b', 'd', 'bf', 'bfdet', 't', 'tf', 'tw',
'twdet', 'tdes', 'tnom', 'x', 'y', 'eo', 'xp', 'yp', 'zA', 'zB', 'zC', 'wA',
'wB', 'wC', 'Ix', 'Iy', 'Iz', 'Iw', 'Sx' 'Sy', 'Sz', 'Zx', 'Zy', 'rx', 'ry',
'rz', 'r', 'Zw', 'Zz', 'J', 'Cw', 'C', 'Wno', 'Sw1', 'Sw2', 'Sw3', 'H',
'cx_left', 'cx_right', 'cy_high', 'cy_low', 'cr_max', '_stress_locations', 'cr',
'A_g', 'A_e', 'Ag', 'Ae', 'A_g', 'A_e', 'Aw', 'A_w', 'label', 'cw', 'cz', 'h',
'h_x', 'h_y', 'hx', 'hy' ]

load_props = [ 'fx', 'fy', 'fz', 'mx', 'my', 'mz', 'mw', 'm_minor', 'm_major',
'primary', 'secondary', 'f_x', 'f_y', 'f_z', 'm_x', 'm_y', 'm_z' ]

material_props = list(material_prop_aliases.keys())