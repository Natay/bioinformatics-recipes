import sqlite3
import csv, os, sys
from itertools import *

# LIMIT = 1000

STATUS_CODE = dict(N="native", NN="non-native", SOC="species of concern",
                   E="endemic", I="introduced", R="reported", W="watchlist",
                   X="extinct")

REGION_CODE = {
    "North America": 2,
    "Great Lakes Basin": 3,
    "Planet Earth": 4,
}


def get_conn(dbname):
    """
    Creates database of name dbname
    """
    conn = ""
    try:
        conn = sqlite3.connect(dbname)
    except sqlite3.OperationalError:
        print(f"Database {dbname} not found.")

    return conn


def create_db(dbname):
    if os.path.isfile(dbname):
        os.remove(dbname)

    conn = get_conn(dbname)
    curs = conn.cursor()

    # create fish occurrence table
    #

    curs.execute('''CREATE TABLE species_geography
                    (scientific_name, common_name, region,status)''')

    curs.execute('''CREATE TABLE sequence
                    (accession, length, seq_marker,title, genomic_location, taxid)''')

    curs.execute('''CREATE TABLE organism
                    (taxid,scientific_name,common_name)''')

    # Save table within database (Save changes)
    conn.commit()
    # conn.close()
    # curs.close()


def parse_status_file(fname):
    data = []

    stream = csv.DictReader(open(fname), delimiter="\t")

    for row in stream:
        genus = row['Genus']
        species = row['Species']
        subspecies = row['Subspecies']
        common_name = row['Common name']
        status = row['Status']
        region = row['Region']

        d = {'genus': genus, 'species': species, 'subspecies': subspecies,
             'common_name': common_name, 'status': status, 'region': region}

        data.append(d)

    return data


def get_status(term):
    return STATUS_CODE.get(term, term)


def get_region_code(region):
    return REGION_CODE.get(region, 0)


def make_rows(terms, common_name, scientific_name, region):
    data = []
    for term in terms:
        status = get_status(term)
        # region_code = get_region_code(region)

        data.append((scientific_name, common_name, region, status,))
    return data


def load_species_geography(dbname, data):
    conn = get_conn(dbname)
    curs = conn.cursor()

    for index, row in enumerate(data):
        genus = row['genus']
        species = row['species']
        subspecies = row['subspecies']
        common_name = row['common_name']
        region = row['region']
        scientific_name = " ".join([genus, species]) if subspecies == "" else  " ".join([genus, species, subspecies])
        terms = row['status'].split("/")

        # parse status column
        # if a species has multiple status (separated by '/'), then add that many rows into the table.
        #
        if len(terms) == 1:

            term = row['status']

            status_code = term
            status = get_status(status_code)
            # region_code = get_region_code(region)
            vals = (scientific_name, common_name, region, status,)
            curs.execute('INSERT INTO species_geography VALUES (?,?,?,?)', vals)
        else:
            # terms = list(map(get_status, terms))
            # can we use partial here?
            vals = make_rows(terms=terms, common_name=common_name, scientific_name=scientific_name, region=region)
            curs.executemany('INSERT INTO species_geography VALUES (?,?,?,?)', vals)

        conn.commit()

    print("Species grography table creation Done")

    # indexing

    sql_commands = [
        'CREATE INDEX species_geography_scientific_name ON species_geography(scientific_name )',
        'CREATE INDEX species_geography_common_name ON species_geography(common_name )',
        'CREATE INDEX species_geography_region ON species_geography(region )',
        'CREATE INDEX species_geography_status ON species_geography(status )',

    ]

    for sql in sql_commands:
        curs.execute(sql)

    print("Indexing done")
    curs.close()
    conn.close()
    return


def load_sequence(dbname, fname):
    conn = get_conn(dbname)
    curs = conn.cursor()

    stream = csv.DictReader(open(fname), delimiter="\t")

    for row in stream:
        acc = row['accession']
        title = row['title']
        slen = row['length']
        taxid = row['taxid']
        sc_name = row['scientific_name']
        com_name = row['common_name']
        marker = row['marker']
        location = row['genomic_location']

        data = (acc, slen, marker, title, location, taxid)

        species_info = (taxid, sc_name, com_name)

        curs.execute('INSERT INTO sequence VALUES (?,?,?,?,?,?)', data)
        curs.execute('INSERT INTO organism VALUES (?,?,?)', species_info)

    conn.commit()
    print(" Sequence table creation done")
    print(" Organism table creation done")

    # Indexing

    sql_commands = [
        'CREATE INDEX sequence_taxid ON sequence(taxid)',
        'CREATE INDEX sequence_accession ON sequence(accession)',
        'CREATE INDEX sequence_seq_marker ON sequence(seq_marker)',
        'CREATE INDEX sequence_genomic_location ON sequence(genomic_location)',
        'CREATE INDEX organism_taxid ON organism(taxid)',
        'CREATE INDEX organism_scientific_name ON organism(scientific_name)',
        'CREATE INDEX organism_common_name ON organism(common_name)',
    ]

    for sql in sql_commands:
        curs.execute(sql)

    print("Indexing done")
    curs.close()
    conn.close()
    return


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='SQL database name', required=True)
    parser.add_argument('--sequence_table',
                        help="""Tab delimiter file. Columns include accession,seq_title,seq_length,
                        taxid,scientific_name,common_name, seq_marker, genomic_location""", required=True)
    parser.add_argument('--status_table',
                        help="""Tab delimited file specifying fish status(endemic,native etc) in different regions.""",
                        required=True)
    args = parser.parse_args()

    dbname = args.database
    status_file = args.status_table
    mito_file = args.sequence_table

    # category_file = "fish_categories.txt"
    # mito_file = "all_fish_mito_complete_genome.txt"
    # dbname = sys.argv[1]
    create_db(dbname)

    status_data = parse_status_file(status_file)
    load_species_geography(dbname=dbname, data=status_data)
    load_sequence(dbname=dbname, fname=mito_file)
    return


if __name__ == "__main__":
    main()
