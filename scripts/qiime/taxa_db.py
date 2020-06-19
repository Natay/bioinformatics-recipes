import sqlite3
import os, sys
import csv
from itertools import *
from argparse import ArgumentParser

# set tmp directory for sqlite3
os.system('mkdir -p ./tmp')
os.environ["SQLITE_TMPDIR"] = "./tmp"

LIMIT = None
CHUNK = 100000

cols = "taxid taxname species genus family order class phylum kingdom superkingdom"
fields = cols.split()


def get_conn(dbname):
    conn = sqlite3.connect(dbname)
    return conn


# A function which creates database
def create_db(dbname):
    if os.path.isfile(dbname):
        os.remove(dbname)
    conn = get_conn(dbname)
    curs = conn.cursor()

    # create taxa table
    curs.execute('''CREATE TABLE taxa
                         (taxid INTEGER NOT NULL PRIMARY KEY , lineage)''')

    # curs.execute('''CREATE TABLE accession (acc PRIMARY KEY , acc_version, FOREIGN KEY (taxid)  REFERENCES taxa(
    # taxid))''')


    curs.execute('''CREATE TABLE accession
                    (acc PRIMARY KEY , acc_version, taxid INTEGER REFERENCES taxa(taxid))''')

    # Save the table within the database (Save changes)
    conn.commit()


def create_accession_table(dbname, fname):
    conn = get_conn(dbname)
    curs = conn.cursor()

    data = []

    stream = csv.reader(open(fname), delimiter="\t")

    # stream = islice(stream, LIMIT)

    def insert_vals(data):
        curs.executemany('INSERT INTO accession VALUES (?,?,?)', data)
        conn.commit()
        print("commit")

    for index, row in enumerate(stream):
        row = [x.strip() for x in row]
        acc = row[0]
        acc_version = row[1]
        taxid = row[2]

        data.append((acc, acc_version, taxid))

        if len(data) == CHUNK:
            insert_vals(data)
            data = []

    # For the remaining
    if data:
        insert_vals(data)

    print("Table creation Done")

    # Create index

    sql_commands = [
        'CREATE INDEX accession_acc ON accession(acc)',
        # 'CREATE INDEX accession_acc_version ON accession(acc_version)',
        # 'CREATE INDEX accession_taxid ON accession(taxid)',

    ]

    for sql in sql_commands:
        curs.execute(sql)

    print("Indexing done")

    return


def create_taxa_table(dbname, fname):
    # Read lineage dmp file.
    lineage_map = read_ranked_lineage(fname)

    conn = get_conn(dbname)
    curs = conn.cursor()

    data = []

    def insert(data):
        curs.executemany('INSERT INTO taxa VALUES (?,?)', data)
        conn.commit()
        print("commit")
        return

    for taxid, lineage in lineage_map.items():
        data.append((taxid, lineage))

        if len(data) == CHUNK:
            insert(data)
            data = []

    # For the remaining to be inserted.
    if data:
        insert(data)

    print("Table creation Done")

    # Create index

    sql_commands = [
        'CREATE INDEX taxa_taxid ON taxa(taxid)',
        'CREATE INDEX taxa_lineage ON taxa(lineage)',

    ]

    for sql in sql_commands:
        curs.execute(sql)

    print("Indexing done")

    return


def read_ranked_lineage(fname):
    ranks = dict()
    stream = csv.reader(open(fname), delimiter="|")
    # stream = islice(stream, LIMIT)

    for row in stream:
        # remove empty string at the end.
        row.pop()

        row = [x.strip() for x in row]
        taxid = row[0]

        # Make a ranked dictionary.
        d = dict(zip(fields, row))
        taxon = get_ranks(d)

        # Remove empty ranks  eg:Eukaryota;Chordata;;;;;Actinopteri
        # Include only non-empty ranks eg: Eukaryota;Chordata;Actinopteri
        taxon = list(filter(None, taxon.split(";")))
        taxon = ";".join(taxon)
        ranks[taxid] = taxon

    return ranks


def get_ranks(ranks):
    """
    returns superkingdon, phylum, class, order, family, genus, species
    """
    out = ";".join([ranks['superkingdom'], ranks['phylum'],
                    ranks['class'], ranks['order'], ranks['family'],
                    ranks['genus'], ranks['taxname']])
    return out


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('--dbpath', dest='dbpath', required=True,
                        help="Specify the full path of the database destination.")
    parser.add_argument('--accession', dest='acc', required=True,
                        help="Specify the path to NCBI nucl_gb.accession2taxid file.")
    parser.add_argument('--lineage', dest='lineage', required=True,
                        help="Specify the path to NCBI rankedlineage.dmp file.")

    args = parser.parse_args()
    dbpath = args.dbpath
    accessions = args.acc
    lineages = args.lineage

    # dbname = 'taxon_db'
    create_db(dbpath)
    # print_db(dbname)
    create_accession_table(dbpath, accessions)
    create_taxa_table(dbpath, lineages)