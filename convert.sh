#!/bin/bash

error () {
    echo "$1"
    exit 1
}

# Get input file to process
if [ "$1" == "" ]; then error "Usage: $0 CSVFILE [ > OUTFILE ]"; fi
infile="$1"

# Get filename and extension and check to the extension to be XLSX
#filename=$(basename -- "$infile")
#extension="${filename##*.}"
#filename="${filename%.*}"
#if [ "$extension" != "xlsx" ]; then
#    error "error: '$infile' is not a valid .xlsx file"
#fi

# Convert xlsx file to CSV
#csvfile="${filename}.csv"
#python -m xlsx2csv "$infile" -d ';' | tail -n +7 | head -n -2 > "$csvfile"

# Remove invalid characters
sed -i 's/[\x9b|\x90|\xd7|\xc7|\x91|\x9d|\xb7]//g' "$infile"

# Output converted csv
python stoconv.py "$infile"
