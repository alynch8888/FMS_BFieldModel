#List of all the Official Imports I use.
import pickle
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

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Scripts_setup.utils import shift_x, coord_shift, pkl_2_txt, sum_field_maps, sum_field_maps_w_shift
from Comp_Mine_Vs_CVMFS.Show_BF_Diff_and_Err import cvmfs_coord, frac_error, mydata_field, mydata_coord, my_data



#Useful names that can be used elsewhere
today = date.today()

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

step = 0.25  # in meters
z_starts = np.arange(8.5, 9.0, step)
z_ranges = [(z * 1e3, (z + step) * 1e3) for z in z_starts]
def make_isosurface(data, value_col, title, colorscale='Viridis',
                     n_isomin_pct=10, n_isomax_pct=90, surface_count=15,
                     max_points=200_000):
    """
    Build a 3D isosurface/volume plot of `value_col` for a single slice of data.
    """
    data = data[['X', 'Y', 'Z', value_col]].dropna()

    if len(data) == 0:
        return None

    if len(data) > max_points:
        data = data.sample(max_points, random_state=42)

    vmin = np.percentile(data[value_col], n_isomin_pct)
    vmax = np.percentile(data[value_col], n_isomax_pct)

    # Guard against flat/degenerate slices
    if vmin == vmax:
        return None
    units = "G"
    fig = go.Figure(data=go.Isosurface(
        x=data['X'],
        y=data['Y'],
        z=data['Z'],
        value=data[value_col],
        isomin=vmin,
        isomax=vmax,
        surface_count=surface_count,
        colorscale=colorscale,
        caps=dict(x_show=False, y_show=False, z_show=False),
        colorbar=dict(
            title=dict(text=f"{value_col} ({units})", side="right")
    )))

    fig.update_layout(
        title=title,
        scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
        width=900,
        height=700
    )

    return fig


def plot_isosurfaces_by_zslice(df, value_col, colorscale, z_ranges):
    df['Bmag'] = np.sqrt(df['Bx']**2 + df['By']**2 + df['Bz']**2) if value_col == 'Bmag' else df.get('Bmag')

    figs = []
    for z_min, z_max in z_ranges:
        slice_df = df[(df['Z'] >= z_min) & (df['Z'] < z_max)]

        title = f"{value_col} Isosurface | Z: {z_min:.0f}-{z_max:.0f} mm"
        fig = make_isosurface(slice_df, value_col, title=title, colorscale=colorscale)

        if fig is not None:
            figs.append(fig)
            fig.show()
        else:
            print(f"Skipped Z range {z_min}-{z_max} 'mm'(no data or flat slice)")

    return figs

# print(type(field_data))

field_data = pd.DataFrame({
    'X': cvmfs_coord[:, 0],
    'Y': cvmfs_coord[:, 1],
    'Z': cvmfs_coord[:, 2],
    'Bx': mydata_field[:, 0],
    'By': mydata_field[:, 1],
    'Bz': mydata_field[:, 2],
})
# print(field_data)

# ----- Compute magnitude once -----
# field_data['Bmag'] = np.sqrt(field_data['Bx']**2 + field_data['By']**2 + field_data['Bz']**2)
# print(field_data)
# print(field_data['Z'].min(), field_data['Z'].max())
# print(field_data['Z'].describe())
# ----- Run for each component -----
figs_bmag = plot_isosurfaces_by_zslice(field_data, 'Bmag', 'Viridis', z_ranges)
# figs_bx   = plot_isosurfaces_by_zslice(field_data, 'Bx', 'RdBu', z_ranges)
# figs_by   = plot_isosurfaces_by_zslice(field_data, 'By', 'RdBu', z_ranges)
# figs_bz   = plot_isosurfaces_by_zslice(field_data, 'Bz', 'RdBu', z_ranges)