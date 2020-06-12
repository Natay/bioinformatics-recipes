"""
Evaluates a kraken2/centrtifuge report files.

Requires a taxonomy file that identifies the taxonomy id of each accession number.
"""
import csv, sys, argparse
from pprint import pprint

try:
    from pathlib import Path
except ImportError:  # in Python 2.7
    Path = str

try:
    import plac
except ImportError as exc:
    print(f"*** Error: {exc}", file=sys.stderr)
    print("*** Run: pip install plac", file=sys.stderr)
    sys.exit(1)

from collections import defaultdict

def parse_qiime_output(fname):
    """
    Parses lines such as:

        Feature ID	Taxid	Taxon	Confidence
        MG570454|1|13346-13446	186623	Eukaryota;Chordata;Actinopteri	0.9905904770433329

    Returns a dictionary keyed by accession/taxid that counts how many times that key was seen in the output.

        { ("AP012081", 67547): 3994  }

    """
    store = defaultdict(int)
    stream = open(fname)
    reader = csv.DictReader(stream, delimiter="\t")
    for row in reader:
        name, taxid = row["Feature ID"], row["Taxid"]
        name = name.split("|")[0]
        key = (name, taxid)
        store[key] += 1
    
    return store



def parse_centrifuge_output(fname):
    """
    Parses lines such as:

        readID	seqID	taxID	score	2ndBestScore	hitLength	queryLength	numMatches
        AP012081.1|1|15631-15731	AP012081.1	67547	7225	0	100	100	1

    Returns a dictionary keyed by accession/taxid that counts how many times that key was seen in the output.

        { ("AP012081", 67547): 3994  }

    """
    store = defaultdict(int)
    stream = open(fname)
    reader = csv.DictReader(stream, delimiter="\t")
    for row in reader:
        name, taxid = row["seqID"], row["taxID"]
        name = name.split(".")[0]
        key = (name, taxid)
        store[key] += 1
    return store


def parse_kraken2_output(fname):
    """
    Parses lines such as:

        C	AP012081.1|3|14228-14328	67547	100	67547:66

    Returns a dictionary keyed by accession/taxid that counts how many times that key was seen in the data.

        { ("AP012081", 67547): 3994  }
    """
    store = defaultdict(int)
    stream = open(fname)
    reader = csv.reader(stream, delimiter="\t")
    reader = filter(lambda row: row[0] == "C", reader)
    for row in reader:
        label, name, taxid = row[:3]
        name = name.split("|")[0].split(".")[0]
        key = (name, taxid)
        store[key] += 1
    return store


def evaluate(tname, lookup, expected):
    """
    Evaluates a taxon file with a lookup relative to expected counts.
    """
    stream = open(tname)
    reader = csv.reader(stream, delimiter="\t")

    # Validation table header.
    header = "accession expect actual percent taxid title".split()
    print("\t".join(header))

    for row in reader:
        name, taxid, title = row[:3]
        key = (name, taxid)
        found = int(lookup.get(key, 0))
        perc = found / expected * 100
        perc = "%.1f" % perc
        found = str(found)
        row.insert(1, str(expected))
        row.insert(2, str(found))
        row.insert(3, str(perc))

        print("\t".join(row))


#@plac.annotations(
#    fname=("kraken2/centrifuge output of classified reads", "option", "f", str),
#    tname=("file to connect each accession to a taxid", "option", "t", str, None, "PATH"),
#    count=("the expected read counts for each accession", "option", "c", int, None, "INT"),
#)

@plac.opt('fname', "results file", type=Path)
@plac.opt('tname', "taxid file", type=Path)
@plac.opt('count', "expected counts", type=int)
def run(fname, tname, count=1000):

    # Decide if it is kraken2 or centrifuge output
    header = open(fname).readline()

    if "seqID" in header:
        # Centrifuge output has a header
        lookup = parse_centrifuge_output(fname)
    elif "Feature" in header:
        lookup = parse_qiime_output(fname)
    else:
        lookup = parse_kraken2_output(fname)

    evaluate(tname, lookup=lookup, expected=count)


if __name__ == '__main__':
    plac.call(run)

