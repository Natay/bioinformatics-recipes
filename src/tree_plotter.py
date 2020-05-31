# Load sankey
import os
import django
import subprocess

from django.template import loader

from django.conf import settings


def config_django(template_dir):
    """
    Set the template dir in django
    """

    # Configure the template directory
    settings.configure(TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [template_dir],
            'APP_DIRS': False,
        },
    ])

    # Set up django.
    django.setup()


def gen_data(fname):
    """
    Return data in file as generator
    """
    stream = open(fname, "r")

    for line in stream:
        # ['id', 'childLabel', 'parent', 'size', 'color']
        item_id, child_label, parent, size, color = line.strip().split(",")

        yield (int(item_id), child_label, int(parent), int(size), color)


def taxa_data(fname):
    """
    Extract taxa data from a file
    """
    from subprocess import PIPE

    # Ordered list of taxonomic ranks
    ranks = ["R", "R1", "D", "K", "P", "C", "O", "F", "G", "S"]
    counts = dict()
    for rank in ranks:

        cmd = "awk -v col=4 '{print $col}' " + f"{fname} | grep -c -w '{rank}'"
        proc = subprocess.run(cmd, shell=True, stderr=PIPE, stdout=PIPE)
        counts[rank] = int(proc.stdout.decode().strip())

    possible_roots = [x[0] for x in counts.items() if x[1] == 1]
    possible_roots = sorted(possible_roots, key=lambda x: ranks.index(x), reverse=True)
    root = possible_roots[0]

    return counts, root


def parse_kraken2(fname):

    # The root rank in the each file, all paths lead back here.
    ROOT = "R1"

    # Keep track of the latest taxids for each rank
    most_recent = dict()

    # Map a rank to it's direct parent rank.
    parent_rank_map = dict(D=ROOT, K="D", P="K", C="P", O="C", F="O", G="F", S="G")

    stream = open(fname, "r")

    for line in stream:

        perc, covered, assigned, rank, taxid, name = line.strip().split("\t")
        name = name.strip()
        perc = int(float(perc)) or 1
        # Store rank and name
        most_recent[rank] = name

        # We are at the root.
        if rank == ROOT:
            most_recent[rank] = name
            continue

        # Line being ignored.
        if rank not in parent_rank_map:
            continue

        # Get the parent taxid of this rank.
        parent_rank = parent_rank_map[rank]
        parent_name = most_recent.get(parent_rank, ROOT)

        # Return the next child to plot.
        yield parent_name, name, 2


def parse_kraken(fname):

    # Gather some preliminary meta data about the file
    counts, root = taxa_data(fname=fname)

    # Keep track of the latest taxids for each rank
    most_recent = dict()

    # Map a rank to it's direct parent rank.
    parent_rank_map = dict(D="R", K="D", P="K", C="P", O="C", F="O", G="F", S="G")
    color_map = dict(R="black", D="black", K="pink", P="purple", C="brown", O="orange", F="blue", G="red", S="green")

    stream = open(fname, "r")
    idcount = 0
    hit_root = False

    for line in stream:

        perc, covered, assigned, rank, taxid, name = line.strip().split("\t")
        name = name.strip()
        perc = int(float(perc)) or 1
        color = color_map.get(rank, "black")

        # We are at the root.
        if rank == root:
            most_recent[rank] = 0
            hit_root = True
            yield 0, name, -1, perc, color
            continue

        # Line being ignored.
        if rank not in parent_rank_map:
            continue

        if not hit_root:
            continue

        # Get the parent taxid of this rank.
        parent_rank = parent_rank_map[rank]

        parent_id = most_recent.get(parent_rank)
        parent_id = int(parent_id)

        idcount += 1
        # Store rank and id
        most_recent[rank] = idcount

        # Return the next child to plot.
        if rank == "S":
            perc = 10000

        yield idcount, name, parent_id, perc, color


def plot(files, tmpl=None, is_kraken=False, outdir=None):
    """
    Load data in files into template
    """

    # Load local template if it exists
    template = tmpl or "tree_template.html"
    plots_tmpl = "tree_plots.html"

    # Gather for each file
    plots = []

    for fname in files:

        fullpath = os.path.abspath(fname)
        title = os.path.basename(fname)

        # Get the data for each file
        if is_kraken:
            data = parse_kraken(fullpath)
        else:
            data = gen_data(fullpath)

        tmpl = loader.get_template(template)
        context = dict(plot_id=title, id=title, title=title, data=data)
        template = tmpl.render(context=context)

        plots.append(template)

    # Render final report with all of the plots.
    tmpl = loader.get_template(plots_tmpl)
    context = dict(plots=plots)
    report = tmpl.render(context=context)

    print(report)

    return


def main():

    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('files', metavar='FILES', type=str, nargs='+', help='a file list')

    parser.add_argument('--tmpl', required=False, default="sankey_template.html",
                        help="Base template to load data into", type=str)

    parser.add_argument('--outdir', required=False, default="",
                        help="""Output directory to put final html in. 
                                Default to current directory""", type=str)
    parser.add_argument('--kraken', action="store_true", default=False, help="""Files come from kraken.""")
    args = parser.parse_args()

    # Set the template directory in django.
    tmpl_dir = os.path.abspath(os.path.dirname(args.tmpl))

    config_django(template_dir=tmpl_dir)

    tmpl = os.path.basename(args.tmpl)

    # Plot the files into given template.
    plot(files=args.files, tmpl=tmpl, outdir=args.outdir, is_kraken=args.kraken)


if __name__ == '__main__':
    main()
