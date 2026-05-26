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
.table-wrap { overflow-x: auto; }
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
    if pct >= 0.9:
        return 'score-ok'
    if pct >= 0.7:
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

    for src in [
        ROOT / 'results' / 'livefire-may-2026.json',
        ROOT / 'results' / 'livefire-may-2026.md',
        ROOT / 'results' / 'livefire-may-2026.csv',
        ROOT / 'results' / 'livefire-openai-gpt5x-2026-05-26.json',
        ROOT / 'results' / 'livefire-openai-gpt5x-2026-05-26.md',
        ROOT / 'results' / 'livefire-openai-gpt5x-2026-05-26.csv',
    ]:
        if src.exists():
            (RESULTS_OUT / src.name).write_bytes(src.read_bytes())

    leaderboard_rows = []
    ordered_results = sorted(
        results['results'],
        key=lambda result: (
            -(result.get('correct', 0) / max(result.get('total_items', 1), 1)),
            result.get('model_ref', ''),
        ),
    )
    for result in ordered_results:
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
            f"<img loading=\"lazy\" src=\"images/{html.escape(Path(row['image_path']).name)}\" alt=\"{html.escape(row['id'])} benchmark image\">"
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
  <title>Shibboleth Bench — Visual Anomaly Benchmark for Multimodal Models</title>
  <meta name=\"description\" content=\"Benchmark for testing how multimodal models handle clear visual anomalies.\">
  <meta property=\"og:title\" content=\"Shibboleth Bench\">
  <meta property=\"og:description\" content=\"A focused benchmark: do multimodal models catch obvious visual anomalies?\">
  <meta property=\"og:image\" content=\"https://spitfire-cowboy.github.io/shibboleth-bench/images/two-hat-logo.png\">
  <meta property=\"og:url\" content=\"https://spitfire-cowboy.github.io/shibboleth-bench/\">
  <meta name=\"twitter:card\" content=\"summary_large_image\">
  <style>{CSS}</style>
</head>
<body>
  <main class=\"wrapper\">
    <section class=\"hero\">
      <div class=\"kicker\">Visual anomaly benchmark · {len(dataset)} items · May 2026</div>
      <h1>Testing multimodal models on clear visual anomalies</h1>
      <p class=\"lede\">A focused benchmark for one narrow question: does a model miss obvious image-generation mistakes or discrete-object anomalies?</p>
      <div class=\"badges\">
        <span class=\"badge\">{len(dataset)} benchmark items</span>
        <span class=\"badge\">Apache 2.0</span>
        <span class=\"badge\">Published snapshot SHA {html.escape(results['dataset_sha256'][:12])}…</span>
      </div>
    </section>

    <section class=\"section\">
      <h2>Latest May 2026 results</h2>
      <p class=\"lede\">This published snapshot still uses the original 10-item public corpus. The current dataset in <code>main</code> has additional photographic probes that are ready for the next livefire pass.</p>
      <div class=\"table-wrap\">
      <table>
        <thead><tr><th>Model</th><th>Score</th><th>Misses</th></tr></thead>
        <tbody>{''.join(leaderboard_rows)}</tbody>
      </table>
      </div>
    </section>

    <section class=\"section grid cols-2\">
      <article class=\"card\">
        <h3>What this benchmark is</h3>
        <p>A small set of high-signal probes: mirror mismatches, reflections, malformed text, finger counts, attachment failures, repeated objects, and lighting contradictions.</p>
      </article>
      <article class=\"card\">
        <h3>What this benchmark is not</h3>
        <p>Not a general measure of multimodal competence. Passing Shibboleth does not imply broad reliability. Failing it means the model misses simple anomalies it should likely catch.</p>
      </article>
    </section>

    <section class=\"section\">
      <h2>Method</h2>
      <div class=\"grid cols-2\">
        <article class=\"card\"><h3>Structured grading</h3><p>Models are prompted for strict JSON answers, with raw responses and parsed answers preserved alongside the grader result.</p></article>
        <article class=\"card\"><h3>Controlled probes</h3><p>Nine of the fourteen current items are self-authored synthetic probe images designed to be simple, legible, and easy to score consistently. The rest are photographic derivatives built from public-domain source photos.</p></article>
      </div>
    </section>

    <section class=\"section\">
      <h2>Benchmark items</h2>
      <div class=\"gallery\">{''.join(gallery)}</div>
    </section>

    <section class=\"section\">
      <h2>Artifacts</h2>
      <div class=\"grid cols-2\">
        <article class=\"card\"><h3>Machine-readable results</h3><p><a href=\"results/livefire-may-2026.json\">May 2026 JSON snapshot</a><br><a href=\"results/livefire-may-2026.csv\">May 2026 CSV summary</a><br><a href=\"results/livefire-may-2026.md\">May 2026 Markdown summary</a><br><br><a href=\"results/livefire-openai-gpt5x-2026-05-26.json\">OpenAI frontier JSON snapshot</a><br><a href=\"results/livefire-openai-gpt5x-2026-05-26.csv\">OpenAI frontier CSV summary</a><br><a href=\"results/livefire-openai-gpt5x-2026-05-26.md\">OpenAI frontier Markdown summary</a></p></article>
        <article class=\"card\"><h3>Repository</h3><p><a href=\"https://github.com/Spitfire-Cowboy/shibboleth-bench\">View on GitHub</a></p></article>
      </div>
    </section>

    <footer class=\"footer\">Shibboleth is a focused benchmark for visual anomalies, not a claim about overall model quality. · <a href=\"https://github.com/Spitfire-Cowboy/shibboleth-bench\">GitHub</a> · <a href=\"https://www.apache.org/licenses/LICENSE-2.0\">Apache 2.0</a></footer>
  </main>
</body>
</html>
"""
    (SITE / 'index.html').write_text(html_out, encoding='utf-8')


if __name__ == '__main__':
    main()
