"""
Temperature Experiment - Test LLM Creativity at Different Temperatures

Inspired by temperature_experiment.html design
Tests how temperature=0 gives consistent results and higher temps give creativity
Run 1 vs Run 2 comparison format
"""

import os
import json
import sys
from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment
current_dir = Path(__file__).parent
for directory in [current_dir, current_dir.parent, current_dir.parent.parent]:
    env_file = directory / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

# Initialize OpenAI client
api_key = os.getenv("PROXY_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("PROXY_BASE_URL")

if not api_key:
    print("❌ Error: PROXY_API_KEY or OPENAI_API_KEY not set in .env")
    sys.exit(1)

client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
model = os.getenv("MODEL_NAME", "gpt-4.1-mini")

app = Flask(__name__)

# Sample prompts for testing (Myanmar language)
PROMPTS = [
    {"label": "🥗 ကျန်းမာရေး", "q": "ကျန်းမာရေးကောင်းဖို့ ဘာတွေ လုပ်သင့်သလဲ?"},
    {"label": "😴 အိပ်ရေး", "q": "ညဘက် ကောင်းကောင်းအိပ်ဖို့ နည်းလမ်းတွေ ပြောပြပါ။"},
    {"label": "📚 စာဖတ်", "q": "စာဖတ်တဲ့ အလေ့အကျင့် ဘယ်လို တည်ဆောက်မလဲ?"},
    {"label": "💼 အလုပ်", "q": "အလုပ်မှာ productive ဖြစ်ဖို့ tip တွေ ပေးပါ။"},
    {"label": "🐶 ခွေးမွေး", "q": "ခွေးလေးတစ်ကောင် မွေးမယ်ဆိုရင် ဘာတွေ ပြင်ဆင်ရမလဲ?"},
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Temperature Experiment</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #F6F3EE;
    --card: #fff;
    --border: #E8E2D8;
    --text: #1A1714;
    --muted: #9A9189;
    --t0:   #2A6A4A;
    --t07:  #D4622A;
    --t10:  #7A2A6A;
    --t0-bg:   #EBF5EF;
    --t07-bg:  #FDF0EB;
    --t10-bg:  #F5EBF5;
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

  h1 em { font-style: normal; color: var(--t07); }

  .subtitle {
    font-size: 12px;
    color: var(--muted);
    margin-top: 8px;
    letter-spacing: 0.3px;
  }

  .model-info {
    font-size: 11px;
    color: var(--muted);
    margin-top: 12px;
  }

  .model-info strong { color: var(--t07); }

  .legend {
    display: flex;
    justify-content: center;
    gap: 16px;
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

  .input-card {
    max-width: 680px;
    margin: 0 auto 20px;
    background: var(--card);
    border-radius: 16px;
    border: 1.5px solid var(--border);
    padding: 20px 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  }

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

  .field textarea:focus { border-color: var(--t07); }

  .presets {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 14px;
  }

  .preset-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
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

  .pill:hover { border-color: var(--t07); color: var(--t07); background: var(--t07-bg); }

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

  .results-wrap {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .temp-row {
    background: var(--card);
    border-radius: 16px;
    border: 1.5px solid var(--border);
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    animation: fadeUp 0.4s ease both;
  }

  .row-header {
    padding: 14px 20px;
    border-bottom: 1.5px solid;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .temp-badge {
    font-family: 'Fraunces', serif;
    font-size: 22px;
    font-weight: 900;
  }

  .temp-meta { flex: 1; }

  .temp-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .temp-desc { font-size: 10px; color: var(--muted); margin-top: 2px; }

  .runs-grid {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 0;
    align-items: stretch;
  }

  .run-box {
    padding: 16px 20px;
  }

  .run-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
  }

  .divider {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 12px;
    font-size: 11px;
    font-weight: 700;
    color: var(--muted);
    border-left: 1px solid var(--border);
    border-right: 1px solid var(--border);
    background: var(--bg);
    letter-spacing: 1px;
  }

  .answer-box {
    font-size: 13px;
    line-height: 1.7;
    color: var(--text);
    min-height: 60px;
  }

  .match-row {
    padding: 10px 20px;
    border-top: 1px solid var(--border);
    font-size: 12px;
    min-height: 36px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--bg);
  }

  .loading-text {
    font-size: 12px;
    color: var(--muted);
    text-align: center;
  }

  .spinner {
    width: 14px; height: 14px;
    border: 2px solid var(--border);
    border-top-color: var(--t07);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    display: inline-block;
    vertical-align: middle;
    margin-right: 6px;
  }

  .consistency-row {
    max-width: 900px;
    margin: 16px auto 0;
    background: var(--card);
    border-radius: 12px;
    border: 1.5px solid var(--border);
    padding: 14px 20px;
    display: none;
    font-size: 12px;
    color: var(--muted);
    text-align: center;
    line-height: 1.7;
  }

  .consistency-row.visible { display: block; }
  .consistency-row strong { color: var(--text); }

  .footer {
    text-align: center;
    margin-top: 32px;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 2px;
  }

  .footer em { color: var(--t07); font-style: normal; }

  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
</head>
<body>

<div class="header">
  <div class="eyebrow">AI Engineering Experiment Lab</div>
  <h1>Temperature <em>Effect</em></h1>
  <div class="subtitle">တူတဲ့ မေးခွန်း · တူတဲ့ AI · ဒါပေမယ့် temperature ကွဲရင် result ကွဲသလား?</div>
  <div class="model-info">🤖 Model: <strong>{{ model_name }}</strong></div>
</div>

<div class="legend">
  <div class="legend-item">
    <div class="legend-dot" style="background:var(--t0)"></div>
    <span style="color:var(--t0)">Temperature 0 — Consistent 🧊</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:var(--t07)"></div>
    <span style="color:var(--t07)">Temperature 0.7 — Balanced ⚖️</span>
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:var(--t10)"></div>
    <span style="color:var(--t10)">Temperature 1.0 — Creative 🎲</span>
  </div>
</div>

<div class="input-card">
  <div class="preset-label">💡 Preset Questions</div>
  <div class="presets" id="presets"></div>

  <div class="field">
    <label>မေးခွန်း — တူတဲ့ question ကို temperatures ၃ ခုနဲ့ run မယ်</label>
    <textarea id="question" placeholder="ဥပမာ — ကျန်းမာရေးကောင်းဖို့ ဘာတွေ လုပ်သင့်သလဲ?"></textarea>
  </div>

  <button class="run-btn" id="run-btn" onclick="runAll()">🌡️ Run with all 3 temperatures</button>
</div>

<div class="results-wrap" id="results-wrap" style="display:none">

  <!-- Temp 0 -->
  <div class="temp-row">
    <div class="row-header" style="background:var(--t0-bg);border-color:#C0E0CA">
      <div class="temp-badge" style="color:var(--t0)">0</div>
      <div class="temp-meta">
        <div class="temp-label" style="color:var(--t0)">Temperature 0 🧊</div>
        <div class="temp-desc">Deterministic — Run နှစ်ကြိမ်လုံး တူသင့်တယ်</div>
      </div>
    </div>
    <div class="runs-grid">
      <div class="run-box">
        <div class="run-label">Run 1</div>
        <div class="answer-box" id="r1-0">—</div>
      </div>
      <div class="divider">VS</div>
      <div class="run-box">
        <div class="run-label">Run 2</div>
        <div class="answer-box" id="r2-0">—</div>
      </div>
    </div>
    <div class="match-row" id="match-0"></div>
  </div>

  <!-- Temp 0.7 -->
  <div class="temp-row">
    <div class="row-header" style="background:var(--t07-bg);border-color:#F0C8A8">
      <div class="temp-badge" style="color:var(--t07)">0.7</div>
      <div class="temp-meta">
        <div class="temp-label" style="color:var(--t07)">Temperature 0.7 ⚖️</div>
        <div class="temp-desc">Balanced — ကွဲနိုင်တယ်</div>
      </div>
    </div>
    <div class="runs-grid">
      <div class="run-box">
        <div class="run-label">Run 1</div>
        <div class="answer-box" id="r1-07">—</div>
      </div>
      <div class="divider">VS</div>
      <div class="run-box">
        <div class="run-label">Run 2</div>
        <div class="answer-box" id="r2-07">—</div>
      </div>
    </div>
    <div class="match-row" id="match-07"></div>
  </div>

  <!-- Temp 1.0 -->
  <div class="temp-row">
    <div class="row-header" style="background:var(--t10-bg);border-color:#D8C0D8">
      <div class="temp-badge" style="color:var(--t10)">1.0</div>
      <div class="temp-meta">
        <div class="temp-label" style="color:var(--t10)">Temperature 1.0 🎲</div>
        <div class="temp-desc">Creative — အများဆုံး ကွဲပြားမယ်</div>
      </div>
    </div>
    <div class="runs-grid">
      <div class="run-box">
        <div class="run-label">Run 1</div>
        <div class="answer-box" id="r1-10">—</div>
      </div>
      <div class="divider">VS</div>
      <div class="run-box">
        <div class="run-label">Run 2</div>
        <div class="answer-box" id="r2-10">—</div>
      </div>
    </div>
    <div class="match-row" id="match-10"></div>
  </div>

</div>

<div class="consistency-row" id="insight-row"></div>

<div class="footer" style="margin-top:32px">
  <em>📚 AI Engineering</em> — Temperature Experiment
</div>

<script>
const prompts = {{ prompts|tojson }};

const container = document.getElementById('presets');
prompts.forEach(p => {
  const btn = document.createElement('button');
  btn.className = 'pill';
  btn.textContent = p.label;
  btn.onclick = () => {
    document.getElementById('question').value = p.q;
    resetResults();
  };
  container.appendChild(btn);
});

function resetResults() {
  document.getElementById('results-wrap').style.display = 'none';
  document.getElementById('insight-row').classList.remove('visible');
  ['0','07','10'].forEach(t => {
    document.getElementById('r1-' + t).innerHTML = '—';
    document.getElementById('r2-' + t).innerHTML = '—';
    document.getElementById('match-' + t).innerHTML = '';
  });
}

function setLoading(run, t) {
  document.getElementById(`r${run}-${t}`).innerHTML =
    `<div class="loading-text"><span class="spinner"></span> Generating...</div>`;
}

async function showMatch(t, a, b) {
  const el = document.getElementById('match-' + t);
  try {
    const compareRes = await fetch('/api/compare', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text1: a, text2: b})
    }).then(r => r.json());

    const similarity = compareRes.similarity;
    const percentage = compareRes.percentage;
    const exact = compareRes.exact_match;

    if (exact) {
      el.innerHTML = `<span style="color:var(--t0);font-weight:500">✅ Run 1 နဲ့ Run 2 တူညီတယ်!</span> <span style="color:var(--muted);font-size:11px">— 100% match · Temperature ${t === '0' ? '0' : t === '07' ? '0.7' : '1.0'} consistent</span>`;
      el.style.background = 'var(--t0-bg)';
    } else {
      el.innerHTML = `<span style="color:var(--t07);font-weight:500">🎲 Run 1 နဲ့ Run 2 ကွဲပြားတယ်!</span> <span style="color:var(--muted);font-size:11px">— ${percentage}% similarity</span>`;
      el.style.background = 'var(--t07-bg)';
    }
  } catch (err) {
    el.innerHTML = `<span style="color:#C0392B;font-size:11px">Error comparing: ${err.message}</span>`;
  }
}

async function runAll() {
  const q = document.getElementById('question').value.trim();
  if (!q) return alert('မေးခွန်း ထည့်ပါ။');

  const btn = document.getElementById('run-btn');
  btn.disabled = true;
  btn.textContent = '⏳ Running... (1/6)';

  document.getElementById('results-wrap').style.display = 'flex';
  document.getElementById('insight-row').classList.remove('visible');
  ['0','07','10'].forEach(t => {
    setLoading(1, t);
    setLoading(2, t);
    document.getElementById('match-' + t).innerHTML = '';
  });

  const prompt = `Answer this question in 2-3 sentences in Burmese (Myanmar language). Be helpful and clear.

Question: ${q}

Answer:`;

  try {
    const r1_0 = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: prompt, temperature: 0})
    }).then(r => r.json()).then(d => d.answer);
    document.getElementById('r1-0').innerHTML = r1_0;
    btn.textContent = '⏳ Running... (2/6)';

    const r1_07 = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: prompt, temperature: 0.7})
    }).then(r => r.json()).then(d => d.answer);
    document.getElementById('r1-07').innerHTML = r1_07;
    btn.textContent = '⏳ Running... (3/6)';

    const r1_10 = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: prompt, temperature: 1.0})
    }).then(r => r.json()).then(d => d.answer);
    document.getElementById('r1-10').innerHTML = r1_10;
    btn.textContent = '⏳ Running... (4/6)';

    const r2_0 = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: prompt, temperature: 0})
    }).then(r => r.json()).then(d => d.answer);
    document.getElementById('r2-0').innerHTML = r2_0;
    btn.textContent = '⏳ Running... (5/6)';

    const r2_07 = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: prompt, temperature: 0.7})
    }).then(r => r.json()).then(d => d.answer);
    document.getElementById('r2-07').innerHTML = r2_07;
    btn.textContent = '⏳ Running... (6/6)';

    const r2_10 = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: prompt, temperature: 1.0})
    }).then(r => r.json()).then(d => d.answer);
    document.getElementById('r2-10').innerHTML = r2_10;

    await showMatch('0',  r1_0,  r2_0);
    await showMatch('07', r1_07, r2_07);
    await showMatch('10', r1_10, r2_10);

    // Fetch similarity data for final insights
    const getSimilarity = async (a, b) => {
      const res = await fetch('/api/compare', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text1: a, text2: b})
      }).then(r => r.json());
      return res.exact_match;
    };

    const t0Same  = await getSimilarity(r1_0,  r2_0);
    const t07Same = await getSimilarity(r1_07, r2_07);
    const t10Same = await getSimilarity(r1_10, r2_10);

    const insight = document.getElementById('insight-row');
    insight.classList.add('visible');
    insight.innerHTML = `
      🔬 <strong>ရလဒ် အချုပ်</strong> —
      Temperature 0: ${t0Same ? '✅ တူတယ်' : '🎲 ကွဲတယ်'} &nbsp;|&nbsp;
      Temperature 0.7: ${t07Same ? '✅ တူတယ်' : '🎲 ကွဲတယ်'} &nbsp;|&nbsp;
      Temperature 1.0: ${t10Same ? '✅ တူတယ်' : '🎲 ကွဲတယ်'}
      <br><br>
      ${t0Same
        ? '🧊 <strong>Temperature 0 ဟာ တကယ်ပဲ consistent ဖြစ်တယ်</strong> — AI Judge အတွက် ဒါကြောင့် temperature 0 ကောင်းတယ် ✅'
        : '😮 <strong>Temperature 0 တောင် ကွဲသွားတယ်!</strong> — ဒီ model မှာ temperature 0 မှာပဲ တခါတရံ ကွဲနိုင်တယ်ဆိုတာ သတိပြုပါ ⚠️'
      }
    `;

  } catch(e) {
    ['0','07','10'].forEach(t => {
      document.getElementById('r1-' + t).innerHTML =
      document.getElementById('r2-' + t).innerHTML =
        `<span style="color:#C0392B;font-size:12px">Error: ${e.message}</span>`;
    });
  }

  btn.disabled = false;
  btn.textContent = '🌡️ Run again';
}
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        model_name=model,
        prompts=PROMPTS
    )

def calculate_similarity(text1, text2):
    """Calculate similarity score between two texts (0-1)"""
    from difflib import SequenceMatcher

    # Normalize texts
    t1 = text1.lower().strip()
    t2 = text2.lower().strip()

    # Exact match
    if t1 == t2:
        return 1.0

    # Calculate similarity ratio
    ratio = SequenceMatcher(None, t1, t2).ratio()
    return round(ratio, 2)

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        question = data.get('question', '').strip()
        temperature = float(data.get('temperature', 0.7))

        if not question:
            return jsonify({'error': 'Question required'}), 400

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
            temperature=temperature,
            max_tokens=300
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({'answer': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare():
    """Compare two texts and return similarity score"""
    try:
        data = request.json
        text1 = data.get('text1', '').strip()
        text2 = data.get('text2', '').strip()

        if not text1 or not text2:
            return jsonify({'error': 'Both texts required'}), 400

        similarity = calculate_similarity(text1, text2)
        is_exact = text1 == text2

        return jsonify({
            'similarity': similarity,
            'exact_match': is_exact,
            'percentage': int(similarity * 100)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧪 Temperature Experiment Server Starting...")
    print("="*70)
    print("\n📖 Open your browser: http://localhost:5001")
    print("\nExperiment:")
    print("  • Run same question with different temperatures")
    print("  • T=0.0: Same every time (consistent)")
    print("  • T=0.7: Similar with variation")
    print("  • T=1.0: Different each time (creative)")
    print("\n" + "="*70 + "\n")
    app.run(debug=True, port=5001)
