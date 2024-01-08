import json
import time
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv


import os 

load_dotenv()

# Load your JSONL file and create a list of Document objects
def process_jsonl_line_v4(line):
    item = json.loads(line)
    page_content = ' '.join([v for k, v in item.items() if k.endswith('_text')])
    metadata = item
    return Document(page_content=page_content, metadata=metadata)

def process_large_jsonl_file_v4(file_path):
    docs = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            document = process_jsonl_line_v4(line)
            docs.append(document)
    return docs

file_path = 'fractions_denormalized_enhanced.jsonl'  
docs = process_large_jsonl_file_v4(file_path)

# Set up Elasticsearch
openai_api_key =os.getenv("API_KEY")
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

es_url = "http://localhost:9200" # 
index_name = "test_index"



# Create ElasticsearchStore from documents
# Acordarse de poner sleep 
ElasticsearchStore.from_documents(
    docs[:len(docs)//2],
    embedding,
    es_url=es_url,
    index_name="test",
    strategy=ElasticsearchStore.ApproxRetrievalStrategy()
)
time.sleep(40)

ElasticsearchStore.from_documents(
    docs[len(docs)//2:],
    embedding,
    es_url=es_url,
    index_name="test",
    strategy=ElasticsearchStore.ApproxRetrievalStrategy()
)

db = ElasticsearchStore(
    embedding=embedding,
    es_url=es_url,
    index_name="test"
)


# Problem description: 
# when a samller jsonl is provided in the file_path no error is generated
# when the size of the file is increased an token error is generated 
# posible solution: implement chunks
