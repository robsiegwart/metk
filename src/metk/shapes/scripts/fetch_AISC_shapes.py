'''
Download and parse structural shapes database from AISC and save to a SQLite
database. The source data is available at:

    https://www.aisc.org/aisc/publications/steel-construction-manual/aisc-shapes-database-v160/

Fetches the AISC shapes Excel database, splits it by shape type, and writes
each type as a table in a SQLite database at:

    ../structural_shape_data/shapes.db

Run this script whenever the upstream database is updated. The output file is
committed to the repository in place of the previous per-type pickle files.
'''

import os
import sqlite3
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

DB_URL  = 'https://cloud.aisc.org/biggie_bin/aisc-shapes-database-v160-2.xlsx'
OUT_PATH = os.path.join('..', 'structural_shape_data', 'shapes.db')

print('Downloading AISC shapes database...')
data = pd.read_excel(DB_URL, sheet_name='Database v16.0')
print(f'  {len(data)} rows, {len(data.columns)} columns')

shape_types = sorted(data['Type'].dropna().unique())
print(f'  Shape types: {shape_types}')

def dedup_columns(df):
    '''
    Rename columns that are case-insensitive duplicates of each other.

    SQLite column names are case-insensitive, so a DataFrame with both 'B' and
    'b' will fail on to_sql(). The second occurrence of any case-insensitive
    duplicate is renamed by appending '_1', '_2', etc.

    Returns (renamed_df, renames_dict).
    '''
    seen = {}
    new_cols = []
    renames = {}
    for col in df.columns:
        key = col.lower()
        if key in seen:
            n = seen[key]
            seen[key] += 1
            new_name = f'{col}_{n}'
            renames[col] = new_name
            new_cols.append(new_name)
        else:
            seen[key] = 1
            new_cols.append(col)
    df = df.copy()
    df.columns = new_cols
    return df, renames


data, renames = dedup_columns(data)
if renames:
    print(f'  Column renames (SQLite case conflict): {renames}')

print(f'\nWriting to {os.path.abspath(OUT_PATH)}')
with sqlite3.connect(OUT_PATH) as conn:
    for shape_type in shape_types:
        subset = data[data['Type'] == shape_type].reset_index(drop=True)
        # Drop columns with no data for this shape type. The AISC spreadsheet
        # uses an en dash (–, U+2013) for non-applicable properties, sometimes
        # mixed with NaN, so treat both as empty.
        empty = ((subset == '\u2013') | subset.isna()).all()
        subset = subset.loc[:, ~empty]
        subset.to_sql(shape_type, conn, if_exists='replace', index=False)
        print(f'  {shape_type:<6} {len(subset)} shapes, {len(subset.columns)} columns')

print('\nDone.')
