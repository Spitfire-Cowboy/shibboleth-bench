#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'dataset' / 'items.jsonl'
RESULTS = ROOT / 'results' / 'livefire-may-2026.json'
SITE = ROOT / 'site'
IMAGES_OUT = SITE / 'images'
RESULTS_OUT = SITE / 'results'

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
.wrapper { max-width: 1100px; margin: 0 auto; padding: 32px 20px 72px; }
.hero { padding: 40px 0 24px; }
.kicker { text-transform: uppercase; letter-spacing: .12em; color: var(--muted); font-size: 12px; font-weight: 700; }
h1 { font-size: clamp(2.5rem, 5vw, 4rem); line-height: 1.05; margin: 12px 0 14px; }
.lede { max-width: 720px; font-size: 1.1rem; color: var(--muted); }
.badges { display:flex; flex-wrap:wrap; gap:10px; margin:20px 0 0; }
.badge { border:1px solid var(--line); background: var(--card); border-radius:999px; padding:8px 12px; font-size:14px; }
.section { margin-top: 42px; }
.section h2 { font-size: 1.6rem; margin: 0 0 14px; }
.grid { display:grid; gap:16px; }
.grid.cols-2 { grid-template-columns: repeat(auto-fit, minmax(280px,1fr)); }
.card { background: var(--card); border:1px solid var(--line); border-radius: 18px; padding: 18px; box-shadow: 0 1px 0 rgba(0,0,0,.03); }
.card h3 { margin: 0 0 8px; font-size: 1.05rem; }
.card p { margin: 0; color: var(--muted); }
table { width:100%; border-collapse: collapse; background: var(--card); border:1px solid var(--line); border-radius:18px; overflow:hidden; }
th, td { padding: 12px 14px; border-bottom: 1px solid var(--line); text-align:left; vertical-align: top; }
th { background: #f2ece0; font-size: 14px; }
tr:last-child td { border-bottom: none; }
.score-ok { color: var(--ok); font-weight: 700; }
.score-mid { color: var(--warn); font-weight: 700; }
.score-bad { color: var(--bad); font-weight: 700; }
.gallery { display:grid; gap:20px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.figure { background: var(--card); border:1px solid var(--line); border-radius:18px; padding:14px; }
.figure img { width:100%; height:auto; border-radius:12px; display:block; background:#fff; }
.figure h3 { margin: 12px 0 6px; font-size: 1rem; }
.figure code { font-size: 12px; }
.footer { margin-top: 60px; color: var(--muted); font-size: 14px; }
@media (max-width: 640px) { .wrapper { padding-inline: 14px; } th, td { padding:10px; } }
"""


def load_dataset():
    rows = []
    for line in DATASET.read_text(encoding='utf-8').splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def score_class(correct: int, total: int) -> str:
    pct = correct / total if total else 0
    if pct >= 1:
        return 'score-ok'
    if pct >= 0.8:
        return 'score-mid'
    return 'score-bad'


def main() -> None:
    SITE.mkdir(exist_ok=True)
    IMAGES_OUT.mkdir(exist_ok=True)
    RESULTS_OUT.mkdir(exist_ok=True)

    dataset = load_dataset()
    results = json.loads(RESULTS.read_text(encoding='utf-8'))

    # copy assets
    for row in dataset:
        src = ROOT / row['image_path']
        dst = IMAGES_OUT / src.name
        dst.write_bytes(src.read_bytes())

    for src in [ROOT / 'results' / 'livefire-may-2026.json', ROOT / 'results' / 'livefire-may-2026.md', ROOT / 'results' / 'livefire-may-2026.csv']:
        if src.exists():
            (RESULTS_OUT / src.name).write_bytes(src.read_bytes())

    leaderboard_rows = []
    for result in results['results']:
        misses = [item['item_id'] for item in result['items'] if item['score_label'] != 'correct']
        leaderboard_rows.append(
            f"<tr><td><code>{html.escape(result['model_ref'])}</code></td>"
            f"<td class=\"{score_class(result['correct'], result['total_items'])}\">{result['correct']} / {result['total_items']}</td>"
            f"<td>{', '.join(misses) if misses else 'none'}</td></tr>"
        )

    gallery = []
    for row in dataset:
        gallery.append(
            f"<article class=\"figure\">"
            f"<img src=\"images/{html.escape(Path(row['image_path']).name)}\" alt=\"{html.escape(row['id'])} benchmark image\">"
            f"<h3>{html.escape(row['id'])} — {html.escape(row['category'])}</h3>"
            f"<p><strong>Prompt:</strong> {html.escape(row['prompt'])}</p>"
            f"<p><strong>Expected:</strong> <code>{html.escape(row['expected'])}</code></p>"
            f"<p>{html.escape(row.get('notes',''))}</p>"
            f"</article>"
        )

    html_out = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Shibboleth Bench</title>
  <meta name=\"description\" content=\"Visual anomaly screening benchmark for multimodal models.\">
  <style>{CSS}</style>
</head>
<body>
  <main class=\"wrapper\">
    <section class=\"hero\">
      <div class=\"kicker\">Shibboleth Bench</div>
      <h1>Visual anomaly screening for multimodal models</h1>
      <p class=\"lede\">A small benchmark for one narrow question: does a model miss obvious image-generation mistakes or discrete-object anomalies? This is a screening benchmark, not a broad multimodal leaderboard.</p>
      <div class=\"badges\">
        <span class=\"badge\">10 benchmark items</span>
        <span class=\"badge\">Apache 2.0</span>
        <span class=\"badge\">Dataset SHA {html.escape(results['dataset_sha256'][:12])}…</span>
      </div>
    </section>

    <section class=\"section\">
      <h2>Latest May 2026 leaderboard</h2>
      <table>
        <thead><tr><th>Model</th><th>Score</th><th>Misses</th></tr></thead>
        <tbody>{''.join(leaderboard_rows)}</tbody>
      </table>
    </section>

    <section class=\"section grid cols-2\">
      <article class=\"card\">
        <h3>What this benchmark is</h3>
        <p>A cheap screen for narrow, high-signal failure modes: mirror mismatches, reflections, malformed text, finger counts, attachment failures, repeated objects, and lighting contradictions.</p>
      </article>
      <article class=\"card\">
        <h3>What this benchmark is not</h3>
        <p>Not a general measure of multimodal competence. Passing Shibboleth does not mean a model is broadly reliable. Failing it means the model misses simple anomalies it should probably catch.</p>
      </article>
    </section>

    <section class=\"section\">
      <h2>Method</h2>
      <div class=\"grid cols-2\">
        <article class=\"card\"><h3>Structured grading</h3><p>Models are prompted for strict JSON answers, with raw responses and parsed answers preserved alongside the grader result.</p></article>
        <article class=\"card\"><h3>Controlled probes</h3><p>Most items are self-authored synthetic probe images designed to be simple, legible, and easy to score consistently.</p></article>
      </div>
    </section>

    <section class=\"section\">
      <h2>Benchmark items</h2>
      <div class=\"gallery\">{''.join(gallery)}</div>
    </section>

    <section class=\"section\">
      <h2>Artifacts</h2>
      <div class=\"grid cols-2\">
        <article class=\"card\"><h3>Machine-readable results</h3><p><a href=\"results/livefire-may-2026.json\">JSON snapshot</a><br><a href=\"results/livefire-may-2026.csv\">CSV summary</a><br><a href=\"results/livefire-may-2026.md\">Markdown summary</a></p></article>
        <article class=\"card\"><h3>Repository</h3><p><a href=\"https://github.com/Spitfire-Cowboy/shibboleth-bench\">View on GitHub</a></p></article>
      </div>
    </section>

    <footer class=\"footer\">Shibboleth is a narrow benchmark harness for anomaly detection, not a claim of general model quality.</footer>
  </main>
</body>
</html>
"""
    (SITE / 'index.html').write_text(html_out, encoding='utf-8')


if __name__ == '__main__':
    main()
