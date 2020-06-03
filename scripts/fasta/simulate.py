"""
Simulates single end reads from a FASTA file.

Usage:

    simulate.py  input.fasta  100

The main difference to other tools (and reason for this tool to even exist)
is it that it generates exactly N reads per each sequence contig.
"""
import sys, argparse
from random import randint, random, choice
import itertools

try:
    import plac
except ImportError as exc:
    print(f"*** Error: {exc}", file=sys.stderr)
    print("*** Run: pip install plac", file=sys.stderr)
    sys.exit(1)


def strip(x):
    return x.strip()

BASES = "ATGC"

def parse_fasta(stream):
    """
    Returns fasta records.
    Loads the entire fasta record into memory.
    """
    #stream = open(fname)
    stream = map(strip, stream)

    name = desc = seq = ''
    for line in stream:
        if line.startswith(">"):
            if name:
                yield name, desc, seq
            elems = line.split(maxsplit=1)
            name = elems[0][1:]
            desc = elems[1] if len(elems) == 2 else ''
            seq = ''
        else:
            seq += line

    yield name, desc, seq


def simulate(line, count=10, size=5):
    end = len(line) - size
    end = size if end < 0 else end
    for _ in range(count):
        f_start = randint(0, end)
        f_end = f_start + size
        yield f_start, f_end, line[f_start:f_end]


def apply_error(seq, prob=0.1):
    while 1:
        p = random()
        if p < prob and prob < 0.9:
            bases = list(seq)
            pos = randint(0, len(seq) - 1)
            bases[pos] = choice(BASES)
            seq = "".join(bases)
        else:
            break
    return seq


@plac.annotations(
    fname=("fasta reference file", "option", "f", argparse.FileType(), None, "PATH"),
    count=("number of reads per accession", "option", "c", int, None, "INT"),
    size=("lenght of each read", "option", "s", int, None, "INT"),
)
def run(fname, count=1000, size=100):
    # Read size.

    f_qual = "I" * size

    counter = itertools.count(1)


    out = parse_fasta(fname)
    for name, desc, seq in out:

        for f_start, f_end, f_seq in simulate(seq, count=count, size=size):
            index = next(counter)
            f_name = f"@{name}|{index}|{f_start}-{f_end}"
            print(f_name)
            print(f_seq)
            print("+")
            print(f_qual)


if __name__ == '__main__':
    plac.call(run)




