
GPU = []
gpu_type = input("Are you using a singular or multiple GPUs? (s/m): ") 
shift = 1  # how much to shift each run
for i in range(4):
    GPU.append(i)
if gpu_type == 's':
    # for i in range(4):
    #     # GPU.append(input(f"What GPU # do you want to set GPU_{i}? "))
    #     GPU.append(i)
    for run in range(4):
        indices = [(i - run) % 4 for i in range(4)]
        gpu_assignment = [GPU[j] for j in indices]
        print(f"Run {run + 1}: {gpu_assignment}")
elif gpu_type == 'm':
    print(GPU)



GPU = []
gpu_type = input("Are you using a singular or multiple GPUs? (s/m): ") 
shift = 1  # how much to shift each run
for i in range(4):
    GPU.append(i)
if gpu_type == 's':
    indices = [(i - run) % 4 for i in range(4)]
    gpu_assignment = [GPU[j] for j in indices]
    print(f"Run {run + 1}: {gpu_assignment}")
elif gpu_type == 'm':
    print(f"GPU #s': {GPU}")



    GPU.append(i)
if gpu_type == 's':
    # for i in range(4):
    #     # GPU.append(input(f"What GPU # do you want to set GPU_{i}? "))
    #     GPU.append(i)
    for run in range(4):
        indices = [(i - run) % 4 for i in range(4)]
        gpu_assignment = [GPU[j] for j in indices]
        print(f"Run {run + 1}: {gpu_assignment}")
elif gpu_type == 'm':
    print(GPU)
