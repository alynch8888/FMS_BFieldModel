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
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Scripts_setup.utils import fit_and_plot_gaussian
from Show_BF_Diff_and_Err import field_diff
#Useful names that can be used elsewhere
today = date.today()

#Start of actual code
print("Running "+os.path.splitext(os.path.basename(__file__))[0]+"...")

field_data = [field_diff[:, 0], field_diff[:, 1], field_diff[:, 2]]

# Example usage for ΔBx, ΔBy, ΔBz
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

results = {}
results['ΔBx'] = fit_and_plot_gaussian(field_data[0], axes[0], 'ΔBx', color='C0')
results['ΔBy'] = fit_and_plot_gaussian(field_data[1], axes[1], 'ΔBy', color='C1')
results['ΔBz'] = fit_and_plot_gaussian(field_data[2], axes[2], 'ΔBz', color='C2')

plt.tight_layout()

script_dir = os.path.dirname(os.path.abspath(__file__))
plot_dir = os.path.join(script_dir, "Comparison_Plots", f"{today}")
os.makedirs(plot_dir, exist_ok=True)

filename = f"Gaussian_fits_{today}.png"
fig.savefig(os.path.join(plot_dir, filename), bbox_inches='tight', dpi=150)
print(f"Saved: {os.path.join(plot_dir, filename)}")


# plt.show()

# Print fit results
for key, res in results.items():
    if res:
        print(f"{key}: mean = {res['mean']:.4g} ± {res['mean_err']:.4g}, "
      f"σ = {res['sigma']:.4g} ± {res['sigma_err']:.4g}")