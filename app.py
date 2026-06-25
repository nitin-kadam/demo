from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from ddgs import DDGS
import wikipedia
from cricket_info import get_cricket_captain
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import TokenTextSplitter
import torch
import os

# === Load Embeddings ===
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# === Load your file ===
file_path = "my_docs.txt"  # Change this to your actual file name
if file_path.endswith(".txt"):
    loader = TextLoader(file_path)
elif file_path.endswith(".pdf"):
    loader = PyPDFLoader(file_path)
elif file_path.endswith(".csv"):
    loader = CSVLoader(file_path)
else:
    raise ValueError("Unsupported file format")
documents = loader.load()

# === Token-aware Splitter ===
splitter = TokenTextSplitter(chunk_size=400, chunk_overlap=50)
docs = splitter.split_documents(documents)

# === Create FAISS vector store ===
vectorstore = FAISS.from_documents(docs, embedding_model)
retriever = vectorstore.as_retriever()

# === Load LLaMA Model (TinyLlama runs well on M2) ===
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"🚀 Loading {model_id} on {device}")

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if device.type == "mps" else torch.float32,
    device_map="auto"
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9
)

llm = HuggingFacePipeline(pipeline=pipe)

# === Prompt Template ===
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an intelligent assistant. Use the following context to answer the question accurately and concisely.

Context:
{context}

Question:
{question}

Answer:"""
)

# === Create QA Chain ===
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# === Utility functions ===
def improved_duckduckgo_search(query, max_results=3):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results*2)]
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return [{'title': 'No web results found.', 'body': '', 'href': ''}]
    return results[:max_results]

def improved_wikipedia_search(query, sentences=2):
    try:
        page = wikipedia.page(query)
        summary = wikipedia.summary(page.title, sentences=sentences)
        return summary
    except Exception:
        try:
            summary = wikipedia.summary(query, sentences=sentences)
            return summary
        except Exception as e:
            return f"No Wikipedia info found: {e}"

def truncate_text(text, max_tokens=512):
    tokens = tokenizer.tokenize(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return tokenizer.convert_tokens_to_string(tokens)

# === FastAPI App ===
app = FastAPI()

# CORS (so frontend JS can call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# === In-memory chat history (since no Flask session) ===
chat_history = []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    query = data.get("query", "")

    # Add user message
    chat_history.append({"role": "user", "text": query})

    # Build history context
    history_context = ''
    for msg in chat_history[-5:]:
        history_context += f"{msg['role'].capitalize()}: {msg['text']}\n"

    cricket_captain = None
    if "captain" in query.lower() and "india" in query.lower() and "t20" in query.lower():
        cricket_captain = get_cricket_captain("India", "T20")

    ddg_results = improved_duckduckgo_search(query)
    wiki_result = improved_wikipedia_search(query)

    context = history_context + "\n" + wiki_result
    question = query
    context_trunc = truncate_text(context, max_tokens=400)
    question_trunc = truncate_text(question, max_tokens=100)

    if not context_trunc.strip() or not question_trunc.strip():
        bot_answer = 'Sorry, not enough information to answer.'
    else:
        try:
            result = qa_chain.invoke({"context": context_trunc, "question": question_trunc, "query": query})
            bot_answer = result['result']
        except Exception as e:
            bot_answer = f'Sorry, error: {e}'

    chat_history.append({"role": "bot", "text": bot_answer})

    # === Final answer ===
    answer = "<b>🤖 LLaMA-powered Chatbot</b><br>"
    if cricket_captain:
        answer += f"🏏 Cricket Info: Current T20 Captain of India: {cricket_captain}<br>"

    answer += "<b>🔎 Latest Web Information:</b><br>"
    for i, r in enumerate(ddg_results, 1):
        answer += f"{i}. {r['title']}<br>{r['body']}<br><a href='{r['href']}' target='_blank'>{r['href']}</a><br>"

    answer += "<b>🌐 Wikipedia Summary:</b><br>" + wiki_result + "<br>"
    answer += f"<b>🤖 Chatbot Answer:</b><br>{bot_answer}"

    return JSONResponse({"answer": answer})

# Run: uvicorn app:app --reload
