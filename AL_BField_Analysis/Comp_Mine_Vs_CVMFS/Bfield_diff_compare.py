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
from Scripts_setup.utils.utils import load_pkl, countdown, navigate, load_field_map  # adjust the module path to match your directory depth

#Useful names that can be used elsewhere
today = date.today()

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...\n") #This prints out the name of the script and the fact that it is running.

coord_cols = ['X', 'Y', 'Z']
field_cols = ['Bx', 'By', 'Bz']
#region = input("What region are you looking at? ")
#If your X coords were shifted (coord_shift/actual_shift) and you want them displayed un-shifted, set this.
x_offset_for_display = 0  # e.g. 3896 to undo a -3.896 m shift when printing in mm

data_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data/"

Summed_Files_path =  "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/AL_BField_Analysis/Comp_Mine_Vs_CVMFS/Make_File/Summed_Files/pkl_files"
mydata_path = navigate(Summed_Files_path, "for your data \".pkl\" file?", ".pkl")
mydata_name = os.path.splitext(os.path.basename(mydata_path[0]))[0]


# mydata_path = f"{region}_Summed.pkl"#input(f"\n Which of your computed pkl field maps do you want to use?\n {Summed_Files_path}").strip()
if not os.path.isabs(mydata_path[0]):
    mydata_path = os.path.join(Summed_Files_path, mydata_path[0])

# comparison_path = f"{data_path}Cole_valMaps/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars.txt".strip()
# comparison_name = os.path.splitext(os.path.basename(comparison_path))[0]
comparison_file = navigate(data_path,"for your comparison \".pkl\" file?", ".pkl")
comparison_path, comparison_name = comparison_file[0],comparison_file[1]

mydata_df = load_field_map(mydata_path[0])[coord_cols + field_cols].copy()
comparison_df  = load_field_map(comparison_path)[coord_cols + field_cols].copy()

##Diagnostic: compare coordinate ranges before merging##
for label, df in [(f"\"{mydata_name}\"", mydata_df), (f"\"{comparison_name}\"", comparison_df)]:
    print(f"\n{label} coordinate ranges:")
    for col in coord_cols:
        print(f"  {col}: {df[col].min():.4f} to {df[col].max():.4f}")

#Round coords to avoid float precision mismatches on merge (per known issue with shifted X values)
for df in (mydata_df, comparison_df):
    for col in coord_cols:
        df[col] = df[col].round(3)

#Inner merge — the two files are NOT the same size, so only compare rows where X,Y,Z match in BOTH
merged = mydata_df.merge(comparison_df, on=coord_cols, how='inner', suffixes=('_mine', '_cvmfs'))
merged = merged.dropna()
# print(f"\nMatched points ({len(merged)}):")
# print(merged[coord_cols + [f'{c}_mine' for c in field_cols] + [f'{c}_cvmfs' for c in field_cols]].to_string(index=False))


print(f"\n{mydata_name} rows: {len(mydata_df)}")
print(f"{comparison_name} rows:  {len(comparison_df)}")
print(f"Matching rows (inner join on X,Y,Z): {len(merged)}\n")

if merged.empty:
    print("No matching X, Y, Z coordinates between the two files — nothing to compare.")
    sys.exit(0)


comparison_coord  = merged[coord_cols].to_numpy()
mydata_field = merged[[f'{c}_mine' for c in field_cols]].to_numpy()
comparison_field  = merged[[f'{c}_cvmfs' for c in field_cols]].to_numpy()

with np.errstate(divide='ignore', invalid='ignore'):
    field_diff = mydata_field - comparison_field
    frac_error = field_diff / comparison_field
    frac_diff = mydata_field / comparison_field

field_error = [frac_error[:, 0], frac_error[:, 1], frac_error[:, 2]]
sep = "--------------------------------------------------"
sep_n = "\n--------------------------------------------------\n"

if __name__ == "__main__":
    print(sep_n)
    # fe_bound = input("What field error bound do you want to look at? ")
    # print(f"You chose: {fe_bound}")
    # mask1 = field_error[2] > float(fe_bound)

    while True:
        bf_trigger_min = 0
        bf_trigger_max = 0
        fe_bound_min = 0
        fe_bound_max = 0
        print(f"Min BField(T): {round(np.min(mydata_field[:, 2]),4)}    Min FracErr: {round(np.min(field_error[2]),4)}")
        print(f"Ave BField(T): {round(np.mean(mydata_field[:, 2]),4)}   Ave FracErr: {round(np.mean(field_error[2]),4)}")
        print(f"Max BField(T): {round(np.max(mydata_field[:, 2]),4)}    Max FracErr: {round(np.max(field_error[2]),4)}")
        bf_trigger_min = input("\nWhat min Bfield(T) do you want to cutoff? (or 'q' to quit) ")
        if bf_trigger_min.strip().lower() == 'q':
            break
        bf_trigger_max = input("\nWhat max Bfield(T) do you want to cutoff? (or 'q' to quit) ")
        if bf_trigger_max.strip().lower() == 'q':
            break
        fe_bound_min = input("\nWhat min frac field error bound do you want to look at? (or 'q' to quit) ")
        if fe_bound_min.strip().lower() == 'q':
            break
        fe_bound_max = input("\nWhat max frac field error bound do you want to look at? (or 'q' to quit) ")
        if fe_bound_max.strip().lower() == 'q':
            break
        print(sep)
        

        # print(f"You are triggering between {fe_bound_min} & {fe_bound_max}")

        mask1 = (abs(field_error[2]) > float(fe_bound_min)) & (abs(field_error[2]) < float(fe_bound_max))
        mask2 = (abs(mydata_field[:, 2]) > float(bf_trigger_min)) & (abs(mydata_field[:, 2]) < float(bf_trigger_max))
        mask = mask1 & mask2

        if mask.any():
            coords = comparison_coord[mask]
            errors = field_error[2][mask]
            my_field = mydata_field[mask]
            cv_field = comparison_field[mask]
            true_count = 0
            for (x, y, z), err, (bx0, by0, bz0), (bx1, by1, bz1) in zip(coords, errors, my_field, cv_field):
                print(f"Coords: X: {x + x_offset_for_display:.2f}mm  Y: {y:.2f}mm  Z: {z:.2f}mm | frac_error_Bz: {err:.4f}")
                print(f"MyData Field: Bx: {bx0:.3f} G, By: {by0:.3f} G, Bz: {bz0:.3f} G")
                print(f"CVMFS Field:  Bx: {bx1:.3f} G, By: {by1:.3f} G, Bz: {bz1:.3f} G")
                print(sep + "\n")
                true_count += 1
            print(sep, f"\n|B| Field Trigger: {bf_trigger_min} < |B| < {bf_trigger_max}")
            print(f"# of |B| {fe_bound_min} < FracErrs < {fe_bound_max}: ", true_count)
            
            trigger_frac = true_count / len(merged)
            print(f"Triggered Frac Error: {round(trigger_frac, 5)}","\n")
        else:
            print(f"No rows found matching both conditions.")
