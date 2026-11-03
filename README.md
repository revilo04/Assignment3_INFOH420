# INFO-H420 Assignment 3: Research Library Airflow Pipeline

**Repository:** [https://github.com/revilo04/Assignment3_INFOH420](https://github.com/revilo04/Assignment3_INFOH420)

An automated local data pipeline built with [Apache Airflow](https://airflow.apache.org/docs/), [PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/), [Ollama](https://ollama.com/) (via the [OpenAI Python SDK](https://github.com/openai/openai-python)), and [SQLite (`sqlite3`)](https://docs.python.org/3/library/sqlite3.html) that monitors a [Google Drive for Desktop](https://www.google.com/drive/download/) `papers/` directory, extracts structured metadata from research PDFs, generates an interactive static HTML library, and posts notifications via [Discord Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

## Project Structure

```text
├── dags/
│   └── paper_pipeline.py     # Main Airflow DAG and task orchestration
├── scripts/
│   ├── db.py                 # SQLite database initialization and CRUD helpers
│   ├── llm_extractor.py      # (Person B) PyMuPDF4LLM conversion + Local LLM JSON extraction
│   └── downstream.py         # (Person C) Static HTML generator + Discord webhook client
├── data/                     # Local SQLite database storage (git-ignored, outside Drive)
├── mock_drive/               # Fallback local test folders (papers/ and output/)
├── start_airflow.sh          # Helper script to configure AIRFLOW_HOME and launch standalone
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variable template
```

## Clone & Set up virtual environment

```Shell
git clone [https://github.com/revilo04/Assignment3_INFOH420.git](https://github.com/revilo04/Assignment3_INFOH420.git)
cd Assignment3_INFOH420
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Configure environment variables

```shell
cp .env.example .env
```

## Start Local LLM Server

```shell
ollama pull llama3.2:3b
ollama serve
```

## Launch Airflow Standalone

```shell
./start_airflow.sh
```


```
- Open http://localhost:8080 in your browser.
- Log in using username admin and the password stored in airflow_home/standalone_admin_password.txt.
- Unpause and trigger the research_paper_pipeline DAG
```
## PDF Conversion and Metadata Extraction

`scripts/llm_extractor.py` converts PDFs to Markdown using PyMuPDF4LLM and extracts metadata using the local Ollama model `llama3.2:3b`.

The function `extract_paper_metadata(pdf_path)` returns a dictionary containing `title`, `summary`, `keywords`, and `category`. Responses are parsed with `json.loads()` and checked for required fields and types. Invalid responses are retried once.

Long PDFs are processed in chunks, and their results are progressively merged. Intermediate summaries may lose detail. Chunk sizes are calculated from the running model’s context capacity, reserving space for instructions and responses. The number of chunks varies with the document length. Chunk metadata is merged in multiple rounds until a single record remains.

### Configuration

Ollama must be running with `llama3.2:3b` installed. Set these values in the project’s `.env` file:

```env
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3.2:3b
```

### Run Without Airflow

From the project root, using the project’s Python environment:

```bash
python -c "import json; from scripts.llm_extractor import extract_paper_metadata; print(json.dumps(extract_paper_metadata('mock_drive/papers/attention_is_all_you_need.pdf'), indent=2, ensure_ascii=False))"
```

On Windows PowerShell, replace `python` with `.\.venv\Scripts\python.exe` if the environment is not activated.

This command prints the extracted metadata without writing to SQLite or triggering HTML generation and Discord notifications.