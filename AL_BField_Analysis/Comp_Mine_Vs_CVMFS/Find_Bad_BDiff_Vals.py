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
from Comp_Mine_Vs_CVMFS.Show_BF_Diff_and_Err import frac_error, cvmfs_coord, mydata_field, cvmfs_field
from Combined_Bfield_Eval import fe, fd
#Useful names that can be used elsewhere
today = date.today()

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...\n") #This prints out the name of the script and the fact that it is running. This is done to show which file is running when it is called by another script.

field_error = [frac_error[:, 0], frac_error[:, 1], frac_error[:, 2]]
sep = "--------------------------------------------------"
sep_n = "\n--------------------------------------------------\n"
# print(field_error,sep)
# print(field_error[2],sep)
# print(field_error[2]>1,sep)
# Values where |frac_error| > 1 (greater than 1 OR less than -1)
mask1 = (field_error[2] > 1) | (field_error[2] < -1)

# # Equivalent shorthand using absolute value
# mask1 = np.abs(field_error[2]) > 1
print(sep_n)
fe_bound = input("What field error bound do you want to look at? ")
print(f"You chose: {fe_bound}")
mask1 = field_error[2] > float(fe_bound)
# print("\n # of FracErrs |B|>1: ",len(mask1))

if mask1.any():
    coords = cvmfs_coord[mask1]
    errors = field_error[2][mask1]
    # mydata_field = mydata_field[2][mask1]
    # cvmfs_field = cvmfs_field[2][mask1]
    true_count = 0
    test = 0
    for (x, y, z), err, (bx0,by0,bz0),(bx1,by1,bz1) in zip(coords, errors, mydata_field, cvmfs_field):
        print(f"MyData Field: Bx: {bx0:.3f} G, By: {by0:.3f} G, Bz: {bz0:.3f} G")
        print(f"CVFMS Field: Bx: {bx1:.3f} G, By: {by1:.3f} G, Bz: {bz1:.3f} G")
        print(f"X: {x+3896:.2f}mm  Y: {y:.2f}mm  Z: {z:.2f}mm | frac_error_Bz: {err:.4f}") 
        print(sep+"\n")
        true_count = true_count + 1
        test += 1
    print(sep,sep,"\n# of |B| FracErrs > {fe_bound}: ",true_count)
    # print(sep, "\n# of |B| FracErrs > 1: ",test)
    # print(sep, "\n# of |B| FracErrs > 1: ",mask1.sum())