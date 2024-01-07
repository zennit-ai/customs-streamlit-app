import streamlit as st
import pandas as pd
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from dotenv import load_dotenv
from backend import llm_response


load_dotenv()

# Loading data frame as csv
df = pd.read_csv("fraction.csv")

# Get the OpenAI API key from environment variables
openai_api_key = os.getenv("API_KEY")

# Create an instance of the OpenAIEmbeddings class with the API key
embedding = OpenAIEmbeddings(api_key=openai_api_key)

# Create an instance of the ElasticsearchStore class
es_url = "http://localhost:9200"
index_name = "test"
elastic_vector_search = ElasticsearchStore(
    es_url=es_url, index_name=index_name, embedding=embedding
)

# Streamlit UI
st.title("Busqueda Arancelaria")

# User input for search query
query = st.text_input("Enter your search query:")

# Number of results to display
k = 7

# Search button
if st.button("Search") and query:
    try:
        # Perform Elasticsearch similarity search
        results = elastic_vector_search.similarity_search(query, k=k)
    
    except Exception as e:
        st.error(f"Error during search: {e}")
        results = []

    # Display search results
    st.markdown("### Reslutado de búsqueda:")
    if results:
        with st.spinner("Aguarda, el LLM anda chambeando un vergo"):
            response = llm_response(results, query)
            st.success(response)
    
        fractions_results = []
        # Set to store lot_id and lot_text 
        lot_info = set()
        for result in results:
            # Extraction of fraction from metadata
            fraction = result.metadata.get('id', 'N/A')
            # Extraction of lot text from metadata
            lot_text = result.metadata.get("lot_text")
            lot_id = fraction.split(".")[0]
            # Tuple lot_id and lot_text
            lot_info.add((lot_id, lot_text))

        for lot_id, lot_text in lot_info: # Iterate in tuple set
            st.subheader(f"Lote: {lot_text} Id de lote: {lot_id}")
            fractions_for_lot_id = [result.metadata.get('id', 'N/A') for result in results if result.metadata.get('id', 'N/A').startswith(lot_id)]
            
            if fractions_for_lot_id:
                st.write(f"Fracciones encontradas en el lote {lot_id}: {', '.join(fractions_for_lot_id)}")
                # Filter to display specific columns on the df
                selected_columns = ["id", "text", "unit", "importTariff", "exportTariff", "lot_text", "category_text", "subcategory_text"]

                # Filtering DataFrame based on the selected fraction
                filtered_df = df[df['lot_id'] == int(lot_id)][selected_columns]

                # Displaying the DataFrame for the selected fraction
                # Highlighting fraction results
                
        
                st.dataframe(filtered_df)
            else:
                st.warning(f"No fractions found for Lot id {lot_id}.")

    else:
        st.warning("No results found.")
# Loaders 
# NOM  con base a ley 
# Span
# Title 
# Subtitles separados | Rec and similars 
# Color minimal 
# Highlights in df 
# search bar grande 
# Title principal petite 
# Zennt property 

                                  

        
        
