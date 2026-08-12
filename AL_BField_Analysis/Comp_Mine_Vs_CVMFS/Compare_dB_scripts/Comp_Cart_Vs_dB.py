#List of all the Official Imports I use.
# import pickle
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import sys
#From import
# from scipy.stats import norm
# from scipy.optimize import curve_fit
from datetime import date
#Useful names that can be used elsewhere
today = date.today()
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from AL_BField_Analysis.Comp_Mine_Vs_CVMFS.Bfield_diff_compare import (comparison_name,
                                                                       comparison_coord,
                                                                       comparison_field,
                                                                       mydata_name,
                                                                       mydata_field,
                                                                       field_diff,
                                                                       field_error,
                                                                       frac_error,
                                                                       frac_diff
)

from Scripts_setup.utils.utils import navigate

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

field_error = [frac_error[:, 0], frac_error[:, 1], frac_error[:, 2]]
field_data = [field_diff[:, 0], field_diff[:, 1], field_diff[:, 2]]

colors = ["steelblue", "darkorange", "seagreen"]
labels = [r"$\Delta B_x(G)$", r"$\Delta B_y(G)$", r"$\Delta B_z(G)$"]
coord_xyz = [f"X(m)", f"Y(m)", f"Z(m)"]
z_ranges = [(i * 1e3, (i + 1) * 1e3) for i in range(3, 17)] # In mm!

# def Comp_Cart_Vs_dB():
fig, axes = plt.subplots(2, 3, figsize=(30, 10), sharex='col')
gs = fig.add_gridspec(2, 3, height_ratios=[2,1], hspace=0)

axes = [[fig.add_subplot(gs[row, col]) for col in range(3)] for row in range(2)]
axes = np.array(axes)

for i in range(3):
    #Top graph: Cartesian coord vs field diff
    axes[0, i].scatter(comparison_coord[:, i], field_diff[:, i])#, color=colors[i], linestyle='--', marker='o',
            # markersize=4, linewidth=1.5,label=labels[i])
    axes[0, i].set_xscale("symlog")#, linthresh=linthresh1)
    axes[0, i].set_ylim(field_diff[:, i].min(), field_diff[:, i].max())
    # ax.set_yscale("symlog")
    axes[0, i].tick_params(labelbottom=False)#axis='x', rotation=45)
    # axes[0, i].set_xlabel(labels[i])
    # axes[0, i].set_xlim(field_data[i].min(), field_data[i].max())
    axes[0, i].set_title(f"{labels[i]} vs ")
    axes[0, i].legend()
    axes[0, i].set_ylabel(labels[i])

    #Bottom graph: mydata_field / comparison_field
    axes[1, i].plot(comparison_coord[:, i], frac_error[:, i],
                    color=colors[i], linestyle='-', linewidth=1)
    axes[1, i].set_xscale("symlog")
    axes[1, i].set_ylim(frac_error[:, i].min(), frac_error[:, i].max())
    axes[1, i].tick_params(axis='x', rotation=45)
    axes[1, i].set_xlabel(coord_xyz[i])
    # axes[1, i].set_title(f"Frac Error {labels[i]}")
axes[0, 0].set_ylabel("ΔB (G)")
axes[1, 0].set_ylabel("Fractional Error")
plt.tight_layout()

# Comp_Cart_Vs_dB

vs_name = f"{mydata_name}_vs_{comparison_name}"
if __name__ == "__main__":
    # Save figure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_dir = os.path.join(script_dir, "Comparison_Plots", vs_name, f"{today}")
    os.makedirs(plot_dir, exist_ok=True)
    filename = f"Comp_dB_XYZ_{today}.png"
    fig.savefig(os.path.join(plot_dir, filename), bbox_inches='tight', dpi=150)
    print(f"Saved: {os.path.join(plot_dir, filename)}")

    # plt.show()