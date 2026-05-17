% nwread

# NAME
nwread - runs automated data analysis tasks on a reading list

# SYNOPSIS
**nwread** [command] [options]

# DESCRIPTION
**nwread** is a CLI application that can run several automated data analysis tasks on a reading list and save the results as a PDF report. It’s designed to facilitate and gamify a continuous learning journey.

# COMMANDS

**save**
Runs all the data analysis tasks against the reading list and saves the outcome as PDF report.

# OPTIONS

**--input_path**
The path to the reading list file in Excel format.

**--nrows**
Latest row number to process in the reading list.

*--folder_path*
The path to the folder into which the PDF report will be saved. Default: current folder.

*--help, -h*
Shows help and usage information.

# EXAMPLES

**Run it against a reading list:**

```text
nwread \
	--input_path "/data/Reading List.xlsx" \
	--nrow 371 
```

**Run it against a reading list with custom `folder_path`:**

```text
nwread \
	--input_path "/data/Reading List.xlsx" \
	--nrow 371 \
	--folder_path "/home/nwreadinglist/"
```

# AUTHOR
numbworks (numbworks@gmail.com)