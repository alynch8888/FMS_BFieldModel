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

from AL_BField_Analysis.Scripts_setup.utils.utils import navigate, print_xyz_coord_txt

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")
filename = os.path.splitext(os.path.basename(__file__))[0]

nav_path = "/mnt/c/Users/alecl/OneDrive/Documents/GitHub/FMS_BFieldModel/AL_BField_Analysis/Comp_Mine_Vs_CVMFS/Make_file"
data_path = navigate(nav_path, "for the data you want to plot", "")
if not data_path:
    sys.exit("No file selected.")


def read_field_txt(path):
    """Read X Y Z Bx By Bz from a whitespace-delimited text file, skipping however many
    header lines it has. save_summed_txt writes 2 header lines (units + column names);
    other files have 3. A fixed skiprows=3 would silently drop the first data row of
    a 2-header file, so count the non-numeric lines at the top instead."""
    n_header = 0
    with open(path) as f:
        for line in f:
            try:
                [float(v) for v in line.split()[:6]]
                if len(line.split()) >= 6:
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
    print(f"Skipped {n_header} header line(s); read {len(df)} rows.")
    return df


data_df = read_field_txt(data_path[0])

# Work in mm and T. If the coordinates look like metres (|Z| < 100), convert them.
coords_in_m = data_df['Z'].abs().max() < 100
if coords_in_m:
    print("Coordinates look like metres -> converting to mm.")
    data_df[['X', 'Y', 'Z']] = data_df[['X', 'Y', 'Z']] * 1000.0
# Round to 0.001 mm to remove float noise (e.g. 8050.000000000001) before matching.
data_df[['X', 'Y', 'Z']] = data_df[['X', 'Y', 'Z']].round(3)

colors = ["steelblue", "darkorange", "seagreen", "orchid"]
print('\n', data_path[0], '\n')

x_coord = data_df['X'].to_numpy()
y_coord = data_df['Y'].to_numpy()
z_coord = data_df['Z'].to_numpy()
Bz = data_df['Bz'].to_numpy()

print_xyz_coord_txt(data_path[0])

# Tracker extent along Z (mm), drawn on every panel
Z_TRACKER_START = 8500.0
Z_TRACKER_END = 11800.0

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

X_AXIS = -3904.0              # DS axis, mm


##########Busbars (optional)##########
def read_busbars(path):
    """Busbar geometry CSV in metres (Mu2e_arc_Bars / Mu2e_Straight_Bars / Mu2e_Arc_Transfer_Bars).
    Returns one row per conductor with its Z extent in mm and where it sits around the DS axis:
      kind = 'axial'    straight bar running along Z (theta2 = 0 -> +Z, 180 -> -Z), from z0 over 'length'
             'fixed-Z'  straight bar lying across at a single Z (theta2 = 90)
             'arc'      arc bar; drawn at its start Z (z0). Transfer arcs (with R_curve) also curve in Z,
                        so for those only the start Z is exact.
    The CSV z_mid column is not used: it is wrong for several 'return ... to splice box' rows."""
    t = pd.read_csv(path).dropna(how='all')
    t = t[t['Name/role'].notna() & t['z0'].notna()].copy()
    for c in ['z0', 'x0', 'y0', 'length', 'theta2']:
        t[c] = pd.to_numeric(t[c], errors='coerce') if c in t.columns else np.nan
    # Arc files (Mu2e_arc_Bars, Mu2e_Arc_Transfer_Bars) carry beta/alpha arc columns; the
    # straight-bar file does not. (Both have a dphi column, so that can't be used to tell them apart.)
    fname = os.path.basename(path).lower()
    is_arc_file = ('beta_rad' in t.columns) or ('R_curve' in t.columns) or ('arc' in fname and 'straight' not in fname)
    if is_arc_file:
        t['kind'] = 'arc'
    else:
        t['kind'] = np.where(t['theta2'].isin([0, 180]) & t['length'].notna(), 'axial', 'fixed-Z')
    sign = np.where(t['theta2'] == 180, -1.0, 1.0)
    z_end = np.where(t['kind'] == 'axial', t['z0'] + sign * t['length'], t['z0'])
    t['Z_lo_mm'] = np.minimum(t['z0'], z_end) * 1000.0
    t['Z_hi_mm'] = np.maximum(t['z0'], z_end) * 1000.0
    t['X_mm'] = t['x0'] * 1000.0
    t['Y_mm'] = t['y0'] * 1000.0
    t['R_mm'] = np.hypot(t['X_mm'] - X_AXIS, t['Y_mm'])
    t['phi_deg'] = np.degrees(np.arctan2(t['Y_mm'], t['X_mm'] - X_AXIS)) % 360.0
    t['approx'] = ('R_curve' in t.columns)
    t['source'] = os.path.basename(path)
    out = t[['Name/role', 'cond N', 'kind', 'Z_lo_mm', 'Z_hi_mm', 'X_mm', 'Y_mm', 'R_mm', 'phi_deg', 'approx', 'source']]
    print(f"Read {len(out)} conductors from {os.path.basename(path)} "
          f"({', '.join(f'{k}: {v}' for k, v in out['kind'].value_counts().items())})")
    return out


def busbars_in(bus, lo, hi):
    """Conductors whose Z extent overlaps [lo, hi]."""
    return bus[(bus['Z_hi_mm'] >= lo) & (bus['Z_lo_mm'] <= hi)]


def angle_between(phi1, phi2):
    """Smallest angle (deg) between two azimuths."""
    return np.abs((np.asarray(phi1) - phi2 + 180.0) % 360.0 - 180.0)


SAME_SIDE_DEG = 90.0   # conductors within this azimuth of the plotted column are drawn solid; others faint


bus_df = None
if input("Mark busbar conductors from geometry CSV(s)? (y/n) ").strip().lower() == 'y':
    parts = []
    while True:
        bus_path = navigate(nav_path, "for a busbar geometry CSV (arc, straight or transfer bars)", "")
        if bus_path:
            parts.append(read_busbars(bus_path[0]))
        if input("Add another busbar CSV? (y/n) ").strip().lower() != 'y':
            break
    if parts:
        bus_df = pd.concat(parts, ignore_index=True)
        print(f"{len(bus_df)} conductors in total; "
              f"{len(busbars_in(bus_df, Z_TRACKER_START, Z_TRACKER_END))} overlap the tracker.")
BUS_LABEL_NAMES = False   # True: full names on the fixed-Z busbar lines (busy over the full Z range); False: numbers only

script_dir = os.path.dirname(os.path.abspath(__file__))
vs_name = "dBz_dZ_vs_z"
plot_dir = os.path.join(script_dir, "Comparison_Plots", vs_name, f"{today}")
os.makedirs(plot_dir, exist_ok=True)


def first_derivative(z, f):
    """Direct 3-point first derivative on an uneven grid (2nd-order accurate everywhere).
    Interior:  f'_i = [h-^2 f_{i+1} - h+^2 f_{i-1} + (h+^2 - h-^2) f_i] / [h- h+ (h- + h+)]
               with h- = z_i - z_{i-1}, h+ = z_{i+1} - z_i  (slope of the parabola through 3 points)
    Ends:      the same parabola through the first / last 3 points, differentiated at the end point."""
    d = np.empty_like(f)
    hm = z[1:-1] - z[:-2]
    hp = z[2:] - z[1:-1]
    d[1:-1] = (hm**2 * f[2:] - hp**2 * f[:-2] + (hp**2 - hm**2) * f[1:-1]) / (hm * hp * (hm + hp))
    # start: points 0,1,2   (h1 = z1-z0, h2 = z2-z1)
    h1, h2 = z[1] - z[0], z[2] - z[1]
    d[0] = (-(2*h1 + h2) / (h1*(h1 + h2)) * f[0] + (h1 + h2) / (h1*h2) * f[1] - h1 / (h2*(h1 + h2)) * f[2])
    # end: points n-3,n-2,n-1  (h1 = z[-2]-z[-3], h2 = z[-1]-z[-2])
    h1, h2 = z[-2] - z[-3], z[-1] - z[-2]
    d[-1] = (h2 / (h1*(h1 + h2)) * f[-3] - (h1 + h2) / (h1*h2) * f[-2] + (h1 + 2*h2) / (h2*(h1 + h2)) * f[-1])
    return d


def second_derivative(z, f):
    """Direct 3-point second derivative on an uneven grid.
    Interior:  f''_i = 2 [h- f_{i+1} - (h- + h+) f_i + h+ f_{i-1}] / [h- h+ (h- + h+)]
               (curvature of the parabola through 3 points; exact 2nd-order on an even grid,
               and the 12/13 mm unevenness here adds only a tiny 1st-order term)
    Ends:      exact 2nd derivative of the cubic through the first / last 4 points, so the
               end values are as accurate as the interior instead of copying a neighbour."""
    d = np.empty_like(f)
    hm = z[1:-1] - z[:-2]
    hp = z[2:] - z[1:-1]
    d[1:-1] = 2.0 * (hm * f[2:] - (hm + hp) * f[1:-1] + hp * f[:-2]) / (hm * hp * (hm + hp))
    for idx, sl in ((0, slice(0, 4)), (-1, slice(-4, None))):
        zz, ff = z[sl], f[sl]
        x0 = z[idx]
        c = np.polyfit(zz - x0, ff, 3)          # exact cubic through 4 points, centred on the end point
        d[idx] = 2.0 * c[1]                     # polyfit order is [x^3, x^2, x, 1]; f''(x0) = 2 * (x^2 coefficient)
    return d


def derivatives_and_zeros(z_mm, bz):
    """dBz/dZ and d2Bz/dZ2 (T/m, T/m^2) on the grid from the direct formulas above,
    plus the Z where dBz/dZ = 0. The zero points come from a cubic spline through Bz,
    which locates them to a fraction of a mm."""
    z_m = z_mm / 1000.0
    dbz = first_derivative(z_m, bz)         # T/m
    d2bz = second_derivative(z_m, bz)       # T/m^2
    spline = CubicSpline(z_mm, bz)
    roots = spline.derivative().roots(extrapolate=False)
    zeros = pd.DataFrame({
        'Z_mm': roots,
        'Bz_T': spline(roots),
        'd2Bz_dZ2_T_per_m2': spline(roots, 2) * 1e6,   # spline is in mm -> convert to /m^2
    })
    zeros['type'] = np.where(zeros['d2Bz_dZ2_T_per_m2'] < 0, 'max', 'min')
    return dbz, d2bz, zeros


while True:
    xin = input("X-Coordinate Mask in mm ('q' to quit): ").strip()
    if xin.lower() == 'q':
        break
    yin = input("Y-Coordinate Mask in mm ('q' to quit): ").strip()
    if yin.lower() == 'q':
        break
    try:
        xmask, ymask = float(xin), float(yin)
    except ValueError:
        print("Please enter numbers (or 'q').")
        continue

    nearest_x = x_coord[np.argmin(np.abs(x_coord - xmask))]
    nearest_y = y_coord[np.argmin(np.abs(y_coord - ymask))]
    if not np.isclose(nearest_x, xmask) or not np.isclose(nearest_y, ymask):
        print(f"Note: exact X={xmask}, Y={ymask} not in the data; "
              f"using nearest available X={nearest_x}, Y={nearest_y}.")

    xy_mask = np.isclose(x_coord, nearest_x) & np.isclose(y_coord, nearest_y)
    if not xy_mask.any():
        print(f"No rows found for X={nearest_x}, Y={nearest_y}.")
        continue

    # Sort by Z and drop any repeated Z (derivatives need strictly increasing Z)
    order = np.argsort(z_coord[xy_mask])
    z_slice = z_coord[xy_mask][order]
    Bz_slice = Bz[xy_mask][order]
    keep = np.concatenate(([True], np.diff(z_slice) > 0))
    if not keep.all():
        print(f"Dropped {np.sum(~keep)} repeated Z value(s).")
    z_slice, Bz_slice = z_slice[keep], Bz_slice[keep]
    print(f"{len(z_slice)} points at X={nearest_x}, Y={nearest_y}")
    if len(z_slice) < 5:
        print("Not enough points along Z for derivatives.")
        continue

    dBz_dZ, d2Bz_dZ2, zeros = derivatives_and_zeros(z_slice, Bz_slice)
    R = np.hypot(nearest_x + 3904.0, nearest_y)

    phi_col = np.degrees(np.arctan2(nearest_y, nearest_x - X_AXIS)) % 360.0
    if bus_df is not None and not zeros.empty:
        xy_all = np.hypot(bus_df['X_mm'] - nearest_x, bus_df['Y_mm'] - nearest_y).to_numpy()
        info = []
        for v in zeros['Z_mm']:
            dz = np.where(v < bus_df['Z_lo_mm'], bus_df['Z_lo_mm'] - v,
                          np.where(v > bus_df['Z_hi_mm'], bus_df['Z_hi_mm'] - v, 0.0))
            d3 = np.hypot(dz, xy_all)
            i = int(np.argmin(d3))
            b = bus_df.iloc[i]
            info.append((int(b['cond N']), f"{b['Name/role']} ({b['kind']})", float(dz[i]), float(xy_all[i]), float(d3[i])))
        zeros['cond_N'] = [t[0] for t in info]
        zeros['nearest_conductor'] = [t[1] for t in info]
        zeros['conductor_dZ_mm'] = [t[2] for t in info]
        zeros['conductor_3D_dist_mm'] = [t[4] for t in info]

    # ---- print the dBz/dZ = 0 points ----
    print(f"\ndBz/dZ = 0 at X={nearest_x:.1f} mm, Y={nearest_y:.1f} mm (R = {R:.1f} mm):")
    print(zeros.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print("(Broad maxima with |d2Bz/dZ2| < ~0.2 T/m^2 sit where Bz is nearly flat; "
          "their Z is only good to roughly +/-10 mm.)\n")

    # ---- plot: Bz, dBz/dZ, d2Bz/dZ2 ----
    plt.style.use('dark_background')
    fig, ax = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    ax[0].plot(z_slice, Bz_slice, color=colors[2], marker='o', markersize=2, linewidth=1.2, label=r"$B_z$")
    ax[1].plot(z_slice, dBz_dZ, color=colors[1], linewidth=1.4, label=r"$dB_z/dZ$")
    ax[2].plot(z_slice, d2Bz_dZ2, color=colors[3], linewidth=1.4, label=r"$d^2B_z/dZ^2$")

    # mark the dBz/dZ = 0 points on the Bz and dBz/dZ panels
    for _, zr in zeros.iterrows():
        mk = 'v' if zr['type'] == 'max' else '^'
        ax[0].plot(zr['Z_mm'], zr['Bz_T'], mk, color='white', markersize=7)
        ax[1].plot(zr['Z_mm'], 0.0, mk, color='white', markersize=7)
        ax[0].annotate(f"{zr['Z_mm']:.1f}", (zr['Z_mm'], zr['Bz_T']), textcoords='offset points',
                       xytext=(0, 8 if zr['type'] == 'max' else -14), ha='center', fontsize=8, color='white')
    ax[0].plot([], [], 'v', color='white', label=r'$dB_z/dZ=0$ (max)')
    ax[0].plot([], [], '^', color='white', label=r'$dB_z/dZ=0$ (min)')

    for a in ax:
        a.axvline(x=Z_TRACKER_START, color='b', label='Start of Tracker')
        a.axvline(x=Z_TRACKER_END, color='g', label='End of Tracker')
        draw_tracker_geometry(a, label=(a is ax[0]), names=(a is ax[0]))
    for a in ax[1:]:
        a.axhline(0, color='gray', linewidth=0.8)

    if bus_df is not None:
        lo, hi = z_slice[0], z_slice[-1]
        inwin = busbars_in(bus_df, lo, hi)
        pts = inwin[inwin['kind'] != 'axial'].sort_values('Z_lo_mm')
        for a in ax:
            for _, b in pts.iterrows():
                near_side = angle_between(b['phi_deg'], phi_col) <= SAME_SIDE_DEG
                a.axvline(b['Z_lo_mm'], color='tomato', lw=0.9, alpha=0.9 if near_side else 0.3,
                          ls=':' if b['approx'] else '-')
        for m_, (_, b) in enumerate(pts.iterrows()):
            near_side = angle_between(b['phi_deg'], phi_col) <= SAME_SIDE_DEG
            txt = f" {int(b['cond N'])}" + (f": {b['Name/role']}" if BUS_LABEL_NAMES else "")
            ax[1].text(b['Z_lo_mm'], [0.98, 0.84, 0.70][m_ % 3], txt, color='tomato', alpha=1.0 if near_side else 0.5,
                       fontsize=7, rotation=90, va='top', ha='right', transform=ax[1].get_xaxis_transform())
        # bars running along Z: one strip each along the bottom of the Bz panel
        bars = inwin[inwin['kind'] == 'axial'].sort_values('Z_lo_mm')
        if len(bars):
            ax[0].margins(y=0.12); ax[0].autoscale_view()
            frac = 0.02 + len(bars) * 0.045 + 0.02
            y0_, y1_ = ax[0].get_ylim()
            ax[0].set_ylim(y0_ - frac / (1.0 - frac) * (y1_ - y0_), y1_)
        for r_, (_, b) in enumerate(bars.iterrows()):
            near_side = angle_between(b['phi_deg'], phi_col) <= SAME_SIDE_DEG
            z0b, z1b = max(b['Z_lo_mm'], lo), min(b['Z_hi_mm'], hi)
            y0b = 0.02 + r_ * 0.045
            ax[0].add_patch(plt.Rectangle((z0b, y0b), z1b - z0b, 0.037, transform=ax[0].get_xaxis_transform(),
                                          color='tomato', alpha=0.55 if near_side else 0.2, lw=0))
            room_right = (hi - z1b) > 0.25 * (hi - lo)       # put the label beside the strip where there is room
            ax[0].text(z1b if room_right else z0b, y0b + 0.0185, f" {int(b['cond N'])}: {b['Name/role']} " ,
                       transform=ax[0].get_xaxis_transform(), va='center', ha='left' if room_right else 'right',
                       fontsize=6, color='tomato', alpha=1.0 if near_side else 0.6, clip_on=True)
        ax[0].plot([], [], color='tomato', lw=0.9, label='busbar at fixed Z / arc start (numbers on middle panel)')
        ax[0].add_patch(plt.Rectangle((0, 0), 0, 0, color='tomato', alpha=0.55, label='busbar along Z (strip = Z range)'))

    ax[0].margins(y=0.12)   # room for the Z labels on the extrema
    ax[0].set_ylabel(r"$B_z$ (T)")
    ax[1].set_ylabel(r"$dB_z/dZ$ (T/m)")
    ax[2].set_ylabel(r"$d^2B_z/dZ^2$ (T/m$^2$)")
    ax[2].set_xlabel("Z (mm)")
    ax[2].xaxis.set_major_locator(MaxNLocator(nbins=10))
    data_file_name = os.path.basename(data_path[0])
    ax[0].set_title(f"$B_z$ and its Z-derivatives at X={nearest_x:.1f} mm, Y={nearest_y:.1f} mm "
                    f"(R={R:.0f} mm)\n{data_file_name}", pad=(38 if SHOW_STATION_LABELS else 6))
    ax[0].legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.01, 1.0), borderaxespad=0)
    fig.tight_layout()

    tag = f"{filename}_X{nearest_x:.0f}_Y{nearest_y:.0f}_{today}"
    if __name__ == "__main__":
        fig.savefig(os.path.join(plot_dir, tag + ".png"), bbox_inches='tight', dpi=150)
        print(f"Saved: {os.path.join(plot_dir, tag + '.png')}")
    plt.close(fig)

    # ---- text outputs: the slice with derivatives, and the zero points ----
    txt_path = os.path.join(plot_dir, tag + ".txt")
    with open(txt_path, 'w') as f:
        f.write('\t'.join(['z(mm)', 'Bz(T)', 'dBz/dZ(T/m)', 'd2Bz/dZ2(T/m^2)']) + '\n')
        for row in zip(z_slice, Bz_slice, dBz_dZ, d2Bz_dZ2):
            f.write('\t'.join(repr(float(x)) for x in row) + '\n')
    print(f"Saved to {txt_path}")

    zeros_path = os.path.join(plot_dir, tag + "_dBzdZ_zeros.txt")
    zeros.to_csv(zeros_path, sep='\t', index=False, float_format='%.6f')
    print(f"Saved to {zeros_path}")