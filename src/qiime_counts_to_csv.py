'''
This script converts a tsv file created by biom-convert command to a csv file.
It will also convert count data to percentages and produce the produce a percent-csv file required for heatmap generation.
'''

import os
import pandas as pd
from recipes.code import utils
from argparse import ArgumentParser


def get_taxa_name(taxa, taxa_level):
    names = list()
    for elm in taxa:
        elm = elm.strip()
        name = elm.split(";")[taxa_level - 1]
        names.append(name)
    # insert unclassified
    names[-1] = "Unassigned"
    return names


def run(args):
    fname = args.infile
    taxa_level = int(args.taxa_level)
    outdir = args.outdir

    df = pd.read_table(fname, sep="\t", header=1)

    # 1st column with taxa lineage.
    taxa = list(df['#OTU ID'])

    # Get the taxa name at a specific level.
    taxa = get_taxa_name(taxa, taxa_level)

    samples = list(df.columns)[1:]

    #percents, counts = dict(), dict()
    perc_df = pd.DataFrame()
    counts_df = pd.DataFrame()
    perc_df['taxa'] = taxa

    rnum, cnum = df.shape
    perc_df['taxid'] = [''] * rnum
    perc_df['rank'] = [''] * rnum

    counts_df['taxa'] = taxa
    counts_df['taxid'] = [''] * rnum
    counts_df['rank'] = [''] * rnum

    # calculate percent reads in each sample.
    for sample in samples:
        perc = round((df[sample] / sum(df[sample])) * 100, 3)
        perc_df[sample] = list(perc)
        counts_df[sample] = list(df[sample])

    #aliasfile = "/Users/asebastian/work/web-dev/biostar-recipes/export/refs/taxonomy/fishalias.txt"
    #perc_df = utils.alias(df=perc_df, fname=aliasfile, key1='name', key2='sciname', name='name')

    prefix = os.path.splitext(os.path.basename(fname))[0]
    prefix = "_".join(prefix.split("_")[:-1])

    counts_file = os.path.join(outdir, prefix + "_counts.csv")
    percent_file = os.path.join(outdir, prefix + "_perc.csv")

    perc_df.to_csv(percent_file, index=False)
    counts_df.to_csv(counts_file, index=False)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('--infile', dest='infile',
                        help="Specify the input file.")
    parser.add_argument('--taxa-level', dest='taxa_level',
                        help="Specify the output file.")
    parser.add_argument('--outdir', dest='outdir',
                        help="Specify the output directory .")
    args = parser.parse_args()
    run(args)
