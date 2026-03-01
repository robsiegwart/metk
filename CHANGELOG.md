# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `Load` coordinate transformation via rotation matrices, replacing a
  90-degree-only lookup table. Supports both axis label strings (`'x'`,
  `'-z'`) and arbitrary orthogonal unit vectors for `primary`/`secondary`.
- Initial test suite covering `loads`, `shapes`, `materials`, `stress`, and
  integration tests.
- AISC Shapes Database v16.0 converted from Excel to SQLite (`shapes.db`).
  Each shape type is stored as its own table with only applicable columns.
  Fetch/conversion script at `src/metk/shapes/scripts/fetch_AISC_shapes.py`.
- `_GenericStandardShape` fallback class so any shape type in the database
  (e.g. `MC`, `C`, `WT`) is accessible via `StructuralShape()` for scalar
  property access without requiring a dedicated subclass.

### Fixed
- `Load.__add__` and `Load.__mul__` used Python list operators (`+`, `*`)
  instead of element-wise numpy arithmetic; corrected by returning the raw
  numpy array from `value`.
- `Circle.J` torsional constant formula corrected to `π r⁴ / 2`.

### Changed
- Structural shape data migrated from per-type pickle files to a single
  SQLite database, eliminating the pickle dependency and opening the data
  format.
- `Load` transformation refactored from a lookup table to a general
  rotation-matrix approach (`R = [x_local | y_local | z_local]`,
  `v_local = Rᵀ @ v_global`).


## [0.1.0] - July 2025

### Added
- Initial release with core functionality for structural shapes, loads, and
  coordinate transformations.

**Shapes**

- `Circle`, `Rectangle`, `HollowRectangle` generic shape classes.
- `W`, `L`, `HSS` structural shape classes with compactness checks
(`is_compact`, `is_slender`) per AISC 360-16.
- Generic `StructuralShape` class for accessing any shape in the database by
  name.
-  Weld shapes `LineWeld`, `DoubleLineWeld`, `BoxWeld` for weld calculations.

**Materials**
- `Material`, `NamedMaterial` material classes with properties like `E`, `Fy`,
  `Fu`.

**Loads**
- `Factor`, `Load`, `Force`, `Moment`, `CombinedLoad` load classes.

**Structural**
- `Member`, `Weld`, and `Bolt` classes for representing structural elements and
  connections.