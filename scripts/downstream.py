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
    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Research Library</title>
<style>
* { box-sizing: border-box; }
body { margin: 0; background: #f4f6fa; color: #253047; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.7; }
.topbar { background: #fff; border-bottom: 1px solid #e1e6ef; }
.nav-inner { max-width: 1120px; margin: auto; padding: 24px 28px; display: flex; align-items: center; gap: 28px; flex-wrap: wrap; }
h1 { margin: 0; font-size: 1.55rem; letter-spacing: -.04em; color: #182b4d; }
.search { flex: 1; min-width: 220px; }
.search span { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); }
input { width: 100%; padding: 12px 16px; border: 1px solid #ccd5e3; border-radius: 10px; background: #f8fafc; color: inherit; font: inherit; }
input:focus-visible { outline: 3px solid #a7c7ff; outline-offset: 2px; }
#count { margin: 0; font-size: .92rem; color: #53627b; white-space: nowrap; }
main { max-width: 1120px; margin: auto; padding: 32px 28px 56px; }
article { background: #fff; border: 1px solid #e3e8f0; border-radius: 14px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 4px 14px rgba(25, 43, 76, .06); overflow-wrap: anywhere; }
h2 { margin: 0 0 18px; font-size: 1.3rem; line-height: 1.45; color: #182b4d; }
a { color: #2456a6; text-decoration: none; }
a:hover { text-decoration: underline; }
a:focus-visible { outline: 3px solid #a7c7ff; outline-offset: 3px; }
article p { margin: 12px 0; }
article p:last-child { margin-bottom: 0; }
strong { color: #263c5f; }
#empty { text-align: center; color: #53627b; padding: 40px 16px; }
[hidden] { display: none !important; }
@media (max-width: 640px) {
  .nav-inner { padding: 20px; gap: 14px; }
  .search { order: 3; flex-basis: 100%; min-width: 0; }
  #count { margin-left: auto; white-space: normal; }
  main { padding: 22px 16px 40px; }
  article { padding: 22px; }
  h1 { font-size: 1.3rem; }
}
</style></head><body>
<header class="topbar"><div class="nav-inner">
<h1>Research Library</h1>
<label class="search"><span>Search papers</span><input type="search" id="query" placeholder="Search papers…" aria-controls="papers"></label>
<p id="count" aria-live="polite"></p>
</div></header>
<main id="papers">""" + "".join(entries) + """
<p id="empty" hidden>No papers match your search.</p>
</main><script>
const query = document.getElementById('query');
const papers = Array.from(document.querySelectorAll('article'));
function filterPapers() {
  const term = query.value.trim().toLowerCase();
  let count = 0;
  for (const row of papers) {
    row.hidden = !row.textContent.toLowerCase().includes(term);
    if (!row.hidden) count++;
  }
  document.getElementById('count').textContent = term
    ? count + ' of ' + papers.length + ' papers'
    : papers.length + (papers.length === 1 ? ' paper in library' : ' papers in library');
  const empty = document.getElementById('empty');
  empty.hidden = count !== 0;
  empty.textContent = papers.length ? 'No papers match your search.' : 'No papers in the library yet.';
}
query.addEventListener('input', filterPapers);
filterPapers();
</script></body></html>"""
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
