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

# Directory to store the final HTML report.
OUTPUT_DIR = args[2]

# Ensure DIRs does not have a trailing /

# Output file name
OUT_FILE = args[3] #'pavion-report.html'

# Report title
REPORT_TITLE = args[4] #"Report title"

# Date to put on the report
DATE = args[5]

# Comma seperated string to filter taxa in sankey.
# Example: Chordata,artificial sequences
FILTER_TAXA = trimws(unlist(strsplit(args[6], ",")))

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

# Gather the reports
reports <- pavian::read_reports(data$ReportFilePath, data$Name)

# Get the R Markdown template for final report file
rmd_file <- system.file("pavian-report.Rmd",package="pavian")

# Make a local copy of the template file
local_temp <- file.path(OUTPUT_DIR, "template.Rmd")

file.copy(rmd_file, local_temp, overwrite = TRUE)

# Set up parameters to pass to Rmd document
params <- list(doc_title=REPORT_TITLE,
             doc_author="",
             doc_date=DATE,
             set_name=sample_set_names_combined(),
             all_data_loaded=TRUE,
             sample_data=data,
             reports=reports,
             include_sankey=TRUE,
             filter_taxa=FILTER_TAXA)

# Create the final html report.
rmarkdown::render(local_temp, output_file = OUT_FILE ,
                  params = params, output_format = "html_document",
                  envir = new.env())

# Remove the temporary R Markdown template used to create report.
file.remove(local_temp)