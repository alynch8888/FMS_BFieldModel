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
# from Comp_Mine_Vs_CVMFS.Make_txt_files import my_data, cvmfs_data

#Useful names that can be used elsewhere
today = date.today()


#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

data_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/AL_BField_Analysis/Comp_Mine_Vs_CVMFS/Map_Files/Combined_BField_2026-07-10.txt"
data = np.loadtxt(
    data_path,
    skiprows=4000000,#1,
    comments='#',
    delimiter='\t',
)
##########***Remember that cvmfs is initially in mm and Tesla***##########
cvmfs_coord = data[:,0:3]#milimeter
cvmfs_field = data[:,3:6]#Gauss
mydata_field = data[:,6:9]#Gauss

##########Everything should now be in m and Gauss##########
sep = "\n ######################### \n"
j = cvmfs_field.shape[0]
print(j)
for i in range(j):
    fdbx=(cvmfs_field[i,0] - mydata_field[i,0]) / cvmfs_field[i,0]
    fdby=(cvmfs_field[i,1] - mydata_field[i,1]) / cvmfs_field[i,1]
    fdbz=(cvmfs_field[i,2] - mydata_field[i,2]) / cvmfs_field[i,2]
    if i%100000==0:
        print(sep,i,sep)
    if abs(fdbx) > 0.1:
        print("X: ",cvmfs_coord[i,:],cvmfs_field[i,:],mydata_field[i,:])
    if abs(fdby) > 0.1:
        print("Y: ",cvmfs_coord[i,:],cvmfs_field[i,:],mydata_field[i,:])
    if abs(fdbz) > 0.1:
        print("Z: ",cvmfs_coord[i,:],cvmfs_field[i,:],mydata_field[i,:])



# fd = mydata_field - cvmfs_field
# fe = fd/cvmfs_field
# # per_err = 100*frac_error

# if __name__ == "__main__":
#     print("CMVFS_coord",'\n',cvmfs_coord,sep)
#     print("CMVFS_field",'\n',cvmfs_field,sep)
#     print("mydata_field",'\n',mydata_field,sep)
#     print("")
#     print(sep,"Field Difference(Gauss)")
#     print(fd.round(7))
#     print(sep,"Fractional Error")
#     print(fe.round(7))
#     # print(sep,"\n","Percent Error")
#     # print(per_err)
