from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain.schema import Document
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
import re
import os

# Define the directory for storing JSONL files
data_directory = 'document_data'
os.makedirs(data_directory, exist_ok=True)  # Create the directory if it doesn't exist

# Queue to manage URLs to scrape
queue = ["https://en.uesp.net/wiki/Lore:Main_Page"]
visited = set(queue)  # Keep track of visited URLs to avoid loops

# Regular expression pattern to match relevant links
pattern = re.compile(r"https://en.uesp.net/wiki/Lore:[\w_]+$")

# File path for JSONL storage
file_path = os.path.join(data_directory, 'all_documents.jsonl')

# Function to save documents to JSONL
def save_docs_to_jsonl(docs, file_path):
    with open(file_path, 'a', encoding='utf-8') as jsonl_file:
        for doc in docs:
            doc_json = json.dumps({'page_content': doc.page_content, 'metadata': doc.metadata})
            jsonl_file.write(doc_json + '\n')

# Function to process each URL
def process_url(url):
    loader = AsyncHtmlLoader([url])
    docs = loader.load()  # Load the HTML as Document objects
    
    # Parse HTML for link extraction from the first document's page_content (raw HTML)
    soup = BeautifulSoup(docs[0].page_content, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        full_url = urljoin(url, link['href'])
        if pattern.match(full_url) and full_url not in visited:
            links.append(full_url)
            visited.add(full_url)

    # Transform HTML to text and return Document objects
    html2text = Html2TextTransformer()
    docs_transformed = html2text.transform_documents(docs)
    
    return docs_transformed, links

# Main function to manage the scraping loop
def main():
    while queue:
        current_url = queue.pop(0)
        docs_transformed, links = process_url(current_url)
        
        # Save each document to JSONL file
        save_docs_to_jsonl(docs_transformed, file_path)
        
        # Add new links to the queue
        queue.extend(links)

# Execute the main function
main()
