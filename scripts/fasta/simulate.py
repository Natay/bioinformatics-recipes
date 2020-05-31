"""
Simulates single end reads from a FASTA file.

Usage:

    simulate.py  input.fasta  100

The main difference to other tools (and reason for this tool to even exist)
is it that it generates exactly N reads per each sequence contig.
"""
import sys
from random import randint, random, choice
import itertools

def strip(x):
    return x.strip()

BASES = "ATGC"

def parse_fasta(fname):
    """
    Returns fasta records.
    Loads the entire fasta record into memory.
    """
    stream = open(fname)
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


if __name__ == '__main__':

    if (len(sys.argv) != 3):
        print (f"Usage: simulate.py input.fa count ")
        sys.exit(1)

    # Input fasta file
    fname = sys.argv[1]

    # How many reads to generate.
    count = int(sys.argv[2])

    # Read size.
    size = 100

    # Error probability as a fraction.
    prob = 0.02

    f_qual = "I" * size

    counter = itertools.count(1)
    out = parse_fasta(fname)
    for name, desc, seq in out:

        for f_start, f_end, f_seq in simulate(seq, count=count, size=size):
            index = next(counter)
            f_name = f"@{name}|{index}|{f_start}-{f_end}"
            print (f_name)
            print(f_seq)
            print("+")
            print(f_qual)

