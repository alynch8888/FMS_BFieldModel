import os
import sys
import time
import subprocess
import pandas as pd

from scipy.interpolate import RegularGridInterpolator
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from AL_BField_Analysis.Scripts_setup.utils.utils import countdown, navigate
import numpy as np


#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...\n") #This prints out the name of the script and the fact that it is running.

# interpolator_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/AL_BField_Analysis/Comp_Mine_Vs_CVMFS/Make_file/Summed_Files"
# interpolatee_file_path ="/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data"

interpolator_path ="/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data/Cole_valMaps"
interpolatee_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/AL_BField_Analysis/Comp_Mine_Vs_CVMFS/Make_file/Summed_Files/txt_files"

# interpolator_file = navigate(interpolator_path, "to interpolate(.txt)", ".txt")
# interpolatee_file = navigate(interpolatee_file_path, "to interpolate against(.txt)", ".txt")
interpolator_path = navigate(interpolator_path, "as your interpolator \".txt\" file? Interpolator is the reference grid from which you are interpolating.", ".txt")
interpolatee_path = navigate(interpolatee_path, "as you interpolatee \".txt\" file? Interpolatee is the file whose coordinate you are interpolating onto.", ".txt")

interpolator_df = pd.read_csv(interpolator_path[0], sep=r'\s+', skiprows=3, header=None, names=['X', 'Y', 'Z', 'Bx', 'By', 'Bz'])
# print(interpolatee_df)
interpolatee_df = pd.read_csv(interpolatee_path[0], sep='\t', skiprows=[0], low_memory=False)

interpolator_df = interpolator_df.apply(pd.to_numeric, errors='coerce').dropna()
interpolatee_df = interpolatee_df.apply(pd.to_numeric, errors='coerce').dropna()

interpolator_name = interpolator_path[1]
interpolatee_name = interpolatee_path[1]

x_pts = np.unique(interpolator_df['X'])
y_pts = np.unique(interpolator_df['Y'])
z_pts = np.unique(interpolator_df['Z'])

mask_confirm = input("Do you only want to see overlapping points?(y/n) ").strip().lower() == 'y'

if mask_confirm:
    ##-----This is creating a using a datafile masked by the interpolator-----##

    # Find interpolator bounds
    x_min, x_max = interpolator_df['X'].min(), interpolator_df['X'].max()
    y_min, y_max = interpolator_df['Y'].min(), interpolator_df['Y'].max()
    z_min, z_max = interpolator_df['Z'].min(), interpolator_df['Z'].max()

    # Filter interpolatee to overlap region only
    overlap_mask = (
        (interpolatee_df['X'] >= x_min) & (interpolatee_df['X'] <= x_max) &
        (interpolatee_df['Y'] >= y_min) & (interpolatee_df['Y'] <= y_max) &
        (interpolatee_df['Z'] >= z_min) & (interpolatee_df['Z'] <= z_max)
    )
    query_df = interpolatee_df[overlap_mask].copy()
    print(f"Overlap points: {len(query_df)}")

else:
    ##-----This is not using a mask-----##
    query_df = interpolatee_df.copy()


##-----Now we will interpolate-----##

comp_sorted = interpolator_df.sort_values(['X', 'Y', 'Z'])
shape = (len(x_pts), len(y_pts), len(z_pts))
query_pts = query_df[['X', 'Y', 'Z']].values

for component in ['Bx', 'By', 'Bz']:
    comp_grid = comp_sorted[component].values.reshape(shape)
    interp = RegularGridInterpolator((x_pts, y_pts, z_pts), comp_grid, method='linear', bounds_error=False, fill_value=np.nan)
    query_df[f'{component}_interp'] = interp(query_pts)

for component in ['Bx', 'By', 'Bz']:
    orig = query_df[component].astype(float)
    interp_vals = query_df[f'{component}_interp']
    frac_err    = (interp_vals - orig) / orig.abs()
    print(f"\n{component} fractional error (interp vs DSTracker):")
    print(f"  mean:  {frac_err.mean():.4f}")
    print(f"  std:   {frac_err.std():.4f}")
    print(f"  min:   {frac_err.min():.4f}")
    print(f"  max:   {frac_err.max():.4f}")

output_df = query_df[['X', 'Y', 'Z', 'Bx_interp', 'By_interp', 'Bz_interp']].copy()
output_df.rename(columns={'Bx_interp': 'Bx', 'By_interp': 'By', 'Bz_interp': 'Bz'}, inplace=True)


output_txt_path = os.path.join(os.path.dirname(interpolator_path[0]), f"{interpolator_name}_Interpolated.txt")
output_pkl_path = os.path.join(os.path.dirname(interpolator_path[0]), f"{interpolator_name}_Interpolated.pkl")

output_df.to_csv(output_txt_path, sep='\t', index=False)
output_df.to_pickle(output_pkl_path)
print(f"Saved to {output_txt_path}")
print(f"Saved to {output_pkl_path}")



    
    # for component in ['Bx', 'By', 'Bz']:
    #     comp_grid = comp_sorted[component].values.reshape(shape)
    #     interp    = RegularGridInterpolator((x_pts, y_pts, z_pts), comp_grid, method='linear', bounds_error=False, fill_value=np.nan)
    #     overlap_df[f'{component}_interp'] = interp(query_pts)

    # for component in ['Bx', 'By', 'Bz']:
    #     orig   = overlap_df[component].astype(float)
    #     interp_vals = overlap_df[f'{component}_interp']
    #     frac_err = (interp_vals - orig) / orig.abs()
    #     print(f"\n{component} fractional error (interp vs DSTracker):")
    #     print(f"  mean:  {frac_err.mean():.4f}")
    #     print(f"  std:   {frac_err.std():.4f}")
    #     print(f"  min:   {frac_err.min():.4f}")
    #     print(f"  max:   {frac_err.max():.4f}")

    # output_df = overlap_df[['X', 'Y', 'Z', 'Bx_interp', 'By_interp', 'Bz_interp']].copy()
    # output_df.rename(columns={'Bx_interp': 'Bx', 'By_interp': 'By', 'Bz_interp': 'Bz'}, inplace=True)


    # output_txt_path = os.path.join(os.path.dirname(interpolator_path[0]), f"{interpolator_name}_Interpolated.txt")
    # output_pkl_path = os.path.join(os.path.dirname(interpolator_path[0]), f"{interpolator_name}_Interpolated.pkl")

    # output_df.to_csv(output_txt_path, sep='\t', index=False)
    # output_df.to_pickle(output_pkl_path)
    # print(f"Saved to {output_txt_path}")
    # print(f"Saved to {output_pkl_path}")