#List of all the Official Imports I use.
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.ticker import MaxNLocator
from scipy.interpolate import CubicSpline
from datetime import date
#Useful names that can be used elsewhere
today = date.today()
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from AL_BField_Analysis.Scripts_setup.utils.utils import navigate, load_pkl

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")
filename = os.path.splitext(os.path.basename(__file__))[0]

##########Settings##########
nav_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel"
Z_TRACKER_START = 8500.0      # mm
Z_TRACKER_END = 11800.0       # mm
X_AXIS = -3904.0              # DS axis, mm
WIDE_HALF = 200.0             # +/- mm for the wide (left) column
NARROW_HALF = 50.0            # +/- mm for the close-up (right) column
B_OFFSET = 1.0                # T; Bz is plotted as (Bz - B_OFFSET) in mT
colors = ["steelblue", "darkorange", "seagreen", "orchid", "gold", "tomato"]
##########Tracker geometry along Z (mm)##########
# End bronze rings sit inside the tracker length at each end. 17 bronze shielding rings sit
# midway between the 18 station centres. The first station centre is FIRST_STATION_OFFSET
# from the inner (downstream) face of the upstream end ring; each next centre is STATION_PITCH further.
END_RING_THICK = 50.80
SHIELD_RING_THICK = 19.05
N_STATIONS = 18
STATION_PITCH = 174.0
FIRST_STATION_OFFSET = 105.20
end_rings = [(Z_TRACKER_START, Z_TRACKER_START + END_RING_THICK),
             (Z_TRACKER_END - END_RING_THICK, Z_TRACKER_END)]
station_z = Z_TRACKER_START + END_RING_THICK + FIRST_STATION_OFFSET + STATION_PITCH * np.arange(N_STATIONS)
shield_centres = 0.5 * (station_z[:-1] + station_z[1:])
shield_rings = [(c - SHIELD_RING_THICK / 2, c + SHIELD_RING_THICK / 2) for c in shield_centres]
# Physical slot (0 = most upstream, at station_z[0]) -> station number, from the tracker slot map
SLOT_TO_STATION = [13, 12, 16, 10, 11, 1, 8, 7, 0, 2, 14, 5, 4, 17, 6, 15, 3, 9]
# Slots whose map entries carry a Flag ("NOT IN RUN124155 BLOCK" or "CHECK")
FLAGGED_SLOTS = {0, 1, 4, 5, 6, 7, 8, 11}
SHOW_STATION_LABELS = True
print(f"Station centres ({N_STATIONS}, {STATION_PITCH:g} mm pitch): {station_z[0]:.1f} ... {station_z[-1]:.1f} mm; "
      f"gap after last centre to inner face of downstream end ring = {end_rings[1][0] - station_z[-1]:.1f} mm "
      f"(vs {FIRST_STATION_OFFSET:.1f} mm at the upstream end)")


def draw_tracker_geometry(a, lo=-np.inf, hi=np.inf, label=True, names=False):
    """Shade the end bronze rings and shielding rings, and draw the station centres.
    names=True writes 'slot / station' above each station centre (use on the top panel only)."""
    if names and SHOW_STATION_LABELS:
        for k, s in enumerate(station_z):
            if lo <= s <= hi:
                a.text(s, 1.01, f"{k}/S{SLOT_TO_STATION[k]}" + ("*" if k in FLAGGED_SLOTS else ""),
                       transform=a.get_xaxis_transform(), rotation=90, ha='center', va='bottom',
                       fontsize=7, color='lightgray', clip_on=False)
    lab = label
    for z0, z1 in end_rings:
        if z1 >= lo and z0 <= hi:
            a.axvspan(z0, z1, color='peru', alpha=0.45, lw=0, label='end bronze ring (50.80 mm)' if lab else None)
            lab = False
    lab = label
    for z0, z1 in shield_rings:
        if z1 >= lo and z0 <= hi:
            a.axvspan(z0, z1, color='peru', alpha=0.25, lw=0, label='shielding ring (19.05 mm)' if lab else None)
            lab = False
    lab = label
    for s in station_z:
        if lo <= s <= hi:
            a.axvline(s, color='lightgray', ls='--', lw=0.8, alpha=0.8, label='station centre' if lab else None)
            lab = False


##########Reader##########
def read_field_file(path):
    """Read X, Y, Z, Bx, By, Bz from a .pkl or a whitespace-delimited .txt (any number of
    header lines). Coordinates returned in mm (converted from metres if needed, rounded to
    0.001 mm to remove float noise); fields in T."""
    if path.endswith('.pkl'):
        df = load_pkl(path).iloc[:, :6].copy()
        df.columns = ['X', 'Y', 'Z', 'Bx', 'By', 'Bz']
    else:
        n_header = 0
        with open(path) as f:
            for line in f:
                parts = line.split()
                try:
                    [float(v) for v in parts[:6]]
                    if len(parts) >= 6:
                        break
                except ValueError:
                    pass
                n_header += 1
        df = pd.read_csv(path, sep=r'\s+', skiprows=n_header, header=None,
                         names=['X', 'Y', 'Z', 'Bx', 'By', 'Bz'], usecols=range(6))
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    bad = df.isna().any(axis=1)
    if bad.any():
        print(f"Warning: {bad.sum()} row(s) had non-numeric values and were dropped.")
        df = df.loc[~bad].reset_index(drop=True)
    if df['Z'].abs().max() < 100:
        print("Coordinates look like metres -> converting to mm.")
        df[['X', 'Y', 'Z']] = df[['X', 'Y', 'Z']] * 1000.0
    df[['X', 'Y', 'Z']] = df[['X', 'Y', 'Z']].round(3)
    print(f"Read {len(df)} rows from {os.path.basename(path)}")
    return df


def column_spline(df, x, y):
    """Cubic spline of Bz(Z) at the nearest grid column to (x, y)."""
    xs, ys = df['X'].to_numpy(), df['Y'].to_numpy()
    nx = xs[np.argmin(np.abs(xs - x))]
    ny = ys[np.argmin(np.abs(ys - y))]
    sel = df[np.isclose(df['X'], nx) & np.isclose(df['Y'], ny)].sort_values('Z')
    sel = sel.loc[~sel['Z'].duplicated()]
    z, bz = sel['Z'].to_numpy(), sel['Bz'].to_numpy()
    return nx, ny, z, bz, CubicSpline(z, bz)


def parse_list(text):
    return [float(v) for v in text.replace(',', ' ').split()]


##########Pick file##########
data_path = navigate(nav_path, "for the field map you want to zoom on", "")
if not data_path:
    sys.exit("No file selected.")
data_df = read_field_file(data_path[0])
data_file_name = os.path.basename(data_path[0])

script_dir = os.path.dirname(os.path.abspath(__file__))
vs_name = "dBz_dZ_zero_zoom"
plot_dir = os.path.join(script_dir, "Comparison_Plots", vs_name, f"{today}")
os.makedirs(plot_dir, exist_ok=True)

##########Main loop##########
while True:
    xin = input("X-Coordinate(s) in mm, comma separated, e.g. -4854,-4842 ('q' to quit): ").strip()
    if xin.lower() == 'q':
        break
    yin = input("Y-Coordinate in mm ('q' to quit): ").strip()
    if yin.lower() == 'q':
        break
    zin = input("Approximate Z of the dBz/dZ = 0 point to zoom on, in mm (e.g. 10120) ('q' to quit): ").strip()
    if zin.lower() == 'q':
        break
    try:
        x_list, ymask, z_guess = parse_list(xin), float(yin), float(zin)
    except ValueError:
        print("Please enter numbers (or 'q').")
        continue
    if not x_list:
        continue

    # find the dBz/dZ = 0 point nearest z_guess on each X line
    lines = []
    for i, x in enumerate(x_list):
        nx, ny, z, bz, cs = column_spline(data_df, x, ymask)
        if len(z) < 5:
            print(f"Not enough points at X={nx}, Y={ny}; skipping.")
            continue
        roots = cs.derivative().roots(extrapolate=False)
        if len(roots) == 0:
            print(f"No dBz/dZ = 0 point at X={nx}, Y={ny}; skipping.")
            continue
        z0 = roots[np.argmin(np.abs(roots - z_guess))]
        curv = cs(z0, 2) * 1e6                            # T/m^2
        lines.append(dict(X=nx, Y=ny, R=np.hypot(nx - X_AXIS, ny), z=z, bz=bz, cs=cs, Z0=z0,
                          Bz0=float(cs(z0)), curv=curv, type='max' if curv < 0 else 'min',
                          shift_per_mT_per_m=1e-3 / abs(curv) * 1e3 if curv != 0 else np.inf,
                          color=colors[i % len(colors)]))
    if not lines:
        continue

    print(f"\ndBz/dZ = 0 nearest Z = {z_guess:.1f} mm (Y = {ymask:.1f} mm):")
    for L in lines:
        print(f"  X={L['X']:.1f} (R={L['R']:.1f} mm): Z={L['Z0']:.2f} mm, Bz={L['Bz0']:.6f} T, "
              f"d2Bz/dZ2={L['curv']:.4f} T/m^2 ({L['type']}); "
              f"1 mT/m of extra gradient moves it {L['shift_per_mT_per_m']:.1f} mm")
    if abs(min(L['Z0'] for L in lines) - z_guess) > WIDE_HALF:
        print(f"Note: the nearest zero point is more than {WIDE_HALF:.0f} mm from {z_guess:.1f} mm.")

    # windows centred on the mean zero point
    zc = np.mean([L['Z0'] for L in lines])
    windows = [(zc - WIDE_HALF, zc + WIDE_HALF, 'wide'), (zc - NARROW_HALF, zc + NARROW_HALF, 'close-up')]

    # ---- plot: 2 x 2 (Bz on top, dBz/dZ below; wide left, close-up right) ----
    plt.style.use('dark_background')
    fig, ax = plt.subplots(2, 2, figsize=(14, 8.5))
    for col, (lo, hi, lab) in enumerate(windows):
        for L in lines:
            zf = np.linspace(max(lo, L['z'][0]), min(hi, L['z'][-1]), 1000)
            k = (L['z'] >= lo) & (L['z'] <= hi)
            ax[0, col].plot(zf, (L['cs'](zf) - B_OFFSET) * 1e3, color=L['color'], lw=1.6,
                            label=f"X={L['X']:.0f} mm (R={L['R']:.0f})")
            ax[0, col].plot(L['z'][k], (L['bz'][k] - B_OFFSET) * 1e3, 'o', color=L['color'], ms=3)
            ax[1, col].plot(zf, L['cs'](zf, 1) * 1e6, color=L['color'], lw=1.6)     # T/mm -> mT/m
            if lo <= L['Z0'] <= hi:
                mk = 'v' if L['type'] == 'max' else '^'
                ax[0, col].plot(L['Z0'], (L['Bz0'] - B_OFFSET) * 1e3, mk, color=L['color'], ms=9)
                ax[1, col].plot(L['Z0'], 0, mk, color=L['color'], ms=9)
        shown = [s for s in station_z if lo <= s <= hi]
        for a in ax[:, col]:
            draw_tracker_geometry(a, lo, hi, label=(a is ax[0, col]), names=(a is ax[0, col]))
            a.set_xlim(lo, hi)
            a.xaxis.set_major_locator(MaxNLocator(nbins=6))
            a.set_xlabel("Z (mm)")
        ax[1, col].axhline(0, color='gray', lw=0.8)
        st_txt = (", station centre(s) at " + ", ".join(f"{s:.1f}" for s in shown)) if shown else ""
        ax[0, col].set_title(f"{lab}: Z = {lo:.0f} to {hi:.0f} mm{st_txt}", fontsize=10, pad=(38 if SHOW_STATION_LABELS else 6))
        ax[0, col].set_ylabel(rf"$B_z$ $-$ {B_OFFSET:g} T (mT)")
        ax[1, col].set_ylabel(r"$dB_z/dZ$ (mT/m)")
    ax[0, 0].legend(fontsize=9, loc='best')
    fig.suptitle(f"Zoom on the $dB_z/dZ = 0$ point near Z = {zc:.1f} mm, Y = {ymask:.1f} mm "
                 f"(markers: $dB_z/dZ = 0$)\n{data_file_name}")
    fig.tight_layout()

    xs_tag = "_".join(f"{L['X']:.0f}" for L in lines)
    tag = f"{filename}_Z{zc:.0f}_X{xs_tag}_Y{ymask:.0f}_{today}"
    if __name__ == "__main__":
        fig.savefig(os.path.join(plot_dir, tag + ".png"), bbox_inches='tight', dpi=150)
        print(f"Saved: {os.path.join(plot_dir, tag + '.png')}")
    plt.close(fig)

    txt_path = os.path.join(plot_dir, tag + ".txt")
    with open(txt_path, 'w') as f:
        f.write('\t'.join(['X(mm)', 'Y(mm)', 'R(mm)', 'Z_zero(mm)', 'Bz(T)', 'd2Bz/dZ2(T/m^2)',
                           'type', 'shift_per_1mT/m(mm)']) + '\n')
        for L in lines:
            f.write(f"{L['X']:.3f}\t{L['Y']:.3f}\t{L['R']:.3f}\t{L['Z0']:.3f}\t{L['Bz0']:.9f}\t"
                    f"{L['curv']:.6f}\t{L['type']}\t{L['shift_per_mT_per_m']:.3f}\n")
    print(f"Saved to {txt_path}")