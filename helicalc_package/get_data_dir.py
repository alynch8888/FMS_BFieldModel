# for bash script awareness of data directory.
import helicalc_utilities; print(helicalc_utilities.__file__)
from helicalc_utilities import helicalc_data
print("Getting Data Directory...")
print(helicalc_data)
