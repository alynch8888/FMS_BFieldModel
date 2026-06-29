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
from Comp_Mine_Vs_CVMFS.Make_txt_files import my_data, cvmfs_data

#Useful names that can be used elsewhere
today = date.today()


#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")
# z = [0,1,2,3,4,5]
#Conversions
#1E4G=1T
#1000mm=1m
##########***Remember that cvmfs is initially in mm and Tesla***##########
cvmfs_coord = cvmfs_data[:,0:3]# This is initially in mm. We are using only one of these so there is not reason to change.
cvmfs_field = cvmfs_data[:,3:6]*1e4 #Unit Change to Gauss

#########***Remember that my_data is initially in m and Gauss***##########
mydata_coord = my_data[:,0:3]#/1e3 #Unit change to m. This change is not actually needed since the coordinates are the same. I use the coordinates from cvmfs, just because.
mydata_field = my_data[:,3:6]#/1e4 #Keep in Gauss for easier to look at values.

##########Everything should now be in m and Gauss##########
# print(cvmfs_data)
# print(cvmfs_coord)
# print(cvmfs_field)
sep = "######################### \n"
# print(sep)
# print(mydata_coord)
# print(mydata_field)
# print(sep)

field_diff = mydata_field - cvmfs_field
frac_error = field_diff/cvmfs_field
per_err = 100*frac_error

if __name__ == "__main__":
    print("")
    print(sep,"Field Difference(Gauss)")
    print(field_diff.round(7))
    print(sep,"Fractional Error")
    print(frac_error.round(7))
    # print(sep,"\n","Percent Error")
    # print(per_err)
