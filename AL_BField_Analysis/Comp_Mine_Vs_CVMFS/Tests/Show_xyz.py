#Imports
import pickle
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import sys
#From import

from scipy.stats import norm
from scipy.optimize import curve_fit
from datetime import date
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from FMS_BFieldModel.AL_BField_Analysis.Scripts_setup.utils.utils import load_pkl, pkl_2_txt, print_xyz_coord
#Useful names that can be used elsewhere
today = date.today()

if len(sys.argv) < 2:
    print("Usage: python3 Show_xyz.py <directory> [substring]")
    sys.exit(1)
region = input("What region are you using? ")
directory = sys.argv[1]
substring = sys.argv[2] if len(sys.argv) > 2 else f"{region}"

file_paths = [
    os.path.join(directory, f)
    for f in os.listdir(directory)
    if substring in f and f.endswith('.pkl')
]

print(f"Found {len(file_paths)} files matching '{substring}' in {directory}")

print_xyz_coord(file_paths)