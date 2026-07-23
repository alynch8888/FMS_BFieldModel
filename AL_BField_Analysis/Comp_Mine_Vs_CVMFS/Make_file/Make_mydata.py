#List of all the Official Imports I use.
import pickle
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

#From import
from scipy.stats import norm
from scipy.optimize import curve_fit
from datetime import date
from FMS_BFieldModel.AL_BField_Analysis.Scripts_setup.utils.utils import load_pkl, sum_field_maps, shift_x, print_xyz_coord, coord_shift, actual_shift, prep_group, save_summed_txt, find_xyz_mismatches
#Useful names that can be used elsewhere
today = date.today()

##Paths (same as Make_txt_files)##
helicalc_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data/Bmaps/helicalc_partial"
solcalc_path  = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data/Bmaps/SolCalc_partial"

region_name = input("What is the region name for the files you are summing? ")
m_to_mm = input("Do you want to change from m to mm?(y/n) ").strip().lower() == 'y'
T_to_G = input("Do you want to change from Tesla to Gauss?(y/n) ").strip().lower() == 'y'

##Find files in helicalc_partial and SolCalc_partial whose filename contains region_name##
helicalc_region_files = [
    f for f in glob.glob(os.path.join(helicalc_path, "*.pkl"))
    if region_name in os.path.basename(f)
]
solcalc_region_files = [
    f for f in glob.glob(os.path.join(solcalc_path, "*.pkl"))
    if region_name in os.path.basename(f)
]

print(f"Found {len(helicalc_region_files)} helicalc files matching '{region_name}'")
print(f"Found {len(solcalc_region_files)} solcalc files matching '{region_name}'")

if not helicalc_region_files:
    print(f"Warning: no helicalc files matched '{region_name}' — skipping helicalc sum.")
if not solcalc_region_files:
    print(f"Warning: no solcalc files matched '{region_name}' — skipping solcalc sum.")



##########Save the summed pkl as a tab-delimited txt, truncated to `digits` decimals,##########

##Check XYZ alignment (and shift if needed) before summing each group##
if helicalc_region_files:
    helicalc_region_files = prep_group(helicalc_region_files, "helicalc")

if solcalc_region_files:
    solcalc_region_files = prep_group(solcalc_region_files, "solcalc")

file_output_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/AL_BField_Analysis/Comp_Mine_Vs_CVMFS/Make_file/Summed_Files/"

##Sum and save, named after region_name##
if helicalc_region_files:
    sum_field_maps(
        fileoutput_path=file_output_path,#helicalc_path,
        filename=f"helicalcSummed_{region_name}",
        pklarray=helicalc_region_files
    )
    # print("Changing m to mm and Tesla to Gauss...")
    save_summed_txt(
        os.path.join(file_output_path, f"helicalcSummed_{region_name}.pkl"),
        os.path.join(file_output_path, f"helicalcSummed_{region_name}.txt"),
        convert_m_to_mm=m_to_mm,
        convert_T_to_G=T_to_G,
    )

if solcalc_region_files:
    sum_field_maps(
        fileoutput_path=file_output_path,#solcalc_path,
        filename=f"SolCalcSummed_{region_name}",
        pklarray=solcalc_region_files
    )
    # print("Changing m to mm and Tesla to Gauss...")
    save_summed_txt(
        os.path.join(file_output_path, f"SolCalcSummed_{region_name}.pkl"),
        os.path.join(file_output_path, f"SolCalcSummed_{region_name}.txt"),
        convert_m_to_mm=m_to_mm,
        convert_T_to_G=T_to_G,
    )


# Call after definition — combine the two summed outputs into one file
combined_inputs = [
    os.path.join(file_output_path, f"helicalcSummed_{region_name}.pkl"),
    os.path.join(file_output_path, f"SolCalcSummed_{region_name}.pkl"),
]

missing = [f for f in combined_inputs if not os.path.exists(f)]
if missing:
    print("Cannot combine — missing summed file(s):")
    for f in missing:
        print(f"  {f}")
else:
    sum_field_maps(file_output_path, "DS_Summed", combined_inputs)
    # if m_to_mm and T_to_G == 'y':
    #     print("Changing m to mm and Tesla to Gauss...")
    # elif m_to_mm =='y' and T_to_G == 'n':
    #     print("Changed m to mm")
    # elif m_to_mm == 'n' and T_to_G == 'y':
    #     print("Changed Tesla to Gauss")
    save_summed_txt(
        os.path.join(file_output_path, "DS_Summed.pkl"),
        os.path.join(file_output_path, "DS_Summed.txt"),
        convert_m_to_mm= False,
        convert_T_to_G= False,
    )