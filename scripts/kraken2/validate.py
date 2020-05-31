"""
Evaluates a kraken2 report file with respect of read file generated with the simulate.py tool

Requires a taxonomy file that identifies the taxonomy id of each accession number.
"""
import csv, sys
from collections import defaultdict

def parse_kraken2_output(fname):
    """
    Parses lines such as:
    C	AP012081.1|3|14228-14328	67547	100	67547:66
    """
    count = defaultdict(int)
    stream = open(fname)
    reader = csv.reader(stream, delimiter="\t")
    reader = filter(lambda row: row[0] == "C", reader)
    for row in reader:
        label, name, taxid = row[:3]
        name = name.split("|")[0].split(".")[0]
        key  = (name, taxid)
        count[key] += 1
    return count

def evaluate_taxonfile(fname, count, expect):
    stream = open(fname)
    reader = csv.reader(stream, delimiter="\t")

    header = "accuracy accession taxid title".split()
    print ("\t".join(header))

    for row in reader:
        name, taxid, title = row[:3]
        key = (name, taxid)
        found = int(count.get(key, 0))
        perc = found/expect * 100
        perc = "%.1f" % perc
        row = [ perc ] + row
        print ("\t".join(row))

def run():
    pass


if __name__ == '__main__':

    kname = sys.argv[1]
    tname = sys.argv[2]
    expect = int(sys.argv[3])

    count = parse_kraken2_output(kname)

    evaluate_taxonfile(tname, count=count, expect=expect)