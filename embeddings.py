import json
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Load your JSONL file and create a list of Document objects
def process_jsonl_line_v4(line):
    item = json.loads(line)
    page_content = ' '.join([v for k, v in item.items() if k.endswith('_text')])
    metadata = item
    return Document(page_content=page_content, metadata=metadata)

def process_large_jsonl_file_v4(file_path, chunk_size=1000):
    docs = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i in range(0, len(lines), chunk_size):
            chunk = lines[i:i + chunk_size]
            chunk_docs = [process_jsonl_line_v4(line) for line in chunk]
            docs.extend(chunk_docs)
    return docs

file_path = 'fractions_denormalized_enhanced.jsonl'
docs = process_large_jsonl_file_v4(file_path)

# Set up Elasticsearch
openai_api_key = os.getenv("API_KEY")
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

es_url = "http://localhost:9200"
index_name = "test_index"

# Retry function for embedding with a delay
def embed_with_retry(text):
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            return embedding.embed(text)
        except Exception as e:
            if "RateLimitError" in str(e):
                print(f"Rate limit exceeded. Retrying in 5 seconds... (Attempt {retries + 1}/{max_retries})")
                time.sleep(5)
                retries += 1
            else:
                raise
    raise Exception("Max retries reached. Unable to obtain embeddings.")

# Create ElasticsearchStore from documents
db = ElasticsearchStore.from_documents(
    docs,
    embed_fn=embed_with_retry,
    es_url=es_url,
    index_name="test",
    strategy=ElasticsearchStore.ApproxRetrievalStrategy()
)
