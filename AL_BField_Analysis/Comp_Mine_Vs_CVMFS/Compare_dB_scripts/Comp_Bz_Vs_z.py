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
# from AL_BField_Analysis.Comp_Mine_Vs_CVMFS.Bfield_diff_compare import (comparison_name,
#                                                                        comparison_coord,
#                                                                        comparison_field,
#                                                                        mydata_name,
#                                                                        mydata_field,
#                                                                        field_diff,
#                                                                        field_error,
#                                                                        frac_error,
#                                                                        frac_diff
# )
# from Comp_Cart_Vs_dB import

from AL_BField_Analysis.Scripts_setup.utils.utils import navigate, print_xyz_coord_txt

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")
filename = os.path.splitext(os.path.basename(__file__))[0]
# field_error = [frac_error[:, 0], frac_error[:, 1], frac_error[:, 2]]
# field_data = [field_diff[:, 0], field_diff[:, 1], field_diff[:, 2]]

nav_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel"
data_path = navigate(nav_path,"for the data you want to plot", ".txt")
# data_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/AL_BField_Analysis/Comp_Mine_Vs_CVMFS/Make_file/Summed_Files/DS_Summed.txt"
data_df = pd.read_csv(data_path[0], sep=r'\s+', skiprows=3, header=None, names=['X', 'Y', 'Z', 'Bx', 'By', 'Bz'])

# PATCH: guard against the DTypePromotionError from last run. If any cell in
# a numeric column failed to parse (stray token, Fortran 'D' exponent, a
# misaligned row, etc.), pandas silently leaves that whole column as
# object/string dtype instead of float64 -- which is what broke np.isclose.
# Coercing explicitly here surfaces the problem instead of hiding it.
numeric_cols = ['X', 'Y', 'Z', 'Bx', 'By', 'Bz']
before_dtypes = data_df[numeric_cols].dtypes
for col in numeric_cols:
    data_df[col] = pd.to_numeric(data_df[col], errors='coerce')
bad_rows = data_df[numeric_cols].isna().any(axis=1)
if bad_rows.any():
    print(f"Warning: {bad_rows.sum()} row(s) had non-numeric values and were dropped. "
          f"Original dtypes were:\n{before_dtypes}")
    print(data_df.loc[bad_rows].head())
    data_df = data_df.loc[~bad_rows].reset_index(drop=True)

colors = ["steelblue", "darkorange", "seagreen"]
labels = [r"$\Delta B_x(G)$", r"$\Delta B_y(G)$", r"$\Delta B_z(G)$"]
coord_xyz = [f"X(m)", f"Y(m)", f"Z(m)"]
print('\n',data_path[0],'\n')
# print(data_df)

x_coord = data_df['X'].to_numpy()
y_coord = data_df['Y'].to_numpy()
z_coord = data_df['Z'].to_numpy()
Bz = data_df['Bz'].to_numpy()

# PATCH: cast the typed-in values to float right away -- input() always
# returns a string, and comparing a string against a numeric column either
# errors (as it did) or silently never matches.
print_xyz_coord_txt([data_path[0]])
xmask = float(input("X-Coordinate Mask in mm: "))
ymask = float(input("Y-Coodinate Mask in mm: "))

# PATCH: build the xy slice off the *nearest available* grid point rather
# than requiring an exact match. Real grid data almost never lands exactly
# on the value you type in, and float rounding from the source file means
# even "the same" coordinate can differ by a tiny amount row to row.
nearest_x = x_coord[np.argmin(np.abs(x_coord - xmask))]
nearest_y = y_coord[np.argmin(np.abs(y_coord - ymask))]
if not np.isclose(nearest_x, xmask) or not np.isclose(nearest_y, ymask):
    print(f"Note: exact X={xmask}, Y={ymask} not in the data; "
          f"using nearest available X={nearest_x}, Y={nearest_y}.")

xy_mask = np.isclose(x_coord, nearest_x) & np.isclose(y_coord, nearest_y)
if not xy_mask.any():
    raise ValueError(f"No rows found for X={nearest_x}, Y={nearest_y}. Check the mask values.")

print(f"{xy_mask.sum()} rows matched at X={nearest_x}, Y={nearest_y}")

# Sort by Z so the line plot below reads left-to-right instead of following
# the file's original row order.
order = np.argsort(z_coord[xy_mask])
z_slice = z_coord[xy_mask][order]
Bz_slice = Bz[xy_mask][order]

vs_name = r"Bz_vs_z"
plt.style.use('dark_background')
units = 'z(mm)', r'B_z(T)'



# print(z_slice,Bz_slice)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(z_slice, Bz_slice, color=colors[2], marker='o', markersize=3, linewidth=1.2, label=r"$B_z$")
ax.set_xlabel("Z (mm)")
ax.set_ylabel(r"$B_z$ (T)")
data_file_name = os.path.basename(data_path[0])
ax.set_title(f"$B_z$ vs $Z$ at X={nearest_x:.1f} mm, Y={nearest_y:.1f} mm\n{data_file_name}")
ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
ax.legend()
plt.tight_layout()



if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_dir = os.path.join(script_dir, "Comparison_Plots", vs_name, f"{today}")
    os.makedirs(plot_dir, exist_ok=True)
    out_filename = f"{filename}_X{nearest_x:.0f}_Y{nearest_y:.0f}_{today}.png"
    fig.savefig(os.path.join(plot_dir, out_filename), bbox_inches='tight', dpi=150)
    print(f"Saved: {os.path.join(plot_dir, out_filename)}")

plt.close(fig)
txt_filename = f"{filename}_X{nearest_x:.0f}_Y{nearest_y:.0f}_{today}.txt"
txt_path = plot_dir + "/" + txt_filename
with open(txt_path, 'w') as f:
        # f.write('\t'.join(units) + '\n')
        f.write('\t'.join(['z(mm)','Bz(T)']) + '\n')
        for row in zip(z_slice, Bz_slice):
                f.write('\t'.join(str(x) for x in row) + '\n')
        # f.write(os.path.join(plot_dir, txt_filename), bbox_inches='tight', dpi=150)
print(f"Saved to {txt_path}")

# zmask = data_df[:, 2]

# print(zmask)
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