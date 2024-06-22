import streamlit as st
from dataclasses import dataclass
from py2neo import Graph
 
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
import re

USER = "user"
MESSAGES = 'message'
ASSISTANT = 'ai'
 
custom_css = """
<style>
.chat-container {
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 10px;
    max-height: 400px;
    overflow-y: auto;
    background-color: #f9f9f9;
}
.user-message, .assistant-message {
    padding: 8px;
    border-radius: 8px;
    margin-bottom: 10px;
}
.user-message {
    background-color: #007bff;
    color: white;
    text-align: right;
}
.assistant-message {
    background-color: #e2e2e2;
    color: black;
    text-align: left;
}
/* Custom spinner styles */
[data-testid="stStatusWidget"] div {
    color: blue; /* Change the color of the spinner text */
    font-size: 16px; /* Change the font size */
    font-style: italic; /* Change the font style to italic */
}
</style>
"""
# Apply the custom CSS styles
st.markdown(custom_css, unsafe_allow_html=True)
 
@dataclass
class Message:
    actor: str
    payload: str

NEO4J_URI = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
NEO4J_USERNAME = 'neo4j'
NEO4J_PASSWORD = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 
auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
graph = Graph(NEO4J_URI, auth=auth)
 
embeddings = OllamaEmbeddings(model='llama3')
llm = Ollama(model="llama3")
db3 = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
 
def extract_symptoms_from_query(query):
    pattern = r'WHERE s\.name IN \[(.*?)\]'
    match = re.search(pattern, query, re.IGNORECASE)
    if match:
        symptoms_str = match.group(1)
        symptoms = [symptom.strip().strip('"').strip("'") for symptom in symptoms_str.split(',')]
        return symptoms
    else:
        return None
 
def read_query(query):  
    try:
        result = graph.run(query)
    except:
        result = "Can't give you output right now."
    return result
 
node_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
WITH label AS nodeLabels, collect(property) AS properties
RETURN {labels: nodeLabels, properties: properties} AS output
"""
node_props = read_query(node_properties_query)
 
rel_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE type = "RELATIONSHIP" AND elementType = "node"
RETURN {source: label, relationship: property, target: other} AS output
"""
rels = read_query(rel_query)
 
schema = f"""
Nodes and their properties are the following:
{node_props}
 
The relationships are the following:
{rels}
"""
 
def generate_cypher_query(prompt):
    system_prompt = f"""
    You are an experienced graph databases developer.
    This is the schema representation of a Neo4j database.
    Provide answers in Cypher based on the following schema and example.
    ### Important: when ever you use node Drug denote its object with d eg.(d:Drug)
                   -Disease node's object is g eg. (g:Disease)
                   -Symptom node's object is s eg. (s:Symptom)
                   -Composition node's object is c eg. (c:Composition)
    ### Give only one cypher text.
    ### The Schema
    {schema}
    ### ONLY PROVIDE THE CYPHER TEXT NO EXPLANATION NOTHING
    ### Consider that all the nodes values are in lowercase latters and type of the node starts with capital latter followed by small latters.
    ### Example
    Question:
    ->find alternate of zometa drug
    cypher text- MATCH p=(d:Drug)-[:HAS_COMPOSITION]->(c:Composition)<-[:HAS_COMPOSITION]-(d2:Drug) where d.name='zometa' return d2.name;
    -> Give the drugs for cancer disease.
    cypher text- MATCH p=(d:Drug)-[:TREATS]->(g:Disease) where g.name='cancer' return d.name Limit 5;
    -> I have chest pain, vomiting, nausea. what diseas may i have?
    cypher text- MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptoms) where s.name IN ["vomiting","increased thirst","nausea"] return DISTINCT d.name;
    ### Give answer to the following quetions based on above examples.
    {prompt}
    """
    response = llm.invoke(system_prompt)
    return response
 
def process_response(response):
    if 's.name IN' in response:
        symptoms = extract_symptoms_from_query(response)
        updated_symptoms = []
        for query in symptoms:
            docs = db3.similarity_search(query)
            updated_symptoms.append(docs[0].page_content)
        symptom_list = '["' + '", "'.join(symptoms) + '"]'
        updated_response = response.replace(symptom_list, f'{updated_symptoms}')
        ans = read_query(updated_response)
    else:
        ans = read_query(response)
    return ans
 
def generate_natural_language_from_results(results):
    formatted_results = "\n".join([str(result) for result in results])
    nl_prompt = f"""
    You are an AI language model specifically designed for recommendation.
    Convert the following Cypher query results into a natural language description.
    Description should be a brief paragraph and patient friendly as a doctor is recommending something to a patient.
 
    Results:
    {formatted_results}
 
    Description:
    """
    nl_response = llm.invoke(nl_prompt)
    return nl_response
 
# Streamlit app starts here
def main():
    st.title("Drug recommendation system")
 
    api_key = st.text_input("Insert API Key")
 
    if api_key:
        start_time = st.session_state.get('start_time')
        if start_time is None:
            bot = None
            st.session_state['main_obj'] = bot
 
        if MESSAGES not in st.session_state:
            st.session_state[MESSAGES]= [Message(actor=ASSISTANT, payload="Hi!")]
 
        msg: Message
        for msg in st.session_state[MESSAGES]:
            st.chat_message(msg.actor).write(msg.payload)
 
        prompt: str = st.chat_input("Enter here")
        if prompt:
            st.session_state[MESSAGES].append(Message(actor=USER, payload=prompt))
            st.chat_message(USER).write(prompt)
            with st.spinner("Typing......"):
                cypher_query = generate_cypher_query(prompt)
                results = process_response(cypher_query)
                if results:
                    ans_list = results.data()
                    if ans_list:
                        response = generate_natural_language_from_results(ans_list)
                    else:
                        response = "No results found."
                else:
                    response = "No results found."
                st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=response))
                st.chat_message(ASSISTANT).write(response)
 
if __name__ == "__main__":
    main()