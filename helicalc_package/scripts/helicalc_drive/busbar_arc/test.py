import torch as tc

# arc_bar_GPU_dict = {2: range(0, N_cond_per_GPU),
#                     1: range(N_cond_per_GPU, 2*N_cond_per_GPU),
#                     0: range(2*N_cond_per_GPU, 3*N_cond_per_GPU),
#                     3: range(3*N_cond_per_GPU, N_cond)}

# gpu_count = tc.cuda.device_count()
# gpu_shift = int(round(4/gpu_count,0))
# for run in range(gpu_shift):
#     coil_list = arc_bar_GPU_dict[run]
#     print(f'Run {run+1}: Running coil group {run} on GPU {Dev}')
#     # print(f'Running on GPU: {Dev}')
#     for i in arc_bar_GPU_dict[Dev]:
#         if i < len(df_arc):
#             df_cn = df_arc.iloc[i]
#         else:
#             df_cn = df_arc_transfer.iloc[i-len(df_arc)]
#         cn = df_cn['cond N']
#         append = '' if args.infile is None else f' -i {args.infile}'
#         print(f'Calculating {i}: cond N={cn}, info={df_cn["Name/role"]}')
#         _ = subprocess.run(f'python calculate_single_arc_bar_grid.py'+
#                         f' -r {reg} -C {cn} -D {Dev} -j {Jac} -d {dxyz} -t {Test}'+append, shell=True,
#                         capture_output=False)
#         print("\n") 
Dev = 0
from drive_arc_bar import arc_bar_GPU_dict
gpu_count = tc.cuda.device_count()
gpu_shift = int(round(4/gpu_count,0))
for run in range(gpu_shift):
    coil_list = arc_bar_GPU_dict[run]
    print(f'Run {run+1}: Running coil group {run} on GPU {Dev}')
    # print(f'Running on GPU: {Dev}')
    for i in arc_bar_GPU_dict[run]:
        print(coil_list)
        # print(coil_list[i])