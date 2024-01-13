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
# Higlight function 
def id_highlight(row, lot_ids):
    return ['background-color: #173928'] * len(row) if row['id'] in lot_ids else ['background-color: black'] * len(row)


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

# Usage message 
with st.expander("¿Cómo funciona?"):
        st.markdown("""
#### Búsqueda Arancelaria

Esta sección te permite buscar la fracción arancelaria y conocer su arancel de importación y exportación. 
En el resultado, se proporciona la opción que mejor se ajusta a la búsqueda, 
junto con recomendaciones para mejorarla en caso de que presente ambigüedades.

#### Posibles Fracciones Relacionadas

Si la búsqueda no arrojó los resultados esperados incluso después de haber probado las recomendaciones, 
esta sección presenta varias opciones posibles de aranceles en las cuales puedes buscar. 
También puedes experimentar con nuevas formas de búsqueda para obtener información más precisa y específica.

[¿Tienes dudas?](https://google.com)                   
                                        
""")
# Streamlit UI
st.title("Busqueda Arancelaria")

# User input for search query
query = st.text_input("Ingrese su arancel a buscar:")

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
        with st.spinner("Porfavor espere"):
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
        
        
        st.markdown("### Posibles fracciones relacionadas:")
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
                
        
                #st.dataframe(filtered_df)
                st.dataframe(filtered_df.style.apply(id_highlight, lot_ids=fractions_for_lot_id, axis=1))
            else:
                st.warning(f"No fractions found for Lot id {lot_id}.")

    else:
        st.warning("No results found.")

# Based on lot_id higlight each lot_id values for the data frame displayed

                                  

        
        
