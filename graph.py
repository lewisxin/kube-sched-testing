import plotly.express as px
import pandas as pd
import numpy as np
import os
import sys
import getopt
from datetime import datetime
import plotly.graph_objects as go


def convert_to_relative(df: pd.DataFrame) -> pd.DataFrame:
    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = pd.to_datetime(df['End'])
    df['Deadline'] = pd.to_datetime(df['Deadline'])
    start_min = df["Start"].min()
    df["Start"] = (df["Start"] - start_min).dt.total_seconds()
    df["End"] = (df["End"] - start_min).dt.total_seconds()
    df["Deadline"] = (df["Deadline"] - start_min).dt.total_seconds()
    df["delta"] = df["End"] - df["Start"]
    return df


def update_fig_xdata(fig: go.Figure, df: pd.DataFrame):
    for data in fig.data:
        status = data.name
        subset_df = df[df["Status"] == status]
        if not subset_df.empty:
            data.x = subset_df["delta"].tolist()


def insert_paused_events(df: pd.DataFrame):
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


def shorten_node_name(node_name: str) -> str:
    # Extract the last numeric part from the node name
    node_number = "".join(filter(str.isdigit, node_name.split('-')[-1])) or "1"
    return f"<b>node-{node_number}</b>"


def read_data(inputfile: str) -> pd.DataFrame:
    df = pd.read_csv(filepath_or_buffer=inputfile, header=0, delimiter=",")
    df = insert_paused_events(df)
    df = convert_to_relative(df)
    return df


def plot(name: str, df: pd.DataFrame):
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
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
    text_values = df.apply(lambda row: row["Node"] if row["End"] ==
                           df[df["Job"] == row["Job"]]["End"].max() else None, axis=1)
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
                size=10,
                symbol="x-thin",
                line=dict(width=2, color='darkblue')
            ),
            name="Deadline"
        )
    )

    fig.update_layout(
        title_text=f"Plot based on {name} (generated at {current_time})", title_x=0.5)
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(type="linear", title_text="Relative Time (seconds)")
    update_fig_xdata(fig, df)
    fig.show()

    # Create the "plots" folder if it doesn't exist
    folder = "plots"
    if not os.path.exists(folder):
        os.makedirs(folder)

    output = f'{folder}/{current_time}_gantt_{name}.png'
    fig.write_image(output, width=1440, height=800, scale=2)


def report_metrics(df: pd.DataFrame, precision=3):
    job_df = df.groupby('ID').agg(
        Name=('Job', lambda x: x.iloc[0].rsplit('-', 1)[0]),  # Extracting Job name without index
        Job_Start=('Start', 'min'),
        Job_End=('End', 'max'),
        Deadline=('Deadline', 'min')
    )

    job_df['Resp_Time'] = job_df['Job_End'] - job_df['Job_Start']
    job_df['Lateness'] = job_df['Job_End'] - job_df['Deadline']
    job_df['Tardiness'] = job_df['Lateness'].clip(lower=0)
    job_df['DDL_Missed'] = (job_df['Lateness'] > 0).astype(int)

    print(job_df)
    print("Total Deadline Misses:", job_df['DDL_Missed'].sum())
    print(f"Max Resp Time: {round(job_df['Resp_Time'].max(), precision)}s")
    print(f"Max Lateness: {round(job_df['Lateness'].max(), precision)}s")
    print(f"Max Tardiness: {round(job_df['Tardiness'].max(), precision)}s")
    print(f"Avg Resp Time: {round(job_df['Resp_Time'].mean(), precision)}s")
    print(f"Avg Tardiness: {round(job_df['Tardiness'].mean(), precision)}s")
    print(f"Avg Lateness: {round(job_df['Lateness'].mean(), precision)}s")


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
    df = read_data(inputfile)
    plot(inputfile.removesuffix(".csv"), df)
    report_metrics(df)


if __name__ == "__main__":
    main(sys.argv[1:])
