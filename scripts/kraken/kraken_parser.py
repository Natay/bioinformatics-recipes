"""
Parses and combines Kraken output files.
Takes as the input a file that contains filepaths
to kraken report files.
"""
import os
import sys

import pandas


def parse(path, column=0, rank='S'):
    """
    Parses a kraken output into a Pandas dataframe.

    Since the dataframes are merged later, the column names need to be changed to reflect the sample file name.
    """

    # Keep only file name component of the path.
    fname = os.path.split(path)[1]

    # Drop all extension from filename.
    fname = fname.split(".", 1)[0]

    # The new name of the percent column.
    col_0 = f'{fname}_percent'

    # The new name of the clade count column.
    col_1 = f'{fname}_clade_count'

    # The new name of the rank count column.
    col_2 = f'{fname}_count'

    # The order of columns in the kraken report file.
    names = [col_0, col_1, col_2, 'rank', 'tax_id', 'name']

    # Read the report file into a dataframe.
    store = pandas.read_csv(path, sep="\t", names=names)

    # Strip the whitespace from the name column.
    store.name = store.name.str.strip()

    # Index filter for the species ranks.
    species_idx = store['rank'] == rank

    # Index filter for unclassified rows.
    unclass_idx = store['name'] == 'unclassified'

    # Combine the to indices with "or".
    index = species_idx | unclass_idx

    # Slice the dataframe.
    store = store[index]

    # Rearrange columns for simpler format.
    cols = store.columns

    # Name, tax id, value
    cols = ["name", "rank", "tax_id", cols[column]]

    # Slice the dataframe to contain only the columns of interest.
    store = store[cols]

    # Return new dataframe.
    return store


def merge_frames(frames):
    """
    Merges and sorts a list of dataframes.

    After merging sorts rows in descending order on mean
    values across all frames but will keep the unclassified entries as first.
    """
    # Take the first element of the collection.
    out = frames[0]

    # Merge all others into the first.
    for other in frames[1:]:
        out = out.merge(other, on=["name", "rank", "tax_id"])

    # The columns on which the total should be computed.
    valid_cols = out.columns[3:]

    # The average by row on the valid columns.
    total = out[valid_cols].mean(axis=1)

    # We always want the unclassified to end up first in the table
    # so we will pretend that first entry is the highest.
    total[0] = max(total) + 1

    # Assign the totals
    out['total'] = total

    # Sort the dataframe by totals.
    out = out.sort_values(by=['total'], ascending=False)

    # Drop the total column.
    del out['total']

    # Print output to standard out
    out.to_csv(sys.stdout, index=False)


__PROG__ =  os.path.split(__file__)[1]
USAGE = f"""

Combine multiple kraken style reports into a single file

    python {__PROG__} *.reports.txt

Produces a single CSV file that contains the merged and combined reports.
"""


def main():
    """
    Main entry to command line functionality.
    """
    import argparse
    parser = argparse.ArgumentParser(usage=USAGE)

    if len(sys.argv) < 2:
        sys.argv.append("-h")

    parser.add_argument("--rank", action="store", default="S")
    parser.add_argument("--column", type=int, default=0)
    parser.add_argument("paths", nargs='+')
    args = parser.parse_args()

    paths = args.paths
    rank = args.rank
    column = args.column

    collect = [parse(path, column=column, rank=rank) for path in paths]

    merge_frames(collect)


if __name__ == '__main__':
    main()