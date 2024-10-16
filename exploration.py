import netCDF4 as nc
#Exploring how netCDF file is formatted

file_path = '250725/sgpdlfptS5.b1.20230911.051918.cdf'
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

# Check specific variable attributes (like 'units')
print("\nUnits of key variables:")
print(f"base_time: {dataset.variables['base_time'].units}")
print(f"time_offset: {dataset.variables['time_offset'].units}")
print(f"range: {dataset.variables['range'].units}")
print(f"radial_velocity: {dataset.variables['radial_velocity'].units}")

dataset.close()
