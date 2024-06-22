from langchain_community.llms import Ollama
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.docstore.document import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings

documents = ["vomiting", "abdominal pain", "nausea", "increased thirst", "frequent urination", "fatigue", "blurred vision", "deep breathing", "unintended weight loss", "slow healing sores", "frequent infections", "excessive production of ketone bodies", "kussmaul breathing", "dry mouth", "increased hunger", "itchy skin", "nipple changes", "breast pain", "breast tissue swelling", "nipple retraction", "breast rash", "nipple discharge", "enlarged lymph nodes", "breast itching", "changes in breast size or shape", "increased breast sensitivity", "changes in breast density", "breast ulceration", "breast vein appearance", "persistent cough", "shortness of breath", "easy bruising or bleeding", "night sweats", "swollen lymph nodes", "fever or chills", "shortness of breath", "rashes or itchy skin", "frequent infections", "fatigue", "frequent nosebleeds", "headaches", "dizziness or lightheadedness", "petechiae (tiny red spots on the skin)", "unexplained weight loss", "paleness", "abdominal pain or swelling", "bone or joint pain", "coughing up blood", "hoarseness", "shortness of breath", "feeling tired or weak", "infections such as bronchitis", "blood clots", "persistent cough that worsens", "loss of appetite", "pneumonia that don't go away or keep coming back", "chest pain that worsens with deep breathing, coughing, or laughing", "unexplained weight loss", "new onset of wheezing", "swelling in the face or neck", "bone pain", "nail clubbing", "headache", "coughing up blood or mucus", "chest pain", "pain with breathing or coughing", "fever", "chills", "night sweats", "weight loss", "not wanting to eat", "tiredness", "not feeling well in general", "fever", "fatigue", "chest pain", "chest pressure or tightness", "vomiting", "coughing or wheezing", "nausea", "anxiety like panic attack", "neck or jaw pain", "arms or back pain", "heartburn or indigestion", "sweaty or clammy skin", "shortness of breath", "dizziness", "lightheadedness", "trouble sleeping (insomnia)"]

ldoc = []
for text in documents:
    ldoc.append(Document(page_content=text))

# print(ldoc)

embeddings = (
    OllamaEmbeddings(model = 'llama3')
)

# load it into Chroma
# db = Chroma.from_documents(ldoc, embeddings, persist_directory="./chroma_db")

# print(db)

db3 = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

query = 'I am feeling pain while breathing and coughing'

docs = db3.similarity_search(query)
print(docs[0].page_content)


'''

user_query >> 
            prompt >> 
                    chyper >> 
                        stand [simi] 
                                >> chyper >> neo4j
MATCH (d:Drug)-[:TREATS]->(e:Disease) WHERE e.name IN ["chest pain", "neck pain", "vomiting"] RETURN DISTINCT d.name AS drugName, COLLECT(e.name) AS diseaseNames;


'''