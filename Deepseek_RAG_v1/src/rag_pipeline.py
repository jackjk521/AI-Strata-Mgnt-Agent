from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load Qwen-2.5 model
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-2.5-chat")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-2.5-chat")

# RAG function
def rag_query(estate_name, question):
    # Load vector DB for the estate
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
    vector_db = Chroma(persist_directory=f"./vector_dbs/{estate_name}", embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})

    # Retrieve relevant chunks
    docs = retriever.invoke(question)

    # Generate answer
    prompt = ChatPromptTemplate.from_template(
        "You are an estate assistant. Answer the question using ONLY this context: {context}\n Question: {question}"
    )
    inputs = tokenizer(
        prompt.format(context=docs, question=question),
        return_tensors="pt"
    )
    outputs = model.generate(**inputs, max_length=512)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
