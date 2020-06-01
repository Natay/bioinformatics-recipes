"""

This program is used to get taxonomy lineage for an accession from 'taxon_db' database.

"""

import sys, os
import sqlite3
from argparse import ArgumentParser


def strip(s):
    return s.strip()


def get_conn(dbname):
    conn = sqlite3.connect(dbname)
    return conn


def get_cursor(dbname):
    conn = get_conn(dbname)
    curs = conn.cursor()
    return curs


def get_taxa(fname):
    fname = args.accessions
    outfile = args.outfile
    dbpath = args.dbpath

    outfile = open(outfile, "w")

    curs = get_cursor(dbpath)

    data = dict()
    stream = open(fname, "r")
    accessions = stream.readlines()
    accessions = list(map(strip, accessions))

    for acc in accessions:

        curs.execute('SELECT lineage FROM acc2taxon WHERE accession=?', (acc,))
        res = curs.fetchone()
        if res is not None:
            taxon = res[0]
            data[acc] = taxon
        else:
            print("taxonomy id {acc} not found".format(acc=acc))

    header = "\t".join(["Feature ID", "Taxon"])
    outfile.write(header)
    outfile.write("\n")
    # print(header)
    for k, v in data.items():
        out = "\t".join([k, v])
        outfile.write(out)
        outfile.write("\n")
        # print(out)

    outfile.close()


if __name__ == "__main__":
    # print(dbname)

    parser = ArgumentParser()

    parser.add_argument('--dbpath', dest='dbpath',
                        help="Specify the full path of the lineage database destination.")
    parser.add_argument('--accessions', dest='accessions',
                        help="Text file with accessions")
    parser.add_argument('--outfile', dest='outfile',
                        help="Specify the output file.")
    args = parser.parse_args()

    # fname = sys.argv[1]
    get_taxa(args)
