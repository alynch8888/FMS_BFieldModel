#List of all the Official Imports I use.
# import pickle
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import sys
from matplotlib.ticker import MaxNLocator
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
# from Comp_Cart_Vs_dB import 

from Scripts_setup.utils.utils import navigate

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

field_error = [frac_error[:, 0], frac_error[:, 1], frac_error[:, 2]]
field_data = [field_diff[:, 0], field_diff[:, 1], field_diff[:, 2]]

colors = ["steelblue", "darkorange", "seagreen"]
labels = [r"$\Delta B_x(G)$", r"$\Delta B_y(G)$", r"$\Delta B_z(G)$"]
coord_xyz = [f"X(m)", f"Y(m)", f"Z(m)"]

# xy_coord = comparison_coord[:, :2]
z_coord = comparison_coord[:, 2]
# z_unique = np.sort(np.unique(z_coord))
# step = np.unique(np.diff(unique))
# print(f"Unique Z step(s): {step} mm")
# print(f"Number of unique Z values: {len(unique)}")
# coord_min, coord_max = coord.min(), coord.max()
# print(f"Coord Min: {coord_min} mm, Coord Max: {coord_max} mm")
# z_ranges = [(i, i + step) for i in range(int(coord_min), int(coord_max))] # In mm!


# # for row, (lo, hi) in enumerate(z_ranges):
# for val in unique:
#     mask = (coord == val)
#     # mask = (z_coord >= lo) & (z_coord < hi)
#     if not mask.any():
#         continue

#     ##Start of Comp_Cart_Vs_db##
#     fig, axes = plt.subplots(2, 3, figsize=(30, 10), sharex='col')
#     gs = fig.add_gridspec(2, 3, height_ratios=[2,1], hspace=0.4)
#     axes = np.array([[fig.add_subplot(gs[r, c]) for c in range(3)] for r in range(2)])

#     for i in range(3):
#         #Top graph: Cartesian coord vs field diff
#         axes[0, i].scatter(comparison_coord[mask, i], field_diff[mask, i], color=colors[i], linestyle='--', marker='o',
#                 markersize=4, linewidth=1.5,label=labels[i])
#         # axes[0, i].set_xscale("symlog")
#         axes[0, i].set_ylim(field_diff[mask, i].min(), field_diff[mask, i].max())
#         axes[0, i].tick_params(labelbottom=False)
#         axes[0, i].set_title(f"{labels[i]} vs ")
#         axes[0, i].legend()
#         axes[0, i].set_ylabel(labels[i])
#         axes[0, i].yaxis.set_major_locator(MaxNLocator(nbins=5, prune='lower'))  # drop bottom tick
#         axes[1, i].yaxis.set_major_locator(MaxNLocator(nbins=5, prune='upper'))  # drop top tick
#         #Bottom graph: mydata_field / comparison_field
#         axes[1, i].plot(comparison_coord[mask, i], frac_error[mask, i],
#                         color=colors[i], linestyle='-', linewidth=1)
#         # axes[1, i].set_xscale("symlog")
#         axes[1, i].set_ylim(frac_error[mask, i].min(), frac_error[mask, i].max())
#         axes[1, i].tick_params(axis='x', rotation=45)
#         axes[1, i].set_xlabel(coord_xyz[i])
#     axes[0, 0].set_ylabel("ΔB (G)")
#     axes[1, 0].set_ylabel("Fractional Error")
#     # fig.suptitle(f"Z: {int(lo)}-{int(hi)} mm")
#     fig.suptitle(f"X = {val:.1f} mm")
#     plt.tight_layout()
#     ##End of Comp_Cart_Vs_db##
#     vs_name = f"{mydata_name}_vs_{comparison_name}"
#     if __name__ == "__main__":
#         # Save figure
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         plot_dir = os.path.join(script_dir, "Comparison_Plots", vs_name, "split_plots", f"{today}")
#         os.makedirs(plot_dir, exist_ok=True)
#         # filename = f"Comp_dB_XYZ_splits_{int(lo)}_{int(hi)}_{today}.png"
#         filename = f"Comp_dB_XYZ_Z{val:.0f}_{today}.png"
#         fig.savefig(os.path.join(plot_dir, filename), bbox_inches='tight', dpi=150)
#         print(f"Saved: {os.path.join(plot_dir, filename)}")

#     plt.close(fig)

vs_name = f"{mydata_name}_vs_{comparison_name}"
z_unique = np.sort(np.unique(z_coord))
bin_width = 100  # mm — adjust as needed
z_min, z_max = int(z_coord.min()), int(z_coord.max())
z_ranges = [(lo, lo + bin_width) for lo in range(z_min, z_max, bin_width)]
plt.style.use('dark_background')

chunks = [z_ranges[i:i+4] for i in range(0, len(z_ranges), 4)]

for chunk in chunks:
    nrows = len(chunk)
    fig, axes = plt.subplots(nrows, 3, figsize=(24, nrows * 5))
    if nrows == 1:
        axes = axes[np.newaxis, :]  # keep 2D if only 1 row
    axes = np.array(axes)

    for row, (lo, hi) in enumerate(chunk):
        mask = (z_coord >= lo) & (z_coord < hi)
        if not mask.any():
            for col in range(3):
                axes[row, col].set_visible(False)
            continue

        vmax = np.abs(field_diff[mask]).max()

        for col, label in enumerate(labels):
            sc = axes[row, col].scatter(
                comparison_coord[mask, 0],
                comparison_coord[mask, 1],
                c=field_diff[mask, col],
                cmap='inferno', vmin=-vmax, vmax=vmax, s=20
            )
            plt.colorbar(sc, ax=axes[row, col], label=label)
            axes[row, col].set_xlabel("X (mm)")
            axes[row, col].set_ylabel("Y (mm)")
            axes[row, col].set_title(f"Z: {int(lo)}–{int(hi)} mm | {label}")

    fig.suptitle(f"Z: {int(chunk[0][0])}–{int(chunk[-1][1])} mm", fontsize=14)
    plt.tight_layout()

    if __name__ == "__main__":
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plot_dir = os.path.join(script_dir, "Comparison_Plots", vs_name, "split_plots", "colorbar", f"{today}")
        os.makedirs(plot_dir, exist_ok=True)
        filename = f"Comp_dB_XY_Z{int(chunk[0][0])}-{int(chunk[-1][1])}_{today}.png"
        fig.savefig(os.path.join(plot_dir, filename), bbox_inches='tight', dpi=150)
        print(f"Saved: {filename}")

    plt.close(fig)