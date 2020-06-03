import os
import sys
from random import shuffle
import pandas as pd

import matplotlib

# Is it an interactive plot.
SHOW_PLOT = '--show' in sys.argv

if not SHOW_PLOT:
    # Turn off interactive display.
    matplotlib.use('Agg')


import matplotlib.pyplot as plt


def join(*args):
    return os.path.abspath(os.path.join(*args))


DATA_DIR = join(os.path.dirname(__file__), "data")


def randomize_and_count(data, niter=10, percent=10):
    # Turn the percent into fraction.
    frac = float(percent / 100.0)

    # The selection size.
    sample_size = int(len(data) * frac)

    counts = []

    # For performance reasons we moved the shuffle out
    for n in range(niter):
        shuffle(data)
        subset = data[n:n+sample_size]
        counts.append(len(set(subset)))

    mean_count = 0 if not len(counts) else sum(counts) / len(counts)

    return mean_count


def generate_plot(files, niter=10, outplot=None, show=False, outfile=None):

    # Percents of the data to compute the counts over
    percents = list(range(5, 100, 10))

    plt.figure(figsize=(12, 8))

    outstream = sys.stdout if not outfile else open(outfile, 'w')
    header = ','.join(['filename'] + [str(p) for p in percents])
    outstream.write(header + '\n')

    for fname in files:
        df = pd.read_csv(fname, sep='\t', header=0)
        column = df["taxID"].tolist()

        x = percents
        y = [randomize_and_count(data=column, niter=niter, percent=p) for p in percents]
        label = os.path.basename(fname)
        if outstream:
            row = ','.join([os.path.basename(fname)] + [str(p) for p in y])
            outstream.write(row + '\n')

        plt.plot(x, y, 'o-', label=label)

    plt.suptitle(f"Rarefaction curve with: niter={niter}, nsamples={len(files)}")
    plt.ylabel("Number of unique species ")
    plt.xlabel("Percentage of data sampled")
    plt.ylim(ymin=0)

    plt.legend()

    plt.savefig(outplot)

    if show:
        plt.show()

    return (x, y)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                        help='a file list')

    parser.add_argument('--niter', dest='niter',
                        help="How many times to reshuffle and take subset.",
                        type=int, default=200)

    parser.add_argument('--plot', dest='plot', default="rarefaction.png", type=str,
                        help="The name of the plot file.")

    parser.add_argument('--outdir', dest='outdir', type=str,
                        help="Directory to store plot and csv file.")

    parser.add_argument('--show', dest='show', default=False, action="store_true",
                        help="Show the plot in in a GUI window.")

    if len(sys.argv) == 1:
        sys.argv.extend([join(DATA_DIR, "WI-28.rep"), join(DATA_DIR, "WI-28.rep"), '--show', '--niter=100'])

    args = parser.parse_args()

    if args.outdir:
        outfile = os.path.join(args.outdir, 'rarefaction.csv')
        outplot = os.path.join(args.outdir, args.plot)
    else:
        outfile, outplot = None, args.plot

    generate_plot(files=args.files, show=args.show,
                  outplot=outplot, niter=args.niter,
                  outfile=outfile)


if __name__ == '__main__':
    main()