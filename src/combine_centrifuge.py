

import csv
import os
import sys

import pandas as pd
from . import utils

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')



def map_name(name, files, delim='\t'):
    "Maps a column name to an index after checking if it is the same across files."
    idx_set = set()

    for fname in files:
        stream = csv.reader(open(fname, 'rt'), delimiter=delim)
        header = next(stream)
        idx_set.add(header.index(name))

    if len(idx_set) > 1:
        msg = f"The column name ({name}) does not have the same index across files."
        raise Exception(msg)

    return list(idx_set)[0]


def colnames(fnames):
    names = [os.path.basename(fname) for fname in fnames]
    names = [os.path.splitext(fname)[0] for fname in names]
    return names


def print_kreport(df, outdir=None, rank='', colidx=0, summary=False):

    rankmap = dict(S="Species", G="Genus", F='Family', C='Class', D='Domain')
    ranks = rank or 'SGFCD'
    colmap = {0: "percent", 1: "numreads", 2: "uniquereads"}
    pd.set_option('display.expand_frame_repr', False)

    def write_to(dataframe, fname):
        path = sys.stdout if not outdir else os.path.join(str(outdir), fname)
        dataframe.to_csv(index=False, path_or_buf=path)
        return

    # Print a summary of all taxonomic levels.
    if summary:
        write_to(dataframe=df, fname=f'summary_{colmap.get(colidx, "")}_classification.csv')
        return

    # Print a summary file for each taxonomic level.
    for rank in ranks:
        subset = utils.get_subset(df, rank)
        label = rankmap.get(rank, 'Unknown')
        write_to(dataframe=subset, fname=f'{label.lower()}_{colmap.get(colidx, "")}_classification.csv')


def generate_ktable(files, colidx=0):
    "Generate table compatible with k-report"

    storage, allkeys = [], {}

    for fname in files:
        stream = csv.reader(open(fname, 'rt'), delimiter="\t")
        # Keep only known rank codes
        stream = filter(lambda x: x[3] != '-', stream)
        # Collect all data into a dictionary keyed by keyID
        data = dict()
        for row in stream:
            data[row[4].strip()] = [elem.strip() for elem in row]
        storage.append(data)
        # Collect all keys across all data.
        allkeys.update(data)

    table = []
    for key, fields in allkeys.items():
        collect = list(reversed(fields[3:]))

        for data in storage:
            value = data.get(key, [0] * (colidx+1))[colidx]
            value = float(value)
            collect.append(value)
        table.append(collect)

    return table


def generate_table(files, keyidx, has_header=True):

    name_dict = dict()

    for fname in files:
        stream = csv.reader(open(fname, 'rt'), delimiter="\t")
        if has_header:
            next(stream)
        for row in stream:
            key = ','.join(row[0:3])
            colidx = colnames(files).index(colnames([fname])[0])
            value = float(row[keyidx])
            name_dict.setdefault(key, []).append((colidx, value))

    table = []
    for name, value in name_dict.items():
        swap = [float(0)] * len(colnames(files))
        for col, val in value:
            swap[col] = val
        table.append(name.split(',') + swap)

    return table


def tabulate(files, keyidx=4, cutoff=0, has_header=True, is_kreport=False):
    """
    Summarize result found in data_dir by grouping them.
    """

    # The final table that can be printed and further analyzed
    if is_kreport:
        table = generate_ktable(files=files, colidx=keyidx)
    else:
        table = generate_table(files=files, keyidx=keyidx ,has_header=has_header)

    # Filter table by cutoffs
    cond1 = lambda row: sum(row[3:]) > cutoff
    table = list(filter(cond1, table))

    # Sort by reverse of the abundance.
    compare = lambda row: (row[2], sum(row[3:]))
    table = sorted(table, key=compare, reverse=True)

    # Make a panda dataframe
    columns = ["name", "taxid", "rank"] + colnames(files)
    df = pd.DataFrame(table, columns=columns)

    # Attempt to fill in common names at species level.
    #fname = "/export/refs/alias/fishalias.txt"
    #df = utils.alias(df=df, fname=fname, key1='name', key2='sciname', name='name')

    return df


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                        help='a file list')

    parser.add_argument('--column', dest='column', type=str,
                        help="Name of column to combine across all files")

    parser.add_argument('--idx', dest='idx', type=int,
                        help="idx of column to combine across all files for kreports.",
                        default=0)

    parser.add_argument('--cutoff', dest='cutoff', default=0.0,
                        help="The sum of rows have to be larger than the cutoff to be registered default=%(default)s.",
                        type=float)

    parser.add_argument('--is_kreport', default=False, action='store_true',
                        help="The files to be analyzed are centrifuge kraken reports.")

    parser.add_argument('--outdir', dest='outdir', type=str,
                        help="Directory name to write data out to." )

    parser.add_argument('--summary', dest='summary', action='store_true', default=False,
                        help="Generates a summary file with all of the taxonomic levels.")

    if len(sys.argv) == 1:
        join = lambda path: os.path.join(DATA_DIR, path)
        kreport_sample = [join('centrifuge-1.txt'), join('centrifuge-2.txt'), '--is_kreport']
        tsv_sample = [join('sample-1.tsv'), join('sample-2.tsv'), '--column=numReads', '--cutoff=0.0' ]

        sys.argv.extend(kreport_sample)

    args = parser.parse_args()

    if args.is_kreport:
        # Special case to handle kraken reports
        df = tabulate(files=args.files, keyidx=args.idx, cutoff=args.cutoff, is_kreport=True)
        print_kreport(df, outdir=args.outdir, colidx=args.idx, summary=args.summary)
    else:
        assert args.column, "--column or --idx argument required."
        # Map the column name to an index
        colidx = map_name(name=args.column, files=args.files)
        df = tabulate(files=args.files, cutoff=args.cutoff, keyidx=colidx)
        df.to_csv(index=False, path_or_buf=sys.stdout)




if __name__ == '__main__':
    main()
