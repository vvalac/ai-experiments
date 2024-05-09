from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
import os
import re

# Define the directory for storing JSONL files
data_directory = 'document_data'
os.makedirs(data_directory, exist_ok=True)

# File paths
file_path = os.path.join(data_directory, 'all_documents.jsonl')
visited_file_path = os.path.join(data_directory, 'visited.json')
links_file_path = os.path.join(data_directory, 'links.json')

# Set to manage URLs to scrape
queue = set()
visited = set()

# Regex pattern to match relevant links
pattern = re.compile(r"http://ac2hero\.e5i5o\.com/[\w/-]*\.html$")

# Load visited set and links queue if they exist
if os.path.exists(visited_file_path):
    with open(visited_file_path, 'r', encoding='utf-8') as f:
        visited = set(json.load(f))
if os.path.exists(links_file_path):
    with open(links_file_path, 'r', encoding='utf-8') as f:
        queue = set(json.load(f))

# If the queue is empty, add the base starter URL
if not queue:
    queue.add("http://ac2hero.e5i5o.com")

# Function to save visited set and links queue
def save_state():
    with open(visited_file_path, 'w', encoding='utf-8') as f:
        json.dump(list(visited), f)
    with open(links_file_path, 'w', encoding='utf-8') as f:
        json.dump(list(queue), f)

# Function to save documents to JSONL
def save_docs_to_jsonl(docs, file_path):
    with open(file_path, 'a', encoding='utf-8') as jsonl_file:
        for doc in docs:
            doc_json = json.dumps({'page_content': doc.page_content, 'metadata': doc.metadata})
            jsonl_file.write(doc_json + '\n')

# Function to process each URL
def process_url(url):
    # Normalize URL to ignore hash fragments
    url = url.split('#')[0]
    
    loader = AsyncHtmlLoader([url])
    docs = loader.load()  # Load the HTML as Document objects
    
    soup = BeautifulSoup(docs[0].page_content, 'html.parser')
    for link in soup.find_all('a', href=True):
        # Normalize and resolve the URL
        full_url = urljoin(url, link['href'].split('#')[0])
        if not pattern.match(full_url):
            continue
        if not 'forum' in full_url and full_url not in visited:
            queue.add(full_url)
            visited.add(full_url)

    html2text = Html2TextTransformer()
    print("grabbed html")
    docs_transformed = html2text.transform_documents(docs)
    print("processed html")

    return docs_transformed

# Main function to manage the scraping loop
def main():
    try:
        while queue:
            current_url = queue.pop()
            print(f"Processing {current_url}")  # Debug print
            docs_transformed = process_url(current_url)
            # Save each document to JSONL file
            save_docs_to_jsonl(docs_transformed, file_path)
            
    except KeyboardInterrupt:
        print("Saving state and exiting...")
        save_state()

# Execute the main function
main()
