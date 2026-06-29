##Official Imports
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

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
##My Definitions
from Scripts_setup.utils import load_pkl

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

Mount_Directory = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel"

DS_Summed_txt_path = Mount_Directory + "/AL_BField_Analysis/Map_Files/DS_Summed.txt"
DS_Summed_pkl_path = Mount_Directory + "/AL_BField_Analysis/Map_Files/DS_Summed.pkl"

cvmfs_DSMap_txt_path = Mount_Directory + "/helicalc_package/data/cvmfs_BMaps/DSMap.txt"


load_DS_Sum = load_pkl(DS_Summed_pkl_path)

cvmfs_data = np.loadtxt(
    cvmfs_DSMap_txt_path,
    skiprows=4,        # skip a header row
    comments='#',      # ignore lines starting with #
    delimiter=None,    # whitespace by default; use ',' for CSV-like
)

my_data = np.loadtxt(
    DS_Summed_txt_path,
    skiprows=1,        # skip a header row
    comments='#',      # ignore lines starting with #
    delimiter=",",    # whitespace by default; use ',' for CSV-like
)



if __name__ == "__main__":
    print("cvmfs_data: XYZ(mm), BxByBx(Tesla)")
    print(cvmfs_data.round(4))
    print("my_data: XYZ(m), BxByBx(Gauss)")
    print(my_data.round(4))