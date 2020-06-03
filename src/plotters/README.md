







## Run tree plotter on kraken data

    python src/plotters/tree.py data/*-report.txt --tmpl src/templates/tree_template.html --kraken
    
    # Produce sankey plot.
    python src/plotters/tree.py data/*-report.txt --tmpl src/templates/tree_template.html --kraken --sankey 