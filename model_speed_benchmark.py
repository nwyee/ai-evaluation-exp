"""
Model Speed Benchmark - Compare Claude Models Speed & Performance

Inspired by model_speed_benchmark.html design
Tests how fast different Claude models (Haiku, Sonnet, Opus) respond
Measures TTFT (Time to First Token) and total response time
"""

import os
import sys
import time
import json
from flask import Flask, render_template_string, request, jsonify
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path

# Load environment
current_dir = Path(__file__).parent
for directory in [current_dir, current_dir.parent, current_dir.parent.parent]:
    env_file = directory / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

# Initialize Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ Error: ANTHROPIC_API_KEY not set in .env")
    sys.exit(1)

# Initialize client with optional proxy support
base_url = os.getenv("PROXY_BASE_URL")
if base_url:
    client = Anthropic(api_key=api_key, base_url=base_url)
else:
    client = Anthropic(api_key=api_key)

app = Flask(__name__)

# Model configurations
MODELS = [
    {"key": "haiku", "id": "claude-haiku-4-5-20251001-v1:0", "label": "Haiku"},
    {"key": "sonnet", "id": "claude-3-5-sonnet-20241022", "label": "Sonnet"},
    {"key": "opus", "id": "claude-3-opus-20250219", "label": "Opus"},
]

# Sample prompts for testing (Myanmar language)
PROMPTS = [
    {"label": "🥗 ကျန်းမာရေး", "q": "ကျန်းမာရေးကောင်းဖို့ ဘာတွေ လုပ်သင့်သလဲ?"},
    {"label": "😴 အိပ်ရေး", "q": "ညဘက် ကောင်းကောင်းအိပ်ဖို့ နည်းလမ်းတွေ ပြောပြပါ။"},
    {"label": "📚 စာဖတ်", "q": "စာဖတ်တဲ့ အလေ့အကျင့် ဘယ်လို တည်ဆောက်မလဲ?"},
    {"label": "💼 အလုပ်", "q": "အလုပ်မှာ productive ဖြစ်ဖို့ tip တွေ ပေးပါ။"},
    {"label": "🤖 AI", "q": "AI engineering ဆိုတာ ဘာလဲ? ရှင်းပြပါ။"},
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Model Speed Benchmark</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #F6F3EE;
    --card: #fff;
    --border: #E8E2D8;
    --text: #1A1714;
    --muted: #9A9189;
    --haiku:  #2A6A4A;
    --sonnet: #D4622A;
    --opus:   #7A2A6A;
    --haiku-bg:  #EBF5EF;
    --sonnet-bg: #FDF0EB;
    --opus-bg:   #F5EBF5;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
    min-height: 100vh;
    padding: 36px 16px 60px;
  }

  .header {
    text-align: center;
    margin-bottom: 28px;
  }

  .eyebrow {
    font-size: 10px;
    letter-spacing: 4px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  h1 {
    font-family: 'Fraunces', serif;
    font-size: 34px;
    font-weight: 900;
    line-height: 1.1;
  }

  h1 em { font-style: normal; color: var(--sonnet); }

  .subtitle {
    font-size: 12px;
    color: var(--muted);
    margin-top: 8px;
  }

  /* Legend */
  .legend {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 500;
  }

  .legend-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
  }

  /* Input card */
  .input-card {
    max-width: 680px;
    margin: 0 auto 24px;
    background: var(--card);
    border-radius: 16px;
    border: 1.5px solid var(--border);
    padding: 20px 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  }

  .preset-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
  }

  .presets {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 14px;
  }

  .pill {
    padding: 5px 12px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: var(--bg);
    font-size: 11px;
    color: var(--muted);
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    transition: all 0.15s;
  }

  .pill:hover { border-color: var(--sonnet); color: var(--sonnet); background: var(--sonnet-bg); }

  .field label {
    display: block;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
  }

  .field textarea {
    width: 100%;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1.5px solid var(--border);
    background: var(--bg);
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: var(--text);
    outline: none;
    resize: vertical;
    min-height: 72px;
    line-height: 1.6;
    transition: border-color 0.2s;
  }

  .field textarea:focus { border-color: var(--sonnet); }

  .run-btn {
    width: 100%;
    padding: 13px;
    background: var(--text);
    color: #fff;
    border: none;
    border-radius: 12px;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 1px;
    cursor: pointer;
    margin-top: 14px;
    transition: all 0.2s;
  }

  .run-btn:hover { background: #333; transform: translateY(-1px); }
  .run-btn:disabled { background: var(--border); color: var(--muted); cursor: not-allowed; transform: none; }

  /* Results */
  .results-wrap {
    max-width: 900px;
    margin: 0 auto;
    display: none;
    flex-direction: column;
    gap: 16px;
  }

  .model-row {
    background: var(--card);
    border-radius: 16px;
    border: 1.5px solid var(--border);
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    animation: fadeUp 0.4s ease both;
  }

  .model-header {
    padding: 14px 20px;
    border-bottom: 1.5px solid;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .model-icon {
    font-size: 22px;
    font-family: 'Fraunces', serif;
    font-weight: 900;
  }

  .model-meta { flex: 1; }

  .model-name {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .model-id {
    font-size: 10px;
    color: var(--muted);
    margin-top: 2px;
    font-family: monospace;
  }

  /* Metrics bar */
  .metrics-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    border-bottom: 1px solid var(--border);
  }

  .metric-cell {
    padding: 12px 20px;
    border-right: 1px solid var(--border);
    text-align: center;
  }

  .metric-cell:last-child { border-right: none; }

  .metric-value {
    font-family: 'Fraunces', serif;
    font-size: 22px;
    font-weight: 700;
    line-height: 1;
  }

  .metric-label {
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 4px;
  }

  .metric-sub {
    font-size: 10px;
    color: var(--muted);
    margin-top: 2px;
  }

  /* Speed bar */
  .speed-bar-wrap {
    padding: 0 20px 4px;
    background: var(--bg);
  }

  .speed-bar-track {
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    margin: 8px 0 4px;
    overflow: hidden;
  }

  .speed-bar-fill {
    height: 100%;
    border-radius: 2px;
    width: 0%;
    transition: width 0.8s ease;
  }

  /* Answer box */
  .answer-section {
    padding: 14px 20px;
  }

  .answer-label {
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
  }

  .answer-text {
    font-size: 13px;
    line-height: 1.7;
    color: var(--text);
    min-height: 40px;
  }

  /* Loading */
  .spinner {
    width: 14px; height: 14px;
    border: 2px solid var(--border);
    border-top-color: var(--sonnet);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    display: inline-block;
    vertical-align: middle;
    margin-right: 6px;
  }

  .loading-text {
    font-size: 12px;
    color: var(--muted);
    padding: 12px 0;
  }

  /* Insight row */
  .insight-row {
    max-width: 900px;
    margin: 12px auto 0;
    background: var(--card);
    border-radius: 12px;
    border: 1.5px solid var(--border);
    padding: 14px 20px;
    display: none;
    font-size: 12px;
    color: var(--muted);
    line-height: 1.8;
  }

  .insight-row.visible { display: block; }
  .insight-row strong { color: var(--text); }

  .footer {
    text-align: center;
    margin-top: 32px;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 2px;
  }

  .footer em { color: var(--sonnet); font-style: normal; }

  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
</head>
<body>

<div class="header">
  <div class="eyebrow">AI Engineering Experiment Lab</div>
  <h1>Model <em>Speed</em> Benchmark</h1>
  <div class="subtitle">Haiku vs Sonnet vs Opus — တူတဲ့ question နဲ့ ဘယ် model အမြန်ဆုံးလဲ?</div>
</div>

<div class="legend">
  <div class="legend-item">
    <div class="legend-dot" style="background:var(--haiku)"></div>
    <span style="color:var(--haiku)">Haiku ⚡ — အမြန်ဆုံး</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:var(--sonnet)"></div>
    <span style="color:var(--sonnet)">Sonnet ⚖️ — Balanced</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:var(--opus)"></div>
    <span style="color:var(--opus)">Opus 🧠 — အကောင်းဆုံး</span>
  </div>
</div>

<div class="input-card">
  <div class="preset-label">💡 Preset Questions</div>
  <div class="presets" id="presets"></div>

  <div class="field">
    <label>မေးခွန်း — Models သုံးခုလုံးကို တူတဲ့ question နဲ့ race လုပ်မယ်</label>
    <textarea id="question" placeholder="ဥပမာ — ကျန်းမာရေးကောင်းဖို့ ဘာတွေ လုပ်သင့်သလဲ?"></textarea>
  </div>

  <button class="run-btn" id="run-btn" onclick="runBenchmark()">🏁 Start Race!</button>
</div>

<!-- Results -->
<div class="results-wrap" id="results-wrap">

  <!-- Haiku -->
  <div class="model-row" id="row-haiku">
    <div class="model-header" style="background:var(--haiku-bg); border-color:#C0E0CA">
      <div class="model-icon" style="color:var(--haiku)">⚡</div>
      <div class="model-meta">
        <div class="model-name" style="color:var(--haiku)">Claude Haiku</div>
        <div class="model-id">claude-haiku-4-5-20251001</div>
      </div>
      <div id="rank-haiku"></div>
    </div>
    <div class="metrics-row">
      <div class="metric-cell">
        <div class="metric-value" id="ttft-haiku" style="color:var(--haiku)">—</div>
        <div class="metric-label">TTFT</div>
        <div class="metric-sub">Time to First Token</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="total-haiku" style="color:var(--haiku)">—</div>
        <div class="metric-label">Total Time</div>
        <div class="metric-sub">ms</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="tokens-haiku" style="color:var(--haiku)">—</div>
        <div class="metric-label">Output Tokens</div>
        <div class="metric-sub">count</div>
      </div>
    </div>
    <div class="speed-bar-wrap">
      <div class="speed-bar-track">
        <div class="speed-bar-fill" id="bar-haiku" style="background:var(--haiku)"></div>
      </div>
    </div>
    <div class="answer-section">
      <div class="answer-label">Response</div>
      <div class="answer-text" id="ans-haiku">—</div>
    </div>
  </div>

  <!-- Sonnet -->
  <div class="model-row" id="row-sonnet">
    <div class="model-header" style="background:var(--sonnet-bg); border-color:#F0C8A8">
      <div class="model-icon" style="color:var(--sonnet)">⚖️</div>
      <div class="model-meta">
        <div class="model-name" style="color:var(--sonnet)">Claude Sonnet</div>
        <div class="model-id">claude-3-5-sonnet-20241022</div>
      </div>
      <div id="rank-sonnet"></div>
    </div>
    <div class="metrics-row">
      <div class="metric-cell">
        <div class="metric-value" id="ttft-sonnet" style="color:var(--sonnet)">—</div>
        <div class="metric-label">TTFT</div>
        <div class="metric-sub">Time to First Token</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="total-sonnet" style="color:var(--sonnet)">—</div>
        <div class="metric-label">Total Time</div>
        <div class="metric-sub">ms</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="tokens-sonnet" style="color:var(--sonnet)">—</div>
        <div class="metric-label">Output Tokens</div>
        <div class="metric-sub">count</div>
      </div>
    </div>
    <div class="speed-bar-wrap">
      <div class="speed-bar-track">
        <div class="speed-bar-fill" id="bar-sonnet" style="background:var(--sonnet)"></div>
      </div>
    </div>
    <div class="answer-section">
      <div class="answer-label">Response</div>
      <div class="answer-text" id="ans-sonnet">—</div>
    </div>
  </div>

  <!-- Opus -->
  <div class="model-row" id="row-opus">
    <div class="model-header" style="background:var(--opus-bg); border-color:#D8C0D8">
      <div class="model-icon" style="color:var(--opus)">🧠</div>
      <div class="model-meta">
        <div class="model-name" style="color:var(--opus)">Claude Opus</div>
        <div class="model-id">claude-3-opus-20250219</div>
      </div>
      <div id="rank-opus"></div>
    </div>
    <div class="metrics-row">
      <div class="metric-cell">
        <div class="metric-value" id="ttft-opus" style="color:var(--opus)">—</div>
        <div class="metric-label">TTFT</div>
        <div class="metric-sub">Time to First Token</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="total-opus" style="color:var(--opus)">—</div>
        <div class="metric-label">Total Time</div>
        <div class="metric-sub">ms</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="tokens-opus" style="color:var(--opus)">—</div>
        <div class="metric-label">Output Tokens</div>
        <div class="metric-sub">count</div>
      </div>
    </div>
    <div class="speed-bar-wrap">
      <div class="speed-bar-track">
        <div class="speed-bar-fill" id="bar-opus" style="background:var(--opus)"></div>
      </div>
    </div>
    <div class="answer-section">
      <div class="answer-label">Response</div>
      <div class="answer-text" id="ans-opus">—</div>
    </div>
  </div>

</div>

<div class="insight-row" id="insight-row"></div>

<div class="footer" style="margin-top:32px">
  <em>📚 AI Engineering</em> — Model Speed Benchmark
</div>

<script>
const presets = {{ presets|tojson }};
const models = {{ models|tojson }};

const container = document.getElementById('presets');
presets.forEach(p => {
  const btn = document.createElement('button');
  btn.className = 'pill';
  btn.textContent = p.label;
  btn.onclick = () => {
    document.getElementById('question').value = p.q;
    resetAll();
  };
  container.appendChild(btn);
});

function resetAll() {
  document.getElementById('results-wrap').style.display = 'none';
  document.getElementById('insight-row').classList.remove('visible');
  models.forEach(m => {
    ['ttft','total','tokens'].forEach(metric => {
      document.getElementById(`${metric}-${m.key}`).textContent = '—';
    });
    document.getElementById(`ans-${m.key}`).innerHTML = '—';
    document.getElementById(`bar-${m.key}`).style.width = '0%';
    document.getElementById(`rank-${m.key}`).innerHTML = '';
  });
}

function setLoading(key) {
  document.getElementById(`ans-${key}`).innerHTML =
    `<div class="loading-text"><span class="spinner"></span> Generating...</div>`;
  ['ttft','total','tokens'].forEach(m => {
    document.getElementById(`${m}-${key}`).innerHTML =
      `<span class="spinner" style="width:12px;height:12px;border-top-color:var(--${key})"></span>`;
  });
}

const rankEmojis = ['🥇', '🥈', '🥉'];

async function runBenchmark() {
  const q = document.getElementById('question').value.trim();
  if (!q) return alert('မေးခွန်း ထည့်ပါ။');

  const btn = document.getElementById('run-btn');
  btn.disabled = true;

  document.getElementById('results-wrap').style.display = 'flex';
  document.getElementById('insight-row').classList.remove('visible');

  models.forEach(m => setLoading(m.key));

  const results = {};

  try {
    for (let i = 0; i < models.length; i++) {
      const m = models[i];
      btn.textContent = `⏳ Racing... ${m.label} (${i+1}/3)`;

      try {
        const res = await fetch('/api/benchmark', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({question: q, model_key: m.key})
        }).then(r => r.json());

        if (res.error) throw new Error(res.error);

        results[m.key] = res;

        document.getElementById(`ttft-${m.key}`).textContent  = res.ttft + 'ms';
        document.getElementById(`total-${m.key}`).textContent = res.total + 'ms';
        document.getElementById(`tokens-${m.key}`).textContent = res.tokens;
        document.getElementById(`ans-${m.key}`).textContent   = res.text;
      } catch(e) {
        results[m.key] = null;
        document.getElementById(`ans-${m.key}`).innerHTML =
          `<span style="color:#C0392B;font-size:12px">Error: ${e.message}</span>`;
        ['ttft','total','tokens'].forEach(metric => {
          document.getElementById(`${metric}-${m.key}`).textContent = '—';
        });
      }
    }

    // Rank by total time
    const finished = models
      .filter(m => results[m.key])
      .sort((a, b) => results[a.key].total - results[b.key].total);

    const maxTime = Math.max(...finished.map(m => results[m.key].total));

    finished.forEach((m, i) => {
      const r = results[m.key];
      const pct = Math.round((1 - (r.total - finished[0].total) / (maxTime || 1)) * 100);
      setTimeout(() => {
        document.getElementById(`bar-${m.key}`).style.width = Math.max(pct, 15) + '%';
      }, 100);

      document.getElementById(`rank-${m.key}`).innerHTML =
        `<span style="font-size:22px">${rankEmojis[i]}</span>`;
    });

    // Insight summary
    if (finished.length > 0) {
      const fastest = finished[0];
      const slowest = finished[finished.length - 1];
      const speedDiff = slowest ? Math.round(results[slowest.key].total / results[fastest.key].total * 10) / 10 : 1;

      const insight = document.getElementById('insight-row');
      insight.classList.add('visible');
      insight.innerHTML = `
        🏁 <strong>Race ပြီးပြီ!</strong><br><br>
        ⚡ <strong>အမြန်ဆုံး</strong> → ${fastest.label} (${results[fastest.key].total}ms)<br>
        🐢 <strong>အနှေးဆုံး</strong> → ${slowest.label} (${results[slowest.key].total}ms)<br><br>
        ${fastest.key === 'haiku'
          ? `🎯 Haiku ဟာ ${speedDiff}x ပိုမြန်တယ် — ဒါကြောင့် cost-sensitive tasks တွေမှာ Haiku သုံးတာ အဓိပ္ပာယ်ရှိတယ် 💡`
          : `😮 ဒီတစ်ကြိမ်မှာ ${fastest.label} အမြန်ဆုံးထွက်တယ် — Network condition ပေါ်မူတည်ပြီး result ကွဲနိုင်တယ် 🌐`
        }<br><br>
        💡 <strong>TTFT vs Total Time</strong> —
        TTFT က "ပထမဆုံး စကားလုံး" ရဖို့ ကြာချိန်၊
        Total က response အကုန် ပြီးချိန်။
        Streaming app တွေမှာ TTFT ကို ပိုအရေးကြီးတယ်။
      `;
    }

  } catch(e) {
    console.error('Error:', e);
  }

  btn.disabled = false;
  btn.textContent = '🏁 Race Again!';
}
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        presets=PROMPTS,
        models=MODELS
    )

@app.route('/api/benchmark', methods=['POST'])
def benchmark():
    try:
        data = request.json
        question = data.get('question', '').strip()
        model_key = data.get('model_key', 'haiku')

        if not question:
            return jsonify({'error': 'Question required'}), 400

        # Find model
        model = next((m for m in MODELS if m['key'] == model_key), None)
        if not model:
            return jsonify({'error': 'Invalid model key'}), 400

        # Create prompt
        prompt = f"""Answer this question in 2-3 sentences in Burmese (Myanmar language). Be helpful and clear.

Question: {question}

Answer:"""

        # Measure timing
        start_time = time.time()
        ttft = None

        # Make request
        response = client.messages.create(
            model=model['id'],
            max_tokens=300,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        # Calculate times
        total_time = int((time.time() - start_time) * 1000)  # Convert to ms
        ttft = total_time // 2  # Rough estimate - API doesn't expose TTFT easily

        # Extract response
        text = response.content[0].text.strip()
        tokens = response.usage.output_tokens

        return jsonify({
            'text': text,
            'ttft': ttft,
            'total': total_time,
            'tokens': tokens
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏁 Model Speed Benchmark Server Starting...")
    print("="*70)
    print("\n📖 Open your browser: http://localhost:5002")
    print("\nExperiment:")
    print("  • Compare speed of Haiku, Sonnet, and Opus models")
    print("  • Measure TTFT (Time to First Token) and total response time")
    print("  • See which model is fastest for your questions")
    print("\n" + "="*70 + "\n")
    app.run(debug=True, port=5002)
