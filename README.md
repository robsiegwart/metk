# metk
**M**echanical **E**ngineering **T**ool**k**it

Some classes and utilties for performing mechanical engineering machine design
calculations written in Python.

Originally conceived to address some deficiencies encountered when performing
stress analyses on welds in Excel. In Excel, calculating weld geometric
properties is cumbersome and error-prone, as each weld shape requires its own
formulas for properties like area, I<sub>x</sub>, I<sub>y</sub>, etc. This
complexity prevents the use of Excel drag-down operations and leads to
repetitive, manual work. To solve this, I developed a set of Python classes to
more flexibly handle stress evaluations of welds, particularly those based on
FEA results and following a Blodgett-style approach.

⚠️ Heads up: this is a work-in-progress project. It may contain bugs, incomplete
features, or incorrect assumptions. Don’t use it for real-world engineering work
just yet.

## Package Contents

- `loads` — Classes for defining loads with support for transformation into
  other coordinate systems
- `shapes` — Standard and custom structural shape classes including a built-in
  library of structural shapes from the AISC shapes database
- `materials` — Material classes including a built-in library of some
  engineering materials with basic mechanical properties
- `stress` — Stress analysis and transformation
- `structural` — Classes for structural components (e.g. welds, bolts)

## Examples

### Overview Example

Stress analysis of a weld, given its geometry and loading.

```python
from metk import Weld, DoubleLineWeld, Load

shape = DoubleLineWeld(b=1, d=3)
load = Load(fx=1000, fz=5000, my=-500)
weld = Weld(shape, loads=load, s=0.25, name='Weld 1')

print(weld.max_tensile)
print(weld.max_shear)
print(weld.von_mises)
```

```
4714.757190004715
942.951438000943
5888.72984290278
```

### Shapes

Classes for defining custom shapes or retrieving standard shapes (W, C, HSS,
etc.).

#### Standard shapes

Standard, named, structural shapes as defined in the AISC Shapes Database:
- `W`
- `L`
- `HSS`

```
>>> shape = W('W8X24')
>>> print(shape.A)
7.08
```

The complete AISC Shapes Database (v16) has been converted to a SQLite database
with a table per shape and is included in the package. Properties from this are
retrieved automatically when a standard shape is instantiated.

In any case, you can use the generic `StructuralShape` class and specify the
shape name as a string:

```python
>>> shape = StructuralShape('C9X15')
>>> print(shape.A)
4.4
```

For ones not `W`, `L`, or `HSS`, the raw scalar values from the database are
available on the object.

#### Custom Shapes

Weld shapes:
- `LineWeld`
- `DoubleLineWeld`
- `BoxWeld`

```python
shape = DoubleLineWeld(b=1, d=2)
```

Generic:
- `HollowRectangle`
- `Circle`
- `Rectangle`

Define a custom shape by entering the shape parameters and then access derived
attributes:

```
>>> from metk import Rectangle
>>> shape = Rectangle(4, 6)
>>> print(shape.Ix)
72.0
>>> print(shape.properties)
------  ----
A       24
height  6
width   4
Ix      72
Iy      32
J       75.1
cx_max  2
cy_max  3
------  ----
```

Importing a standard shape from the AISC shapes library:

```
>>> from metk import HSS
>>> shape = HSS('HSS2X2X.125')
>>> print(shape.A)
0.84
>>> print(shape.properties)
------  -----
A       0.84 
height  2    
width   2    
Ix      0.486
Iy      0.486
J       0.796
cx_max  1    
cy_max  1    
tnom    0.125
tdes    0.116
------  -----
```

### Materials

Material classes defining a material with its properties accessible as object
properties (e.g. mat.E or mat.YS).

- `Material`
- `NamedMaterial`

Define a custom material with the `Material` class and assign properties to it.

```python
my_material = Material(E=29e6, mu=0.3, YS=46e3)
```

Or, import a standard library material - some are included in the package (in
English Engineering units):

*steel*
- 4140
- A36
- A500-A (-B, -C, -D)
- A572-50 (-55, -60, -65)
- A992
  
*welding*
- E6010

*bolting*
- Grade 5
- Grade 8

```
>>> from metk import NamedMaterial
>>> material = NamedMaterial('A572-60')
>>> print(material.properties)
---------------------  ----------
density                0.282     
YS_min                 60200     
UTS_min                75400     
modulus of elasticity  29000000.0
elongation             0.16      
---------------------  ----------
>>> print(material.YS)
60200
>>> print(material.Fy)
60200
```

### Stress

`StressElement` represents a 3D stress point defined by its stress components:
normal stresses in x, y, and z; and shear stresses in xy, yz, and xz planes.
Derived stress quantities are then available:

- principal stresses (normal, shear)
- equivelent/von Mises stress
- stress intensity
- max shear, max principal

```
>>> from metk import StressElement
>>> elem = StressElement([12000, 2000, 0, 9000, 0,-200])
>>> print(elem.von_mises)
19160.375779195998
>>> print(elem.intensity)
20600.847753831724
```

### Loads

The `loads` module provides two complementary systems for representing
mechanical loads.

**`Load`** is a complete, self-contained 6-DOF state: all six components
(Fx, Fy, Fz, Mx, My, Mz) in one object, with coordinate transformation built
in. Use it when you already know the full load at a point — for example, from
FEA output — and want to work with it directly or express it in a local
coordinate system.

**`Force` / `Moment` / `CombinedLoad`** are a compositional system for
building up a resultant load from individual contributions. The key capability
that `Load` lacks is `Force.r` — a position vector. When multiple forces are
applied at different locations, `CombinedLoad` sums them and computes the
resultant moment at the origin via `r × F` for each one. `Factor` scales
individual `Force` or `Moment` objects before summing, which is useful for
load combinations (e.g. 1.2D + 1.6L).


#### Axis convention

The `primary` and `secondary` arguments follow a **passive transformation**
convention: they define where the local axes point, expressed in the global
frame. `primary='z'` means "the local x-axis points in the global +z
direction" — not "the global x-axis is renamed z." The load vector itself does
not move; it is simply re-expressed in the new frame by projecting onto the
local axes.

<!-- TODO: add a diagram showing the global frame, the local frame, and a
sample load vector expressed in both -->

#### Transforming loads

```python
>>> from metk import Load
>>> load = Load(fx=1000, fy=500, fz=200)

# by default, the load is defined in the standard coordinate system so the loads
# are aligned and unchanged
>>> print(load.primary, load.secondary)
x y
>>> print(load)
f_x=1,000   f_y=500   f_z=200

# Change it to a new coordinate system orthogonal to the global cartesian
# coordinate system with the local x-axis pointing in the global z direction and
# the local y-axis pointing in the global -x direction.
>>> load.set_axes('z', '-x')
>>> print(load)
f_x=200   f_y=-1,000   f_z=-500

# Define the local coordinate system by numerical unit vectors
>>> load.set_axes([0, 1, 0], [1, 0, 0])
>>> print(load)
f_x=500   f_y=1,000   f_z=-200

# Define the local coordinate system by arbitrary unit vectors
>>> v = np.array([3.0, 1.0, -2.0])
>>> w = np.array([-0.22237479  0.96362411  0.14824986])
# NB: w was calculated to be orthogonal to v as determined via the Gram-Schmidt
# process:
#   ref = np.array([0.0, 1.0, 0.0])     # arbitrary reference vector
#   w = ref - np.dot(ref, u) * u
#   w = w / np.linalg.norm(w)
>>> load.set_axes(v, w)
>>> print(load)
f_x=829   f_y=289   f_z=721
```
