import netCDF4 as nc
import numpy as np
#Exploring how netCDF file is formatted

file_path = 'SiteC1A/sc1.lidar.z03.c0.20220828.172400.sta.nc'
dataset = nc.Dataset(file_path)

# Check the global attributes of the file (metadata)
print("Global attributes:")
for attr in dataset.ncattrs():
    print(f"{attr}: {dataset.getncattr(attr)}")

# Check the variable names and associated attributes (metadata)
print("\nVariables and their attributes:")
for var in dataset.variables:
    print(f"\nVariable: {var}")
    print(f"Dimensions: {dataset.variables[var].dimensions}")
    print(f"Shape: {dataset.variables[var].shape}")
    for attr in dataset.variables[var].ncattrs():
        print(f" - {attr}: {dataset.variables[var].getncattr(attr)}")

