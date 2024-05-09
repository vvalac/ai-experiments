import json
import os
import re  # Import regular expressions module

# File paths
input_file_path = 'document_data\\all_documents.jsonl'
output_file_path = 'document_data\\cleaned_documents.jsonl'

# Text to remove
remove_text = "|---"

# Function to clean the page content
def clean_page_content(content):
    content = content.replace(remove_text, "")  # Remove specified text
    content = re.sub(r'\s+', ' ', content)  # Replace multiple spaces with a single space
    return content.strip()  # Remove leading and trailing spaces

# Read from the input file and write to the output file
with open(input_file_path, 'r', encoding='utf-8') as infile, open(output_file_path, 'w', encoding='utf-8') as outfile:
    for line in infile:
        # Load the JSON data from the line
        data = json.loads(line)
        # Clean the page content
        if 'page_content' in data:
            data['page_content'] = clean_page_content(data['page_content'])
        # Write the modified JSON back to file
        json.dump(data, outfile)
        outfile.write('\n')

## Optional: Delete all_documents and rename cleaned_documents
## This enables rapid re-running of the script
## Uncomment the following lines if needed
#if os.path.exists("document_data\\all_documents.jsonl"):
#    os.remove("document_data\\all_documents.jsonl")
#    os.rename("document_data\\cleaned_documents.jsonl", "document_data\\all_documents.jsonl")

print("Documents cleaned and saved to:", output_file_path)
