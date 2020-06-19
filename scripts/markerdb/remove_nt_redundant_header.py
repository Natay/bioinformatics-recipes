# This script removes multiple ">" from fasta header
# and writes the redundant sequences with unique header


import sys, re


def is_header(line):
    return line.startswith(">")


def format_seq(seqs):
    """
    Splits a single line sequence into multi-lines.
    """
    new = dict()
    for header, seq in seqs.items():
        # split seq into 70 characters each line
        seq1 = "\n".join([seq[i:i + 70] for i in range(0, len(seq), 70)])
        new[header] = seq1
    return new


def make_fasta_dict(fa):
    store = dict()
    header = None

    for line in fa:
        line = line.strip()

        # Start of fasta header
        if line.startswith(">"):
            # Removing the accession version numbers.
            header = re.sub(r'\.\d+', '', line)
            store[header] = ""
        else:
            # Fasta body.
            store[header] = store[header] + line

    store = format_seq(store)

    return store


def write_all_seq(header, seq):
    vals = re.split('(>[A-Z])', header)
    vals = [acc for acc in vals if acc != '']

    accessions = []

    for i in range(0, len(vals), 2):
        string = vals[i] + vals[i + 1]
        accessions.append(string)

    all_accessions = accessions[:]

    for acc in all_accessions:
        accessions.remove(acc)
        out = "".join(accessions)
        out = out.replace(">", ":")
        # out = ':'.join(accessions)
        newh = acc + out
        print(newh)
        print(seq)
        accessions.append(acc)
    return


if __name__ == "__main__":
    fasta = sys.argv[1]
    fa = open(fasta)
    store = make_fasta_dict(fa)

    for header, seq in store.items():
        vals = re.split('(>[A-Z])', header)
        vals = [v for v in vals if v != ""]

        if len(vals) - 1 > 1:
            write_all_seq(header, seq)
            continue

        print(header)
        print(seq)
