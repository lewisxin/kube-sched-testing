import plotly.express as px
import pandas as pd
import os
import sys
import getopt
from datetime import datetime
import plotly.graph_objects as go


def insert_paused_events(df):
    paused_rows = []
    # Iterate through each job group
    for _, group in df.groupby("Job"):
        # Sort the group by "Start"
        group = group.sort_values(by=["Start"])
        for i in range(1, len(group)):
            prev_end = group.iloc[i - 1]["End"]
            start = group.iloc[i]["Start"]
            deadline = group.iloc[i]["Deadline"]
            if start > prev_end:
                row1 = group.iloc[i - 1].copy()
                row1["Start"] = prev_end
                row1["End"] = min(deadline, start)
                row1["Status"] = "Paused"
                paused_rows.append(row1)
                if deadline > prev_end:
                    row2 = row1.copy()
                    row2["Start"] = min(deadline, start)
                    row2["End"] = start
                    row2["Status"] = "Paused (Overdue)"
                    paused_rows.append(row2)

    # Create DataFrame for "Paused" rows
    paused_df = pd.DataFrame(paused_rows, columns=df.columns)

    # Concatenate with the main DataFrame
    df = pd.concat([df, paused_df], ignore_index=True)
    df = df.sort_values(by=["Node", "Start", "Job"])
    return df

def shorten_node_name(node_name):
    # Extract the last numeric part from the node name
    node_number = "".join(filter(str.isdigit, node_name.split('-')[-1])) or "1"
    return f"<b>node-{node_number}</b>"

def plot(inputfile):
    name = inputfile.removesuffix(".csv")
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    df = pd.read_csv(filepath_or_buffer=inputfile, header=0,
                     delimiter=",").sort_values(by=["Job", "Status"])

    # Insert paused events
    df = insert_paused_events(df)
    # Shorten node names
    df["Node"] = df["Node"].apply(shorten_node_name)

    colors = {
        "Paused": "#C0C0C0",
        "In Queue": "#29b6f6",
        "Running": "#66bb6a",
        "Paused (Overdue)": "#e4bab6",
        "In Queue (Overdue)": "#ff786e",
        "Running (Overdue)": "#f44336",
    }

    # Create a list of the same length as the DataFrame for the 'text' parameter
    text_values = df.apply(lambda row: row["Node"] if row["End"] == df[df["Job"] == row["Job"]]["End"].max() else None, axis=1)
    fig = px.timeline(df, x_start="Start", x_end="End", y="Job", color="Status",
                      color_discrete_map=colors, text=text_values)
    fig.update_traces(textposition='outside')

    # Add vertical lines for deadlines
    fig.add_trace(
        go.Scatter(
            x=df["Deadline"],
            y=df["Job"],
            mode="markers",
            marker=dict(
                color="darkblue",
                size=15,
                symbol="x-thin",
                line=dict(width=2, color='darkblue')
            ),
            name="Deadline"
        )
    )

    fig.update_layout(
        title_text=f"Plot based on {name} (generated at {current_time})", title_x=0.5)
    fig.update_yaxes(autorange="reversed")
    fig.show()

    # Create the "plots" folder if it doesn't exist
    folder = "plots"
    if not os.path.exists(folder):
        os.makedirs(folder)

    output = f'{folder}/{current_time}_gantt_{name}.png'
    fig.write_image(output, width=1200, height=800, scale=2)


def main(argv):
    inputfile = ''
    opts, _ = getopt.getopt(argv, "hi:o:", ["ifile="])
    for opt, arg in opts:
        if opt == '-h':
            print('graph.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
    print("plotting from data file:", inputfile)
    plot(inputfile)


if __name__ == "__main__":
    main(sys.argv[1:])
