import os
from argparse import ArgumentParser

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('--taxdir', dest='taxdir', required=True,
                        help="Specify the taxonomy directory.")

    args = parser.parse_args()
    taxdir = args.taxdir

    script = os.path.join(CURRENT_DIR, "taxon_lineage.sh")

    cmd = f"bash {script} {taxdir} {CURRENT_DIR}"
    os.system(cmd)
