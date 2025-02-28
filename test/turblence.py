import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from netCDF4 import Dataset, num2date

# Define the directory where your CDF files are stored
data_directory = './250725'  # Update to your desired path

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
    beam_elevation = ds.variables['elevation'][:]

    # Save time units from the first file
    if time_units is None:
        time_units = ds.variables['time'].units  # Corrected 'time_offset' to 'time'

    # Append to the datasets list
    datasets.append({
        'radial_velocity': radial_velocity,
        'qc_variable': qc_variable,
        'range': range_data,
        'time': time,
        'azimuth': azimuth,
        'beam' : beam_elevation
    })
    
    ds.close()  # Ensure that each dataset is closed after reading

# Concatenate all datasets along the time dimension
radial_velocity_combined = np.concatenate([data['radial_velocity'] for data in datasets], axis=0)
qc_variable_combined = np.concatenate([data['qc_variable'] for data in datasets], axis=0)
range_data_combined = datasets[0]['range']  # Assuming range_data is the same for all
time_combined = np.concatenate([data['time'] for data in datasets], axis=0)
azimuth_combined = np.concatenate([data['azimuth'] for data in datasets], axis=0)
beam_combined = np.concatenate([data['beam'] for data in datasets], axis=0)

# Convert time to datetime objects using netCDF4.num2date
time_combined_dates = num2date(time_combined, units=time_units, calendar='standard')

# Keeping data where qc is 0
# Create a mask where quality control is good (0 means valid)
azimuth_mask = qc_variable_combined == 0  

# Apply the mask correctly
radial_velocity_qc = np.where(qc_variable_combined == 0, radial_velocity_combined, np.nan)  
azimuth_qc = np.where(azimuth_mask, azimuth_combined[:, np.newaxis], np.nan)  # Extend azimuth_combined to 2D

# Calculate wind speed components
azimuth_radians = np.radians(azimuth_qc)

V_e = radial_velocity_qc * np.cos(azimuth_radians)  # Eastward component
V_n = radial_velocity_qc * np.sin(azimuth_radians)  # Northward component

# Now, let's compute the horizontal and vertical turbulence
horizontal_turbulence = np.std(V_e, axis=0)  # Horizontal component (over time)
vertical_turbulence = np.std(V_n, axis=0)    # Vertical component (over time)

# Create meshgrid for time and range data
X, Y = np.meshgrid(mdates.date2num(time_combined_dates), range_data_combined)

# Reshape turbulence data to match meshgrid dimensions
horizontal_turbulence_reshaped = np.repeat(horizontal_turbulence[:, np.newaxis], len(time_combined_dates), axis=1)
vertical_turbulence_reshaped = np.repeat(vertical_turbulence[:, np.newaxis], len(time_combined_dates), axis=1)

# Create a figure with two subplots for horizontal and vertical turbulence
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

# Create a heatmap for horizontal turbulence
heatmap_hor = ax1.imshow(horizontal_turbulence_reshaped, aspect='auto', cmap='viridis', 
                          extent=[mdates.date2num(time_combined_dates[0]), mdates.date2num(time_combined_dates[-1]), 
                                  range_data_combined[-1], range_data_combined[0]], 
                          origin='upper', interpolation='nearest')

ax1.set_ylabel('Height (m)')
ax1.set_title('Horizontal Turbulence (m/s)')
fig.colorbar(heatmap_hor, ax=ax1, label='Horizontal Turbulence (m/s)')

# Set x-axis limits from start to end time
ax1.set_xlim(mdates.date2num(time_combined_dates[0]), mdates.date2num(time_combined_dates[-1]))

# Manually set x-axis ticks from 00:00 to 24:00
ticks = np.linspace(mdates.date2num(time_combined_dates[0]), mdates.date2num(time_combined_dates[-1]), num=25)
ax1.set_xticks(ticks)
ax1.set_xticklabels([f"{int((t - mdates.date2num(time_combined_dates[0])) * 24 / (mdates.date2num(time_combined_dates[-1]) - mdates.date2num(time_combined_dates[0]))):02}:00" for t in ticks])

# Create a heatmap for vertical turbulence
heatmap_vert = ax2.imshow(vertical_turbulence_reshaped, aspect='auto', cmap='plasma', 
                           extent=[mdates.date2num(time_combined_dates[0]), mdates.date2num(time_combined_dates[-1]), 
                                   range_data_combined[-1], range_data_combined[0]], 
                           origin='upper', interpolation='nearest')

ax2.set_xlabel('Time of Day (HH:MM)')
ax2.set_ylabel('Height (m)')
ax2.set_title('Vertical Turbulence (m/s)')
fig.colorbar(heatmap_vert, ax=ax2, label='Vertical Turbulence (m/s)')

# Manually set x-axis ticks for vertical turbulence
ax2.set_xticks(ticks)
ax2.set_xticklabels([f"{int((t - mdates.date2num(time_combined_dates[0])) * 24 / (mdates.date2num(time_combined_dates[-1]) - mdates.date2num(time_combined_dates[0]))):0}:00" for t in ticks])

# Format the x-axis for better visibility
fig.autofmt_xdate()

# Adjust layout and display the plots
plt.tight_layout()
plt.show()
