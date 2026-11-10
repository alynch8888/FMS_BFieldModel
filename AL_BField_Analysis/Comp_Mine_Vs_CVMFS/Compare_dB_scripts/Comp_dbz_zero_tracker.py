#List of all the Official Imports I use.
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.ticker import MaxNLocator
from matplotlib.lines import Line2D
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
Z_TRACKER_START = 8540.0      # mm
Z_TRACKER_END = 11810.0       # mm
X_AXIS = -3904.0              # DS axis, mm
SHARP_WINDOW = 150.0          # +/- mm shown around a sharp extremum
BROAD_WINDOW = 700.0          # +/- mm shown around a broad (flat) extremum
BROAD_CURVATURE = 1.0         # |d2Bz/dZ2| below this (T/m^2) counts as "broad"
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


##########Readers##########
def read_field_file(path):
    """Read X, Y, Z, Bx, By, Bz from a .pkl or a whitespace-delimited .txt (any number of
    header lines). Returns coordinates in mm (converted if the file is in metres, rounded
    to 0.001 mm to remove float noise) and fields in T."""
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


##########Math##########
def first_derivative(z_mm, f):
    """Direct 3-point dBz/dZ (T/m) on an uneven grid; 3-point one-sided at the ends."""
    z = z_mm / 1000.0
    d = np.empty_like(f)
    hm = z[1:-1] - z[:-2]
    hp = z[2:] - z[1:-1]
    d[1:-1] = (hm**2 * f[2:] - hp**2 * f[:-2] + (hp**2 - hm**2) * f[1:-1]) / (hm * hp * (hm + hp))
    h1, h2 = z[1] - z[0], z[2] - z[1]
    d[0] = -(2*h1 + h2) / (h1*(h1 + h2)) * f[0] + (h1 + h2) / (h1*h2) * f[1] - h1 / (h2*(h1 + h2)) * f[2]
    h1, h2 = z[-2] - z[-3], z[-1] - z[-2]
    d[-1] = h2 / (h1*(h1 + h2)) * f[-3] - (h1 + h2) / (h1*h2) * f[-2] + (h1 + 2*h2) / (h2*(h1 + h2)) * f[-1]
    return d


def column(df, x, y):
    """Bz along Z at the nearest grid column to (x, y); sorted, repeated Z removed."""
    xs, ys = df['X'].to_numpy(), df['Y'].to_numpy()
    nx = xs[np.argmin(np.abs(xs - x))]
    ny = ys[np.argmin(np.abs(ys - y))]
    sel = df[np.isclose(df['X'], nx) & np.isclose(df['Y'], ny)].sort_values('Z')
    sel = sel.loc[~sel['Z'].duplicated()]
    return nx, ny, sel['Z'].to_numpy(), sel['Bz'].to_numpy()


def zeros_in_tracker(z, bz):
    """Z where dBz/dZ = 0 inside the tracker, from a cubic spline through Bz."""
    cs = CubicSpline(z, bz)
    r = cs.derivative().roots(extrapolate=False)
    r = r[(r >= Z_TRACKER_START) & (r <= Z_TRACKER_END)]
    curv = cs(r, 2) * 1e6                         # T/mm^2 -> T/m^2
    return cs, pd.DataFrame({'Z_mm': r, 'Bz_T': cs(r), 'd2Bz_dZ2_T_per_m2': curv,
                             'type': np.where(curv < 0, 'max', 'min'),
                             'broad': np.abs(curv) < BROAD_CURVATURE})


##########Pick files##########
total_path = navigate(nav_path, "for the TOTAL field map (Summed_...)", "")
if not total_path:
    sys.exit("No file selected.")
total_df = read_field_file(total_path[0])

coil_df = None
if input("Also compare against a coils-only map (Coils_Summed_...)? (y/n) ").strip().lower() == 'y':
    coil_path = navigate(nav_path, "for the COILS-ONLY field map", "")
    if coil_path:
        coil_df = read_field_file(coil_path[0])

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

script_dir = os.path.dirname(os.path.abspath(__file__))
vs_name = "dBz_dZ_zeros_in_tracker"
plot_dir = os.path.join(script_dir, "Comparison_Plots", vs_name, f"{today}")
os.makedirs(plot_dir, exist_ok=True)

##########Main loop##########
while True:
    xin = input("X-Coordinate in mm ('q' to quit): ").strip()
    if xin.lower() == 'q':
        break
    yin = input("Y-Coordinate in mm ('q' to quit): ").strip()
    if yin.lower() == 'q':
        break
    try:
        xmask, ymask = float(xin), float(yin)
    except ValueError:
        print("Please enter numbers (or 'q').")
        continue

    nx, ny, z, bz = column(total_df, xmask, ymask)
    if not (np.isclose(nx, xmask) and np.isclose(ny, ymask)):
        print(f"Note: using nearest available X={nx}, Y={ny}.")
    if len(z) < 5:
        print("Not enough points along Z.")
        continue
    R = np.hypot(nx - X_AXIS, ny)
    cs_t, zt = zeros_in_tracker(z, bz)
    dbz_t = first_derivative(z, bz)

    cs_c, zc = None, None
    if coil_df is not None:
        cx, cy, zz_c, bz_c = column(coil_df, nx, ny)
        if np.isclose(cx, nx) and np.isclose(cy, ny) and len(zz_c) >= 5:
            cs_c, zc = zeros_in_tracker(zz_c, bz_c)
        else:
            print("Coils-only map has no matching column; skipping it.")

    print(f"\ndBz/dZ = 0 inside the tracker at X={nx:.1f} mm, Y={ny:.1f} mm (R = {R:.1f} mm):")
    if zt.empty:
        print("  none found.")
        continue
    report = zt.copy()
    report['nearest_station_centre_mm'] = [station_z[np.argmin(np.abs(station_z - v))] for v in report['Z_mm']]
    report['nearest_slot'] = [int(np.argmin(np.abs(station_z - v))) for v in report['Z_mm']]
    report['nearest_station_no'] = [SLOT_TO_STATION[k] for k in report['nearest_slot']]
    if zc is not None and not zc.empty:
        report['coils_only_Z_mm'] = [zc['Z_mm'].iloc[np.argmin(np.abs(zc['Z_mm'] - v))] for v in report['Z_mm']]
        report['shift_from_noncoil_mm'] = report['Z_mm'] - report['coils_only_Z_mm']
    phi_col = np.degrees(np.arctan2(ny, nx - X_AXIS)) % 360.0
    if bus_df is not None:
        # Z distance to each conductor (0 if the zero point lies inside an axial bar's Z range)
        # Nearest conductor by approximate 3D distance: Z gap (0 inside an axial bar's range) combined with
        # the XY distance from the plotted column to the conductor's start point (x0, y0).
        names, conds, dzs, xys, d3s, sides = [], [], [], [], [], []
        xy_all = np.hypot(bus_df['X_mm'] - nx, bus_df['Y_mm'] - ny).to_numpy()
        for v in report['Z_mm']:
            dz = np.where(v < bus_df['Z_lo_mm'], bus_df['Z_lo_mm'] - v,
                          np.where(v > bus_df['Z_hi_mm'], bus_df['Z_hi_mm'] - v, 0.0))
            d3 = np.hypot(dz, xy_all)
            i = int(np.argmin(d3))
            b = bus_df.iloc[i]
            names.append(f"{b['Name/role']} ({b['kind']})")
            conds.append(int(b['cond N']))
            dzs.append(float(dz[i]))
            xys.append(float(xy_all[i]))
            d3s.append(float(d3[i]))
            sides.append(bool(angle_between(b['phi_deg'], phi_col) <= SAME_SIDE_DEG))
        report['nearest_conductor'] = names
        report['cond_N'] = conds
        report['conductor_dZ_mm'] = dzs
        report['conductor_XY_dist_mm'] = xys
        report['conductor_3D_dist_mm'] = d3s
        report['same_side'] = sides
    print(report.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print("(Broad extrema sit where Bz is nearly flat; their Z is only good to roughly +/-10 mm "
          "and moves easily with small extra fields.)\n")

    # ---- plot: one column per zero point, Bz on top, dBz/dZ below ----
    plt.style.use('dark_background')
    n = len(zt)
    fig, ax = plt.subplots(2, n, figsize=(5.8*n, 8.5), squeeze=False)
    for j, row in zt.reset_index(drop=True).iterrows():
        w = BROAD_WINDOW if row['broad'] else SHARP_WINDOW
        lo, hi = row['Z_mm'] - w, row['Z_mm'] + w
        zf = np.linspace(max(lo, z[0]), min(hi, z[-1]), 800)
        k = (z >= lo) & (z <= hi)

        ax[0, j].plot(zf, cs_t(zf), color='seagreen', lw=1.6, label='total')
        ax[0, j].plot(z[k], bz[k], 'o', color='seagreen', ms=2.5)
        ax[1, j].plot(zf, cs_t(zf, 1) * 1000.0, color='darkorange', lw=1.6, label='total')
        if cs_c is not None:
            ax[0, j].plot(zf, cs_c(zf), color='seagreen', ls='--', lw=1.1, label='coils only')
            ax[1, j].plot(zf, cs_c(zf, 1) * 1000.0, color='darkorange', ls='--', lw=1.1, label='coils only')
            for _, r2 in zc[(zc['Z_mm'] >= lo) & (zc['Z_mm'] <= hi)].iterrows():
                mk = 'v' if r2['type'] == 'max' else '^'
                ax[0, j].plot(r2['Z_mm'], r2['Bz_T'], mk, color='white', mfc='none', ms=8)
                ax[1, j].plot(r2['Z_mm'], 0, mk, color='white', mfc='none', ms=8)
        for _, r2 in zt[(zt['Z_mm'] >= lo) & (zt['Z_mm'] <= hi)].iterrows():
            mk = 'v' if r2['type'] == 'max' else '^'
            ax[0, j].plot(r2['Z_mm'], r2['Bz_T'], mk, color='white', ms=8)
            ax[1, j].plot(r2['Z_mm'], 0, mk, color='white', ms=8)

        for a in ax[:, j]:
            draw_tracker_geometry(a, lo, hi, label=False, names=(a is ax[0, j]))
            for zt_ in (Z_TRACKER_START, Z_TRACKER_END):
                if lo <= zt_ <= hi:
                    a.axvline(zt_, color='lightgray', lw=1.0)
            if bus_df is not None:
                # bars at a fixed Z and arc starts: vertical lines on both panels
                for _, b in busbars_in(bus_df, lo, hi).iterrows():
                    if b['kind'] == 'axial':
                        continue
                    near_side = angle_between(b['phi_deg'], phi_col) <= SAME_SIDE_DEG
                    a.axvline(b['Z_lo_mm'], color='tomato', lw=1.2, alpha=1.0 if near_side else 0.35,
                              ls=':' if b['approx'] else '-')
            a.set_xlim(lo, hi)
            a.xaxis.set_major_locator(MaxNLocator(nbins=6))
            a.set_xlabel("Z (mm)")
        if bus_df is not None:
            inwin = busbars_in(bus_df, lo, hi)
            # labels for fixed-Z bars / arcs, staggered so neighbours don't overlap
            pts = inwin[inwin['kind'] != 'axial'].sort_values('Z_lo_mm')
            for m_, (_, b) in enumerate(pts.iterrows()):
                near_side = angle_between(b['phi_deg'], phi_col) <= SAME_SIDE_DEG
                ax[0, j].text(b['Z_lo_mm'], 0.98 if m_ % 2 == 0 else 0.62, f" {int(b['cond N'])}: {b['Name/role']}",
                              color='tomato', alpha=1.0 if near_side else 0.5, fontsize=7, rotation=90,
                              va='top', ha='right', transform=ax[0, j].get_xaxis_transform())
            # bars running along Z: one horizontal strip each along the bottom of the Bz panel
            bars = inwin[inwin['kind'] == 'axial'].sort_values('cond N')
            if len(bars):
                # lower the bottom of the Bz panel so the strips sit below the curve, not on it
                frac = 0.02 + len(bars) * 0.055 + 0.02
                y0_, y1_ = ax[0, j].get_ylim()
                ax[0, j].set_ylim(y0_ - frac / (1.0 - frac) * (y1_ - y0_), y1_)
            for r_, (_, b) in enumerate(bars.iterrows()):
                near_side = angle_between(b['phi_deg'], phi_col) <= SAME_SIDE_DEG
                z0b, z1b = max(b['Z_lo_mm'], lo), min(b['Z_hi_mm'], hi)
                y0b = 0.02 + r_ * 0.055
                ax[0, j].add_patch(plt.Rectangle((z0b, y0b), z1b - z0b, 0.045, transform=ax[0, j].get_xaxis_transform(),
                                                 color='tomato', alpha=0.55 if near_side else 0.2, lw=0, clip_on=True))
                ax[0, j].text(z0b, y0b + 0.0225, f" {int(b['cond N'])}: {b['Name/role']}"
                              f" ({b['Z_lo_mm']:.0f}-{b['Z_hi_mm']:.0f}, phi {b['phi_deg']:.0f} deg)",
                              transform=ax[0, j].get_xaxis_transform(), va='center', ha='left', fontsize=6.5,
                              color='white', alpha=1.0 if near_side else 0.6, clip_on=True)
        ax[1, j].axhline(0, color='gray', lw=0.8)
        kind = ('broad ' if row['broad'] else '') + row['type']
        ax[0, j].set_title(f"{kind} at Z = {row['Z_mm']:.1f} mm\n$B_z$ = {row['Bz_T']:.5f} T", fontsize=11, pad=(38 if SHOW_STATION_LABELS else 6))
        ax[0, j].set_ylabel(r"$B_z$ (T)")
        ax[1, j].set_ylabel(r"$dB_z/dZ$ (T/m)")

    handles = [Line2D([], [], color='seagreen', label='total'),
               Line2D([], [], marker='^', ls='', color='white', label=r'$dB_z/dZ=0$ (total)'),
               Line2D([], [], color='lightgray', ls='--', label=f'station centres ({N_STATIONS})'),
               plt.Rectangle((0, 0), 1, 1, color='peru', alpha=0.25, label='shielding ring (19.05 mm)'),
               plt.Rectangle((0, 0), 1, 1, color='peru', alpha=0.45, label='end bronze ring (50.80 mm)')]
    if cs_c is not None:
        handles[1:1] = [Line2D([], [], color='seagreen', ls='--', label='coils only'),
                        Line2D([], [], marker='^', ls='', color='white', mfc='none', label=r'$dB_z/dZ=0$ (coils only)')]
    if bus_df is not None:
        handles += [Line2D([], [], color='tomato', label='busbar at fixed Z / arc start'),
                    plt.Rectangle((0, 0), 1, 1, color='tomato', alpha=0.55, label='busbar along Z (strip = Z range)'),
                    Line2D([], [], color='tomato', ls=':', label='transfer arc (start Z only)'),
                    Line2D([], [], color='tomato', alpha=0.35, label=f'faint: > {SAME_SIDE_DEG:.0f} deg around the axis')]
    ax[1, -1].legend(handles=handles, fontsize=8, loc='best')
    data_file_name = os.path.basename(total_path[0])
    fig.suptitle(f"$dB_z/dZ = 0$ points inside the tracker at X={nx:.1f} mm, Y={ny:.1f} mm "
                 f"(R={R:.0f} mm)\n{data_file_name}")
    fig.tight_layout()

    tag = f"{filename}_X{nx:.0f}_Y{ny:.0f}_{today}"
    if __name__ == "__main__":
        fig.savefig(os.path.join(plot_dir, tag + ".png"), bbox_inches='tight', dpi=150)
        print(f"Saved: {os.path.join(plot_dir, tag + '.png')}")
    plt.close(fig)

    report_path = os.path.join(plot_dir, tag + ".txt")
    report.to_csv(report_path, sep='\t', index=False, float_format='%.6f')
    print(f"Saved to {report_path}")