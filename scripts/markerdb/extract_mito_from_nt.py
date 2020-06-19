import csv, sys, re

#
# This script extracts fish mitochondrial marker sequence accessions
# by parsing the header from sequenes in nt.
#

csv.field_size_limit(sys.maxsize)

ribosomal_12S = ["12S", "12SrRNA", "rnr1 rRNA", "rRNA small subunit", "rrnS rRNA",
                 "s-rRNA", "small subunit rRNA", "small rRNA subunit RNA"]

ribosomal_16S = ["16S", "l-RNA", "l-rRNA", "large rRNA subunit RNA",
                 "large subunit rRNA", "LSU rRNA", "mtLSU rRNA", "rnl rRNA", "rnr2 rRNA",
                 "rRNA large subunit", "rrnL rRNA"]

cyctochromB = ["cytb", "cytochrome b", "cyt b", "cyto B"]

COI = ["COI", "CO1", "COX1", "COXI", "MT-CO1", "CO 1",
       "CO I", "COX I", "COX 1", "MT CO1", "cytochrome c oxidase I",
       "cytochrome c oxidase 1", "cytochrome oxidase I", "cytochrome oxidase 1",
       "Cytochrome c oxidase subunit I", "Cytochrome c oxidase subunit 1",
       "Cytochrome oxidase subunit I", "Cytochrome oxidase subunit 1",
       "cytochrome c oxidase I"]

COII = ["COII", "CO2", "COX2", "COXII", "MT-CO2", "CO 2",
        "CO II", "COX II", "COX 2", "MT CO2", "cytochrome c oxidase II",
        "cytochrome c oxidase 2", "cytochrome oxidase II", "cytochrome oxidase 2",
        "Cytochrome c oxidase subunit II", "Cytochrome c oxidase subunit 2",
        "Cytochrome oxidase subunit II", "Cytochrome oxidase subunit 2",
        "cytochrome c oxidase II"]

COIII = ["COIII", "CO3", "COX3", "COXIII", "MT-CO3", "CO 3",
         "CO III", "COX IIII", "COX 3", "MT CO3", "cytochrome c oxidase III",
         "cytochrome c oxidase 3", "cytochrome oxidase III", "cytochrome oxidase 3",
         "Cytochrome c oxidase subunit III", "Cytochrome c oxidase subunit 3",
         "Cytochrome oxidase subunit III", "Cytochrome oxidase subunit 3",
         "cytochrome c oxidase III"]

genome = ["complete genome"]

MARKERS = genome + ribosomal_12S + ribosomal_16S + cyctochromB + COI + COII + COIII

REGION = ["mitochondri"]

region_map = {"mitochondri": "Mitochondria"}

marker_map = {"coi": "COI",
              "co1": "COI",
              "coxi": "COI",
              "cox1": "COI",
              "mt-co1": "COI",
              "co 1": "COI",
              "co i": "COI",
              "cox i": "COI",
              "cox 1": "COI",
              "mt co1": "COI",

              "coii": "COII",
              "co2": "COII",
              "coxii": "COII",
              "cox2": "COII",
              "mt-co2": "COII",
              "co 2": "COII",
              "co ii": "COII",
              "cox ii": "COII",
              "cox 2": "COII",
              "mt co2": "COII",

              "coiii": "COIII",
              "co3": "COIII",
              "coxiii": "COIII",
              "cox3": "COIII",
              "mt-co3": "COIII",
              "co 3": "COIII",
              "co iii": "COIII",
              "cox iii": "COIII",
              "cox 3": "COIII",
              "mt co3": "COIII",

              "cytochrome c oxidase subunit i": "COI",
              "cytochrome oxidase subunit i": "COI",
              "cytochrome oxidase subunit 1": "COI",
              "cytochrome c oxidase subunit 1": "COI",
              "cytochrome c oxidase i": "COI",
              "cytochrome c oxidase 1": "COI",
              "cytochrome oxidase i": "COI",
              "cytochrome oxidase 1": "COI",

              "cytochrome c oxidase subunit ii": "COII",
              "cytochrome oxidase subunit ii": "COII",
              "cytochrome oxidase subunit 2": "COII",
              "cytochrome c oxidase subunit 2": "COII",
              "cytochrome c oxidase ii": "COII",
              "cytochrome c oxidase 2": "COII",
              "cytochrome oxidase ii": "COII",
              "cytochrome oxidase 2": "COII",

              "cytochrome c oxidase subunit iii": "COIII",
              "cytochrome oxidase subunit iii": "COIII",
              "cytochrome oxidase subunit 3": "COIII",
              "cytochrome c oxidase subunit 3": "COIII",
              "cytochrome c oxidase iii": "COIII",
              "cytochrome c oxidase 3": "COIII",
              "cytochrome oxidase iii": "COIII",
              "cytochrome oxidase 3": "COIII",

              "cytochrome b": "Cyt b",
              "cyt b": "Cyt b",
              "cyto b": "Cyt b",
              "cytb": "Cyt b",

              "12s": "12S",
              "12Srrna": "12S",
              "rnr1 rrna": "12S",
              "rrna small subunit": "12S", "small rrna subunit rna": "12S",
              "rrnS rrna": "12S", "s-rrna": "12S", "small subunit rRNA": "12S",

              "16s": "16S", "l-rna": "16S", "large rrna subunit rna": "16S",
              "large subunit rrna": "16S", "lsu rrna": "16S", "mtlsu rrna": "16S",
              "rnl rrna": "16S", "rnr2 rrna": "16S", "rrna large subunit": "16S",
              "rrnl rrna": "16S",

              "complete genome": "complete genome",
              }


def read_taxids(fname):
    store = dict()
    stream = csv.reader(open(fname), delimiter="\t")
    for row in stream:
        name, tid = row[0], row[1]
        store[tid] = name if name else None
    return store


def match_patterns(title, pattern_list, func=lambda x: x.lower()):
    # Find a match in a list of patterns
    # Returns first match found.
    for pattern in pattern_list:
        # Apply extra function to pattern to
        # enhance/relax searches.
        pattern = func(pattern)
        match = re.search(pattern, title)
        if match:
            return match.group(0)
    return


def parse_title(title):
    pattern_func = lambda p: r'\b' + p.lower() + r'\b'

    title = title.lower()

    # Return the first matched marker and region
    marker = match_patterns(title, pattern_list=MARKERS, func=pattern_func)
    region = match_patterns(title, pattern_list=REGION)

    return marker, region


def parse_nt_seq_table(fname, taxids):
    """
    This file 'fname' is produced by blastdbcmd command and has the format
    accession#title#seq_length#taxid#scientific_name#common_name
    """

    header = ["accession", "title", "length", "taxid",
              "scientific_name", "common_name", "marker", "genomic_location", ]
    print("\t".join(header))

    stream = csv.reader(open(fname), delimiter="#")

    for row in stream:
        # title = row[1].lower()
        title = row[1]
        taxid = row[3].strip()

        if taxid not in taxids:
            continue

        if not any(reg in title for reg in REGION):
            continue

        marker, genomic_location = parse_title(title)

        if marker is None or genomic_location is None:
            continue

        if marker in marker_map:
            marker = marker_map[marker]

        if genomic_location in region_map:
            genomic_location = region_map[genomic_location]

        out = "\t".join(row)
        parsed = "\t".join([out, marker, genomic_location])
        print(parsed)

    return


def main():
    # nt_file = "nt_seq.txt"
    # taxid_file = "all_fish_species_tids.txt"

    nt_file = sys.argv[1]
    taxid_file = sys.argv[2]

    taxids = read_taxids(taxid_file)
    parse_nt_seq_table(nt_file, taxids)


if __name__ == "__main__":
    main()
