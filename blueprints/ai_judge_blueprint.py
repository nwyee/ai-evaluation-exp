"""
AI Judge Blueprint
"""

import json
from flask import Blueprint, render_template_string, request, jsonify
from openai import OpenAI
import os

# Create blueprint
ai_judge_bp = Blueprint('ai_judge', __name__, url_prefix='/ai-judge')

# Get client from app config (will be set by main app)
def get_client():
    from flask import current_app
    return current_app.config['OPENAI_CLIENT']

def get_model():
    from flask import current_app
    return current_app.config['MODEL_NAME']

# Preset data
SELF_PRESETS = [
    {"label": "🍜 မနက်စာ", "q": "ကောင်းတဲ့ မနက်စာ ဘာစားသင့်သလဲ?"},
    {"label": "😴 အိပ်ရေး", "q": "ညဘက် အိပ်ရေးဝဝ အိပ်ဖို့ ဘာလုပ်သင့်သလဲ?"},
    {"label": "💧 ရေသောက်", "q": "နေ့တိုင်း ရေဘယ်နှစ်ခွက် သောက်သင့်သလဲ?"},
    {"label": "🏃 လေ့ကျင့်ခန်း", "q": "ရုံးမှာ တစ်ရက်ကုန် ထိုင်ပြီးရင် ဘာလေ့ကျင့်ခန်း လုပ်သင့်သလဲ?"}
]

REF_PRESETS = [
    {
        "label": "🌧️ မိုးရာသီ",
        "q": "မိုးရာသီမှာ ဘာတွေ သတိထားသင့်သလဲ?",
        "ref": "မိုးရာသီမှာတော့ ထီးမမေ့ပါနဲ့၊ ရေစိုနေတဲ့နေရာတွေ ဂရုစိုက်ပါ၊ ချမ်းနိုင်လို့ အဝတ်ထပ်ဝတ်ပါ၊ ဝမ်းလျောနိုင်လို့ အပြင်ရေ သောက်တာလည်း သတိထားပါ။"
    },
    {
        "label": "☕ ကော်ဖီ",
        "q": "ကော်ဖီသောက်ခြင်းရဲ့ အကျိုးကျေးဇူးကို ရှင်းပြပါ။",
        "ref": "ကော်ဖီမှာ caffeine ပါဝင်တဲ့အတွက် အိပ်ငိုက်မှု လျော့ကျပြီး အာရုံစူးစိုက်မှု တိုးတက်တယ်။"
    },
    {
        "label": "🍎 သစ်သီး",
        "q": "နေ့တိုင်း သစ်သီးစားသင့်ဖို့ ဘာကြောင့်လဲ?",
        "ref": "သစ်သီးတွေမှာ vitamins နဲ့ minerals ကြွယ်ဝတဲ့အတွက် ခုခံအား ကောင်းတယ်။"
    }
]

H2H_PRESETS = [
    {"label": "🐶 ခွေးမွေး", "q": "ခွေးလေးတစ်ကောင် မွေးဖို့ ဆုံးဖြတ်ချက် မချခင် ဘာတွေ စဉ်းစားသင့်သလဲ?"},
    {"label": "📱 ဖုန်းသုံး", "q": "ကလေးတွေ smartphone ကို ဘယ်နှစ်နှစ်ကနေ သုံးခွင့်ပေးသင့်သလဲ?"},
    {"label": "🌿 ကျန်းမာရေး", "q": "stress လျော့ချဖို့ အကောင်းဆုံး နည်းလမ်း ၃ ခု ဘာတွေလဲ?"}
]

# Prompt templates
PROMPT_GENERATE_ANSWER = "Answer this question in 2-3 sentences in Burmese. Be clear and helpful.\n\nQuestion: {question}\n\nAnswer:"

PROMPT_GENERATE_ANSWER_SIMPLE = "Answer this question in 2-3 sentences in Burmese.\n\nQuestion: {question}\n\nAnswer:"

PROMPT_GENERATE_ANSWER_DETAILED = "Answer in detail in Burmese (2-3 sentences).\n\nQuestion: {question}\n\nAnswer:"

PROMPT_GENERATE_ANSWER_BRIEF = "Answer briefly in Burmese (1-2 sentences).\n\nQuestion: {question}\n\nAnswer:"

PROMPT_JUDGE_SELF = """You are an AI judge. Evaluate this answer fairly (1-5 scale).

Question: {question}
Answer: {answer}

Respond ONLY as JSON:
{{"score": <1-5>, "reasoning": "<2-3 sentences in English>"}}

1=Very bad, 2=Poor, 3=Acceptable, 4=Good, 5=Excellent"""

PROMPT_JUDGE_REFERENCE = """Compare generated answer to reference answer.

Question: {question}
Reference: {reference}
Generated: {generated}

Does generated answer convey same core meaning?
Respond ONLY as JSON:
{{"match": true or false, "reasoning": "<2-3 sentences in English>"}}"""

PROMPT_JUDGE_H2H = """Judge which answer is better.

Question: {question}
Answer A: {answer_a}
Answer B: {answer_b}

Which is better overall?
Respond ONLY as JSON:
{{"winner": "A" or "B", "reasoning": "<2-3 sentences in English>"}}"""

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI as a Judge — Python Web</title>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #F5F2ED;
            --card: #FFFFFF;
            --border: #E8E2D9;
            --text: #1A1714;
            --muted: #9A9189;
            --accent: #D4622A;
            --accent-light: #FDF0EB;
            --green: #2A7A4A;
            --green-light: #EBF5EF;
            --blue: #2A4A7A;
            --blue-light: #EBF0F5;
            --gold: #B8860B;
            --gold-light: #FDF8E6;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: var(--bg);
            font-family: 'DM Sans', sans-serif;
            color: var(--text);
            min-height: 100vh;
            padding: 32px 16px 60px;
        }
        .header {
            text-align: center;
            margin-bottom: 32px;
        }
        .header-title {
            font-family: 'Fraunces', serif;
            font-size: 36px;
            font-weight: 900;
            color: var(--text);
        }
        .header-title em {
            font-style: normal;
            color: var(--accent);
        }
        .header-sub {
            font-size: 12px;
            color: var(--muted);
            margin-top: 8px;
        }
        .tabs {
            display: flex;
            gap: 8px;
            justify-content: center;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }
        .tab {
            padding: 10px 20px;
            border-radius: 40px;
            border: 1.5px solid var(--border);
            background: var(--card);
            font-size: 12px;
            font-weight: 500;
            color: var(--muted);
            cursor: pointer;
            transition: all 0.2s;
        }
        .tab:hover { border-color: var(--accent); color: var(--accent); }
        .tab.active {
            background: var(--accent);
            border-color: var(--accent);
            color: #fff;
        }
        .card {
            max-width: 700px;
            margin: 0 auto;
            background: var(--card);
            border-radius: 20px;
            border: 1.5px solid var(--border);
            overflow: hidden;
            box-shadow: 0 8px 40px rgba(0,0,0,0.06);
        }
        .card-header {
            padding: 20px 28px;
            border-bottom: 1.5px solid var(--border);
        }
        .card-body { padding: 24px 28px; }
        .field { margin-bottom: 16px; }
        .field label {
            display: block;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 6px;
        }
        .field textarea, .field input {
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
        }
        .field textarea { min-height: 80px; line-height: 1.6; }
        .field textarea:focus { border-color: var(--accent); }
        .presets {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 16px;
        }
        .preset-pill {
            padding: 5px 12px;
            border-radius: 20px;
            border: 1px solid var(--border);
            font-size: 11px;
            color: var(--muted);
            background: var(--bg);
            cursor: pointer;
            transition: all 0.15s;
        }
        .preset-pill:hover {
            border-color: var(--accent);
            color: var(--accent);
            background: var(--accent-light);
        }
        .run-btn {
            width: 100%;
            padding: 14px;
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: 12px;
            font-family: 'DM Sans', sans-serif;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 8px;
        }
        .run-btn:hover { background: #b8521f; transform: translateY(-1px); }
        .run-btn:disabled { background: var(--border); color: var(--muted); cursor: not-allowed; transform: none; }
        .run-btn.secondary { background: var(--blue); }
        .run-btn.secondary:hover { background: #1f3860; }
        .result-area {
            margin-top: 20px;
            border-top: 1.5px solid var(--border);
            padding-top: 20px;
            display: none;
        }
        .result-area.visible { display: block; }
        .score-display {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }
        .score-number {
            font-family: 'Fraunces', serif;
            font-size: 56px;
            font-weight: 900;
        }
        .score-stars { font-size: 22px; }
        .verdict-box {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 16px;
            font-size: 15px;
            font-weight: 500;
        }
        .verdict-true { background: var(--green-light); color: var(--green); border: 1.5px solid #C0E0CA; }
        .verdict-false { background: #FEF0F0; color: #C0392B; border: 1.5px solid #F5C0C0; }
        .reasoning-box {
            background: var(--bg);
            border-radius: 10px;
            padding: 14px 16px;
            font-size: 13px;
            line-height: 1.7;
            color: #555;
            border: 1px solid var(--border);
        }
        .loading {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--muted);
            font-size: 13px;
            padding: 12px 0;
        }
        .spinner {
            width: 18px; height: 18px;
            border: 2px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .mode-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
        }
        .badge-self { background: var(--accent-light); color: var(--accent); }
        .badge-ref { background: var(--green-light); color: var(--green); }
        .badge-h2h { background: var(--blue-light); color: var(--blue); }
        .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .info-banner {
            max-width: 700px;
            margin: 0 auto 16px;
            background: var(--gold-light);
            border: 1px solid #E8D890;
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 11px;
            color: var(--gold);
        }
    </style>
</head>
<body>

<div class="header">
    <div class="header-title">AI as a <em>Judge</em></div>
    <div class="header-sub">🐍 Python Flask Edition | Minimal UI Single Page</div>
    <div style="font-size:11px;color:var(--muted);margin-top:12px;letter-spacing:1px">
        🤖 Model: <strong style="color:var(--accent)">{{ model_name }}</strong>
    </div>
</div>

<div class="info-banner">
    🤖 AI တစ်ခုတည်းကပဲ <strong>Answer ထုတ်ပြီး</strong> ကိုယ်တိုင် <strong>Judge လုပ်တယ်</strong>
</div>

<div class="tabs">
    <button class="tab active" onclick="switchTab('self')">1️⃣ Self Evaluation</button>
    <button class="tab" onclick="switchTab('ref')">2️⃣ Reference</button>
    <button class="tab" onclick="switchTab('h2h')">3️⃣ Head-to-Head</button>
</div>

<div class="card" id="card">

    <!-- SELF EVALUATION -->
    <div id="mode-self">
        <div class="card-header">
            <span class="mode-badge badge-self">⚖️ Self Evaluation</span>
            <div style="font-size:12px;color:var(--muted);margin-top:6px">AI ထုတ်တဲ့ answer ကို AI ကိုယ်တိုင် score ပေးတယ်</div>
        </div>
        <div class="card-body">
            <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:6px">💡 Presets</div>
            <div class="presets" id="self-presets"></div>
            <div class="field">
                <label>Question</label>
                <textarea id="self-question" placeholder="မေးခွန်း ထည့်ပါ..."></textarea>
            </div>
            <button class="run-btn secondary" onclick="generateSelfAnswer()">🤖 Step 1: Generate Answer</button>
            <div class="field" style="margin-top:16px;">
                <label>AI Generated Answer</label>
                <textarea id="self-answer" placeholder="Generate ပြီး ပေါ်တယ်..."></textarea>
            </div>
            <button class="run-btn" onclick="runSelf()">⚖️ Step 2: Judge It!</button>
            <div class="result-area" id="self-result"></div>
        </div>
    </div>

    <!-- REFERENCE COMPARISON -->
    <div id="mode-ref" style="display:none">
        <div class="card-header">
            <span class="mode-badge badge-ref">🔍 Reference Comparison</span>
            <div style="font-size:12px;color:var(--muted);margin-top:6px">AI ထုတ်တဲ့ answer နဲ့ reference မှတူမတူ စစ်တယ်</div>
        </div>
        <div class="card-body">
            <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:6px">💡 Presets</div>
            <div class="presets" id="ref-presets"></div>
            <div class="field">
                <label>Question</label>
                <textarea id="ref-question" placeholder="မေးခွန်း..."></textarea>
            </div>
            <div class="field">
                <label>✅ Reference Answer</label>
                <textarea id="ref-reference" placeholder="မှန်တယ်လို့ သတ်မှတ်ထားတဲ့ answer..."></textarea>
            </div>
            <button class="run-btn secondary" onclick="generateRefAnswer()">🤖 Step 1: Generate Answer</button>
            <div class="field" style="margin-top:16px;">
                <label>🤖 AI Generated Answer</label>
                <textarea id="ref-generated" placeholder="Generate ပြီး ပေါ်တယ်..."></textarea>
            </div>
            <button class="run-btn" style="background:var(--green)" onclick="runRef()">🔍 Step 2: Compare!</button>
            <div class="result-area" id="ref-result"></div>
        </div>
    </div>

    <!-- HEAD TO HEAD -->
    <div id="mode-h2h" style="display:none">
        <div class="card-header">
            <span class="mode-badge badge-h2h">⚔️ Head-to-Head</span>
            <div style="font-size:12px;color:var(--muted);margin-top:6px">AI ထုတ်တဲ့ နှစ်ခု answers အချင်းချင်းနှိုင်းယှဥ်</div>
        </div>
        <div class="card-body">
            <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:6px">💡 Presets</div>
            <div class="presets" id="h2h-presets"></div>
            <div class="field">
                <label>Question</label>
                <textarea id="h2h-question" placeholder="မေးခွန်း..."></textarea>
            </div>
            <button class="run-btn secondary" onclick="generateH2HAnswers()">🤖 Step 1: Generate Both</button>
            <div class="two-col" style="margin-top:16px;">
                <div class="field">
                    <label>🔵 Answer A</label>
                    <textarea id="h2h-a" placeholder="Generate နှိပ်ပါ..."></textarea>
                </div>
                <div class="field">
                    <label>🟡 Answer B</label>
                    <textarea id="h2h-b" placeholder="Generate နှိပ်ပါ..."></textarea>
                </div>
            </div>
            <button class="run-btn" style="background:var(--gold)" onclick="runH2H()">⚔️ Step 2: Battle!</button>
            <div class="result-area" id="h2h-result"></div>
        </div>
    </div>

</div>

<script>
const selfPresets = {{ self_presets|tojson }};
const refPresets = {{ ref_presets|tojson }};
const h2hPresets = {{ h2h_presets|tojson }};

function buildPresets(data, containerId, fillFn) {
    const c = document.getElementById(containerId);
    data.forEach((p, i) => {
        const btn = document.createElement('button');
        btn.className = 'preset-pill';
        btn.textContent = p.label;
        btn.onclick = (e) => { e.preventDefault(); fillFn(i); };
        c.appendChild(btn);
    });
}

buildPresets(selfPresets, 'self-presets', i => {
    document.getElementById('self-question').value = selfPresets[i].q;
    document.getElementById('self-answer').value = '';
    document.getElementById('self-result').classList.remove('visible');
});

buildPresets(refPresets, 'ref-presets', i => {
    document.getElementById('ref-question').value = refPresets[i].q;
    document.getElementById('ref-reference').value = refPresets[i].ref;
    document.getElementById('ref-generated').value = '';
    document.getElementById('ref-result').classList.remove('visible');
});

buildPresets(h2hPresets, 'h2h-presets', i => {
    document.getElementById('h2h-question').value = h2hPresets[i].q;
    document.getElementById('h2h-a').value = '';
    document.getElementById('h2h-b').value = '';
    document.getElementById('h2h-result').classList.remove('visible');
});

function switchTab(mode) {
    ['self','ref','h2h'].forEach(m => {
        document.getElementById('mode-' + m).style.display = m === mode ? 'block' : 'none';
    });
    document.querySelectorAll('.tab').forEach((t, i) => {
        t.classList.toggle('active', ['self','ref','h2h'][i] === mode);
    });
}

async function generateSelfAnswer() {
    const q = document.getElementById('self-question').value.trim();
    if (!q) return alert('မေးခွန်း ထည့်ပါ။');
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳ အလုပ်လုပ်နေတယ်...';
    try {
        const res = await fetch('/ai-judge/api/generate_self', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: q})
        });
        const data = await res.json();
        if (data.answer) {
            document.getElementById('self-answer').value = data.answer;
        } else {
            alert('Error: ' + data.error);
        }
    } catch(e) {
        alert('Error: ' + e.message);
    }
    btn.disabled = false;
    btn.textContent = '🤖 Step 1: Generate Answer';
}

async function runSelf() {
    const q = document.getElementById('self-question').value.trim();
    const a = document.getElementById('self-answer').value.trim();
    if (!q || !a) return alert('အဆင့် ၁ ကို အရင် နှိပ်ပါ။');
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳ Judge လုပ်နေတယ်...';
    const result = document.getElementById('self-result');
    result.innerHTML = '<div class="loading"><div class="spinner"></div> AI Judge တွေးနေတယ်...</div>';
    result.classList.add('visible');
    try {
        const res = await fetch('/ai-judge/api/judge_self', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: q, answer: a})
        });
        const data = await res.json();
        if (data.score) {
            const colors = ['','#C0392B','#E67E22','#F39C12','#27AE60','#2ECC71'];
            result.innerHTML = `
                <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:12px">AI JUDGE ရဲ့ အဆင့်သတ်မှတ်ချက်</div>
                <div class="score-display">
                    <div class="score-number" style="color:${colors[data.score]}">${data.score}</div>
                    <div>
                        <div class="score-stars">${'⭐'.repeat(data.score)}${'☆'.repeat(5-data.score)}</div>
                    </div>
                </div>
                <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px">REASONING</div>
                <div class="reasoning-box">${data.reasoning}</div>
            `;
        } else {
            result.innerHTML = '<div class="reasoning-box" style="color:#C0392B">Error: ' + data.error + '</div>';
        }
    } catch(e) {
        result.innerHTML = '<div class="reasoning-box" style="color:#C0392B">Error: ' + e.message + '</div>';
    }
    btn.disabled = false;
    btn.textContent = '⚖️ Step 2: Judge It!';
}

async function generateRefAnswer() {
    const q = document.getElementById('ref-question').value.trim();
    if (!q) return alert('မေးခွန်း ထည့်ပါ။');
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳ အလုပ်လုပ်နေတယ်...';
    try {
        const res = await fetch('/ai-judge/api/generate_ref', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: q})
        });
        const data = await res.json();
        if (data.answer) {
            document.getElementById('ref-generated').value = data.answer;
        } else {
            alert('Error: ' + data.error);
        }
    } catch(e) {
        alert('Error: ' + e.message);
    }
    btn.disabled = false;
    btn.textContent = '🤖 Step 1: Generate Answer';
}

async function runRef() {
    const q = document.getElementById('ref-question').value.trim();
    const ref = document.getElementById('ref-reference').value.trim();
    const gen = document.getElementById('ref-generated').value.trim();
    if (!q || !ref || !gen) return alert('အဆင့် ၁ နှိပ်ပြီး generate လုပ်ပါ။');
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳ နှိုင်းယှဉ်နေတယ်...';
    const result = document.getElementById('ref-result');
    result.innerHTML = '<div class="loading"><div class="spinner"></div> AI Judge နှိုင်းယှဉ်နေတယ်...</div>';
    result.classList.add('visible');
    try {
        const res = await fetch('/ai-judge/api/judge_ref', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: q, reference: ref, generated: gen})
        });
        const data = await res.json();
        if (data.match !== undefined) {
            const isTrue = data.match;
            result.innerHTML = `
                <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:12px">VERDICT</div>
                <div class="verdict-box ${isTrue ? 'verdict-true' : 'verdict-false'}">
                    <div style="font-size:24px">${isTrue ? '✅' : '❌'}</div>
                    <div>
                        <div style="font-size:16px;font-weight:700">${isTrue ? 'MATCH ✅' : 'NO MATCH ❌'}</div>
                    </div>
                </div>
                <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px">REASONING</div>
                <div class="reasoning-box">${data.reasoning}</div>
            `;
        } else {
            result.innerHTML = '<div class="reasoning-box" style="color:#C0392B">Error: ' + data.error + '</div>';
        }
    } catch(e) {
        result.innerHTML = '<div class="reasoning-box" style="color:#C0392B">Error: ' + e.message + '</div>';
    }
    btn.disabled = false;
    btn.textContent = '🔍 Step 2: Compare!';
}

async function generateH2HAnswers() {
    const q = document.getElementById('h2h-question').value.trim();
    if (!q) return alert('မေးခွန်း ထည့်ပါ။');
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳ နှစ်ခု ထုတ်နေတယ်...';
    try {
        const res = await fetch('/ai-judge/api/generate_h2h', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: q})
        });
        const data = await res.json();
        if (data.answer_a && data.answer_b) {
            document.getElementById('h2h-a').value = data.answer_a;
            document.getElementById('h2h-b').value = data.answer_b;
        } else {
            alert('Error: ' + data.error);
        }
    } catch(e) {
        alert('Error: ' + e.message);
    }
    btn.disabled = false;
    btn.textContent = '🤖 Step 1: Generate Both';
}

async function runH2H() {
    const q = document.getElementById('h2h-question').value.trim();
    const a = document.getElementById('h2h-a').value.trim();
    const b = document.getElementById('h2h-b').value.trim();
    if (!q || !a || !b) return alert('အဆင့် ၁ နှိပ်ပါ။');
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳ Battle လုပ်နေတယ်...';
    const result = document.getElementById('h2h-result');
    result.innerHTML = '<div class="loading"><div class="spinner"></div> AI Judge ဆုံးဖြတ်နေတယ်...</div>';
    result.classList.add('visible');
    try {
        const res = await fetch('/ai-judge/api/judge_h2h', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: q, answer_a: a, answer_b: b})
        });
        const data = await res.json();
        if (data.winner) {
            const winA = data.winner === 'A';
            result.innerHTML = `
                <div style="font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:12px">🏆 WINNER</div>
                <div class="verdict-box" style="background:var(--gold-light);color:var(--gold);border:1.5px solid #E8D890;">
                    <div style="font-size:24px">${winA ? '🔵' : '🟡'}</div>
                    <div>
                        <div style="font-size:18px;font-weight:700">Answer ${data.winner} !</div>
                    </div>
                </div>
                <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px">REASONING</div>
                <div class="reasoning-box">${data.reasoning}</div>
            `;
        } else {
            result.innerHTML = '<div class="reasoning-box" style="color:#C0392B">Error: ' + data.error + '</div>';
        }
    } catch(e) {
        result.innerHTML = '<div class="reasoning-box" style="color:#C0392B">Error: ' + e.message + '</div>';
    }
    btn.disabled = false;
    btn.textContent = '⚔️ Step 2: Battle!';
}
</script>

</body>
</html>
"""

# Routes
@ai_judge_bp.route('/')
def index():
    from flask import current_app
    model_name = get_model()

    # Add navigation if function exists
    template = HTML_TEMPLATE
    if hasattr(current_app, 'add_navigation'):
        template = current_app.add_navigation(HTML_TEMPLATE, "AI as a Judge")

    return render_template_string(
        template,
        model_name=model_name,
        self_presets=SELF_PRESETS,
        ref_presets=REF_PRESETS,
        h2h_presets=H2H_PRESETS
    )

@ai_judge_bp.route('/api/generate_self', methods=['POST'])
def api_generate_self():
    try:
        client = get_client()
        model = get_model()
        data = request.json
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Question required'}), 400

        prompt = PROMPT_GENERATE_ANSWER.format(question=question)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_judge_bp.route('/api/judge_self', methods=['POST'])
def api_judge_self():
    try:
        client = get_client()
        model = get_model()
        data = request.json
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()

        prompt = PROMPT_JUDGE_SELF.format(question=question, answer=answer)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text.replace('```json', '').replace('```', '').strip())
        result['score'] = min(5, max(1, int(result['score'])))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_judge_bp.route('/api/generate_ref', methods=['POST'])
def api_generate_ref():
    try:
        client = get_client()
        model = get_model()
        data = request.json
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Question required'}), 400

        prompt = PROMPT_GENERATE_ANSWER_SIMPLE.format(question=question)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_judge_bp.route('/api/judge_ref', methods=['POST'])
def api_judge_ref():
    try:
        client = get_client()
        model = get_model()
        data = request.json
        question = data.get('question', '').strip()
        reference = data.get('reference', '').strip()
        generated = data.get('generated', '').strip()

        prompt = PROMPT_JUDGE_REFERENCE.format(
            question=question,
            reference=reference,
            generated=generated
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text.replace('```json', '').replace('```', '').strip())
        result['match'] = result.get('match', False) in [True, 'True', 'true', 'yes', 'Yes']
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_judge_bp.route('/api/generate_h2h', methods=['POST'])
def api_generate_h2h():
    try:
        client = get_client()
        model = get_model()
        data = request.json
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Question required'}), 400

        prompt_a = PROMPT_GENERATE_ANSWER_DETAILED.format(question=question)
        prompt_b = PROMPT_GENERATE_ANSWER_BRIEF.format(question=question)

        resp_a = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_a}],
            temperature=0.7
        )
        resp_b = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_b}],
            temperature=0.7
        )
        answer_a = resp_a.choices[0].message.content.strip()
        answer_b = resp_b.choices[0].message.content.strip()
        return jsonify({'answer_a': answer_a, 'answer_b': answer_b})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_judge_bp.route('/api/judge_h2h', methods=['POST'])
def api_judge_h2h():
    try:
        client = get_client()
        model = get_model()
        data = request.json
        question = data.get('question', '').strip()
        answer_a = data.get('answer_a', '').strip()
        answer_b = data.get('answer_b', '').strip()

        prompt = PROMPT_JUDGE_H2H.format(
            question=question,
            answer_a=answer_a,
            answer_b=answer_b
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text.replace('```json', '').replace('```', '').strip())
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
