# metk
**M**echanical **E**ngineering **T**ool**k**it

Some classes and utilties for performing mechanical engineering machine design
calculations written in Python.

Originally developed to help perform stress analysis on welds. Having many welds
in your design it was commonplace to use Excel to perform stress analyses.
However, Excel had shortcomings when it came to weld geometry. Geometric
properties like area, Ix, Iy, all have different formulas depending on the shape
of the weld. Thus, this required different formulas and prevented the usual
fill-down operation in Excel. So, I wrote some Python classes to more flexibly
handle stress evalations of welds, and specifically based on FEA analyses and
using the Blodgett-style approach.

## Package contents

- `materials` -- Material classes including a built-in library of common
  engineering materials with mechanical properties
- `shapes` -- Standard and custom structural shape classes including a built-in
  library of structural shapes from the AISC shapes database
- `stress` -- Stress analysis and transformation
- `structural` -- Classes for structural components (e.g. welds)

## Examples

### Overview Example

Input script, defining a weld geometry and its loads:

```python
from metk import Weld, DoubleLineWeld, Load

shape = DoubleLineWeld(b=1.0, d=3)
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

### Materials

Material classes defining a material with its properties accessible as object
properties (e.g. mat.E or mat.YS).

- `Material`
- `NamedMaterial`

Define a custom material with the `Material` class and assign properties to it.
Or, import a standard library material - some are included in the package (in
English Engineering units):

- 4140
- A36
- A500-A
- A500-B
- A500-C
- A500-D
- A572-50
- A572-55
- A572-60
- A572-65
- A992
- E6010
- Grade 5
- Grade 8

```
>>> from metk import NamedMaterial
>>> material = NamedMaterial('A572-60')
>>> print(material.properties)
+-----------------------+------------+
| density               | 0.282      |
+-----------------------+------------+
| YS_min                | 60200      |
+-----------------------+------------+
| UTS_min               | 75400      |
+-----------------------+------------+
| modulus of elasticity | 29000000.0 |
+-----------------------+------------+
| elongation            | 0.16       |
+-----------------------+------------+
>>> print(material.YS)
60200
>>> print(material.Fy)
60200
```

### Shapes

Classes to define and retrieve structural shapes and obtain derived properties.

Structural shapes as defined in the AISC Shapes Database:
- `W`
- `L`
- `HSS`

Weld shapes:
- `LineWeld`
- `DoubleLineWeld`
- `BoxWeld`

Generic:
- `HollowRectangle`
- `Circle`
- `Rectangle`

Defining a custom shape:

```
>>> from metk import Rectangle
>>> shape = Rectangle(4, 6)
>>> print(shape.properties)
+--------+------+
| A      | 24   |
+--------+------+
| height | 6    |
+--------+------+
| width  | 4    |
+--------+------+
| Ix     | 72   |
+--------+------+
| Iy     | 32   |
+--------+------+
| J      | 75.1 |
+--------+------+
| cx_max | 2    |
+--------+------+
| cy_max | 3    |
+--------+------+
>>> print(shape.Ix)
72.0
```

Importing from the shapes library:

```
>>> from metk import HSS
>>> shape = HSS('HSS2X2X.125')
>>> print(shape.properties)
+--------+-------+
| A      | 0.84  |
+--------+-------+
| height | 2     |
+--------+-------+
| width  | 2     |
+--------+-------+
| Ix     | 0.486 |
+--------+-------+
| Iy     | 0.486 |
+--------+-------+
| J      | 0.796 |
+--------+-------+
| cx_max | 1     |
+--------+-------+
| cy_max | 1     |
+--------+-------+
| tnom   | 0.125 |
+--------+-------+
| tdes   | 0.116 |
+--------+-------+
>>> print(shape.A)
0.84
```

### Stress

```
>>> from metk import StressElement
>>> elem = StressElement([12000, 2000, 0, 9000, 0,-200])
>>> print(elem.von_mises)
19160.375779195998
>>> print(elem.intensity)
20600.847753831724
```