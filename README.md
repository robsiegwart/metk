# metk
**M**echanical **E**ngineering **T**ool**k**it

Some classes and utilties for performing mechanical engineering machine design
calculations written in Python.

## Package contents

- `materials` -- Material classes including a built-in library of common
  engineering materials with mechanical properties
- `shapes` -- Standard and custom structural shape classes including a built-in
  library of structural shapes from the AISC shapes database
- `stress` -- Utilities for stress analysis

## Examples

### Materials

Material classes defining a material with its properties accessible as object
properties (e.g. mat.E or mat.YS).

- `Material`
- `NamedMaterial`

Define a custom material with the `Material` class and assign properties to it.
Refer to the naming conventions to for consistency. It basically is just a
container for key-value data accessible as properties on the object.

Or, import a standard library material - some are included in the package so
far:

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

```python
>>> from metk import NamedMaterial
>>> mat1 = NamedMaterial('A572-60')
>>> print(mat1.properties)
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
>>> print(mat1.YS)
60200
>>> print(mat1.Fy)
60200
```


### Shapes

Classes to define and retrive steructural shapes and obtain derived properties.

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


Importing from the shapes library:

```python
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

Defining a custom shape:

```python
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
```

### Stress

```python
from metk import StressElement
elem = StressElement([12000, 2000, 0, 9000, 0,-200])
print(elem.von_mises)
19160.375779195998
print(elem.intensity)
20600.847753831724
```