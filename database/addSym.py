NEO4J_URI = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
NEO4J_USERNAME = 'neo4j'
NEO4J_PASSWORD = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
 
auth=(NEO4J_USERNAME,NEO4J_PASSWORD)

from py2neo import Graph, Node, Relationship
import pandas as pd
from tqdm import tqdm

# Connect to the Neo4j database
graph = Graph(NEO4J_URI, auth=auth)

# Load the data from the CSV file
file_path = 'sym.csv'
df = pd.read_csv(file_path)

for index, row in df.iterrows():
    disease_node = Node("Disease", name=row['disease'].lower())
    graph.merge(disease_node, "Disease", "name")
    for i in range(1,16):
        name=f"s{i}"
        if(row[name]!="X"):
            symtom_node=Node("Symptoms",name=row[name].lower())
            graph.merge(symtom_node,"Symptoms","name")
            symtom_disease_rel=Relationship(disease_node,"HAS_SYMPTOM",symtom_node)
            graph.merge(symtom_disease_rel)