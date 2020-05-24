"""
Plotter for different types of data
"""
import sys
import os
import matplotlib


# Pop a window
SHOW_PLOT = '--show' in sys.argv

if not SHOW_PLOT:
    # Turn off interactive display.
    matplotlib.use('Agg')

import matplotlib.pylab as plt
import numpy as np
import pandas as pd


def join(*args):
    return os.path.abspath(os.path.join(*args))


DATA_DIR = join(os.path.dirname(__file__), "data")


def plot(df, name, args):

    # Plot a heatmap
    if args.type == "heat_map":
        heatmap(data=df, fname=name)


# colidx is the column where the data starts.
# labidx is the column index for the labels
def heatmap(data, colidx=3, labidx=0, fname='heatmap.png'):
    # Based on: https://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor

    plt.rcParams.update({'figure.autolayout': True})

    if data.empty:
        print("Can not plot empty data set.")
        return

    df = pd.DataFrame()

    names = list(data.columns)
    label = names[labidx]
    names = [label] + names[colidx:]

    # A simpler dataframe with only labels and values
    for name in names:
        df[name] = data[name]

    df = df.set_index(label)

    # df = (df - df.mean()) / (df.max() - df.min())

    # Transform the scale to log.
    df = np.log(df + 1)

    # The size of the data frame.
    rnum, cnum = df.shape

    # The size of the plot will grow with the row numbers.
    hsize = 4 + cnum/3
    vsize = 4 + rnum/10
    fig, ax = plt.subplots(figsize=(hsize, vsize))

    heatmap = ax.pcolor(df, cmap=plt.cm.Blues, alpha=0.8)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(rnum) + 0.5, minor=False)
    ax.set_xticks(np.arange(cnum) + 0.5, minor=False)

    # ax.invert_yaxis()
    ax.xaxis.tick_top()

    # Get the vertical labels.
    labels = list(df.columns)

    # Simplify label names.
    #labels = [label.split("_")[0] for label in labels]
    ax.set_xticklabels(labels, minor=False)
    ax.set_yticklabels(df.index, minor=False)

    ax.grid(False)

    # Turn off all the ticks
    ax = plt.gca()

    for t in ax.xaxis.get_major_ticks():
        t.tick1line.set_visible = False
        t.tick2line.set_visible = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1line.set_visible = False
        t.tick2line.set_visible = False

    plt.xticks(rotation=90)
    plt.savefig(f'{fname}.pdf')

    if SHOW_PLOT:
        # Pop a window in non-offline mode.
        plt.show()


# colidx is the column where the data starts.
def horizontal_bars(data, colidx=3, labidx=0, fname='plot.png'):
    # Set plotting parameters.
    plt.rcParams.update({'figure.autolayout': True})
    plt.figure(figsize=(20, 10), dpi=100)

    # How rows and columns in the dataframe.
    rnum, cnum = data.shape

    # The tick positions.
    ypos = np.arange(rnum)

    # The total width for bars.
    space = 0.3

    # How many bars will there be.
    n = cnum - 3

    # Width of one bar.
    width = (1 - space) / n

    # Shift the bar to center
    shift = (n - 1) * width / 2

    # Generate a barplot for each column past the third.
    for i in range(n):
        label = data.columns[colidx + i]
        values = data[label]
        npos = ypos + i * width - shift
        plt.barh(npos, values, width, label=label)

    # Finish up the plot.
    plt.legend()
    # The label column.
    labels = data[data.columns[labidx]]
    plt.yticks(range(len(labels)), labels)
    plt.title(f'Read Classification')
    plt.xlabel("Percent reads")
    plt.savefig(f'{fname}')

    if SHOW_PLOT:
        # Pop a window in non-offline mode.
        plt.show()


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                        help='Files to be plotted')

    parser.add_argument('--type', dest='type', default='hbar',
                        help="Plot type", type=str)

    parser.add_argument('--output', dest='output',
                        help="Name of output plot file", type=str)

    args = parser.parse_args()

    for fname in args.files:
        # Plot each csv file.

        output, ext = os.path.splitext(os.path.basename(fname))
        output = args.output or os.path.join(os.path.dirname(fname), f'{output}_{args.type}.png')

        df = pd.read_csv(filepath_or_buffer=fname, header=0)

        plot(df=df, name=output, args=args)



if __name__ == '__main__':
    main()
