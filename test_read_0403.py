import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import xarray as xr

# Define the directory where your CDF files are stored
data_directory = './250725'  # Update this to your actual path

# Create a pattern to match the desired date (August 24, 2023)
file_pattern = os.path.join(data_directory, 'sgpdlfptS5.b1.20230824.*.cdf')

# List all files matching the pattern
file_list = glob.glob(file_pattern)

# Initialize an empty list to store datasets
datasets = []

# Loop through the list of files and read each one
for file in file_list:
    print(f"Reading: {file}")  # Optional: for tracking progress
    ds = xr.open_dataset(file)  # Read the dataset
    datasets.append(ds)  # Add the dataset to the list

# Concatenate all datasets along a new dimension (e.g., 'time')
combined_data = xr.concat(datasets, dim='time')

# Now, access the relevant variables
radial_velocity = combined_data['radial_velocity']  # Radial velocity variable
qc_variable = combined_data['qc_radial_velocity']  # QC variable
range_data = combined_data['range']  # Using 'range' instead of 'height'
time = combined_data['time']  # Time variable
azimuth = combined_data['azimuth']  # Assuming azimuth is also available

# Apply QC: Keep only data where qc_variable is equal to 0 (good data)
radial_velocity_qc = radial_velocity.where(qc_variable == 0)  # Keep only good data
azimuth_qc = azimuth.where(qc_variable == 0)  # Keep only good azimuth data

# Calculate wind speed using azimuth and radial velocity
azimuth_radians = np.radians(azimuth_qc)  # Convert azimuth to radians

# Initialize arrays for east and north components of wind speed
V_e = np.zeros_like(radial_velocity_qc)
V_n = np.zeros_like(radial_velocity_qc)

# Compute east and north components of wind speed
for i in range(radial_velocity_qc.shape[0]):  # For each time point
    V_e[i, :] = radial_velocity_qc[i, :] * np.cos(azimuth_radians[i])  # East component
    V_n[i, :] = radial_velocity_qc[i, :] * np.sin(azimuth_radians[i])  # North component

# Calculate total wind speed
wind_speed = np.sqrt(V_e**2 + V_n**2)

# Checking if wind_speed is a 2D array
if wind_speed.ndim != 2:
    print("Warning: wind_speed is not a 2D array. Check the dimensions.")

# Create a time-height plot for wind speed
plt.figure(figsize=(12, 6))
# Set the extent based on the time and range (as a proxy for height)
extent = [time.min().values, time.max().values, range_data.min().values, range_data.max().values]

# Plotting the wind speed
plt.imshow(wind_speed, aspect='auto', extent=extent, origin='lower', cmap='jet')

# Formatting the x-axis for military time
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Define y-ticks from 0 to the maximum value in range_data with increments of 500
max_height = int(range_data.max().values)
y_ticks = np.arange(0, max_height + 500, 500)  # Include max_height in ticks
plt.yticks(y_ticks)

# Adding labels and title
plt.colorbar(label='Wind Speed (m/s)')  # Adjust the label to your data's unit
plt.xlabel('Time of Day (Military Time)')
plt.ylabel('Height (m)')
plt.title('Time-Height Profile of Wind Speed on August 24, 2023')

# Show the plot
plt.show()

