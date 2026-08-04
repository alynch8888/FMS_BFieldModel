import subprocess
import argparse
import torch as tc
from helicalc_utilities.constants import dxyz_dict, TSd_grid, DS_grid, helicalc_GPU_dict

if __name__=='__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--Region',
                        help='Which region of Mu2e to calculate? '+
                        '["DS"(default), "TSd", "DSCylFMS", "DSCylFMSAll"]')
    parser.add_argument('-D', '--Device',
                        help='Which GPU (i.e. which coils/layers) to use? [0 (default), 1, 2, 3].')
    parser.add_argument('-j', '--Jacobian',
                        help='Include points for calculating '+
                        'the Jacobian of the field? "n"(default)/"y"')
    parser.add_argument('-d', '--dxyz_Jacobian',
                        help='What step size (in m) to use for points used in '+
                        'the Jacobian calculation? e.g. "0.001" (default)')
    parser.add_argument('-t', '--Testing',
                        help='Calculate using small subset of field points (N=1000)?'+
                        '"y"/"n"(default). If yes (y), region defaults to DS.')
    parser.add_argument('-i', '--infile', help='pickle file with coordinate grid')
    args = parser.parse_args()
    # fill defaults if necessary

    if args.Region is None:
        args.Region = 'DS'
    else:
        args.Region = args.Region.strip()
    reg = args.Region

    if args.Device is None:
        args.Device = 0
    else:
        args.Device = int(args.Device.strip())
    Dev = args.Device

    if args.Jacobian is None:
        args.Jacobian = 'n'
    else:
        args.Jacobian = args.Jacobian.strip()
    Jac = args.Jacobian

    if args.dxyz_Jacobian is None:
        args.dxyz_Jacobian = '0.001'
    else:
        args.dxyz_Jacobian = args.dxyz_Jacobian.strip()
    dxyz = args.dxyz_Jacobian

    if args.Testing is None:
        args.Testing = 'n'
    else:
        args.Testing = args.Testing.strip()
    Test = args.Testing
    # if Test == 'y':
    #     reg = 'DS'


    

    # gpu_type = input("Are you using a single GPU or multiple GPUs? (s/m): ")
    gpu_count = tc.cuda.device_count()
    gpu_shift = int(round(4/gpu_count,0))
    for run in range(gpu_shift):
        coil_list = helicalc_GPU_dict[run]
        print(f'Run {run+1}: Running coil group {run} on GPU {Dev}')
        for info in coil_list:
            append = '' if args.infile is None else f' -i {args.infile}'
            print(f'Calculating: {info}')
            _ = subprocess.run(f'python calculate_single_coil_grid.py -r {reg} -C {info["coil"]}'+
                               f' -L {info["layer"]} -D {Dev} -j {Jac} -d {dxyz} -t {Test}'+append,
                               shell=True, capture_output=False)
    # if gpu_type == 's':
    #     Dev = tc.cuda.current_device()
    #     gpu_count = tc.cuda.device_count()
    #     gpu_shift = int(round(4/gpu_count,0))
    #     for run in range(gpu_shift):
    #         coil_list = helicalc_GPU_dict[run]
    #         print(f'Run {run+1}: Running coil group {run} on GPU {Dev}')

    #         for info in coil_list:
    #             append = '' if args.infile is None else f' -i {args.infile}'
    #             print(f'Calculating: {info}')
    #             _ = subprocess.run(f'python calculate_single_coil_grid.py -r {reg} -C {info["coil"]}'+
    #                             f' -L {info["layer"]} -D {Dev} -j {Jac} -d {dxyz} -t {Test}'+append,
    #                             shell=True, capture_output=False)
    # elif gpu_type == 'm':
    #     print(f'Running on GPU: {Dev}')
    #     for info in helicalc_GPU_dict[Dev]:
    #         append = '' if args.infile is None else f' -i {args.infile}'
    #         print(f'Calculating: {info}')
    #         _ = subprocess.run(f'python calculate_single_coil_grid.py -r {reg} -C {info["coil"]}'+
    #                         f' -L {info["layer"]} -D {Dev} -j {Jac} -d {dxyz} -t {Test}'+append, shell=True,
    #                         capture_output=False)