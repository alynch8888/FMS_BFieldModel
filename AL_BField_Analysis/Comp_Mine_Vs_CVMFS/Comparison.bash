##Don't what's comment here. I am showing the order in which the files run.##
#Make_txt_file.py
#Show_BF_Diff_and_Err.py

##

##Run what's below.
python Comp_dB_XYZ.py && \
python Comp_dB_XYZ_splits.py && \
python Gauss_Fit_XYZ_NoSplit.py && \
python Frac_Err_Plots.py && \
python Frac_Err_Gauss_Fit.py && \
