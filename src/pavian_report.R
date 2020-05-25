# Title     : TODO
# Objective : TODO
# Created by: natay
# Created on: 2020-05-24

# Load pavion
library(pavian)

# Load the command line arguments
args = commandArgs(trailingOnly=TRUE)

# Directory containing input data files.
INPUT_DIR = args[1]

# Date to put on the report
DATE = args[2]

# Comma seperated string to filter taxa in sankey.
# Example: Chordata,artificial sequences
FILTER_TAXA = trimws(unlist(strsplit(args[3], ",")))

# Comma seperated string of
SANKEY_RANKS = args[4]

# Get current working directory as output
OUTDIR = getwd()

# Output file name
OUT_FILE = 'pavion-report.html'

# Report title
REPORT_TITLE = "Pavian classification report "

# Combine sample names into a single
sample_set_names_combined <- function(){
  res <- sapply(data$Name, basename)
  res <- paste(res, collapse="_")
  res <- gsub("[^A-Za-z\\-_]","_", res)
  if (nchar(res) == 0){
    return("Set1")
  } else {
    return(res)
  }
}

# Load data found in directory
#data <- pavian::read_sample_data(system.file("shinyapp","example-data","brain-biopsies",package="pavian"))
data <- pavian::read_sample_data(dir(INPUT_DIR, pattern=NULL, all.files=FALSE, full.names=TRUE), is_files=TRUE)


template = file.path(OUTDIR, 'pavian_template.Rmd')

if file.exists(template){
    temp <- template
}else{
    # Get the R Markdown template for final report file
    rmd_file <- system.file("pavian-report.Rmd",package="pavian")

    # Get the R Markdown template file locally or from the
    # Make a local copy of the template file
    temp <- file.path(OUTPUT_DIR, 'pavian_template.Rmd' )
    file.copy(rmd_file, local_temp, overwrite = TRUE)
}

# Gather the reports
reports <- pavian::read_reports(data$ReportFilePath, data$Name)

# Set up parameters to pass to Rmd document
params <- list(doc_title=REPORT_TITLE,
             doc_author="",
             doc_date=DATE,
             set_name=sample_set_names_combined(),
             all_data_loaded=TRUE,
             sample_data=data,
             reports=reports,
             include_sankey=TRUE,
             filter_taxa=FILTER_TAXA,
             tax_rank=SANKEY_RANKS)

# Create the final html report.
rmarkdown::render(temp, output_file = OUT_FILE ,
                  params = params, output_format = "html_document",
                  envir = new.env())

# Remove the temporary R Markdown template used to create report.
file.remove(local_temp)