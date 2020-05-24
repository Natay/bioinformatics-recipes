import sqlite3
import os, sys
import csv
from itertools import *
from argparse import ArgumentParser

# set tmp directory for sqlite3
os.system('mkdir -p ./tmp')
os.environ["SQLITE_TMPDIR"] = "./tmp"

CHUNK = 100000
LIMIT = 100000
LIMIT = None


def get_conn(dbname):
    conn = sqlite3.connect(dbname)
    return conn


# A function which creates database (even if database is present,
def create_db(dbname):
    if os.path.isfile(dbname):
        os.remove(dbname)
    conn = get_conn(dbname)
    curs = conn.cursor()

    # create acc2taxon table
    curs.execute('''CREATE TABLE acc2taxon
               (accession, lineage)''')

    # Save the table within the database (Save changes)
    conn.commit()


def create_acc2taxon(dbname, fname):
    conn = get_conn(dbname)
    curs = conn.cursor()

    # stream = csv.DictReader(open(fname), delimiter='\t')
    stream = csv.reader(open(fname), delimiter='\t')
    stream = islice(stream, LIMIT)
    data = []
    for index, row in enumerate(stream):

        # data.append((row['Feature ID'], row['Taxon']))
        # removing the version info from accession.
        accession = row[0].split(".")[0]
        lineage = row[1]
        data.append((accession, lineage))

        remain = index % CHUNK

        if remain == 0 and data:
            curs.executemany('INSERT INTO acc2taxon VALUES (?,?)', data)
            conn.commit()
            print("commit")
            print(index)

            data = []
            # print (row['GeneID'])
    print("Table creation Done")

    sql_commands = [
        'CREATE INDEX acc2taxon_accession ON acc2taxon(accession)',

    ]
    for sql in sql_commands:
        curs.execute(sql)

    print("Indexing done")


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('--dbpath', dest='dbpath', required=True,
                        help="Specify the full path of the database destination.")
    parser.add_argument('--infile', dest='infile', required=True,
                        help="Specify the input file required to create the database.")

    args = parser.parse_args()
    dbpath = args.dbpath
    infile = args.infile

    # dbname = 'taxon_db'
    create_db(dbpath)
    # print_db(dbname)
    create_acc2taxon(dbpath, infile)
