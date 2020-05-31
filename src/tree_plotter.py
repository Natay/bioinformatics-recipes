# Load sankey
import os
import django

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

    # The root rank in the each file, all paths lead back here.
    ROOT = "R1"

    # Keep track of the latest taxids for each rank
    most_recent = dict()

    # Map a rank to it's direct parent rank.
    parent_rank_map = dict(D=ROOT, K="D", P="K", C="P", O="C", F="O", G="F", S="G")

    stream = open(fname, "r")
    idcount = 0
    for line in stream:

        perc, covered, assigned, rank, taxid, name = line.strip().split("\t")
        name = name.strip()
        perc = int(float(perc)) or 1

        # We are at the root.
        if rank == ROOT:
            most_recent[rank] = 0
            yield 0, name, -1, perc, "red"

        # Line being ignored.
        if rank not in parent_rank_map:
            continue

        # Get the parent taxid of this rank.
        parent_rank = parent_rank_map[rank]
        parent_id = most_recent.get(parent_rank, ROOT)
        parent_id = int(parent_id)

        idcount += 1
        # Store rank and id
        most_recent[rank] = idcount

        # Return the next child to plot.
        if rank == "S":
            perc = 100
        yield idcount, name, parent_id, perc, "red"


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
