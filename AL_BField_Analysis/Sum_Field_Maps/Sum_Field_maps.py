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
from Scripts_setup.utils import shift_x, coord_shift, pkl_2_txt, sum_field_maps, sum_field_maps_w_shift

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

shift_x("/content/drive/MyDrive/BFields/data/","DSMap.pkl",coord_shift)

pkl_2_txt("/content/drive/MyDrive/BFields/data/DSMap_x_-3.896.pkl")
#!!!Need to change the paths according to files you are working with.
DSMap_path = "/content/drive/MyDrive/BFields/data/"
Busbar_Sum_path = "/content/drive/MyDrive/BFields/data/Bmaps/helicalc_partial/"
Solcalc_Sum_path = "/content/drive/MyDrive/BFields/data/Bmaps/SolCalc_partial/"

Solcalc_test_path = "/content/drive/MyDrive/BFields/data/Bmaps/SolCalc_partial/Solcalc_Summed.pkl"
DS_Summed_pkl_path = "/content/drive/MyDrive/BFields/data/DS_Summed.pkl"
DS_Sum_pkl_array = ("DSMap_x_-3.896.pkl" #"DSMap.pkl"
                    ,"Busbar_Summed.pkl",
                    "Solcalc_Summed.pkl")

DS_Sum_path_array = (
    DSMap_path + DS_Sum_pkl_array[0],
    Busbar_Sum_path + DS_Sum_pkl_array[1],
    Solcalc_Sum_path + DS_Sum_pkl_array[2]
)



# Call after definition
sum_field_maps(DSMap_path,"DS_Summed",DS_Sum_path_array)


if __name__ == "__main__":
    print("Solcalc_Summed.pkl")
    pkl_2_txt(Solcalc_test_path)
    print("Busbar Summed")
    pkl_2_txt("/content/drive/MyDrive/BFields/data/Bmaps/helicalc_partial/Busbar_Summed.pkl")
    print("DSMap.pkl")
    pkl_2_txt("/content/drive/MyDrive/BFields/data/DSMap_x_-3.896.pkl")
    print("DS_Summed.pkl")
    pkl_2_txt(DS_Summed_pkl_path)
    ########################
    dfs = []
    for fpath in DS_Sum_path_array:
        df = load_pkl(fpath)
        cols = df.columns.tolist()
        cols[3], cols[4], cols[5] = 'Bx', 'By', 'Bz'
        df.columns = cols
        df = df[['X', 'Y', 'Z', 'Bx', 'By', 'Bz']]
        dfs.append(df)
        print(f"{fpath}")
        print(f"  shape: {df.shape}")
        print(f"  X: {df['X'].min()} to {df['X'].max()}")
        print(f"  Y: {df['Y'].min()} to {df['Y'].max()}")
        print(f"  Z: {df['Z'].min()} to {df['Z'].max()}")

    # Check overlap between first two
    common = dfs[0].merge(dfs[1], on=['X','Y','Z'], how='inner')
    print(f"\nOverlap between file 0 and 1: {common.shape[0]} rows")

    common2 = dfs[0].merge(dfs[2], on=['X','Y','Z'], how='inner')
    print(f"Overlap between file 0 and 2: {common2.shape[0]} rows")