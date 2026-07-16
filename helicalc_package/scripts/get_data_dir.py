# for bash script awareness of data directory.
import helicalc; print(helicalc.__file__)
from helicalc import helicalc_data
print("Getting Data Directory...")
print(helicalc_data)
