#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path

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
.gallery { display:grid; gap:20px; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
.figure { background: var(--card); border:1px solid var(--line); border-radius:18px; padding:14px; }
.figure .image-link { display:block; }
.figure img { width:100%; height:auto; border-radius:12px; display:block; background:#fff; }
.figure h3 { margin: 12px 0 6px; font-size: 1rem; }
.figure code { font-size: 12px; }
.figure p { margin: 0 0 8px; }
.table-wrap { overflow-x: auto; }
.item-results { margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--line); }
.item-results h4 { margin: 0 0 8px; font-size: .95rem; }
.item-results ul { margin: 0; padding-left: 18px; }
.item-results li { margin: 0 0 4px; }
.footer { margin-top: 60px; color: var(--muted); font-size: 14px; }
@media (max-width: 640px) { .wrapper { padding-inline: 14px; } th, td { padding:10px; } }
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


def build_item_results(dataset: list[dict], snapshots: list[tuple[str, dict]]) -> dict[str, list[str]]:
    by_item = {row['id']: [] for row in dataset}
    for label, snapshot in snapshots:
        for result in snapshot['results']:
            model_ref = result['model_ref']
            for item in result['items']:
                item_id = item['item_id']
                if item_id not in by_item:
                    continue
                score_label = item.get('score_label', 'incorrect')
                by_item[item_id].append(
                    f'<li><code>{html.escape(model_ref)}</code> '
                    f'<span class="{item_status_class(score_label)}">{html.escape(score_label)}</span> '
                    f'· answer: <code>{render_answer(item)}</code> '
                    f'· snapshot: {html.escape(label)}</li>'
                )
    return by_item


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

    snapshots = [
        ('main-14', harness),
        ('openai-14', openai_frontier),
        ('claude-10', claude),
    ]
    item_results = build_item_results(dataset, snapshots)

    leaderboard_rows = []
    ordered_results = sorted(
        harness['results'],
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
        gallery.append(
            f"<article class=\"figure\">"
            f"<a class=\"image-link\" href=\"images/{html.escape(image_name)}\"><img loading=\"lazy\" src=\"images/{html.escape(image_name)}\" alt=\"{html.escape(row['id'])} benchmark image\"></a>"
            f"<h3>{html.escape(row['id'])} — {html.escape(row['category'])}</h3>"
            f"<p><strong>Prompt:</strong> {html.escape(row['prompt'])}</p>"
            f"<p><strong>Expected:</strong> <code>{html.escape(row['expected'])}</code></p>"
            f"<p>{html.escape(row.get('notes', ''))}</p>"
            f"<div class=\"item-results\"><h4>Checked-in per-model results</h4><ul>{results_html}</ul></div>"
            f"</article>"
        )

    html_out = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Shibboleth Bench — Visual Anomaly Benchmark for Multimodal Models</title>
  <meta name=\"description\" content=\"Static site for the Shibboleth benchmark dataset and checked-in result snapshots.\">
  <meta property=\"og:title\" content=\"Shibboleth Bench\">
  <meta property=\"og:description\" content=\"Dataset, benchmark items, and checked-in result snapshots for Shibboleth Bench.\">
  <meta property=\"og:image\" content=\"https://shibboleth.spitfirecowboy.com/images/two-hat-logo.png\">
  <meta property=\"og:url\" content=\"https://shibboleth.spitfirecowboy.com/\">
  <meta name=\"twitter:card\" content=\"summary_large_image\">
  <script defer data-domain=\"spitfire-cowboy.github.io\" src=\"https://analytics.spitfirecowboy.com/js/script.js\"></script>
  <style>{CSS}</style>
</head>
<body>
  <main class=\"wrapper\">
    <section class=\"hero\">
      <div class=\"kicker\">Visual anomaly benchmark · {len(dataset)} items · May 2026</div>
      <h1>Checked-in results for a small visual anomaly benchmark</h1>
      <p class=\"lede\">This site publishes the current dataset, benchmark items, and checked-in model snapshots for Shibboleth Bench.</p>
      <div class=\"badges\">
        <span class=\"badge\">{len(dataset)} benchmark items</span>
        <span class=\"badge\">Apache 2.0</span>
        <span class=\"badge\">Dataset SHA {html.escape(harness['dataset_sha256'][:12])}…</span>
      </div>
    </section>

    <section class=\"section\">
      <h2>Latest May 2026 results</h2>
      <div class=\"table-wrap\">
      <table>
        <thead><tr><th>Model</th><th>Score</th><th>Misses</th></tr></thead>
        <tbody>{''.join(leaderboard_rows)}</tbody>
      </table>
      </div>
    </section>

    <section class=\"section\">
      <h2>Claude compatibility snapshot</h2>
      <div class=\"table-wrap\">
      <table>
        <thead><tr><th>Model</th><th>Score</th><th>Misses</th></tr></thead>
        <tbody>{''.join(claude_rows)}</tbody>
      </table>
      </div>
      <p class=\"lede\" style=\"font-size:1rem; margin-top:12px;\">This Claude snapshot covers SB-001 through SB-010 and is published separately from the 14-item harness snapshots.</p>
    </section>

    <section class=\"section grid cols-2\">
      <article class=\"card\">
        <h3>What this benchmark is</h3>
        <p>A 14-item benchmark covering mirror mismatches, reflections, malformed text, finger counts, attachment failures, repeated objects, and lighting contradictions.</p>
      </article>
      <article class=\"card\">
        <h3>What this benchmark is not</h3>
        <p>Not a general multimodal evaluation. These pages summarize checked-in results for this dataset only.</p>
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
        <article class=\"card\"><h3>Machine-readable results</h3><p><a href=\"results/livefire-may-2026.json\">May 2026 JSON snapshot</a><br><a href=\"results/livefire-may-2026.csv\">May 2026 CSV summary</a><br><a href=\"results/livefire-may-2026.md\">May 2026 Markdown summary</a><br><a href=\"results/livefire-may-2026.json.ots\">May 2026 OpenTimestamps proof</a><br><br><a href=\"results/livefire-openai-gpt5x-2026-05-26.json\">OpenAI frontier JSON snapshot</a><br><a href=\"results/livefire-openai-gpt5x-2026-05-26.csv\">OpenAI frontier CSV summary</a><br><a href=\"results/livefire-openai-gpt5x-2026-05-26.md\">OpenAI frontier Markdown summary</a><br><a href=\"results/livefire-openai-gpt5x-2026-05-26.json.ots\">OpenAI frontier OpenTimestamps proof</a><br><br><a href=\"results/claude-may-2026.json\">Claude 10-item JSON snapshot</a><br><a href=\"results/claude-may-2026.md\">Claude 10-item Markdown summary</a><br><a href=\"results/claude-may-2026.json.ots\">Claude OpenTimestamps proof</a></p></article>
        <article class=\"card\"><h3>Repository</h3><p><a href=\"https://github.com/Spitfire-Cowboy/shibboleth-bench\">View on GitHub</a><br><a href=\"results/claude-may-2026.md\">Claude snapshot summary</a></p></article>
      </div>
    </section>

    <footer class=\"footer\">Repository, dataset, and checked-in result snapshots. · <a href=\"https://github.com/Spitfire-Cowboy/shibboleth-bench\">GitHub</a> · <a href=\"https://www.apache.org/licenses/LICENSE-2.0\">Apache 2.0</a></footer>
  </main>
</body>
</html>
"""
    (SITE / 'index.html').write_text(html_out, encoding='utf-8')


if __name__ == '__main__':
    main()
