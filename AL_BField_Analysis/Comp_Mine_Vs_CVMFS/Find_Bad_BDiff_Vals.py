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

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Comp_Mine_Vs_CVMFS.Show_BF_Diff_and_Err import frac_error, cvmfs_coord
#Useful names that can be used elsewhere
today = date.today()

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...\n") #This prints out the name of the script and the fact that it is running. This is done to show which file is running when it is called by another script.

field_error = [frac_error[:, 0], frac_error[:, 1], frac_error[:, 2]]
sep = "\n--------------------------------------------------\n"

# print(field_error,sep)
# print(field_error[2],sep)
# print(field_error[2]>1,sep)
# Values where |frac_error| > 1 (greater than 1 OR less than -1)
mask1 = (field_error[2] > 1) | (field_error[2] < -1)

# # Equivalent shorthand using absolute value
# mask1 = np.abs(field_error[2]) > 1
print(sep)
mask1 = field_error[2] > 1

if mask1.any():
    coords = cvmfs_coord[mask1]
    errors = field_error[2][mask1]
    for (x, y, z), err in zip(coords, errors):
        print(f"X: {x:.2f}  Y: {y:.2f}  Z: {z:.2f}  frac_error_Bz: {err:.6f}")

