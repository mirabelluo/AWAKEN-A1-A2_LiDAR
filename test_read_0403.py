import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from netCDF4 import Dataset, num2date

# Load the NetCDF file
file_path = 'SiteA1_2023_Onward/sa1.lidar.z04.c0.20231104.001000.sta.nc'
dataset = Dataset(file_path, 'r')

# Extract variables
time_var = dataset.variables['time']
height = dataset.variables['distance'][:]  # Extract height levels - SA2 called height
Vhm = dataset.variables['wind_speed'][:, :]  # Mean horizontal wind speed - SA2 called Vhm
qc_Vhm = dataset.variables['qc_wind_speed'][:, :]  # Quality check results - SA2 called qc_Vhm

# Convert time to UTC
time_units = time_var.units  #right now in 'seconds since 1970-01-01'
time_calendar = time_var.calendar if hasattr(time_var, 'calendar') else 'gregorian'
time_values = num2date(time_var[:], units=time_units, calendar=time_calendar)

# Replace fill values with NaN for Vhm
Vhm[Vhm == -9999.0] = np.nan

# Create a mask for quality checks (1: Bad, 2: Bad, 4: Bad)
# 0 indicates good quality, so we mask out all bad values
valid_mask = (qc_Vhm == 0)

# Apply the mask to Vhm
Vhm_masked = np.where(valid_mask, Vhm, np.nan)

# Create a DataFrame for easy manipulation
df = pd.DataFrame(Vhm_masked, columns=height)  # Create DataFrame with heights as columns
df['time'] = time_values  # Add time as a new column
df.set_index('time', inplace=True)  # Set time as the index

# Ensure all values are numeric
df[height] = df[height].apply(pd.to_numeric, errors='coerce')

# Transpose the DataFrame for contourf (heights in rows, time in columns)
df_t = df.transpose()

# Check for NaN values and drop them if necessary
df_t = df_t.fillna(method='ffill')  # Forward fill NaNs (or choose another method as needed)

# Create meshgrid for plotting (time vs height)
time_numeric = mdates.date2num(df_t.columns)  # Convert time to matplotlib date numbers
X, Y = np.meshgrid(time_numeric, df_t.index)  # Create meshgrid for plotting

# Plot wind speed using contourf
plt.figure(figsize=(12, 6))
contour = plt.contourf(X, Y, df_t.values, cmap='viridis', levels=100)  # Use df_t.values

# Format the x-axis as time (hour:minute)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))
plt.gcf().autofmt_xdate()

# Set y-axis ticks manually (from 40 to 220 in 20m increments)
plt.gca().set_yticks(np.arange(40, 221, 20))  # Adjusting the upper limit to 240 for inclusive 220 tick

# Add a color bar
plt.colorbar(contour, label='Mean Horizontal Wind Speed (m/s)')

# Adding labels and title
plt.xlabel('Time of Day (UTC)')
plt.ylabel('Height (m)')
plt.title('Site A1 Time-Height Profile of Mean Horizontal Wind Speed on November 4, 2023')

# Show the plot
plt.show()

# Close the dataset
dataset.close()
