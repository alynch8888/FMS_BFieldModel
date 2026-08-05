#Imports
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

#Useful names that can be used elsewhere
today = date.today()


##########Load pkl files into a readable format##########
def load_pkl(filepath):
    with open(filepath, "rb") as f:
        return pickle.load(f)

#Print pkl info
def pkl_2_txt(pkl_file):
    with open(pkl_file, 'rb') as f:
        data = pickle.load(f)
    print(data)

##########Print the xyz coordinates from the pkl files##########
def print_xyz_coord(filepath):
    # print(Data_file)
    for i, fpath in enumerate(filepath):
      df = load_pkl(fpath)
      # print(i, df.shape)
      print(f"\n{fpath}")
      for col in ['X','Y','Z']:
        print(f" {col}: {df[col].min()} to {df[col].max()}")

##########Sum Field Maps########## Does not drop R,Phi, BR, and BPhi
def sum_field_maps(filepath,filename,pklarray):
    coord_cols = ['X', 'Y', 'Z']
    field_cols = ['Bx', 'By', 'Bz']

    output_path = os.path.join(filepath, filename+".pkl")

    result = None
    for fname in pklarray:
        fpath = os.path.join(filepath, fname)
        df = load_pkl(fpath)

        # Rename field cols by position
        cols = df.columns.tolist()
        cols[3] = 'Bx'
        cols[4] = 'By'
        cols[5] = 'Bz'
        df.columns = cols

        if result is None:
            result = df
        else:
            merged = result.merge(df, on=coord_cols, how='outer', suffixes=('_a', '_b'))
            for col in field_cols:
                merged[col] = merged[f'{col}_a'].add(merged[f'{col}_b'], fill_value=0)
            result = merged[result.columns.tolist()]

    with open(output_path, "wb") as f:
        pickle.dump(result, f)

    txt_path = output_path.replace('.pkl', '.txt')
    # txt_path = os.path.join(filepath, filename+".txt")
    result.to_csv(txt_path, index=False)
    # result.to_csv(txt_path, sep='\t', index=False)

    print(f"Saved to {output_path}")
    print(f"Saved to {txt_path}")

##########Check if certain files exist##########
def check_file_existence(filepath,pkl_array):
    print("Checking " + filepath + "...")
    missing_data = [f for f in pkl_array if not os.path.exists(os.path.join(filepath, f))]
    found_data   = [f for f in pkl_array if     os.path.exists(os.path.join(filepath, f))]
    print(f"Data Files Found:   {len(found_data)}")
    print(f"Data Files Missing: {len(missing_data)}")
    if missing_data:
        print("\nMissing files:")
        for f in missing_data:
            print(f"  {f}")

##########Sum field maps with a shift on the x-coordinates##########
def sum_field_maps_w_shift(filepath, filename, pklarray, coord_shift=0.0):
    coord_cols = ['X', 'Y', 'Z']
    field_cols = ['Bx', 'By', 'Bz']

    output_path = os.path.join(filepath, filename + f"_x_{coord_shift}.pkl")

    result = None
    for fname in pklarray:
        fpath = os.path.join(filepath, fname)
        df = load_pkl(fpath)

        # Rename field cols by position
        cols = df.columns.tolist()
        cols[3] = 'Bx'
        cols[4] = 'By'
        cols[5] = 'Bz'
        df.columns = cols

        # Apply coordinate shift to X
        df['X'] = df['X'] + coord_shift


        if result is None:
            result = df
        else:
            merged = result.merge(df, on=coord_cols, how='outer', suffixes=('_a', '_b'))
            for col in field_cols:
                merged[col] = merged[f'{col}_a'].add(merged[f'{col}_b'], fill_value=0)
            result = merged[result.columns.tolist()]

    with open(output_path, "wb") as f:
        pickle.dump(result, f)

    txt_path = output_path.replace('.pkl', '.txt')
    result.to_csv(txt_path, index=False)

    print(f"Saved to {output_path}")
    print(f"Saved to {txt_path}")

##########Shift x-coordinates##########
def shift_x(filepath, filename, coord_shift):
    fpath = os.path.join(filepath, filename)
    df = load_pkl(fpath)

    df['X'] = df['X'] + coord_shift
    df['X'] = df['X'].round(3)
    output_path = os.path.join(filepath, filename.replace('.pkl', f'_x_{coord_shift}.pkl'))

    with open(output_path, 'wb') as f:
        pickle.dump(df, f)

    print(f"Saved to {output_path}")

##########Sum Field Maps (Drops R, Phi, Br, and Bphi; keeps X, Y, Z, Bx, By, Bz)##########
def sum_field_maps(pkl_output_path, txt_output_path, filename, pklarray):
    coord_cols = ['X', 'Y', 'Z']
    field_cols = ['Bx', 'By', 'Bz']
    keep_cols = coord_cols + field_cols  # ['X', 'Y', 'Z', 'Bx', 'By', 'Bz']

    output_pkl = os.path.join(pkl_output_path, filename + ".pkl")
    output_csv = os.path.join(txt_output_path, filename + ".txt")

    result = None
    for fpath in pklarray:
        df = load_pkl(fpath)

        cols = df.columns.tolist()
        cols[3], cols[4], cols[5] = 'Bx', 'By', 'Bz'
        df.columns = cols

        # Drop R, Phi, Br, Bphi
        df = df[keep_cols]

        if result is None:
            result = df
        else:
            merged = result.merge(df, on=coord_cols, how='outer', suffixes=('_a', '_b'))
            for col in field_cols:
                merged[col] = merged[f'{col}_a'].add(merged[f'{col}_b'], fill_value=0)
            result = merged[keep_cols]
            # result.loc[:, field_cols] = result[field_cols] / 1000

        # result[field_cols] = result[field_cols] / 1000

    with open(output_pkl, "wb") as f:
        pickle.dump(result, f)

    result.to_csv(output_csv, index=False)

    print(f"Saved to {output_pkl}")
    print(f"Saved to {output_csv}")

#Coordinate Shift from running helicalc_drive. Need to confirm this.
coord_shift = -3.896 #This one is the change from -1.2 to -5.096.
actual_shift = -3.904

##########Gaussian Fits##########
def gaussian(x, amplitude, mean, sigma):
    return amplitude * np.exp(-(x - mean)**2 / (2 * sigma**2))

def fit_and_plot_gaussian(data, ax, label, color='C0', bins=100, linthresh=1e-2):
    data = np.asarray(data)
    data = data[~np.isnan(data)]

    # Histogram (density=True so the Gaussian fit is on the same scale)
    counts, bin_edges = np.histogram(data, bins=bins, density=True)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # Initial guesses: amplitude ~ peak, mean ~ data mean, sigma ~ data std
    p0 = [counts.max(), np.mean(data), np.std(data)]

    try:
        popt, pcov = curve_fit(gaussian, bin_centers, counts, p0=p0, maxfev=10000)
        amplitude, mean, sigma = popt
        perr = np.sqrt(np.diag(pcov))
    except RuntimeError:
        print(f"Fit failed for {label}")
        return None

    # Plot histogram
    ax.hist(data, bins=bins, density=True, alpha=0.5, color=color, label=f'{label} data')

    # Plot fit curve
    x_fit = np.linspace(bin_edges[0], bin_edges[-1], 1000)
    ax.plot(x_fit, gaussian(x_fit, *popt), color=color, linewidth=2,
             label=f'{label} fit: μ={mean:.4g}, σ={sigma:.4g}')

    ax.set_xscale("symlog", linthresh=linthresh)
    ax.set_xlabel(label)
    ax.set_ylabel("Density")
    ax.legend(fontsize=9)

    return {'amplitude': amplitude, 'mean': mean, 'sigma': sigma,
            'amplitude_err': perr[0], 'mean_err': perr[1], 'sigma_err': perr[2]}


##########Warn, offer a shift, re-check, and return the file list to actually sum##########
def prep_group(filepaths, group_label):
    if len(filepaths) < 2:
        return filepaths

    mismatched, ref_path = find_xyz_mismatches(filepaths)
    if not mismatched:
        print(f"{group_label}: XYZ coordinates match across all files. Good to go.")
        return filepaths

    print(f"\nWARNING: {group_label} XYZ coordinates are NOT the same across all files.")
    print(f"Reference file: {ref_path}")
    print_xyz_coord(filepaths)

    make_shift = input(f"\nCreate a shifted file for the mismatched {group_label} file(s)? (y/n): ").strip().lower()
    if make_shift != 'y':
        print(f"Proceeding without shifting {group_label} files. The sum may contain NaNs from mismatched grids.")
        return filepaths

    choice = input("Use coord_shift or actual_shift? (coord_shift/actual_shift/no): ").strip().lower()
    if choice == 'coord_shift':
        shift_value = coord_shift
    elif choice == 'actual_shift':
        shift_value = actual_shift
    else:
        shift_value = float(input("What value do you want to shift the coordinates by? "))

    updated_filepaths = list(filepaths)
    for fpath in mismatched:
        fdir = os.path.dirname(fpath)
        fname = os.path.basename(fpath)
        shift_x(fdir, fname, shift_value)
        shifted_path = os.path.join(fdir, fname.replace('.pkl', f'_x_{shift_value}.pkl'))
        updated_filepaths[updated_filepaths.index(fpath)] = shifted_path

    ##Double check after shifting##
    still_mismatched, _ = find_xyz_mismatches(updated_filepaths)
    if still_mismatched:
        print(f"\nWARNING: {group_label} XYZ coordinates STILL do not match after shifting.")
        print_xyz_coord(updated_filepaths)
    else:
        print(f"\n{group_label}: XYZ coordinates now match after shifting. Good to go.")

    return updated_filepaths

##########with optional m->mm and Tesla->Gauss unit conversion##########
def save_summed_txt(pkl_path, txt_path, convert_m_to_mm=False, convert_T_to_G=False, digits=12):
    coord_cols = ['X', 'Y', 'Z']
    field_cols = ['Bx', 'By', 'Bz']

    df = load_pkl(pkl_path).copy()

    if convert_m_to_mm and convert_T_to_G:
        print("Changing m to mm and Tesla to Gauss...")
        # new_coord_cols = ['X(mm)', 'Y(mm)', 'Z(mm)']
        # new_field_cols = ['Bx(G)', 'By(G)', 'Bz(G)']
    elif convert_m_to_mm:
        print("Changing m to mm...")
        # new_coord_cols = ['X(mm)', 'Y(mm)', 'Z(mm)']
        # new_field_cols = ['Bx(T)', 'By(T)', 'Bz(T)']
    elif convert_T_to_G:
        print("Changing Tesla to Gauss...")
        # new_coord_cols = ['X(m)', 'Y(m)', 'Z(m)']
        # new_field_cols = ['Bx(T)', 'By(T)', 'Bz(T)']
    # else:
        # new_coord_cols = ['X(m)', 'Y(m)', 'Z(m)']
        # new_field_cols = ['Bx(T)', 'By(T)', 'Bz(T)']

    if convert_m_to_mm:
        for col in coord_cols:
            df[col] = df[col] * 1e3 #1m=1e3mm
    if convert_T_to_G:
        for col in field_cols:
            df[col] = df[col] * 1e4 #1e4G=1T

    # df.rename(columns=dict(zip(coord_cols + field_cols)), inplace=True)

    if convert_m_to_mm or convert_T_to_G:
        with open(pkl_path, "wb") as f:
            pickle.dump(df, f)
        print(f"Updated units and re-saved: \nSaved to {pkl_path}")

    coord_digits = 3   # e.g. 3 decimal places for mm
    field_digits = 12  # more precision for field values
    coord_factor = 1 ** coord_digits
    field_factor = 10 ** field_digits
    txt_df = df.copy()
    for col in coord_cols:
        txt_df[col] = np.trunc(txt_df[col] * coord_factor) / coord_factor
    for col in field_cols:
        txt_df[col] = np.trunc(txt_df[col] * field_factor) / field_factor

    coord_unit = 'mm' if convert_m_to_mm else 'm'
    field_unit = 'G' if convert_T_to_G else 'T'
    units = [coord_unit] * 3 + [field_unit] * 3

    with open(txt_path, 'w') as f:
        f.write('\t'.join(units) + '\n')
        f.write('\t'.join(coord_cols + field_cols) + '\n')
        txt_df.to_csv(f, sep='\t', index=False, header=False, float_format=f'%.{digits}f')
    print(f"Saved to {txt_path}")

##########Check if X, Y, Z are the same across a list of files##########
def find_xyz_mismatches(filepaths):
    coord_cols = ['X', 'Y', 'Z']
    ref_path = filepaths[0]
    ref_xyz = load_pkl(ref_path)[coord_cols].sort_values(coord_cols).reset_index(drop=True)

    mismatched = []
    for fpath in filepaths[1:]:
        xyz = load_pkl(fpath)[coord_cols].sort_values(coord_cols).reset_index(drop=True)
        if not ref_xyz.equals(xyz):
            mismatched.append(fpath)

    return mismatched, ref_path