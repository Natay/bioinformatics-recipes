#
# Validates Centrifuge taxonomy.
#

set -uex

# Use the taxonomy specific files to build the custom database.
TAXDIR=~/refs/taxonomy

# Files used in generating the Centrifuge index.
TABLE=$TAXDIR/table.txt
NODES=$TAXDIR/nodes.dmp
NAMES=$TAXDIR/names.dmp

# Make the taxonomy directory.
mkdir -p $TAXDIR

#
# Download the taxonomy for centrifuge.
# Needs to be done separately and only once.
#

#
# Prepare the taxonomy data.
# This operation only needs to be done once for the entire website.
#
# Download the taxonomy files from NCBI.
# (cd $TAXDIR && wget ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz)
# (cd $TAXDIR && wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz)

# Uncompress the taxonomy files.
# (cd $TAXDIR &&  tar -xzvf $TAXDIR/taxdump.tar)
# (cd $TAXDIR && gunzip nucl_gb.accession2taxid.gz)

# Create the conversion table (accession to taxid mapping).
# cat $TAXDIR/nucl_gb.accession2taxid | cut -f 2,3 > $TABLE


# (cd ~/refs && kraken2-build --download-taxonomy --db kraken2)
#

# Input file that contains the accession numbers.
ACC=acc.txt

# How many reads to simulate.
N=1000

# Lenght of reads.
L=100

# Will store data in these locations
mkdir -p input output code

# The FASTA file storing the sequence for accession numbers.
FASTA=input/reference.fa

# The FASTQ file storing the reads simulated from the reference.
READS=input/reads.fq

# The accesion taxonomy file
TAXONOMY=input/taxonomy.txt

# The Centrifuge classification report.
REPORT=output/centrifuge-report.txt

# The Centrifuge output.
OUTPUT=output/centrifuge-output.txt

# The Centrifuge accuracy report.
ACCURACY=output/centrifuge-accuracy.txt

# Copy over the accession file to input folder to aid reproducibility.
cp $ACC input/accessions.txt

# Get sequences from NCBI.
epost -db nuccore -input $ACC | efetch -format fasta > $FASTA

# Identify the taxonomy for each accession number.
epost -db nuccore -input $ACC  | esummary | xtract -pattern DocumentSummary -element Caption,TaxId,Title > $TAXONOMY

# Store the Centrifuge database under the checksum name.
INDEX=index/db

# Make thr directory
mkdir -p index

# Build the centrifuge index.
centrifuge-build -p 2 --conversion-table $TABLE --taxonomy-tree $NODES --name-table $NAMES $FASTA $INDEX >> runlog.txt

# The location of the code that simulates the reads.
URL1=https://raw.githubusercontent.com/biostars/biocode/master/scripts/fasta/simulate.py

# Get the code.
curl $URL1 > code/simulate.py

# Generate the simulated reads.
python code/simulate.py --fname $FASTA --count $N > $READS

# Run Centrifuge
centrifuge -x $INDEX -U $READS -S $OUTPUT  --report-file $REPORT

# Kraken style report
centrifuge-kreport -x $INDEX $OUTPUT > $REPORT

# The location of the code that validates the reads.
URL2=https://raw.githubusercontent.com/biostars/biocode/master/scripts/classify/validate.py

# Get the code.
curl $URL2 > code/validate.py

# Install the plac command parser.
pip install plac -q

# Run the validator
python code/validate.py -f $OUTPUT -t $TAXONOMY -c $N > $ACCURACY
