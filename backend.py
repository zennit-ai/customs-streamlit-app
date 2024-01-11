
# LLM integration 
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from dotenv import load_dotenv
import os 
import re 

load_dotenv()

openai_api_key = os.getenv("API_KEY")

def replace_fractions(text, fractions_dict):
    # Buscar fracciones en el texto (formato nnnn.nn.nn)
    matches = re.finditer(r"\b\d{4}\.\d{2}\.\d{2}\b", text)
    for match in matches:
        fraction = match.group()
        if fraction in fractions_dict:
            # Reemplazar fracción por detalle con tarifas, incluyendo paréntesis
            details = fractions_dict[fraction]
            replacement = f"({fraction}, Arancel de importación: {details['import_tariff']}, Arancel de exportación: {details['export_tariff']})"
            text = text.replace(fraction, replacement)
    return text




# LLM integration 
def llm_response(results, query):
    shown_results = []  
    results_string = ""
    fractions_dict = {}  

    # Pasando resultados a formato para LLM
    for i, result in enumerate(results):
        fraction = result.metadata['id']
        name = result.page_content
        export_tariff = result.metadata['exportTariff']
        import_tariff = result.metadata['importTariff']


    if fraction not in shown_results:
        result_line = f"{i + 1}. Fracción: {fraction}, Nombre: {name}\n"
        results_string += result_line+"\n"  # Append the result to the string
        shown_results.append(result)  # Add the result to the shown list
                # Almacenar en el diccionario
        fractions_dict[fraction] = {
            'export_tariff': export_tariff,
            'import_tariff': import_tariff
        }


    prompt = PromptTemplate.from_template(
        """
Eres un agente aduanal y te encuentras hablando directamente con un cliente a encontrar una fraccion arancelaria. Tu misión es ser util.Instrucciones= [Recibirás un listado de descripciones detalladas de productos, Cada descripción debe ser única y diferente. Tambien recibiras un query del usuario, relacionado con la clasificación de un producto. 

Tu trabajo es hacer un Análisis de las Opciones de Arancel. debes analizar y comparar la descripción ingresada por el usuario con las lista de resultados de fracciones arancelarias proporcionada. Con el fin de seleccionar la opción de arancel correspondiente con el query del usuario. 

Manejo de Incertidumbre:
Si no estás completamente seguro sobre cuál opción de arancel corresponde al query del usuario, debes identificar que ambiguedad y hacerle preguntas claras y explicativas al usario para resolver ambigüedades y obtener información adicional necesaria para clasificar el producto entre las diferentes opciones presentadas.Solo debes de formular preguntas que ayuden a clasificar el producto entre las posibles opciones proporcionadas.

Como debes de responder:
Debes presentar la opción de arancel que consideres más adecuada para el query del usuario. Recuerda formular tu respuesta de una manera simple y clara. Recuerda que estas hablando con el usuario y lo debes ayudar. Ya sea sugiriendo la fracción arancelaria correcta o pidiendo información adicional para clasificar el producto y por que requieres de esa información especificamente, si haces referencia a alguna fracción arancelaria, debes incluir el número de fracción arancelaria y la descripción de la misma. 

Notas Adicionales:
Es importante que mantengas un enfoque objetivo y basado en la información proporcionada.Y presentes la informacion con el fin de que el usuario pueda entenderla facilmente. Cada fraccion es unica y diferente.
Tu habilidad para hacer clasificar correctamente el query del usario con las descripciones de las fracciones es clave para el éxito en la selección precisa del arancel. 

Usuario:"Busco la fraccion arancelaria corresponiente a: [ {user_query} ]"

Opciones de arancel: [{results_string}]

"""
    )

    model = OpenAI(api_key="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", temperature=0, model='gpt-3.5-turbo-instruct')# usar gpt4
    chain = prompt | model
    answer=chain.invoke({'user_query':query,'results_string':results_string})
    answer_content = answer.content
    return replace_fractions(answer_content, fractions_dict)

