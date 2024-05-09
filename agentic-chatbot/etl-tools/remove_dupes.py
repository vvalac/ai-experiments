import json
import os

# File paths
input_file_path = 'document_data\\all_documents.jsonl'
output_file_path = 'document_data\\unique_documents.jsonl'

# Use a set to track unique entries
unique_entries = set()
dupes = 0

# Read from the input file and write to the output file if not duplicate
with open(input_file_path, 'r', encoding='utf-8') as infile, open(output_file_path, 'w', encoding='utf-8') as outfile:
    for line in infile:
        # Check if the line is not in unique_entries
        if line not in unique_entries:
            # Add line to unique_entries set
            unique_entries.add(line)
            # Write the unique line to output file
            outfile.write(line)
        else:
            dupes += 1

print(f"{dupes} Duplicate entries removed. Cleaned documents saved to:", output_file_path)
