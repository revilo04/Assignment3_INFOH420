

./start_airflow.sh


# INFO-H420 Assignment 3: Research Library Airflow Pipeline

**Repository:** [https://github.com/revilo04/Assignment3_INFOH420](https://github.com/revilo04/Assignment3_INFOH420)

An automated local data pipeline built with [Apache Airflow](https://airflow.apache.org/docs/), [PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/), [Ollama](https://ollama.com/) / [LM Studio](https://lmstudio.ai/) (via the [OpenAI Python SDK](https://github.com/openai/openai-python)), and [SQLite (`sqlite3`)](https://docs.python.org/3/library/sqlite3.html) that monitors a [Google Drive for Desktop](https://www.google.com/drive/download/) `papers/` directory, extracts structured metadata from research PDFs, generates an interactive static HTML library, and posts notifications via [Discord Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

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
