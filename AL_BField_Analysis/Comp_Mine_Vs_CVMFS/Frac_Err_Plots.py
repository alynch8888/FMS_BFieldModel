##Fractional Error Plots##

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

from Show_BF_Diff_and_Err import cvmfs_coord, frac_error
#Useful names that can be used elsewhere
today = date.today()

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

# cvmfs_coord = cvmfs_data[:,0:3]# This is initially in mm. We are using only one of these so there is not reason to change.
# cvmfs_field = cvmfs_data[:,3:6]*1e4 #Unit Change to Gauss

z_coord = cvmfs_coord[:,2]

# linthresh2 = 1e-10
# pos_bins = np.logspace(np.log10(linthresh2), np.log10(1e-3), 25)
# neg_bins = -pos_bins[::-1]
# bins = np.concatenate([neg_bins, pos_bins])

z_ranges = [(i * 1e3, (i + 1) * 1e3) for i in range(3, 17)] # In mm!
colors = ["steelblue", "darkorange", "seagreen"]
labels = [r"$B_x(FracErr)$", r"$B_y(FracErr)$", r"$B_z(FracErr)$"]


fig, axes = plt.subplots(len(z_ranges), 3, figsize=(15, 4 * len(z_ranges)))

for row, (lo, hi) in enumerate(z_ranges):
    mask = (z_coord >= lo) & (z_coord < hi)
    fd_slice = frac_error[mask]

    for col in range(3):
        ax = axes[row, col]
        data_col = fd_slice[:, col]

        if data_col.size == 0:
            continue

        ax.hist(data_col, bins=50, edgecolor="black",
                 color=colors[col], alpha=1, label=labels[col])
        # ax.set_xscale("symlog", linthresh=1e-5)
        ax.set_yscale("symlog")
        ax.tick_params(axis='x', rotation=45)
        ax.set_xlabel(labels[col])
        ax.set_xlim(data_col.min(), data_col.max())
        ax.set_title(f"{labels[col]}, z: {lo:.0f}-{hi:.0f}mm")
        ax.legend()

    axes[row, 0].set_ylabel("Count")

#Tracker region Z-range: 8540mm - 1181mm


if __name__ == "__main__":
    fracerror_title = r"$\frac{\mathrm{My\ Data} - \mathrm{CVMFS\ Data}}{\mathrm{CVMFS\ Data}}$"+"\n"+"\n"+"Date made: "+f"{today}"
    fig.suptitle(fracerror_title, fontsize=16, y=1.0)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.tight_layout()

    # Save figure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_dir = os.path.join(script_dir, "Comparison_Plots", f"{today}")
    os.makedirs(plot_dir, exist_ok=True)
    filename = f"Frac_Err_Plots_{today}.png"
    fig.savefig(os.path.join(plot_dir, filename), bbox_inches='tight', dpi=150)
    print(f"Saved: {os.path.join(plot_dir, filename)}")

# plt.show()