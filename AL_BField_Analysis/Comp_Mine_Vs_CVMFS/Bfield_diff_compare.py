#List of all the Official Imports I use.
import pickle
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import sys


#From import
from scipy.stats import norm
from scipy.optimize import curve_fit
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # adjust '..' depth to match where this script lives, same as Show_xyz.py
from Scripts_setup.utils.utils import load_pkl  # adjust the module path to match your directory depth

#Useful names that can be used elsewhere
today = date.today()

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...\n") #This prints out the name of the script and the fact that it is running.

coord_cols = ['X', 'Y', 'Z']
field_cols = ['Bx', 'By', 'Bz']

#If your X coords were shifted (coord_shift/actual_shift) and you want them displayed un-shifted, set this.
x_offset_for_display = 0  # e.g. 3896 to undo a -3.896 m shift when printing in mm

def load_field_map(path):
    """Load a field map from a .pkl, a CVMFS-style grid text file (with '#'/param/grid
    header lines followed by a bare 'data' marker line), or a plain delimited text file."""
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pkl':
        return load_pkl(path)

    with open(path, 'r') as f:
        lines = f.readlines()

    # CVMFS-style grid file: "# Origin shift...", "param ...", "grid X0=...", then a
    # line that is just "data", then raw X Y Z Bx By Bz rows with no column header.
    data_start = None
    for i, line in enumerate(lines):
        if line.strip().lower() == 'data':
            data_start = i + 1
            break

    if data_start is not None:
        return pd.read_csv(
            path, sep=r'\s+', header=None, skiprows=data_start,
            names=['X', 'Y', 'Z', 'Bx', 'By', 'Bz']
        )

    # Fallback: plain delimited text, try with a header row first
    df = pd.read_csv(path, sep=r'\s+', comment='#')
    if not {'X', 'Y', 'Z'}.issubset(df.columns):
        # No usable header row — re-read with no header and assign columns by position
        df = pd.read_csv(path, sep=r'\s+', comment='#', header=None)
        cols = df.columns.tolist()
        cols[0], cols[1], cols[2] = 'X', 'Y', 'Z'
        cols[3], cols[4], cols[5] = 'Bx', 'By', 'Bz'
        df.columns = cols
    return df

data_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data/"
Summed_Files_path =  "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/AL_BField_Analysis/Comp_Mine_Vs_CVMFS/Make_File/Summed_Files/"
# if os.path.isdir(Summed_Files_path):
#     print(f"Contents of {Summed_Files_path}:")
#     for f in sorted(os.listdir(Summed_Files_path)):
#         if f.endswith('.pkl'):
#             print(f"  {f}")
# else:
#     print(f"Warning: {Summed_Files_path} is not a directory — skipping listing.")


mydata_path = "DS_Summed.pkl"#input(f"\n Which of your computed pkl field maps do you want to use?\n {Summed_Files_path}").strip()
if not os.path.isabs(mydata_path):
    mydata_path = os.path.join(Summed_Files_path, mydata_path)
cvmfs_path  = f"{data_path}cvmfs_Maps/DSMap.txt".strip()

mydata_df = load_field_map(mydata_path)[coord_cols + field_cols].copy()
cvmfs_df  = load_field_map(cvmfs_path)[coord_cols + field_cols].copy()

##Diagnostic: compare coordinate ranges before merging##
for label, df in [("MyData", mydata_df), ("CVMFS", cvmfs_df)]:
    print(f"\n{label} coordinate ranges:")
    for col in coord_cols:
        print(f"  {col}: {df[col].min():.4f} to {df[col].max():.4f}")

#Round coords to avoid float precision mismatches on merge (per known issue with shifted X values)
for df in (mydata_df, cvmfs_df):
    for col in coord_cols:
        df[col] = df[col].round(3)

#Inner merge — the two files are NOT the same size, so only compare rows where X,Y,Z match in BOTH
merged = mydata_df.merge(cvmfs_df, on=coord_cols, how='inner', suffixes=('_mine', '_cvmfs'))

print(f"MyData rows: {len(mydata_df)}")
print(f"CVMFS rows:  {len(cvmfs_df)}")
print(f"Matching rows (inner join on X,Y,Z): {len(merged)}\n")

if merged.empty:
    print("No matching X, Y, Z coordinates between the two files — nothing to compare.")
    sys.exit(0)

cvmfs_coord  = merged[coord_cols].to_numpy()
mydata_field = merged[[f'{c}_mine' for c in field_cols]].to_numpy()
cvmfs_field  = merged[[f'{c}_cvmfs' for c in field_cols]].to_numpy()

with np.errstate(divide='ignore', invalid='ignore'):
    frac_error = (mydata_field - cvmfs_field) / cvmfs_field

field_error = [frac_error[:, 0], frac_error[:, 1], frac_error[:, 2]]
sep = "--------------------------------------------------"
sep_n = "\n--------------------------------------------------\n"

print(sep_n)
fe_bound = input("What field error bound do you want to look at? ")
print(f"You chose: {fe_bound}")
mask1 = field_error[2] > float(fe_bound)

while True:
    fe_bound = input("\nWhat field error bound do you want to look at? (or 'q' to quit) ")
    if fe_bound.strip().lower() == 'q':
        break

    print(f"You chose: {fe_bound}")
    mask1 = field_error[2] > float(fe_bound)

    if mask1.any():
        coords = cvmfs_coord[mask1]
        errors = field_error[2][mask1]
        true_count = 0
        for (x, y, z), err, (bx0, by0, bz0), (bx1, by1, bz1) in zip(coords, errors, mydata_field[mask1], cvmfs_field[mask1]):
            print(f"MyData Field: Bx: {bx0:.3f} G, By: {by0:.3f} G, Bz: {bz0:.3f} G")
            print(f"CVMFS Field: Bx: {bx1:.3f} G, By: {by1:.3f} G, Bz: {bz1:.3f} G")
            print(f"X: {x + x_offset_for_display:.2f}mm  Y: {y:.2f}mm  Z: {z:.2f}mm | frac_error_Bz: {err:.4f}")
            print(sep + "\n")
            true_count += 1
        print(sep, sep, f"\n# of |B| FracErrs > {fe_bound}: ", true_count)
    else:
        print(f"No rows found with frac_error_Bz > {fe_bound}")
        # print(sep, "\n# of |B| FracErrs > 1: ",test)
        # print(sep, "\n# of |B| FracErrs > 1: ",mask1.sum())