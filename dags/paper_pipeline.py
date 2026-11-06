import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from scripts.db import init_db, get_processed_filenames, insert_paper, get_all_papers
from scripts.llm_extractor import extract_paper_metadata
from scripts.downstream import render_html_catalog, send_discord_alert


def resolve_storage_dirs() -> tuple[Path, Path]:
    """
    Resolve PAPERS_DIR and OUTPUT_DIR without requiring hardcoded usernames or emails.
    If AUTO_DETECT_GDRIVE=true, automatically finds the mounted Google Drive folder.
    """
    if os.getenv("AUTO_DETECT_GDRIVE", "false").lower() == "true":
        cloud_storage = Path.home() / "Library" / "CloudStorage"
        gdrive_mounts = list(cloud_storage.glob("GoogleDrive-*"))
        if gdrive_mounts:
            for drive_folder_name in ["My Drive", "Meine Ablage", "Mon Drive"]:
                candidate = gdrive_mounts[0] / drive_folder_name / "ResearchLibrary"
                if candidate.exists():
                    return candidate / "papers", candidate / "output"

    papers = (PROJECT_ROOT / os.getenv("PAPERS_DIR", "./mock_drive/papers")).resolve()
    output = (PROJECT_ROOT / os.getenv("OUTPUT_DIR", "./mock_drive/output")).resolve()
    return papers, output


PAPERS_DIR, OUTPUT_DIR = resolve_storage_dirs()


def task_discover_new_pdfs(**context) -> list[str]:
    """Step 1: Check papers/ folder against SQLite and return unprocessed PDF filenames."""
    init_db()
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    
    processed = get_processed_filenames()
    all_pdfs = sorted([f.name for f in PAPERS_DIR.glob("*.pdf")])
    new_pdfs = [pdf for pdf in all_pdfs if pdf not in processed]
    
    print(f"Found {len(new_pdfs)} new PDF(s): {new_pdfs}")
    return new_pdfs


def task_process_pdfs_with_llm(**context) -> list[dict]:
    """Step 2 (Person B): Convert new PDFs to Markdown, extract LLM metadata, and store in SQLite."""
    ti = context["ti"]
    new_pdfs = ti.xcom_pull(task_ids="discover_new_pdfs")
    if not new_pdfs:
        print("No new PDFs to process.")
        return []

    newly_processed = []
    for filename in new_pdfs:
        pdf_path = PAPERS_DIR / filename
        print(f"Processing {filename}...")
        metadata = extract_paper_metadata(pdf_path)
        insert_paper(filename, metadata)
        newly_processed.append({"filename": filename, **metadata})
        
    return newly_processed


def task_generate_html_catalog(**context):
    """Step 3 (Person C): Regenerate output/index.html from SQLite database."""
    papers = get_all_papers()
    output_file = OUTPUT_DIR / "index.html"
    render_html_catalog(papers, output_file)
    print(f"Updated static HTML catalog ({len(papers)} total papers)")


def task_send_discord_notification(**context):
    """Step 4 (Person C): Send Discord webhook notification if new papers were processed."""
    ti = context["ti"]
    newly_processed = ti.xcom_pull(task_ids="process_pdfs_with_llm")
    if not newly_processed:
        print("No new papers processed in this run. Skipping Discord notification.")
        return
    send_discord_alert(newly_processed)


default_args = {
    "owner": "info-h420-group",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="research_paper_pipeline",
    default_args=default_args,
    description="Convert research PDFs to Markdown, extract metadata with local LLM, and build HTML catalog",
    schedule=timedelta(minutes=5),
    start_date=datetime(2026, 11, 1),
    catchup=False,
    max_active_runs=1,
    tags=["assignment3", "research_library"],
) as dag:

    discover_new_pdfs = PythonOperator(
        task_id="discover_new_pdfs",
        python_callable=task_discover_new_pdfs,
    )

    process_pdfs_with_llm = PythonOperator(
        task_id="process_pdfs_with_llm",
        python_callable=task_process_pdfs_with_llm,
    )

    generate_html_catalog = PythonOperator(
        task_id="generate_html_catalog",
        python_callable=task_generate_html_catalog,
    )

    send_discord_notification = PythonOperator(
        task_id="send_discord_notification",
        python_callable=task_send_discord_notification,
    )

    discover_new_pdfs >> process_pdfs_with_llm >> generate_html_catalog >> send_discord_notification