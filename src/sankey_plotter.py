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
        parent, child, count = line.strip().split(",")

        yield (parent, child, 2)


def load_sankey(files, sankey_tmpl=None, plots_tmpl=None, outdir=None):
    """
    Load data into template
    """

    # Load local template if it exists
    sankey_tmpl = sankey_tmpl or "sankey_template.html"
    plots_tmpl = plots_tmpl or "sankey_plots.html"
    outdir = outdir

    # Gather sankey for each file
    plots = []

    for fname in files:

        fullpath = os.path.abspath(fname)

        title = os.path.basename(fname)
        # Get the data for each file
        data = gen_data(fullpath)

        tmpl = loader.get_template(sankey_tmpl)
        context = dict(id=title, title=title, data=data)
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

    args = parser.parse_args()

    # Set the template directory in django.
    tmpl_dir = os.path.abspath(os.path.dirname(args.tmpl))
    config_django(template_dir=tmpl_dir)

    tmpl = os.path.basename(args.tmpl)

    # Load sankey into file.
    load_sankey(files=args.files, sankey_tmpl=tmpl, outdir=args.outdir)


if __name__ == '__main__':
    main()
