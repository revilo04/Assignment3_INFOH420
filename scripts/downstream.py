import html
import os
from pathlib import Path
from urllib.parse import quote

import requests


def render_html_catalog(papers, output_file):
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    for paper in papers:
        title = html.escape(paper["title"])
        summary = html.escape(paper["summary"])
        category = html.escape(paper["category"])
        keywords = html.escape(", ".join(paper["keywords"]))
        filename = quote(paper["filename"], safe="")
        entries.append(
            f'<article><h2>Title: <a href="../papers/{filename}">{title}</a></h2>'
            f'<p><strong>Summary:</strong> {summary}</p>'
            f'<p><strong>Category:</strong> {category}</p>'
            f'<p><strong>Keywords:</strong> {keywords}</p></article>'
        )
    page = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Research Library</title><main><h1>Research Library</h1>
<label>Search papers <input type="search" id="query"></label>
<p id="count" aria-live="polite"></p>""" + "".join(entries) + """
</main><script>
const query = document.getElementById('query');
function filterPapers() {
  const term = query.value.trim().toLowerCase();
  let count = 0;
  for (const row of document.querySelectorAll('article')) {
    row.hidden = !row.textContent.toLowerCase().includes(term);
    if (!row.hidden) count++;
  }
  document.getElementById('count').textContent = count + (count === 1 ? ' paper' : ' papers');
}
query.addEventListener('input', filterPapers);
filterPapers();
</script></html>"""
    output_file.write_text(page, encoding="utf-8")


def send_discord_alert(newly_processed):
    if not newly_processed:
        return
    url = os.getenv("DISCORD_WEBHOOK_URL")
    if not url or url.endswith("your_webhook_here"):
        raise ValueError("Set DISCORD_WEBHOOK_URL in the project .env before sending alerts.")
    for paper in newly_processed:
        message = f"New research paper: {paper['title']}"
        response = requests.post(
            url, json={"content": message[:2000], "allowed_mentions": {"parse": []}},
            timeout=15,
        )
        if not response.ok:
            raise RuntimeError(f"Discord returned HTTP {response.status_code}")
