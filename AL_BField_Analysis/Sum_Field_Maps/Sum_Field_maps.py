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

#Useful names that can be used elsewhere
today = date.today()
from FMS_BFieldModel.AL_BField_Analysis.Scripts_setup.utils.utils import shift_x, coord_shift, pkl_2_txt, sum_field_maps, sum_field_maps_w_shift
from Comp_Mine_Vs_CVMFS.Show_BF_Diff_and_Err import cvmfs_coord,cvmfs_field,mydata_coord,mydata_field

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

# Build combined DataFrame
combined = pd.DataFrame({
    'X':         cvmfs_coord[:, 0],
    'Y':         cvmfs_coord[:, 1],
    'Z':         cvmfs_coord[:, 2],
    'cvmfs_Bx':  cvmfs_field[:, 0],
    'cvmfs_By':  cvmfs_field[:, 1],
    'cvmfs_Bz':  cvmfs_field[:, 2],
    'my_Bx':     mydata_field[:, 0],
    'my_By':     mydata_field[:, 1],
    'my_Bz':     mydata_field[:, 2],
})

# Output directory
script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(script_dir, "Map_Files")
os.makedirs(out_dir, exist_ok=True)

# Save txt
txt_path = os.path.join(out_dir, f"Combined_BField_{today}.txt")
combined.to_csv(txt_path, index=False)
print(f"Saved: {txt_path}")

# Save pkl
pkl_path = os.path.join(out_dir, f"Combined_BField_{today}.pkl")
combined.to_pickle(pkl_path)
print(f"Saved: {pkl_path}")