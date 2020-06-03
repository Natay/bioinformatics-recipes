"""

This program is used to process idx stats files created by samtools idxstats.

"""

import os
import sys

import pandas as pd

pd.set_option('display.expand_frame_repr', False)
pd.options.display.float_format = '{:.1f}'.format


def get_colnames(fnames):
    names = [os.path.basename(fname) for fname in fnames]
    names = [fname.split(".")[0] for fname in names]
    return names


def plot(data, args):
    from src.plotters import plotter

    # Plot a heatmap
    plotter.heatmap(data=data, colidx=2, fname="heatmap.png")


ACCESSION, SIZE, MAPPED, UNMAPPED, SUM = ['accession', 'size', 'mapped', 'unmapped', 'sum']


def tabulate(args):
    """
    Summarize the index stats.
    """

    files = sorted(args.files)
    colnames = [ACCESSION, SIZE, MAPPED, UNMAPPED]
    res = None
    for fname in files:
        df = pd.read_table(fname, header=None)
        df.columns = colnames
        if args.by_percent:
            values = df[MAPPED]
            df[MAPPED] = values / values.sum() * 100

        if res is None:
            res = df[[ACCESSION, SIZE, MAPPED]]
        else:
            df = df[[ACCESSION, MAPPED]]
            res = pd.merge(res, df[[ACCESSION, MAPPED, ]], on=ACCESSION, how='inner')

    # Rename the columns
    fnames = get_colnames(files)

    colnames = [ACCESSION, SIZE] + fnames
    res.columns = colnames

    # Sort table by the sum of columns
    res[SUM] = res[fnames].sum(axis=1)
    res = res.sort_values(by=SUM, ascending=False)
    res = res[res[SUM] > args.cutoff]

    # Drop the sum column
    res = res.drop(SUM, axis=1)

    return res


def main():

    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                        help='a file list')

    parser.add_argument('--cutoff', dest='cutoff', default=0.1,
                        help="The sum of rows have to be larger than the cutoff to be registered default=%(default)s.",
                        type=float)
    parser.add_argument('--by_percent', dest='by_percent', default=False, action="store_true",
                        help="Return the percent mapped reads instead of raw mapped reads.")
    parser.add_argument('--show', dest='show', default=False, action="store_true",
                        help="Show the plot in in a GUI window.")

    if len(sys.argv) == 1:
        sys.argv.extend(['data/idxstats-1.txt', 'data/idxstats-2.txt', '--by_percent'])

    args = parser.parse_args()

    df = tabulate(args)

    # Print the data to screen.
    print(df.to_csv(index=False, float_format='%.1f'))

    plot(df, args=args)


if __name__ == '__main__':
    main()
