#List of all the Official Imports I use.
# import pickle
import os
# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import plotly.graph_objects as go
# import sys


#From import
# from scipy.stats import norm
# from scipy.optimize import curve_fit
from datetime import date

#Useful names that can be used elsewhere
today = date.today()

# Plot Differences between my_data and cvmfs_data
# from Show_BF_Diff_and_Err import field_diff, frac_error
from Bfield_diff_compare import cvmfs_coord, mydata_field, cvmfs_field, field_diff

from Combined_Bfield_Eval import fd, fe
# from Scripts_setup.utils import 

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

# field_error = [frac_error[:, 0], frac_error[:, 1], frac_error[:, 2]]
field_error = [fe[:, 0], fe[:, 1], fe[:, 2]]


#Logarithmic bin setup
linthresh1 = 1e-10
pos_bins = np.logspace(np.log10(linthresh1), np.log10(1e-3), 25)
neg_bins = -pos_bins[::-1]
bins = np.concatenate([neg_bins, pos_bins])

field_data = [field_diff[:, 0], field_diff[:, 1], field_diff[:, 2]]
colors = ["steelblue", "darkorange", "seagreen"]
labels = [r"$\Delta B_x(G)$", r"$\Delta B_y(G)$", r"$\Delta B_z(G)$"]

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for i, ax in enumerate(axes):
    ax.hist(field_data[i], bins=50, edgecolor="black", color=colors[i], alpha=1, label=labels[i])
    # ax.set_xscale("symlog")#, linthresh=linthresh1)
    ax.set_yscale("symlog")
    ax.tick_params(axis='x', rotation=45)
    ax.set_xlabel(labels[i])
    ax.set_xlim(field_data[i].min(), field_data[i].max())
    ax.set_title(f"Histogram of {labels[i]}")
    ax.legend()

axes[0].set_ylabel("Count")

plt.tight_layout()

if __name__ == "__main__":
    # Save figure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_dir = os.path.join(script_dir, "Comparison_Plots", f"{today}")
    os.makedirs(plot_dir, exist_ok=True)
    filename = f"Comp_dB_XYZ_{today}.png"
    fig.savefig(os.path.join(plot_dir, filename), bbox_inches='tight', dpi=150)
    print(f"Saved: {os.path.join(plot_dir, filename)}")

    # plt.show()