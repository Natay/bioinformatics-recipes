### Fish mitochondrial marker database. 

The scripts in this folder are used to create fish specific mitochondrial marker sequence database.

Marker sequences that will be extracted are

* 12S
* 16S
* COI
* COII 
* COIII
* Cytochrome B
* Mitochondrial complete genome

To create fish specific markers, run the script as

	bash fish_marker_db.sh 

Steps involved in extracting the marker sequences are

1. Extract all fish taxids using Taxonkit.
2. Extract all sequences from NCBI 'nt' database.
3. Parse nt sequences to extract fish specific sequences.
4. Parse the sequence titles to extract mitochondrial and marker specific sequences.

**Script details**

1. fish_marker_db.sh  - Main shell script that runs all the commands.
2. get_species_taxids.py  - Extracts fish taxids using taxonkit.
3. extract_mito_from_nt.py - Parses nt sequences to extract mitochondrial and marker specific sequences.
4. remove_nt_redundant_header.py - Write the sequenes separately for the redundant headers.
5. create_fish_db.py - Creates an sqlite3 database of fish marker sequences.

