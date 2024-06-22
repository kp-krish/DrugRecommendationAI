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
file_path = 'drugs(main).csv'
df = pd.read_csv(file_path)

# Clear the graph
graph.delete_all()

# Function to create or merge nodes and relationships
def create_nodes_and_relationships(row):
    try:
        # Create or merge Drug node
        drug_node = Node("Drug", name=row['drug_name'].lower())
        graph.merge(drug_node, "Drug", "name")

        # Create or merge Disease node
        disease_node = Node("Disease", name=row['disease'].lower())
        graph.merge(disease_node, "Disease", "name")

        # Create relationship between Drug and Disease
        drug_disease_rel = Relationship(drug_node, "TREATS", disease_node)
        graph.merge(drug_disease_rel)

        if pd.notna(row['generic_name']) and row['generic_name'] != "X" and pd.notna(row['composition']) and row['composition'] != "X":
            generic_node = Node("Drug", name=row['generic_name'].lower())
            graph.merge(generic_node, "Drug", "name")
            composition_node = Node("Composition", formula=row['composition'].lower())
            graph.merge(composition_node, "Composition", "formula")
            generic_composition_rel = Relationship(generic_node, "HAS_COMPOSITION", composition_node)
            graph.merge(generic_composition_rel)
        # If generic_name is "X" and composition is not "X", create relationship between Drug and Composition
        elif row['generic_name'] == "X" and pd.notna(row['composition']) and row['composition'] != "X":
            composition_node = Node("Composition", formula=row['composition'].lower())
            graph.merge(composition_node, "Composition", "formula")
            # Create relationship between Drug and Composition
            drug_composition_rel = Relationship(drug_node, "HAS_COMPOSITION", composition_node)
            graph.merge(drug_composition_rel)

    except Exception as e:
        print(f"Error processing row {row}: {e}")

# Process each row in the dataframe with progress tracking
for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    create_nodes_and_relationships(row)

print("Data import complete.")
