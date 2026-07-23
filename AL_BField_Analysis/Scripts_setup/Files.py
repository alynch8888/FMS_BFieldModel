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

##Data pkl files##
data_pkl_array = [
    "DSMap.pkl",
    "PSMap.pkl"
]
##Helicalc pkl files##
N_arc        = list(range(1,8,1))
N_straight   = [12, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
N_interlayer = [56, 57]#, 58]
N_layer_1      = list(range(56,67,1))#[56, 60, 63]
N_layer_2      = list(range(56,67,1))#[56]
# print(list(range(1,8,1)))
region_name = input("What is the prefix of the file you are using? ")
helicalc_partial_pkl_array = (
    [f"Mu2e_V13.{region_name}_region.standard-busbar.cond_N_{n}_arc.pkl"                  for n in N_arc] +
    [f"Mu2e_V13.{region_name}_region.standard-busbar.cond_N_{n}_straight.pkl"             for n in N_straight] +
    [f"Mu2e_V13.{region_name}_region.standard-helicalc.coil_{n}_interlayer.pkl"           for n in N_interlayer] +
    [f"Mu2e_V13.{region_name}_region.standard-helicalc.coil_{n}_layer_1.pkl"              for n in N_layer_1] +
    [f"Mu2e_V13.{region_name}_region.standard-helicalc.coil_{n}_layer_2.pkl"              for n in N_layer_2]
)

# print(set(filenames) == set(helicalc_partial_pkl_array))
##Solcalc pkl files##
N_PS_coil = list(range(66, 0, -1))
# N_DSCyFMSAll_coil = list(range(66, 0, -1))
# N_DSCyFMSAll_Jacobian_coil = list(range(66, 0, -1))
solcalc_partial_pkl_array = (
    [f"Mu2e_V13.SolCalc.{region_name}_region.standard.coil_{n}.pkl" for n in N_PS_coil] #+
    # ["Mu2e_V13.SolCalc.D0S_region.standard.coils_1-66.pkl"
    #  ]
)
print(data_pkl_array)
print(helicalc_partial_pkl_array)
print(solcalc_partial_pkl_array)
# print(len(solcalc_partial_pkl_array))
# pkl_2_txt


data_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data"#"/content/drive/MyDrive/BFields/data"
helicalc_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data/Bmaps/helicalc_partial"#"/content/drive/MyDrive/BFields/data/Bmaps/helicalc_partial"
solcalc_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/helicalc_package/data/Bmaps/SolCalc_partial"#"/content/drive/MyDrive/BFields/data/Bmaps/SolCalc_partial"

#Helicalc_Drive Check(Data path)#
print("Checking " + data_path + "...")
missing_data = [f for f in data_pkl_array if not os.path.exists(os.path.join(data_path, f))]
found_data   = [f for f in data_pkl_array if     os.path.exists(os.path.join(data_path, f))]
print(f"Data Files Found:   {len(found_data)}")
print(f"Data Files Missing: {len(missing_data)}")

#Helicalc Busbar Check(helicalc_partial path)#
print("Checking Helicalc " + helicalc_path + "...")
missing_helicalc = [g for g in helicalc_partial_pkl_array if not os.path.exists(os.path.join(helicalc_path, g))]
found_helicalc   = [g for g in helicalc_partial_pkl_array if     os.path.exists(os.path.join(helicalc_path, g))]
print(f"Helicalc Files Found:   {len(found_helicalc)}")
print(f"Helicalc Files Missing: {len(missing_helicalc)}")

#Solcalc Check(solcalc_partial#
print("Checking Solcalc " + solcalc_path + "...")
missing_solcalc = [h for h in solcalc_partial_pkl_array if not os.path.exists(os.path.join(solcalc_path, h))]
found_solcalc   = [h for h in solcalc_partial_pkl_array if     os.path.exists(os.path.join(solcalc_path, h))]
print(f"Solcalc Files Found:   {len(found_solcalc)}")
print(f"Solcalc Files Missing: {len(missing_solcalc)}")

##Directory Names##
DSMap_pkl = data_path + "/" + data_pkl_array[0]
PSMap_pkl = data_path + "/" + data_pkl_array[1]
Data_file = [data_path + "/" + q for q in data_pkl_array]
Helicalc_file = [helicalc_path + "/" + w for w in helicalc_partial_pkl_array]
Solcalc_file = [solcalc_path + "/" + e for e in solcalc_partial_pkl_array]
##Checks if all files are found##
if missing_data:
    print("\nMissing files:")
    for f in missing_data:
        print(f"  {f}")
if missing_helicalc:
    print("\nMissing files:")
    for g in missing_helicalc:
        print(f"  {g}")
if missing_solcalc:
    print("\nMissing files:")
    for h in missing_solcalc:
        print(f"  {h}")