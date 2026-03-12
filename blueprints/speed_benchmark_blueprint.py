"""
Speed Benchmark Blueprint
"""

import time
from flask import Blueprint, render_template_string, request, jsonify

# Create blueprint
speed_benchmark_bp = Blueprint('speed_benchmark', __name__, url_prefix='/speed-benchmark')

# Get client from app config
def get_client():
    from flask import current_app
    return current_app.config['OPENAI_CLIENT']

def get_model():
    from flask import current_app
    return current_app.config['MODEL_NAME']

# Model configurations
MODELS = [
    {"key": "mini", "id": "gpt-4.1-nano", "label": "GPT-4.1 Nano", "params": "~4B"},
    {"key": "standard", "id": "gpt-4.1-mini", "label": "GPT-4.1 Mini", "params": "~13B"},
    {"key": "turbo", "id": "gpt-4.1", "label": "GPT-4.1", "params": "~175B"},
]

# Sample prompts
PROMPTS = [
    {"label": "🥗 ကျန်းမာရေး", "q": "ကျန်းမာရေးကောင်းဖို့ ဘာတွေ လုပ်သင့်သလဲ?"},
    {"label": "😴 အိပ်ရေး", "q": "ညဘက် ကောင်းကောင်းအိပ်ဖို့ နည်းလမ်းတွေ ပြောပြပါ။"},
    {"label": "📚 စာဖတ်", "q": "စာဖတ်တဲ့ အလေ့အကျင့် ဘယ်လို တည်ဆောက်မလဲ?"},
    {"label": "💼 အလုပ်", "q": "အလုပ်မှာ productive ဖြစ်ဖို့ tip တွေ ပေးပါ။"},
    {"label": "🤖 AI", "q": "AI engineering ဆိုတာ ဘာလဲ? ရှင်းပြပါ။"},
]

# Pricing per 1M tokens
PRICING = {
    "gpt-4.1-nano": {"input": 0.08, "output": 0.30},
    "gpt-4.1-mini": {"input": 0.15, "output": 0.60},
    "gpt-4.1": {"input": 5.00, "output": 15.00},
}

# Html template for the benchmark page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GPT Speed Benchmark</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #F6F3EE;
    --card: #fff;
    --border: #E8E2D8;
    --text: #1A1714;
    --muted: #9A9189;
    --mini:   #2A6A4A;
    --standard: #D4622A;
    --turbo:   #7A2A6A;
    --mini-bg:   #EBF5EF;
    --standard-bg: #FDF0EB;
    --turbo-bg:   #F5EBF5;
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

  h1 em { font-style: normal; color: var(--standard); }

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

  .pill:hover { border-color: var(--standard); color: var(--standard); background: var(--standard-bg); }

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

  .field textarea:focus { border-color: var(--standard); }

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
    border-top-color: var(--standard);
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

  .footer em { color: var(--standard); font-style: normal; }

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
  <h1>GPT Model <em>Speed</em> Benchmark</h1>
  <div class="subtitle">GPT-4.1 Nano vs GPT-4.1 Mini vs GPT-4.1 — တူတဲ့ question နဲ့ ဘယ် model အမြန်ဆုံးလဲ?</div>
</div>

<div class="legend">
  <div class="legend-item">
    <div class="legend-dot" style="background:var(--mini)"></div>
    <span style="color:var(--mini)">GPT-4.1 Nano 🚀 — ~4B parameters · အမြန်ဆုံး</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:var(--standard)"></div>
    <span style="color:var(--standard)">GPT-4.1 Mini ⚖️ — ~13B parameters · Balanced</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:var(--turbo)"></div>
    <span style="color:var(--turbo)">GPT-4.1 🧠 — ~175B parameters · အကောင်းဆုံး</span>
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

  <!-- Mini -->
  <div class="model-row" id="row-mini">
    <div class="model-header" style="background:var(--mini-bg); border-color:#C0E0CA">
      <div class="model-icon" style="color:var(--mini)">🚀</div>
      <div class="model-meta">
        <div class="model-name" style="color:var(--mini)">GPT-4.1 Nano</div>
        <div class="model-id">gpt-4.1-nano (~4B params)</div>
      </div>
      <div id="rank-mini"></div>
    </div>
    <div class="metrics-row">
      <div class="metric-cell">
        <div class="metric-value" id="time-mini" style="color:var(--mini)">—</div>
        <div class="metric-label">Total Time</div>
        <div class="metric-sub">ms</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="tokens-mini" style="color:var(--mini)">—</div>
        <div class="metric-label">Output Tokens</div>
        <div class="metric-sub">count</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="cost-mini" style="color:var(--mini)">—</div>
        <div class="metric-label">Est. Cost</div>
        <div class="metric-sub">¢</div>
      </div>
    </div>
    <div class="speed-bar-wrap">
      <div class="speed-bar-track">
        <div class="speed-bar-fill" id="bar-mini" style="background:var(--mini)"></div>
      </div>
    </div>
    <div class="answer-section">
      <div class="answer-label">Response</div>
      <div class="answer-text" id="ans-mini">—</div>
    </div>
  </div>

  <!-- Standard -->
  <div class="model-row" id="row-standard">
    <div class="model-header" style="background:var(--standard-bg); border-color:#F0C8A8">
      <div class="model-icon" style="color:var(--standard)">⚖️</div>
      <div class="model-meta">
        <div class="model-name" style="color:var(--standard)">GPT-4.1 Mini</div>
        <div class="model-id">gpt-4.1-mini (~13B params)</div>
      </div>
      <div id="rank-standard"></div>
    </div>
    <div class="metrics-row">
      <div class="metric-cell">
        <div class="metric-value" id="time-standard" style="color:var(--standard)">—</div>
        <div class="metric-label">Total Time</div>
        <div class="metric-sub">ms</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="tokens-standard" style="color:var(--standard)">—</div>
        <div class="metric-label">Output Tokens</div>
        <div class="metric-sub">count</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="cost-standard" style="color:var(--standard)">—</div>
        <div class="metric-label">Est. Cost</div>
        <div class="metric-sub">¢</div>
      </div>
    </div>
    <div class="speed-bar-wrap">
      <div class="speed-bar-track">
        <div class="speed-bar-fill" id="bar-standard" style="background:var(--standard)"></div>
      </div>
    </div>
    <div class="answer-section">
      <div class="answer-label">Response</div>
      <div class="answer-text" id="ans-standard">—</div>
    </div>
  </div>

  <!-- Turbo -->
  <div class="model-row" id="row-turbo">
    <div class="model-header" style="background:var(--turbo-bg); border-color:#D8C0D8">
      <div class="model-icon" style="color:var(--turbo)">🧠</div>
      <div class="model-meta">
        <div class="model-name" style="color:var(--turbo)">GPT-4.1</div>
        <div class="model-id">gpt-4.1 (~175B params)</div>
      </div>
      <div id="rank-turbo"></div>
    </div>
    <div class="metrics-row">
      <div class="metric-cell">
        <div class="metric-value" id="time-turbo" style="color:var(--turbo)">—</div>
        <div class="metric-label">Total Time</div>
        <div class="metric-sub">ms</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="tokens-turbo" style="color:var(--turbo)">—</div>
        <div class="metric-label">Output Tokens</div>
        <div class="metric-sub">count</div>
      </div>
      <div class="metric-cell">
        <div class="metric-value" id="cost-turbo" style="color:var(--turbo)">—</div>
        <div class="metric-label">Est. Cost</div>
        <div class="metric-sub">¢</div>
      </div>
    </div>
    <div class="speed-bar-wrap">
      <div class="speed-bar-track">
        <div class="speed-bar-fill" id="bar-turbo" style="background:var(--turbo)"></div>
      </div>
    </div>
    <div class="answer-section">
      <div class="answer-label">Response</div>
      <div class="answer-text" id="ans-turbo">—</div>
    </div>
  </div>

</div>

<div class="insight-row" id="insight-row"></div>

<div class="footer" style="margin-top:32px">
  <em>📚 AI Engineering</em> — GPT Model Speed Benchmark
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
    ['time','tokens','cost'].forEach(metric => {
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
  ['time','tokens','cost'].forEach(m => {
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
        const res = await fetch('/speed-benchmark/api/benchmark', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({question: q, model_key: m.key})
        }).then(r => r.json());

        if (res.error) throw new Error(res.error);

        results[m.key] = res;

        document.getElementById(`time-${m.key}`).textContent  = res.time + 'ms';
        document.getElementById(`tokens-${m.key}`).textContent = res.tokens;
        document.getElementById(`cost-${m.key}`).textContent   = res.cost;
        document.getElementById(`ans-${m.key}`).textContent   = res.text;
      } catch(e) {
        results[m.key] = null;
        document.getElementById(`ans-${m.key}`).innerHTML =
          `<span style="color:#C0392B;font-size:12px">Error: ${e.message}</span>`;
        ['time','tokens','cost'].forEach(metric => {
          document.getElementById(`${metric}-${m.key}`).textContent = '—';
        });
      }
    }

    // Rank by total time
    const finished = models
      .filter(m => results[m.key])
      .sort((a, b) => results[a.key].time - results[b.key].time);

    const maxTime = Math.max(...finished.map(m => results[m.key].time));

    finished.forEach((m, i) => {
      const r = results[m.key];
      const pct = Math.round((1 - (r.time - finished[0].time) / (maxTime || 1)) * 100);
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
      const speedDiff = slowest ? Math.round(results[slowest.key].time / results[fastest.key].time * 10) / 10 : 1;

      const insight = document.getElementById('insight-row');
      insight.classList.add('visible');
      insight.innerHTML = `
        🏁 <strong>Race ပြီးပြီ!</strong><br><br>
        🚀 <strong>အမြန်ဆုံး</strong> → ${fastest.label} (${results[fastest.key].time}ms)<br>
        🐢 <strong>အနှေးဆုံး</strong> → ${slowest.label} (${results[slowest.key].time}ms)<br><br>
        ${fastest.key === 'mini'
          ? `🚀 GPT-4.1 Nano ဟာ အမြန်ဆုံးပြီး စျေးသက်သာတယ် — ~4B parameters ကြောင့် Cost-efficient tasks တွေမှာ ideal ✅`
          : `🎯 ဒီတစ်ကြိမ်မှာ ${fastest.label} အမြန်ဆုံးထွက်တယ် — Network condition ပေါ်မူတည်နိုင်တယ် 🌐`
        }<br><br>
        💡 <strong>Speed vs Quality</strong> —
        အမြန်ဆုံးမဆိုအကောင်းဆုံးမဟုတ်ပါ။
        သင့်လျောက်စွာ model ရွေးချယ်ပါ။
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


# Import HTML template from original file
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Routes
@speed_benchmark_bp.route('/')
def index():
    from flask import current_app
    # Add navigation if function exists
    template = HTML_TEMPLATE
    if hasattr(current_app, 'add_navigation'):
        template = current_app.add_navigation(HTML_TEMPLATE, "Speed Benchmark")

    return render_template_string(
        template,
        presets=PROMPTS,
        models=MODELS
    )

@speed_benchmark_bp.route('/api/benchmark', methods=['POST'])
def benchmark():
    try:
        client = get_client()
        data = request.json
        question = data.get('question', '').strip()
        model_key = data.get('model_key', 'mini')

        if not question:
            return jsonify({'error': 'Question required'}), 400

        # Find model
        model_obj = next((m for m in MODELS if m['key'] == model_key), None)
        if not model_obj:
            return jsonify({'error': 'Invalid model key'}), 400

        # Create prompt
        prompt = f"""Answer this question in 2-3 sentences in Burmese (Myanmar language). Be helpful and clear.

Question: {question}

Answer:"""

        # Measure timing
        start_time = time.time()

        # Make request
        response = client.chat.completions.create(
            model=model_obj['id'],
            max_tokens=300,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        # Calculate time
        total_time = int((time.time() - start_time) * 1000)

        # Extract response
        text = response.choices[0].message.content.strip()

        # Handle different token attribute names
        if hasattr(response.usage, 'output_tokens'):
            output_tokens = response.usage.output_tokens
        elif hasattr(response.usage, 'completion_tokens'):
            output_tokens = response.usage.completion_tokens
        else:
            output_tokens = len(text.split())

        # Calculate estimated cost
        pricing = PRICING.get(model_obj['id'], {"input": 0, "output": 0})
        cost_cents = (output_tokens * pricing['output'] / 1_000_000) * 100

        return jsonify({
            'text': text,
            'time': total_time,
            'tokens': output_tokens,
            'cost': f"{cost_cents:.2f}"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
