# Copilot instructions for this repo

These notes make an AI coding assistant productive quickly in this workspace.

Keep edits concise and code-focused. Reference files below when proposing changes.

## Big picture
- Backend: `app.py` implements a FastAPI web app that serves a simple frontend (templates + static) and exposes a POST `/ask` endpoint. It wires a RetrievalQA chain built from a local FAISS vectorstore and a HuggingFace LLM pipeline.
- Indexing: `build_index.py` creates a FAISS index from `my_docs.txt` (or PDF/CSV) and writes the index into `vectorstore_index/` (local files: `index.faiss`, `index.pkl`).
- Variants: `main.py` contains an alternate LLM setup (seq2seq / FLAN-T5) and similar retrieval wiring — treat `app.py` as the primary web entrypoint.
- Small utilities: `cricket_info.py` provides a network-backed (and fallback hardcoded) helper used by `app.py` for cricket-related queries.
- Testing: `test_api.py` and `tests/test_jsonplaceholder_api.py` provide comprehensive API testing workflows for external data sources (see **API Testing Workflow** below).

## Key files and patterns (examples)
- `app.py` — loads embeddings (sentence-transformers/all-MiniLM-L6-v2), builds retriever from local FAISS, loads a LLaMA-like model via HuggingFace `AutoModelForCausalLM`, then exposes `/ask`.
  - Chat history is kept in-memory (`chat_history` list) and only last 5 messages are used to build context.
  - External web lookups: uses `ddgs` (DuckDuckGo) and `wikipedia`; errors are caught and soft-fallbacks returned.
  - Truncation: `truncate_text` uses the model tokenizer to limit tokens (look for `tokenizer.tokenize` usage).
  - CORS middleware is permissive (`allow_origins=['*']`).
- `build_index.py` — loader selection by extension (.txt / .pdf / .csv), `TokenTextSplitter` vs `CharacterTextSplitter` differences (see both `build_index.py` and `main.py`). It saves the vectorstore to `vectorstore_index/`.
- `cricket_info.py` — demonstrates an external API placeholder and a hardcoded fallback. Do not rely on a real API key unless documented; update fallback if changing behavior.
- `requirements.txt` — primary dependencies (langchain, faiss-cpu, sentence-transformers, etc.). Use this file to reproduce the environment.

## Developer workflows and useful commands

### Setup & Run
- Create venv and install deps:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- Rebuild vector index (runs `build_index.py` and writes `vectorstore_index/`):
  ```bash
  python3 build_index.py
  ```
- Start the web server (development):
  ```bash
  uvicorn app:app --reload
  # then open http://127.0.0.1:8000/
  ```
- Quick API test (POST body):
  ```json
  POST /ask
  {"query":"Who is the T20 captain of India?"}
  ```

### API Testing Workflow
The project includes a complete testing suite for external APIs (e.g., JSONPlaceholder, DuckDuckGo, Wikipedia):

**Simple tests (no pytest required):**
```bash
python3 test_api.py
```
Runs CRUD operations (GET, POST, PUT, PATCH, DELETE) against `https://jsonplaceholder.typicode.com/posts`.

**Pytest-based tests:**
```bash
pytest tests/test_jsonplaceholder_api.py -v
```
Includes parametrized tests, mocked tests for CI/CD, and coverage reporting.

**Run via shell script:**
```bash
chmod +x run_tests.sh
./run_tests.sh [simple|pytest|all|coverage]
```

**GitHub Actions workflow:**
`.github/workflows/test-api.yml` runs tests on push/PR and daily schedule. Tests matrix Python 3.9-3.11.

**Test files:**
- `test_api.py` — standalone simple tests with human-readable output (emojis, no dependencies on pytest)
- `tests/test_jsonplaceholder_api.py` — pytest class-based tests with parametrization and mocking
- `API_TESTING_GUIDE.md` — comprehensive guide for adding/maintaining tests

## Project-specific conventions and gotchas
- Documents: code expects a document file at `my_docs.txt` by default. If you change the data file, update `file_path` in `app.py`/`main.py`/`build_index.py`.
- Index storage: vectorstore is saved under `vectorstore_index/` — keep it in gitignore for large indexes (current repo already has one in workspace). If you modify the embedding model, rebuild the index.
- Model/device choices: `app.py` attempts to use `mps` (Apple M-series) when available and falls back to CPU. It also uses `device_map='auto'` and float16/float32. When changing models, verify memory and dtype settings.
- Tokenization/truncation: the project truncates context using the model tokenizer directly (`truncate_text`). When adjusting max tokens, ensure both prompt and model capacities are respected.
- In-memory state: `chat_history` is ephemeral — persistent session/state should be added explicitly if needed.
- External lookups: `improved_duckduckgo_search` and `improved_wikipedia_search` are defensive; avoid introducing blocking network calls on the request path without timeouts.
- Testing: `test_api.py` and pytest tests use real API calls by default (great for development), but include `@patch` mocks for CI/CD to avoid flaky network deps (see `test_mock_get_posts` example).

## Integration points / external dependencies
- HuggingFace models: network download from HF hub; consider local cache or HF auth for private models.
- ddgs (DuckDuckGo scrapper) and `wikipedia` packages: external APIs/scraping; tests should mock these.
- `requests` used in `cricket_info.py` and test suite — placeholder API endpoints; update API key handling if you integrate a real cricket provider.
- JSONPlaceholder API: used in `test_api.py` as a public demo endpoint for testing workflows; production usage should switch to real data sources.

## What to change and where (practical examples)
- To change the embedding model: update `HuggingFaceEmbeddings(model_name=...)` in `app.py` and run `python3 build_index.py` to rebuild `vectorstore_index/`.
- To add query timeouts: wrap `ddgs` and `requests.get` calls with a timeout parameter and propagate partial results to the response (see current `try/except` patterns).
- To persist chat history: replace `chat_history` in `app.py` with a small Redis-backed store and update the context builder to fetch last N messages from Redis.
- To add new API tests: add functions to `test_api.py` (simple approach) or methods to the `TestJSONPlaceholderAPI` class in `tests/test_jsonplaceholder_api.py` (pytest). See `API_TESTING_GUIDE.md` for examples.

## Tests and debugging hints
- There are minimal backend tests for the RAG system itself. When adding tests for `app.py`:
  - Mock the HF model/pipeline to avoid heavy downloads (use a small stubbed pipeline)
  - Mock FAISS retriever (or create a tiny index in-memory)
  - Mock `ddgs`, `wikipedia`, and `requests` calls with canned responses
- API test suite (`test_api.py`, pytest) validates external API behavior:
  - Runs against real JSONPlaceholder by default (for development/CI)
  - Use `@patch` decorator to mock network calls in offline environments
  - See `tests/test_jsonplaceholder_api.py` for examples (`test_mock_get_posts`)
- Debugging startup issues:
  - If model loading crashes on M1/M2, try forcing CPU (`device='cpu'`) or removing `torch_dtype=torch.float16`.
  - Check `vectorstore_index/` presence if retrieval returns empty results.
  - If API tests fail, check internet connectivity or use mocked tests: `pytest tests/test_jsonplaceholder_api.py::TestJSONPlaceholderAPI::test_mock_get_posts -v`

## Minimal acceptance criteria for PRs that change behavior
- If you change embeddings or splitter parameters, include a short script or instructions to rebuild `vectorstore_index/` and validate retrieval quality.
- If you add network calls, include timeouts and a fallback so `/ask` never blocks indefinitely.
- If you add or modify tests, ensure they pass locally: `./run_tests.sh all` should succeed.
- If you change API test endpoints or add new tests, update `API_TESTING_GUIDE.md` with usage examples.

---
If anything here is unclear or you'd like more detail about a particular file (for example, exact prompt format used in `PromptTemplate` or where `index.pkl` is read), tell me which area to expand and I will iterate.
