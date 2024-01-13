import json
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv


import os 

load_dotenv()


def process_large_jsonl_file_v4(file_path):
    docs = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            item = json.loads(line)
            # Rearranging the order of text as specified
            page_content = '{}. -> {} -> {} -> {}'.format(
                item.get('chapter_text', ''),
                item.get('lot_text', ''),
                item.get('subcategory_text', ''),
                item.get('fraction_text', '')
            )
            metadata = item
            document = Document(page_content=page_content, metadata=metadata)
            docs.append(document)
    return docs

file_path = 'fractions_denormalized_enhanced.json'  
docs = process_large_jsonl_file_v4(file_path)
docs_for_embedding = [doc.page_content for doc in docs]

# Set up Elasticsearch

openai_api_key = os.getenv("OPENAI_KEY")
embedding = OpenAIEmbeddings(model="text-embedding-ada-002",openai_api_key=openai_api_key)
es_url = "http://localhost:9200/" 
index_name = "test"


db = ElasticsearchStore(
            es_url="http://localhost:9200",
            index_name="test",
            embedding=embedding,
            strategy=ElasticsearchStore.ApproxRetrievalStrategy(),
            distance_strategy="COSINE"
        )

# Loading Embeddings from non existing image
# 
# db = ElasticsearchStore.from_documents(
#     docs,
#     embedding,
#     es_url=es_url,
#     index_name="test",
#     strategy=ElasticsearchStore.ApproxRetrievalStrategy(),
#     distance_strategy="COSINE"
# )

db.client.indices.refresh(index="test")
