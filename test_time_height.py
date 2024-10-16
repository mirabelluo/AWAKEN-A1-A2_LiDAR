import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from netCDF4 import Dataset, num2date


# Define the directory where your CDF files are stored
data_directory = './250725'  # Update to desired path

# Create a pattern to match the desired date
file_pattern = os.path.join(data_directory, 'sgpdlfptS5.b1.20230403.*.cdf')

# List all files matching the pattern
file_list = glob.glob(file_pattern)
datasets = []
time_units = None  # This will store the units of the time variable

# Loop through the list of files and read each one
for file in file_list:
    ds = Dataset(file, mode='r')  # Open the dataset
    print(f"Reading: {file}")
    # Extract relevant variables
    radial_velocity = ds.variables['radial_velocity'][:]
    qc_variable = ds.variables['qc_radial_velocity'][:]  # Quality control variable
    range_data = ds.variables['range'][:]  # Range = height
    time = ds.variables['time'][:]  # Time variable
    azimuth = ds.variables['azimuth'][:]  # Azimuth due north

    # Save time units from the first file
    if time_units is None:
        time_units = ds.variables['time_offset'].units

    # Append to the datasets list
    datasets.append({
        'radial_velocity': radial_velocity,
        'qc_variable': qc_variable,
        'range': range_data,
        'time': time,
        'azimuth': azimuth
    })
    
    ds.close()  # Ensure that each dataset is closed after reading

# Concatenate all datasets along the time dimension
radial_velocity_combined = np.concatenate([data['radial_velocity'] for data in datasets], axis=0)
qc_variable_combined = np.concatenate([data['qc_variable'] for data in datasets], axis=0)
range_data_combined = datasets[0]['range']  # Assuming range_data is the same for all
time_combined = np.concatenate([data['time'] for data in datasets], axis=0)
azimuth_combined = np.concatenate([data['azimuth'] for data in datasets], axis=0)

# Convert time to datetime objects using netCDF4.num2date
time_combined_dates = num2date(time_combined, units=time_units)

# Keeping data where qc is 0
# Create a mask where quality control is good (0 means valid)
azimuth_mask = qc_variable_combined != 1  

# Apply the mask correctly
radial_velocity_qc = np.where(qc_variable_combined != 1, radial_velocity_combined, np.nan)  
azimuth_qc = np.where(azimuth_mask, azimuth_combined[:, np.newaxis], np.nan)  # Extend azimuth_combined to 2D

# Calculate wind speed using azimuth and radial velocity
azimuth_radians = np.radians(azimuth_qc)

V_e = np.zeros_like(radial_velocity_qc)
V_n = np.zeros_like(radial_velocity_qc)

# Compute east and north components of wind speed
for i in range(radial_velocity_qc.shape[0]):
    V_e[i, :] = radial_velocity_qc[i, :] * np.cos(azimuth_radians[i, :])  
    V_n[i, :] = radial_velocity_qc[i, :] * np.sin(azimuth_radians[i, :]) 

wind_speed = np.sqrt(V_e**2 + V_n**2)

# Checking if wind_speed is a 2D array
if wind_speed.ndim != 2:
    print("Warning: wind_speed is not a 2D array. Check the dimensions.")

# Create meshgrid for time and range data
X, Y = np.meshgrid(mdates.date2num(time_combined_dates), range_data_combined)

# Create a filled contour plot for wind speed
plt.figure(figsize=(12, 6))
contour = plt.contourf(X, Y, wind_speed.T, cmap='viridis', levels=20, extend='both')

# Formatting the x-axis as time
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Set x-axis to have uniform hour-by-hour increments
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))

# Rotate date labels
plt.gcf().autofmt_xdate()

# Add a color bar
plt.colorbar(contour, label='Wind Speed (m/s)')  

# Adding labels and title
plt.xlabel('Time of Day (HH:MM)')
plt.ylabel('Height (m)')
plt.title('Site A2 Time-Height Profile of Wind Speed on April 3, 2023')
print("Height shape: ", range_data_combined.shape)
# Show the plot
plt.show()