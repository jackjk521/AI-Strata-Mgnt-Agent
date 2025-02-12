from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from rag_pipeline import rag_query
app = FastAPI()

class QueryRequest(BaseModel):
    estate: str
    question: str

@app.post("/ask")
async def ask(query: QueryRequest):
    try:
        answer = rag_query(query.estate, query.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="templates"), name="static")

@app.get("/")
async def serve_frontend():
    with open("templates/index.html", "r") as file:
        return HTMLResponse(content=file.read())