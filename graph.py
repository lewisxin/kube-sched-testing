import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import re
import time
from datetime import datetime, timedelta
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# Function to extract the countdown number from the 'NAME' column
def extract_countdown_number(name):
    match = re.match(r'countdown-(\d+)', name)
    if match:
        return f'countdown-{match.group(1)}'
    return name

# Function to convert DDL values to seconds
def convert_ddl_to_seconds(ddl_value):
    total_seconds = 0
    time_units = re.findall(r'(\d+)([hms])', ddl_value)
    for value, unit in time_units:
        value = int(value)
        if unit == 's':
            total_seconds += value
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 'h':
            total_seconds += value * 3600
    return total_seconds

# Check if the filename argument is provided
if len(sys.argv) < 2:
    print("Usage: python graph.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Read the content from the text file and split it into lines
with open(filename, 'r') as file:
    content = file.read()
lines = content.strip().split('\n')

# Extract the column names and data into separate lists
columns = [col.strip() for col in lines[0].split()]
data = [line.split() for line in lines[1:]]

# Create a DataFrame using pandas
df = pd.DataFrame(data, columns=columns).query('STATUS!="<none>"')

# Convert timestamp columns to datetime objects
time_columns = ['POD_CREATED', 'POD_SCHED', 'STARTED', 'FINISHED']
# 2023-08-30T14:22:05Z
for column in time_columns:
    df[column] = pd.to_datetime(df[column])

# Calculate the time difference between POD_SCHED and FINISHED
#df['DELTA_CREAT'] = (df['FINISHED'] - df['POD_CREATED']).dt.total_seconds()
#df['DELTA_SCHED'] = (df['FINISHED'] - df['POD_SCHED']).dt.total_seconds()

# Convert the DDL column to seconds
df['DDL'] = df['DDL'].apply(convert_ddl_to_seconds)
df['Deadline'] = df['POD_CREATED'] + pd.to_timedelta(df["DDL"], unit="s")
df['StartSched'] = df['POD_CREATED']
df['EndSched'] = df['STARTED']
df['EndExec'] = df['FINISHED']
df['StartExec'] = df['STARTED']
min_start_sched = df["StartSched"].min()
min_start_exec = df["StartSched"].min()

# Apply the function to extract countdown numbers from the 'NAME' column
df['NAME'] = df['NAME'].apply(extract_countdown_number)

# Sort the data by the 'NAME' column in ascending order
df.sort_values(by='NAME', ascending=True, inplace=True)

# Plot the graph
#plt.figure(figsize=(10, 7))
#plt.barh(df['NAME'], df['DELTA_CREAT'], color='#ff4040', label='Time Since Pod Creation (Seconds)')
#plt.barh(df['NAME'], df['DELTA_SCHED'], color='#ff7f24', label='Time Since Pod Scheduled (Seconds)')
#plt.barh(df['NAME'], df['DDL'], color='#4169e1', label='DDL (Seconds)')
#plt.xlabel('Time (Seconds)')
#plt.ylabel('Jobs')
#plt.title('Time Lapse Since Pod Creation vs. Pod Scheduled vs. DDL')
#plt.legend()
#plt.tight_layout()

# Plot gantt chart
# Create a Gantt chart using matplotlib
fig, ax = plt.subplots(figsize=(10, 6))

color_bar_sched = '#BFCFFF'
color_bar_exec = '#ff7f24'
color_line = '#ff4040'
# Plot the tasks as horizontal bars
for index, row in df.iterrows():
    offset_sched = (row["StartSched"] - min_start_sched).total_seconds()
    offset_exec = (row["StartExec"] - min_start_sched).total_seconds()
    ax.barh(index, width=(row["EndExec"] - row["StartExec"]).total_seconds(), left=offset_exec, height=0.4, color=color_bar_exec, label="Pod Execution")
    ax.barh(index, width=(row["EndSched"] - row["StartSched"]).total_seconds(), left=offset_sched, height=0.4, color=color_bar_sched, label="Pod in Queue")
    deadline_x = (row["Deadline"] - min_start_sched).total_seconds()
    ax.axvline(x=deadline_x, color=color_line, linestyle="--", label="Deadline")
    ax.text(deadline_x + 0.2, index, row["NAME"], verticalalignment="center")


# Customize the appearance of the chart
ax.set_xlabel("Time")
ax.set_yticks(df.index)
ax.set_yticklabels(df["NAME"])
ax.set_title("Gantt Chart for Jobs")

# Configure the legend to show only two items
line_legend = Line2D([0], [0], color=color_line, linestyle='--', label='Deadline')
bar_exec_legend = Patch(color=color_bar_exec, label='Pod Execution')
bar_sched_legend = Patch(color=color_bar_sched, label='Pod in Queue')
ax.legend(handles=[line_legend, bar_sched_legend, bar_exec_legend], loc='upper right')

plt.tight_layout()

# Create the "plots" folder if it doesn't exist
folder="plots"
if not os.path.exists(folder):
    os.makedirs(folder)

current_timestamp = int(time.time())
#output=f'{folder}/bar_plot_{current_timestamp}.png'
output=f'{folder}/gantt_{current_timestamp}.png'
# Save the bar graph as a PNG file
plt.savefig(output)
print(f"plot saved to {output}")

# Show the graph
# plt.show()

