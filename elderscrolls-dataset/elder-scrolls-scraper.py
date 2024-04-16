from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import json
import os
import re

# Define the directory for storing JSONL files
data_directory = 'document_data'
os.makedirs(data_directory, exist_ok=True)  # Create the directory if it doesn't exist

# File paths
file_path = os.path.join(data_directory, 'all_documents.jsonl')
visited_file_path = os.path.join(data_directory, 'visited.json')
links_file_path = os.path.join(data_directory, 'links.json')

# Queue to manage URLs to scrape
queue = set()
visited = set()

# Regular expression pattern to match relevant links
pattern = re.compile(r"https://en.uesp.net/wiki/Lore:[\w_]+$")

# Load visited set and links queue if they exist
if os.path.exists(visited_file_path):
    with open(visited_file_path, 'r', encoding='utf-8') as f:
        visited = set(json.load(f))
if os.path.exists(links_file_path):
    with open(links_file_path, 'r', encoding='utf-8') as f:
        queue = json.load(f)

# If the queue is empty, add the base starter URL
if not queue:
    queue.append("https://en.uesp.net/wiki/Lore:Main_Page")

# Function to save visited set and links queue
def save_state():
    with open(visited_file_path, 'w', encoding='utf-8') as f:
        json.dump(list(visited), f)
    with open(links_file_path, 'w', encoding='utf-8') as f:
        json.dump(queue, f)

# Function to save documents to JSONL
def save_docs_to_jsonl(docs, file_path):
    with open(file_path, 'a', encoding='utf-8') as jsonl_file:
        for doc in docs:
            doc_json = json.dumps({'page_content': doc.page_content, 'metadata': doc.metadata})
            jsonl_file.write(doc_json + '\n')

# Function to process each URL
def process_url(url):
    if url in visited:
        return [], []
    
    loader = AsyncHtmlLoader([url])
    docs = loader.load()  # Load the HTML as Document objects
    
    # Parse HTML for link extraction from the first document's page_content (raw HTML)
    soup = BeautifulSoup(docs[0].page_content, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        full_url = urljoin(url, link['href'])
        if pattern.match(full_url) and full_url not in visited:
            # Check if the URL is a redirect and split at &oldid=
            parsed_url = urlparse(full_url)
            query_params = parse_qs(parsed_url.query)
            if "oldid" in query_params:
                base_url = parsed_url._replace(query="")
                base_url_str = base_url.geturl()
                if base_url_str not in visited:
                    links.append(base_url_str)
                    visited.add(base_url_str)
            else:
                links.append(full_url)
                visited.add(full_url)

    # Transform HTML to text and return Document objects
    html2text = Html2TextTransformer()
    docs_transformed = html2text.transform_documents(docs)
    
    return docs_transformed, links

# Main function to manage the scraping loop
def main():
    try:
        while queue:
            current_url = queue.pop(0)
            docs_transformed, links = process_url(current_url)
            
            # Save each document to JSONL file
            save_docs_to_jsonl(docs_transformed, file_path)
            
            # Add new links to the queue
            queue.extend(links)
    except KeyboardInterrupt:
        print("Saving state and exiting...")
        save_state()

# Execute the main function
main()
