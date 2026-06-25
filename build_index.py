from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# 1. Load your documents (replace with your file)
loader = TextLoader("my_docs.txt")  
docs = loader.load()

# 2. Split into chunks
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = splitter.split_documents(docs)

# 3. Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 4. Build FAISS vectorstore
vectorstore = FAISS.from_documents(docs, embeddings)

# 5. Save index
vectorstore.save_local("vectorstore_index")

print("✅ FAISS index rebuilt and saved at vectorstore_index/")
