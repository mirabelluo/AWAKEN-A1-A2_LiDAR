import os
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

# Step 1: Define file paths
base_path = '/path/to/files/'  # Replace with right path
netcdf_file = os.path.join(base_path, 'name_of_file.nc')

# Step 2: Open and read NetCDF file
nc = Dataset(netcdf_file, 'r')

#nc.variables[‘variable_name’] - gives access to data of a variable in NetCDF file

time = nc.variables['time'][:]  # Assuming time is one of the variables
height = nc.variables['height'][:]  # Assuming height is a dimension

# Extract the necessary variables (assuming they exist in netCDF file)
U = nc.variables['U'][:]  # Wind speed (m/s)
Phi = nc.variables['Phi'][:]  # Wind direction (degrees)
Theta = nc.variables['Theta'][:]  # Potential temperature (K)

# Step 3: Create the plot
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 10))

# Plot U (wind speed)
ax = axes[0]
U_contour = ax.contourf(time, height, U.T, levels=20, cmap='viridis')
cbar = fig.colorbar(U_contour, ax=ax)
cbar.set_label('U [m s$^{-1}$]')
ax.set_ylabel('Height [m]')
ax.set_title('(a) U (wind speed)')

# Plot Phi (wind direction)
ax = axes[1]
Phi_contour = ax.contourf(time, height, Phi.T, levels=20, cmap='cividis')
cbar = fig.colorbar(Phi_contour, ax=ax)
cbar.set_label('Phi [deg]')
ax.set_ylabel('Height [m]')
ax.set_title('(b) Phi (wind direction)')

# Plot Theta (potential temperature)
ax = axes[2]
Theta_contour = ax.contourf(time, height, Theta.T, levels=20, cmap='plasma')
cbar = fig.colorbar(Theta_contour, ax=ax)
cbar.set_label('Theta [K]')
ax.set_ylabel('Height [m]')
ax.set_xlabel('Time of day [UTC]')
ax.set_title('(c) Theta (potential temperature)')

# Final adjustments
plt.tight_layout()
plt.show()

# Close the dataset
nc.close()
