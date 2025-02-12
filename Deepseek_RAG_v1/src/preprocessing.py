import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastembed import TextEmbedding
from langchain_community.vectorstores import Chroma

# Load and split documents
def load_and_split_documents(estate_folder):
    loader = DirectoryLoader(estate_folder, glob="**/*.pdf")
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {estate_folder}")  # Debug
    if not documents:
        raise ValueError(f"No documents found in {estate_folder}")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    split_docs = text_splitter.split_documents(documents)
    print(f"Split into {len(split_docs)} chunks")  # Debug
    return split_docs

# Create vector database for an estate
def create_vector_db(estate_folder, estate_name):
    documents = load_and_split_documents(estate_folder)
    
    # Initialize FastEmbed's TextEmbedding
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en")
    
    # Extract text from documents
    texts = [doc.page_content for doc in documents]
    
    # Generate embeddings using FastEmbed
    embeddings = list(embedding_model.embed(texts))
    
    # Create Chroma vector store
    persist_directory = f"./vector_dbs/{estate_name}"
    vector_db = Chroma.from_texts(texts, embeddings, persist_directory=persist_directory)
    return vector_db

# Example usage
if __name__ == "__main__":
    estates = ["76_Shenton", "Springhill"]
    for estate in estates:
        print(f"Processing estate: {estate}")
        create_vector_db(f"./data/Raw_estate_data/{estate}", estate)
