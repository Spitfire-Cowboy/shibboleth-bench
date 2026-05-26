#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'dataset' / 'items.jsonl'
HARNESS_RESULTS = ROOT / 'results' / 'livefire-may-2026.json'
OPENAI_FRONTIER_RESULTS = ROOT / 'results' / 'livefire-openai-gpt5x-2026-05-26.json'
CLAUDE_RESULTS = ROOT / 'results' / 'claude-may-2026.json'
SITE = ROOT / 'site'
IMAGES_OUT = SITE / 'images'
RESULTS_OUT = SITE / 'results'
CUSTOM_DOMAIN = 'shibboleth.spitfirecowboy.com'

PUBLISHED_RESULTS = [
    ROOT / 'results' / 'livefire-may-2026.json',
    ROOT / 'results' / 'livefire-may-2026.md',
    ROOT / 'results' / 'livefire-may-2026.csv',
    ROOT / 'results' / 'livefire-may-2026.json.ots',
    ROOT / 'results' / 'livefire-openai-gpt5x-2026-05-26.json',
    ROOT / 'results' / 'livefire-openai-gpt5x-2026-05-26.md',
    ROOT / 'results' / 'livefire-openai-gpt5x-2026-05-26.csv',
    ROOT / 'results' / 'livefire-openai-gpt5x-2026-05-26.json.ots',
    ROOT / 'results' / 'claude-may-2026.json',
    ROOT / 'results' / 'claude-may-2026.md',
    ROOT / 'results' / 'claude-may-2026.json.ots',
]

CSS = """
:root {
  color-scheme: light;
  --bg: #f6f2e8;
  --card: #fffdfa;
  --ink: #221b16;
  --muted: #6c625a;
  --line: #d9cfbf;
  --accent: #7d3f1d;
  --accent-soft: #efe0d1;
  --ok: #205c3b;
  --warn: #8a5a13;
  --bad: #7a1f1f;
}
* { box-sizing: border-box; }
body { margin: 0; font: 16px/1.6 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--ink); }
a { color: var(--accent); }
a:hover { opacity: .85; }
code { font-size: 12px; }
.wrapper { max-width: 1100px; margin: 0 auto; padding: 28px 20px 64px; }
.hero { padding: 24px 0 10px; }
.kicker { text-transform: uppercase; letter-spacing: .12em; color: var(--muted); font-size: 12px; font-weight: 700; }
h1 { font-size: clamp(2.2rem, 5vw, 3.5rem); line-height: 1.05; margin: 12px 0 14px; max-width: 10ch; }
.lede { max-width: 720px; font-size: 1.05rem; color: var(--muted); margin: 0; }
.badges, .jump-links { display:flex; flex-wrap:wrap; gap:10px; margin:18px 0 0; }
.badge, .jump-links a { border:1px solid var(--line); background: var(--card); border-radius:999px; padding:8px 12px; font-size:14px; text-decoration:none; }
.jump-links { margin-top: 12px; }
.section { margin-top: 34px; }
.section h2 { font-size: 1.45rem; margin: 0 0 12px; }
.grid { display:grid; gap:16px; }
.grid.cols-2 { grid-template-columns: repeat(auto-fit, minmax(280px,1fr)); }
.grid.cols-3 { grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); }
.card { background: var(--card); border:1px solid var(--line); border-radius: 18px; padding: 18px; box-shadow: 0 1px 0 rgba(0,0,0,.03); }
.card h3 { margin: 0 0 6px; font-size: 1rem; }
.card p, .card ul { margin: 0; color: var(--muted); }
.card ul { padding-left: 18px; }
.table-wrap { overflow-x: auto; }
table { width:100%; border-collapse: collapse; background: var(--card); border:1px solid var(--line); border-radius:18px; overflow:hidden; }
th, td { padding: 12px 14px; border-bottom: 1px solid var(--line); text-align:left; vertical-align: top; }
th { background: #f2ece0; font-size: 14px; }
tr:last-child td { border-bottom: none; }
.score-ok { color: var(--ok); font-weight: 700; }
.score-mid { color: var(--warn); font-weight: 700; }
.score-bad { color: var(--bad); font-weight: 700; }
.gallery { display:grid; gap:16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); margin-top: 14px; }
.figure { background: var(--card); border:1px solid var(--line); border-radius:18px; padding:14px; }
.figure .image-link { display:block; }
.figure img { width:100%; height:auto; border-radius:12px; display:block; background:#fff; aspect-ratio: 4 / 3; object-fit: cover; }
.figure h3 { margin: 12px 0 6px; font-size: 1rem; }
.figure p { margin: 0 0 6px; }
.meta { color: var(--muted); font-size: 14px; }
.summary-line { margin-top: 10px; font-size: 14px; color: var(--muted); }
details { margin-top: 10px; }
details summary { cursor: pointer; font-weight: 600; color: var(--accent); }
.item-results ul { margin: 8px 0 0; padding-left: 18px; }
.item-results li { margin: 0 0 4px; }
.footer { margin-top: 52px; color: var(--muted); font-size: 14px; }
@media (max-width: 640px) {
  .wrapper { padding-inline: 14px; }
  th, td { padding: 10px; }
  h1 { max-width: none; }
}
"""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def load_dataset() -> list[dict]:
    rows = []
    for line in DATASET.read_text(encoding='utf-8').splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def score_class(correct: int, total: int) -> str:
    pct = correct / total if total else 0
    if pct >= 0.9:
        return 'score-ok'
    if pct >= 0.7:
        return 'score-mid'
    return 'score-bad'


def item_status_class(label: str) -> str:
    return {'correct': 'score-ok', 'partial': 'score-mid'}.get(label, 'score-bad')


def render_answer(item: dict) -> str:
    parsed = item.get('parsed_answer')
    if parsed in (None, ''):
        return '—'
    if isinstance(parsed, (int, float)):
        return html.escape(str(parsed))
    text = str(parsed).strip()
    if text.startswith('{') or text.startswith('['):
        try:
            data = json.loads(text)
            if isinstance(data, dict) and 'answer' in data:
                answer = data.get('answer')
                return html.escape('—' if answer in (None, '') else str(answer))
        except Exception:
            return '—'
    return html.escape(text)


def summarize_item_results(dataset: list[dict], snapshots: list[tuple[str, dict]]) -> tuple[dict[str, list[str]], dict[str, dict]]:
    by_item = {row['id']: [] for row in dataset}
    summary = {row['id']: {'correct': 0, 'partial': 0, 'incorrect': 0, 'total': 0} for row in dataset}
    for label, snapshot in snapshots:
        for result in snapshot['results']:
            model_ref = result['model_ref']
            for item in result['items']:
                item_id = item['item_id']
                if item_id not in by_item:
                    continue
                score_label = item.get('score_label', 'incorrect')
                summary[item_id]['total'] += 1
                summary[item_id][score_label] = summary[item_id].get(score_label, 0) + 1
                by_item[item_id].append(
                    f'<li><code>{html.escape(model_ref)}</code> '
                    f'<span class="{item_status_class(score_label)}">{html.escape(score_label)}</span> '
                    f'· answer: <code>{render_answer(item)}</code> '
                    f'· snapshot: {html.escape(label)}</li>'
                )
    return by_item, summary


def toughest_rows(dataset: list[dict], item_summary: dict[str, dict]) -> list[str]:
    rows = []
    ordered = sorted(dataset, key=lambda row: (-item_summary[row['id']]['incorrect'], -item_summary[row['id']]['partial'], row['id']))
    for row in ordered[:6]:
        s = item_summary[row['id']]
        rows.append(
            f"<tr><td><code>{html.escape(row['id'])}</code></td>"
            f"<td>{html.escape(row['prompt'])}</td>"
            f"<td>{s['correct']} correct / {s['total']}</td>"
            f"<td>{s['incorrect']} misses</td></tr>"
        )
    return rows




def compact_rows(dataset: list[dict], item_summary: dict[str, dict]) -> list[str]:
    rows = []
    for row in dataset:
        s = item_summary[row['id']]
        image_name = Path(row['image_path']).name
        rows.append(
            f"<tr><td><code>{html.escape(row['id'])}</code></td>"
            f"<td>{html.escape(row['category'])}</td>"
            f"<td>{html.escape(row['prompt'])}</td>"
            f"<td>{s['incorrect']} misses / {s['total']}</td>"
            f"<td><a href="#{html.escape(row['id'])}">item</a> · <a href="images/{html.escape(image_name)}">image</a></td></tr>"
        )
    return rows

def artifact_links() -> str:
    groups = [
        ('Main 14-item snapshot', [
            ('JSON', 'results/livefire-may-2026.json'),
            ('CSV', 'results/livefire-may-2026.csv'),
            ('Markdown', 'results/livefire-may-2026.md'),
            ('OpenTimestamps', 'results/livefire-may-2026.json.ots'),
        ]),
        ('OpenAI frontier snapshot', [
            ('JSON', 'results/livefire-openai-gpt5x-2026-05-26.json'),
            ('CSV', 'results/livefire-openai-gpt5x-2026-05-26.csv'),
            ('Markdown', 'results/livefire-openai-gpt5x-2026-05-26.md'),
            ('OpenTimestamps', 'results/livefire-openai-gpt5x-2026-05-26.json.ots'),
        ]),
        ('Claude compatibility snapshot', [
            ('JSON', 'results/claude-may-2026.json'),
            ('Markdown', 'results/claude-may-2026.md'),
            ('OpenTimestamps', 'results/claude-may-2026.json.ots'),
        ]),
    ]
    out = []
    for title, links in groups:
        items = ' · '.join(f'<a href="{href}">{label}</a>' for label, href in links)
        out.append(f'<li><strong>{title}:</strong> {items}</li>')
    return '<ul>' + ''.join(out) + '</ul>'


def main() -> None:
    SITE.mkdir(exist_ok=True)
    IMAGES_OUT.mkdir(exist_ok=True)
    RESULTS_OUT.mkdir(exist_ok=True)

    dataset = load_dataset()
    harness = load_json(HARNESS_RESULTS)
    openai_frontier = load_json(OPENAI_FRONTIER_RESULTS)
    claude = load_json(CLAUDE_RESULTS)

    for row in dataset:
        src = ROOT / row['image_path']
        (IMAGES_OUT / src.name).write_bytes(src.read_bytes())

    for src in PUBLISHED_RESULTS:
        if src.exists():
            (RESULTS_OUT / src.name).write_bytes(src.read_bytes())

    (SITE / 'CNAME').write_text(CUSTOM_DOMAIN + '\n', encoding='utf-8')

    snapshots = [('main-14', harness), ('openai-14', openai_frontier), ('claude-10', claude)]
    item_results, item_summary = summarize_item_results(dataset, snapshots)

    ordered_results = sorted(
        harness['results'],
        key=lambda result: (-(result.get('correct', 0) / max(result.get('total_items', 1), 1)), result.get('model_ref', '')),
    )
    leaderboard_rows = []
    for result in ordered_results:
        misses = [item['item_id'] for item in result['items'] if item['score_label'] != 'correct']
        leaderboard_rows.append(
            f"<tr><td><code>{html.escape(result['model_ref'])}</code></td>"
            f"<td class=\"{score_class(result['correct'], result['total_items'])}\">{result['correct']} / {result['total_items']}</td>"
            f"<td>{', '.join(misses) if misses else 'none'}</td></tr>"
        )

    claude_rows = []
    for result in claude['results']:
        misses = [item['item_id'] for item in result['items'] if item['score_label'] != 'correct']
        claude_rows.append(
            f"<tr><td><code>{html.escape(result['model_ref'])}</code></td>"
            f"<td class=\"{score_class(result['correct'], result['total_items'])}\">{result['correct']} / {result['total_items']}</td>"
            f"<td>{', '.join(misses) if misses else 'none'}</td></tr>"
        )

    gallery = []
    for row in dataset:
        image_name = Path(row['image_path']).name
        results_html = ''.join(item_results.get(row['id'], [])) or '<li>No checked-in model rows for this item.</li>'
        s = item_summary[row['id']]
        gallery.append(
            f"<article class=\"figure\" id=\"{html.escape(row['id'])}\">"
            f"<a class=\"image-link\" href=\"images/{html.escape(image_name)}\"><img loading=\"lazy\" src=\"images/{html.escape(image_name)}\" alt=\"{html.escape(row['id'])} benchmark image\"></a>"
            f"<h3>{html.escape(row['id'])} — {html.escape(row['category'])}</h3>"
            f"<p><strong>Prompt:</strong> {html.escape(row['prompt'])}</p>"
            f"<p><strong>Expected:</strong> <code>{html.escape(row['expected'])}</code></p>"
            f"<p class=\"meta\">{html.escape(row.get('notes', ''))}</p>"
            f"<p class=\"summary-line\">{s['correct']} correct · {s['partial']} partial · {s['incorrect']} incorrect across {s['total']} checked-in model rows.</p>"
            f"<details class=\"item-results\"><summary>Show per-model results</summary><ul>{results_html}</ul></details>"
            f"</article>"
        )

    html_out = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shibboleth Bench — Visual anomaly benchmark</title>
  <meta name="description" content="Checked-in dataset, benchmark items, and result snapshots for Shibboleth Bench.">
  <meta property="og:title" content="Shibboleth Bench">
  <meta property="og:description" content="Checked-in dataset and result snapshots for a compact visual anomaly benchmark.">
  <meta property="og:image" content="https://shibboleth.spitfirecowboy.com/images/two-hat-logo.png">
  <meta property="og:url" content="https://shibboleth.spitfirecowboy.com/">
  <meta name="twitter:card" content="summary_large_image">
  <script defer data-domain="shibboleth.spitfirecowboy.com" src="https://analytics.spitfirecowboy.com/js/script.js"></script>
  <style>{CSS}</style>
</head>
<body>
  <main class="wrapper">
    <section class="hero">
      <div class="kicker">Visual anomaly benchmark · {len(dataset)} items · May 2026</div>
      <h1>A compact benchmark for obvious multimodal misses</h1>
      <p class="lede">This page is the human-readable front door for Shibboleth Bench: current checked-in snapshots, the hardest items, and the full item gallery with per-model results hidden until you want them.</p>
      <div class="badges">
        <span class="badge">{len(dataset)} benchmark items</span>
        <span class="badge">Apache 2.0</span>
        <span class="badge">Dataset SHA {html.escape(harness['dataset_sha256'][:12])}…</span>
      </div>
      <nav class="jump-links">
        <a href="#results">Results</a>
        <a href="#hardest">Hardest items</a>
        <a href="#items">All items</a>
        <a href="#artifacts">Artifacts</a>
      </nav>
    </section>

    <section class="section grid cols-3">
      <article class="card"><h3>What it is</h3><p>A small benchmark for counting errors, mirror/reflection mismatches, malformed text, attachment failures, and other visible anomalies.</p></article>
      <article class="card"><h3>What it is not</h3><p>Not a general multimodal score. Every claim here is only about this checked-in dataset and these checked-in snapshots.</p></article>
      <article class="card"><h3>How to read it</h3><p>Start with the snapshot tables. Then use the hardest-items table. Open per-item details only when you need the model-by-model rows.</p></article>
    </section>

    <section class="section" id="results">
      <h2>Current snapshots</h2>
      <div class="grid cols-2">
        <article>
          <div class="table-wrap">
            <table>
              <thead><tr><th colspan="3">Main 14-item snapshot</th></tr><tr><th>Model</th><th>Score</th><th>Misses</th></tr></thead>
              <tbody>{''.join(leaderboard_rows)}</tbody>
            </table>
          </div>
        </article>
        <article>
          <div class="table-wrap">
            <table>
              <thead><tr><th colspan="3">Claude compatibility snapshot (10 items)</th></tr><tr><th>Model</th><th>Score</th><th>Misses</th></tr></thead>
              <tbody>{''.join(claude_rows)}</tbody>
            </table>
          </div>
        </article>
      </div>
    </section>

    <section class="section" id="hardest">
      <h2>Where models struggled most</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Item</th><th>Prompt</th><th>Correct rows</th><th>Misses</th></tr></thead>
          <tbody>{''.join(toughest_rows(dataset, item_summary))}</tbody>
        </table>
      </div>
    </section>

    <section class="section grid cols-2">
      <article class="card"><h3>Method</h3><p>Models answer with strict JSON. Raw responses, parsed answers, and grader outcomes are all preserved in the checked-in snapshots.</p></article>
      <article class="card"><h3>Dataset shape</h3><p>Nine items are self-authored synthetic probes. Five are photographic derivatives built from public-domain source photos.</p></article>
    </section>

    <section class="section" id="items">
      <h2>Full corpus index</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Item</th><th>Type</th><th>Prompt</th><th>Misses</th><th>Links</th></tr></thead>
          <tbody>{''.join(compact_rows(dataset, item_summary))}</tbody>
        </table>
      </div>
      <details class="card">
        <summary>Open full image gallery and per-model detail</summary>
        <div class="gallery">{''.join(gallery)}</div>
      </details>
    </section>

    <section class="section" id="artifacts">
      <h2>Artifacts</h2>
      <div class="grid cols-2">
        <article class="card"><h3>Machine-readable snapshots</h3>{artifact_links()}</article>
        <article class="card"><h3>Repository</h3><p><a href="https://github.com/Spitfire-Cowboy/shibboleth-bench">View on GitHub</a></p></article>
      </div>
    </section>

    <footer class="footer">Repository, dataset, and checked-in result snapshots. · <a href="https://github.com/Spitfire-Cowboy/shibboleth-bench">GitHub</a> · <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache 2.0</a></footer>
  </main>
</body>
</html>
'''
    (SITE / 'index.html').write_text(html_out, encoding='utf-8')


if __name__ == '__main__':
    main()
