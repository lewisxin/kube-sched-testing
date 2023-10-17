import plotly.express as px
import pandas as pd
import os
import sys
import getopt
from datetime import datetime


def plot(inputfile):
    df = pd.read_csv(filepath_or_buffer=inputfile, header=0,
                     delimiter=",").sort_values(by=["Job", "Status"])
    colors = {
        "In Queue": "#29b6f6",
        "Running": "#66bb6a",
        "Overdue": "#f44336"
    }
    fig = px.timeline(df, x_start="Start", x_end="End", y="Job",
                      color="Status", color_discrete_map=colors, text="Node")
    fig.update_yaxes(autorange="reversed")
    fig.show()

    # Create the "plots" folder if it doesn't exist
    folder = "plots"
    if not os.path.exists(folder):
        os.makedirs(folder)
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    name = inputfile.removesuffix(".csv")
    output = f'{folder}/{current_time}_gantt_{name}.png'
    fig.write_image(output)


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
