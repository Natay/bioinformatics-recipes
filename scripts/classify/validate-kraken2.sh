
set -uex

#
# Download the taxonomy for kraken2.
# Needs to be done separately and only once.
#
# mkdir -p ~/refs
#
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

# The Kraken 2 classification report.
REPORT=output/kraken2-report.txt

# The Kraken2 output.
OUTPUT=output/kraken2-output.txt

# The Kraken2 accuracy report.
ACCURACY=output/kraken2-accuracy.txt

# Copy over the accession file to input folder to aid reproducibility.
cp $ACC input/accessions.txt

# Get sequences from NCBI.
epost -db nuccore -input $ACC | efetch -format fasta > $FASTA

# Identify the taxonomy for each accession number.
epost -db nuccore -input $ACC  | esummary | xtract -pattern DocumentSummary -element Caption,TaxId,Title > $TAXONOMY

# To avoid recomputing the same kraken2 library store with a unique name.
SHA=`shasum $FASTA | cut -c 1-8`

# Store the Kraken2 database under the checksum name.
DB=~/tmp/$SHA

# Create the directory for the kraken2 database.
mkdir -p $DB

# Link the taxonomy.
ln -sf ~/refs/kraken2/taxonomy $DB

# Add marker sequences to the kraken2 library.
kraken2-build --add-to-library $FASTA --db $DB

# Build the marker library.
kraken2-build --build --db $DB

# The location of the code that simulates the reads.
URL1=https://raw.githubusercontent.com/biostars/biocode/master/scripts/fasta/simulate.py

# Get the code.
curl $URL1 > code/simulate.py

# Generate the simulated reads.
python code/simulate.py --fname $FASTA --count $N > $READS

# Run kraken2 classifier.
kraken2 -db $DB $READS --report-zero-counts --report $REPORT > $OUTPUT

# The location of the code that generates the validation.
URL2=https://raw.githubusercontent.com/biostars/biocode/master/scripts/classify/validate.py

# Get the code.
curl $URL2 > code/validate.py

# Install the plac command parser.
pip install plac -q

# Run the validator on the results.
python validate.py $OUTPUT $TAXONOMY $N > $ACCURACY
