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

today = date.today()

##Paths##
helicalc_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data/Bmaps/helicalc_partial"
solcalc_path  = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data/Bmaps/SolCalc_partial"

region_name = input("What is the region name for the files you are summing? ")
m_to_mm = input("Do you want to change from m to mm?(y/n) ").strip().lower() == 'y'
T_to_G  = input("Do you want to change from Tesla to Gauss?(y/n) ").strip().lower() == 'y'

##Find files##
busbar_arc_region_files = [
    f for f in glob.glob(os.path.join(helicalc_path, "*arc.pkl"))
    if region_name in os.path.basename(f)
]
busbar_straight_region_files = [
    f for f in glob.glob(os.path.join(helicalc_path, "*straight.pkl"))
    if region_name in os.path.basename(f)
]
interlayer_region_files = [
    f for f in glob.glob(os.path.join(helicalc_path, "*_interlayer*.pkl"))
    if region_name in os.path.basename(f)
]
layers_region_files = [
    f for f in glob.glob(os.path.join(helicalc_path, "*_layer_*.pkl"))
    if region_name in os.path.basename(f)
]
solcalc_region_files = [
    f for f in glob.glob(os.path.join(solcalc_path, "*.pkl"))
    if region_name in os.path.basename(f)
]

print(f"Individual helicalc files matching '{region_name}':")
print(f"  Busbar Arc:      {len(busbar_arc_region_files)}")
print(f"  Busbar Straight: {len(busbar_straight_region_files)}")
print(f"  Interlayer:      {len(interlayer_region_files)}")
print(f"  Coil Layers:     {len(layers_region_files)}")
print(f"  SolCalc:         {len(solcalc_region_files)}")

if not any([busbar_arc_region_files, busbar_straight_region_files,
            interlayer_region_files, layers_region_files]):
    print(f"Warning: no helicalc files matched '{region_name}'.")
if not solcalc_region_files:
    print(f"Warning: no solcalc files matched '{region_name}'.")

##Check XYZ alignment (and shift if needed) before summing each group##
print("Checking if XYZ coordinates match...\n")
if busbar_arc_region_files:
    busbar_arc_region_files = prep_group(busbar_arc_region_files, "busbar_arc")
if busbar_straight_region_files:
    busbar_straight_region_files = prep_group(busbar_straight_region_files, "busbar_straight")
if interlayer_region_files:
    interlayer_region_files = prep_group(interlayer_region_files, "interlayer")
if layers_region_files:
    layers_region_files = prep_group(layers_region_files, "layers")
if solcalc_region_files:
    solcalc_region_files = prep_group(solcalc_region_files, "solcalc")
print("\n")

file_output_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/AL_BField_Analysis/Comp_Mine_Vs_CVMFS/Make_file/Summed_Files/"
pkl_output_path = os.path.join(file_output_path, "pkl_files/")
txt_output_path = os.path.join(file_output_path, "txt_files/")
os.makedirs(pkl_output_path, exist_ok=True)
os.makedirs(txt_output_path, exist_ok=True)

map_files = [
    f"busbar_arc_Summed_{region_name}",
    f"busbar_straight_Summed_{region_name}",
    f"interlayerSummed_{region_name}",
    f"Coils_Summed_{region_name}",
    f"SolCalc_Summed_{region_name}",
]
region_file_lists = [
    busbar_arc_region_files,
    busbar_straight_region_files,
    interlayer_region_files,
    layers_region_files,
    solcalc_region_files,
]

##Sum and save each sub-category##
for filename, file_list in zip(map_files, region_file_lists):
    if file_list:
        sum_field_maps(pkl_output_path=pkl_output_path, txt_output_path=txt_output_path, filename=filename, pklarray=file_list)
        save_summed_txt(
            os.path.join(pkl_output_path, f"{filename}.pkl"),
            os.path.join(txt_output_path, f"{filename}.txt"),
            convert_m_to_mm=m_to_mm,
            convert_T_to_G=T_to_G,
        )
        print('\n')

##Combine all into {Region}_Summed##
combined_inputs = [
    os.path.join(pkl_output_path, f"{f}.pkl") for f in map_files
]

missing = [f for f in combined_inputs if not os.path.exists(f)]
if missing:
    print("Cannot combine — missing summed file(s):")
    for f in missing:
        print(f"  {f}")
else:
    sum_field_maps(pkl_output_path=pkl_output_path, txt_output_path=txt_output_path, filename = f"{region_name}_Summed", pklarray = combined_inputs)
    save_summed_txt(
        os.path.join(pkl_output_path, f"{region_name}_Summed.pkl"),
        os.path.join(txt_output_path, f"{region_name}_Summed.txt"),
        convert_m_to_mm=False,
        convert_T_to_G=False,
    )
    print('\n')