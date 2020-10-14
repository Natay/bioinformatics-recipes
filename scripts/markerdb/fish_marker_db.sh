set -uex
#
# Fish specific mitochondrial marker sequences are obtained by parsing the sequences in 'nt' database by fish taxids.
# Taxonkit is used to obtain all fish species's taxids.
# nt sequenes are filtered based on fish taxids.
# Titles of the Fish specific nt sequences are parsed to obtain the specific markers.
#

# Get all fish species and taxids. This uses taxon kit.
python get_species_taxids.py --taxids fish_taxids.txt >fish_species_tids.txt

# Extract all sequence info from nt.
# Since sequence title can include commas and other special characters, '#' is specified as delimiter here.
time  blastdbcmd -db nt -dbtype 'nucl' -outfmt "%a#%t#%l#%T#%S#%L" -out nt_seq.txt -entry all

# Extract fish specific mitochondrial sequence info from nt.
python extract_mito_from_nt.py nt_seq.txt fish_species_tids.txt >fish_mito_marker_table.txt

# Extract accessions.
cat fish_mito_marker_table.txt |cut -f 1 | grep -v "accession"  >fish_mito_marker_acc.txt

# Get fish mitochondrial marker sequences
blastdbcmd -db nt -entry_batch fish_mito_marker_acc.txt >fish_mito_markers_nt.fa

# Format fasta file ( duplicated sequences with same headers are written with different headers)
python remove_nt_redundant_header.py fish_mito_markers_nt.fa >fish_mito_markers.fa

# make blastdb
makeblastdb -dbtype 'nucl' -parse_seqids -in fish_mito_markers.fa -out fish_mito_markers.fa

# Create Fish database
python create_fish_db.py --database fish_mito.db --sequence_table fish_mito_marker_table.txt --status_table fish_categories.txt



