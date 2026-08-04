import sys
from time import time
from datetime import datetime
import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm
from helicalc_utilities import helicalc_dir, helicalc_data
from helicalc_utilities.auxiliary_integrators import RadialStraightIntegrator1D
from helicalc_utilities.tools import generate_cartesian_grid_df, generate_cylindrical_grid_df, add_points_for_J
from helicalc_utilities.constants import dr_radial_dict, TSd_grid, DS_grid, DS_FMS_cyl_grid, DS_FMS_cyl_grid_SP, DS_cyl_grid_fine, DSCartVal_grid
from helicalc_utilities.solenoid_geom_funcs import load_all_geoms

# data
datadir = helicalc_data+'Bmaps/auxiliary_partial/'

# load straight bus bars, dump all other geometries
paramname = 'Mu2e_V13'
version = paramname.replace('Mu2e_V', '')
df_dict = load_all_geoms(version=version, return_dict=True)
df_radial_coils = df_dict['radial_coils']

# assume same chunk size for everything, for now
# N_per_chunk = 10000 # original, from busbars
N_per_chunk = 8000

regions = {'TSd': TSd_grid, 'DS': DS_grid, 'DSCylFMS': DS_FMS_cyl_grid,
           'DSCylFMSAll': [DS_FMS_cyl_grid, DS_FMS_cyl_grid_SP], 'DSCylFine': DS_cyl_grid_fine, 'DSCartVal': DSCartVal_grid}

if __name__=='__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--Region',
                        help='Which region of Mu2e to calculate? '+
                        '["DS"(default), "TSd", "DSCylFMS", "DSCylFMSAll", "DSCylFine", "DSCartVal"]')
    parser.add_argument('-C', '--Coil',
                        help='Coil number [56(default), 57, 58, ... , 66]. '+
                        'This is supported only for DS coils.')
    parser.add_argument('-R', '--Reverse',
                        help='Reverse "I_flow" for radial bars? '+
                        '"y"/"n"(default). Useful e.g. for bus bars.')
    parser.add_argument('-D', '--Device',
                        help='Which GPU to use? [0 (default), 1, 2, 3].')
    parser.add_argument('-j', '--Jacobian',
                        help='Include points for calculating '+
                        'the Jacobian of the field? "n"(default)/"y"')
    parser.add_argument('-d', '--dxyz_Jacobian',
                        help='What step size (in m) to use for points used in '+
                        'the Jacobian calculation? e.g. "0.001" (default)')
    parser.add_argument('-t', '--Testing',
                        help='Calculate using small subset of field points '+
                        ' (N=100000)? "y"/"n"(default).')
    args = parser.parse_args()
    # fill defaults where needed
    if args.Region is None:
        args.Region = 'DS'
    else:
        args.Region = args.Region.strip()
    reg = args.Region
    if args.Coil is None:
        args.Coil = "56"
    else:
        args.Coil = args.Coil.strip()
    if args.Reverse is None:
        args.Reverse = False
    else:
        args.Reverse = args.Reverse.strip() == 'y'
    df_conds = df_radial_coils[np.isin(df_radial_coils,
                                       [f'{args.Coil}in', f'{args.Coil}out'])\
                               ].copy()
    # reverse if necessary
    if args.Reverse:
        df_conds.loc[:, 'I_flow'] = -1 * df_conds.loc[:, 'I_flow']
        rev_str = '_reversed'
    else:
        rev_str = ''
    # pick correct integration grid based on ???
    ind_dr = 1
    dr_ = dr_radial_dict[ind_dr]
    if args.Device is None:
        args.Device = 0
    else:
        args.Device = int(args.Device.strip())
    if args.Jacobian is None:
        args.Jacobian = False
    else:
        if args.Jacobian.strip() == 'y':
            args.Jacobian = True
        else:
            args.Jacobian = False
    if args.dxyz_Jacobian is None:
        args.dxyz_Jacobian = 0.001
    else:
        args.dxyz_Jacobian = float(args.dxyz_Jacobian)
    if args.Testing is None:
        args.Testing = False
    else:
        args.Testing = args.Testing.strip() == 'y'
    # print configs
    print(f'Region: {reg}')
    # redirect stdout to log file
    dt = datetime.strftime(datetime.now(), '%Y-%m-%d_%H%M%S')
    log_file = open(datadir+f"logs/{dt}_calculate_{reg}_"+
                    f"region_radial_coil{rev_str}.log", "w")
    old_stdout = sys.stdout
    sys.stdout = log_file
    # find correct chunk size
    N_calc = N_per_chunk
    # create grid
    if reg in ['DSCylFMS', 'DSCylFMSAll']:
        df = generate_cylindrical_grid_df(regions[reg], dec_round=9)
    else:
        df = generate_cartesian_grid_df(regions[reg])
    if args.Testing:
        df = df.iloc[:100000].copy()
    # add extra points for Jacobian?
    if args.Jacobian:
        df = add_points_for_J(df, dxyz=args.dxyz_Jacobian)
        suff = '_Jacobian'
    else:
        suff = ''
    # set up base directory/name
    if args.Testing:
        base_name = f'Bmaps/auxiliary_partial/tests/{paramname}.{reg}_region.'+\
                     f'test-radial_coil{suff}.'
    else:
        base_name = f'Bmaps/auxiliary_partial/{paramname}.{reg}_region.'+\
                     f'standard-radial_coil{suff}.'
    # initialize conductor
    for i in range(len(df_conds)):
        df_cond = df_conds.iloc[i]
        myRadial = RadialStraightIntegrator1D(df_cond, dr=dr_, dev=args.Device)
        # integrate!
        df = myRadial.integrate_grid(df, N_batch=N_calc, tqdm=tqdm)
    # save!
    myRadial.save_grid_calc(savetype='pkl', savename=base_name+
                            f'Coil_Num_{args.Coil}_radial{rev_str}',
                            all_cols=True)
