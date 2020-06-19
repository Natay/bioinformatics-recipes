# This script parses a taxon id and extracts all species/sub-species under it.
# Output(s)
# 1. Species name and taxids are written to standard out.
# 2. Original taxonkit output is written to taxonkit_results.txt
# Usage: python get_species_taxids.py --taxids fish_taxids.txt >fish_species_tids.txt
# Requirement - Taxonkit must be installed


import sys, csv
import subprocess
import argparse


def get_lower_taxa(taxid):
    """
    Runs taxonkit list command and returns its  output
    """
    cmd = f"taxonkit list --show-rank --show-name --indent \"    \" --ids {taxid}"
    result = subprocess.run([cmd], stdout=subprocess.PIPE, shell=True)
    return result.stdout.decode('utf-8')


def parse_taxa(taxa_line):
    # print(taxa_line)
    taxa_line = taxa_line.lstrip()
    arr = taxa_line.split(" ")
    tid, taxa, name = arr[0], arr[1], " ".join(arr[2:])
    taxa = taxa.replace('[', '')
    taxa = taxa.replace(']', '')

    return tid, taxa, name


def read_taxids(fname):
    store = list()
    store_error = list()
    stream = csv.reader(open(fname), delimiter="\t")
    for row in stream:
        taxa, taxid = row[0], row[1]
        store.append(taxid) if taxid else store_error.append(taxa)

    return store, store_error


def get_species(taxa_file):
    """
    taxa_list is a string with results of taxonkit list command.
    taxonkit list command output is parsed and species/subspecies list are returned.
    """
    species, subspecies = list(), list()
    taxa = open(taxa_file)

    for taxa_line in taxa:
        tid, taxa, name = parse_taxa(taxa_line)

        if taxa == "species":
            species.append((name.strip(), tid))
        elif taxa == "subspecies":
            subspecies.append((name.strip(), tid))
        else:
            continue
    #
    # Remove species and keep subspecies if subspecies is present
    #
    sp = set([" ".join(s[0].split(" ")[:2]) for s in subspecies])
    sp_without_subsp = [s for s in species if s[0] not in sp]
    species.extend(sp_without_subsp)
    all_species = sp_without_subsp + subspecies
    all_species = set(all_species)
    return all_species


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--taxids', dest='fname', type=str, required=True,
                        help="""Tab delimited file with taxa name and taxid for which 
                            all species under the specified taxid needs to be extracted.
                            First column should contain taxa name and second column should contain taxid.
                            """)

    args = parser.parse_args()
    taxid_file = args.fname

    taxids, no_taxid_list = read_taxids(taxid_file)

    # File with with lower taxa from Taxonkit
    lower_faxa_file = "taxonkit_results.txt"

    fh = open(lower_faxa_file, "a")
    for taxid in taxids:
        taxa_list = get_lower_taxa(taxid).strip()
        fh.write(taxa_list)
        fh.write("\n")

    # Write the species list
    species = get_species(lower_faxa_file)

    for s in species:
        print("\t".join([s[0], s[1]]))

    # Write if a taxid is not found.
    # This may be because of spelling mistakes in taxa name.
    if no_taxid_list:
        fn = open("taxid_not_found.txt", "a")
        for t in no_taxid_list:
            fn.write(t)
            fn.write("\n")

    return


if __name__ == "__main__":
    main()
