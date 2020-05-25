is.installed <- function(mypkg){
  is.element(mypkg, installed.packages()[,1])
} 

if (!is.installed("taxonomizr")){
  install.packages("taxonomizr")
}

library("taxonomizr")

# Read the command line arguments.
args = commandArgs(trailingOnly=TRUE)

nodes = args[1]
names = args[2]
accessions = args[3]
#dbpath = args[4]

# Convert accessions to database. This could take a while.
read.accession2taxid(list.files('.','nucl_gb.accession2taxid'),'accessionTaxa.sql')

taxaNodes<-read.nodes(nodes)
taxaNames<-read.names(names)


accessions = read.table(accessions, header=FALSE, sep="",stringsAsFactors=FALSE, strip.white = TRUE)
for( acc in accessions) {
  taxaId<-accessionToTaxa(acc, 'accessionTaxa.sql')
}

taxonomy = getTaxonomy(taxaId,taxaNodes,taxaNames)
taxonomy=data.frame(taxonomy)
out = cbind(accessions, taxonomy)

if(dim(accessions)[1] == dim(taxonomy)[1]) {
write.table(out, file ="lineage.tsv", sep=";", quote=FALSE, row.names = FALSE)
}

# Modify the header
#content = readLines("lineage.tsv",-1)
#content[1]="Feature ID\tTaxon"
#writeLines(content,"lineage.tsv")
