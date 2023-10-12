import plotly.express as px
import pandas as pd
import os
import time

df = pd.read_csv(filepath_or_buffer="pod_events.csv", header=0, delimiter=",").sort_values(by=["Job","Status"])

colors = {
    "In Queue": "#29b6f6",
    "Running": "#66bb6a",
    "Overdue": "#f44336"
}
fig = px.timeline(df, x_start="Start", x_end="End", y="Job", color="Status", color_discrete_map=colors, text="Node")
fig.update_yaxes(autorange="reversed")
fig.show()

# Create the "plots" folder if it doesn't exist
folder="plots"
if not os.path.exists(folder):
    os.makedirs(folder)
current_timestamp = int(time.time())
output=f'{folder}/gantt_{current_timestamp}.png'
fig.write_image(output)
