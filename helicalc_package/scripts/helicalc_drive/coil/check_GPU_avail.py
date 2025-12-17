import torch as tc

print("Is Torch Cuda available?")
print(tc.cuda.is_available())
print("How many GPU devices are available?")
print(tc.cuda.device_count())
print("What is the current device?")
current_device= tc.cuda.current_device()
print(current_device)
print("What is the name of the device?")
print(tc.cuda.get_device_name(current_device))
