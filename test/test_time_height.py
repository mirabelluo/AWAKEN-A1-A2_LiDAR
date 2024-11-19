import numpy as np
from netCDF4 import Dataset

# Define the path to your NetCDF file
file_path = 'SiteA2/sa2.lidar.z03.c0.20230403.000200.sta.nc'

def read_uv_from_netcdf(file_path):
    # Open the NetCDF file
    with Dataset(file_path, 'r') as nc_file:
        try:
            # Read u, v, and Vhm components
            u = nc_file.variables['um'][:]  # Adjust this based on actual variable names
            v = nc_file.variables['vm'][:]  # Adjust this based on actual variable names
            vhm = nc_file.variables['Vhm'][:]  # Adjust this based on actual variable names
            
            # Ensure u, v, and vhm are numpy arrays and check their shapes
            if not all(isinstance(var, np.ndarray) for var in [u, v, vhm]):
                raise ValueError("u, v, and Vhm must be numpy arrays.")

            # Print the shapes
            print(f"u shape: {u.shape}, v shape: {v.shape}, Vhm shape: {vhm.shape}")

            # Check that all variables have the same shape
            if not (u.shape == v.shape == vhm.shape):
                raise ValueError("u, v, and Vhm must have the same shape.")

            # Calculate expected Vhm
            expected_vhm = np.sqrt(u**2 + v**2)

            # Print the first 10 values of u, v, expected Vhm, and actual Vhm
            print("First 10 values of um (u component):", u[:10])
            print("First 10 values of vm (v component):", v[:10])
            print("First 10 values of Expected Vhm (calculated):", expected_vhm[:10])
            print("First 10 values of Actual Vhm from file:", vhm[:10])

            # Tolerance for floating point comparison
            tolerance = 1e-6
            
            # Check if calculated Vhm is approximately equal to the Vhm from the file
            if not np.allclose(expected_vhm, vhm, atol=tolerance):
                raise ValueError("Calculated wind speed from u and v does not match Vhm.")

            print("u and v are defined correctly in relation to Vhm.")

            # Return u, v, and Vhm components
            return u, v, vhm

        except KeyError as e:
            raise ValueError(f"Variable not found in the NetCDF file: {e}")

# Call the function
try:
    u, v, vhm = read_uv_from_netcdf(file_path)
    # Further processing can be done with u, v, and Vhm here
except ValueError as e:
    print(f"Error: {e}")
