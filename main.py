from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import TokenTextSplitter
from ddgs import DDGS
import wikipedia
from cricket_info import get_cricket_captain

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

# === Token-aware Splitter (better for seq2seq models) ===
splitter = TokenTextSplitter(chunk_size=400, chunk_overlap=50)
docs = splitter.split_documents(documents)

# === Create FAISS vector store ===
vectorstore = FAISS.from_documents(docs, embedding_model)
retriever = vectorstore.as_retriever()

# === Load LLM ===
model_id = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
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

# === Create QA Chain with custom prompt ===
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# === DuckDuckGo Search Functionality ===
def improved_duckduckgo_search(query, max_results=3):
    """Perform a DuckDuckGo search with improved query and filter for English/India-specific results."""
    specific_query = f"{query} India site:en"
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(specific_query, max_results=max_results*2)]
    except Exception:
        return []
    # Filter for English/India-specific results
    filtered = []
    for r in results:
        url = r.get('href', '')
        title = r.get('title', '')
        # Only include results with English letters and India in title or url
        if any(x in url for x in ['.in', 'india']) or 'India' in title or 'Rupee' in title:
            filtered.append(r)
        elif all(ord(c) < 128 for c in title):
            filtered.append(r)
        if len(filtered) >= max_results:
            break
    return filtered

# === Wikipedia Search Functionality ===
def improved_wikipedia_search(query, sentences=2):
    """Search Wikipedia for more specific info."""
    try:
        page = wikipedia.page(query)
        summary = wikipedia.summary(page.title, sentences=sentences)
        return summary
    except Exception:
        # fallback to basic summary
        try:
            summary = wikipedia.summary(query, sentences=sentences)
            return summary
        except Exception as e:
            return f"No Wikipedia info found: {e}"

# === Token Truncation Functionality ===
def truncate_text(text, max_tokens=512):
    """Truncate text to fit within max token limit for the model."""
    tokens = tokenizer.tokenize(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return tokenizer.convert_tokens_to_string(tokens)

# Removed terminal input loop for web-only usage


