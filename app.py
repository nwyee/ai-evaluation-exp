"""
AI Engineering Experiment Lab - Unified Application with Blueprints
All experiments integrated using Flask Blueprints
"""

import os
import sys
from flask import Flask, render_template_string
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

# Initialize Flask app
app = Flask(__name__)

# Store client and model in app config for blueprints to access
app.config['OPENAI_CLIENT'] = client
app.config['MODEL_NAME'] = model

# ═══════════════════════════════════════════════════════════════════════════
# NAVIGATION BAR COMPONENT
# ═══════════════════════════════════════════════════════════════════════════

NAV_BAR_STYLE = """
<style>
.nav-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1.5px solid #E8E2D8;
    padding: 12px 24px;
    z-index: 1000;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.nav-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.nav-home {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: #1A1714;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.2s;
}
.nav-home:hover {
    color: #D4622A;
}
.nav-home-icon {
    font-size: 18px;
}
.nav-title {
    font-size: 12px;
    color: #9A9189;
    text-transform: uppercase;
    letter-spacing: 1px;
}
body {
    padding-top: 60px !important;
}
</style>
"""

NAV_BAR_HTML = """
<div class="nav-bar">
    <div class="nav-content">
        <a href="/" class="nav-home">
            <span class="nav-home-icon">🏠</span>
            <span>Back to Home</span>
        </a>
        <div class="nav-title">{title}</div>
    </div>
</div>
"""

def add_navigation(html_template, page_title):
    """Add navigation bar to experiment page"""
    nav_html = NAV_BAR_HTML.format(title=page_title)
    html_with_nav = html_template.replace('<body>', f'<body>{NAV_BAR_STYLE}{nav_html}')
    return html_with_nav

# Register function for blueprints
app.add_navigation = add_navigation

# ═══════════════════════════════════════════════════════════════════════════
# REGISTER BLUEPRINTS
# ═══════════════════════════════════════════════════════════════════════════

from blueprints.ai_judge_blueprint import ai_judge_bp
from blueprints.speed_benchmark_blueprint import speed_benchmark_bp
from blueprints.temperature_blueprint import temperature_bp

app.register_blueprint(ai_judge_bp)
app.register_blueprint(speed_benchmark_bp)
app.register_blueprint(temperature_bp)

# ═══════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════════════════

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Engineering Experiment Lab</title>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #F6F3EE;
            --card: #FFFFFF;
            --border: #E8E2D8;
            --text: #1A1714;
            --muted: #9A9189;
            --accent: #D4622A;
            --accent-light: #FDF0EB;
            --green: #2A7A4A;
            --green-light: #EBF5EF;
            --blue: #2A4A7A;
            --blue-light: #EBF0F5;
            --purple: #7A2A6A;
            --purple-light: #F5EBF5;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: var(--bg);
            font-family: 'DM Sans', sans-serif;
            color: var(--text);
            min-height: 100vh;
            padding: 48px 24px;
        }

        .container { max-width: 1200px; margin: 0 auto; }

        .header {
            text-align: center;
            margin-bottom: 48px;
        }

        .eyebrow {
            font-size: 11px;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 12px;
            font-weight: 500;
        }

        h1 {
            font-family: 'Fraunces', serif;
            font-size: 48px;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 16px;
        }

        h1 .highlight { color: var(--accent); }

        .subtitle {
            font-size: 16px;
            color: var(--muted);
            line-height: 1.6;
            max-width: 600px;
            margin: 0 auto;
        }

        .experiments-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 24px;
            margin-bottom: 48px;
        }

        .experiment-card {
            background: var(--card);
            border-radius: 20px;
            border: 2px solid var(--border);
            overflow: hidden;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            text-decoration: none;
            color: inherit;
            display: block;
        }

        .experiment-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.12);
        }

        .card-header {
            padding: 24px;
            border-bottom: 2px solid var(--border);
        }

        .card-icon {
            font-size: 40px;
            margin-bottom: 12px;
            display: block;
        }

        .card-title {
            font-family: 'Fraunces', serif;
            font-size: 24px;
            font-weight: 900;
            margin-bottom: 8px;
            color: var(--text);
        }

        .card-subtitle {
            font-size: 12px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }

        .card-body { padding: 24px; }

        .card-description {
            font-size: 14px;
            line-height: 1.7;
            color: var(--text);
            margin-bottom: 20px;
        }

        .features-list {
            list-style: none;
            margin-bottom: 24px;
        }

        .features-list li {
            font-size: 13px;
            color: var(--muted);
            padding: 6px 0;
            padding-left: 20px;
            position: relative;
        }

        .features-list li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: var(--green);
            font-weight: 600;
        }

        .launch-btn {
            display: block;
            width: 100%;
            padding: 14px;
            background: var(--text);
            color: #fff;
            text-align: center;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 14px;
            letter-spacing: 0.5px;
            transition: all 0.2s ease;
        }

        .launch-btn:hover {
            background: var(--accent);
            transform: translateY(-1px);
        }

        .card-1 .card-header { background: var(--accent-light); border-color: #F0C8A8; }
        .card-1 .card-icon { color: var(--accent); }
        .card-1:hover { border-color: var(--accent); }

        .card-2 .card-header { background: var(--blue-light); border-color: #C0D8E8; }
        .card-2 .card-icon { color: var(--blue); }
        .card-2:hover { border-color: var(--blue); }

        .card-3 .card-header { background: var(--purple-light); border-color: #D8C0D8; }
        .card-3 .card-icon { color: var(--purple); }
        .card-3:hover { border-color: var(--purple); }

        .info-section {
            background: var(--card);
            border-radius: 16px;
            border: 2px solid var(--border);
            padding: 32px;
            margin-bottom: 32px;
        }

        .info-title {
            font-family: 'Fraunces', serif;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 16px;
            color: var(--text);
        }

        .info-text {
            font-size: 14px;
            line-height: 1.8;
            color: var(--muted);
        }

        .footer {
            text-align: center;
            padding: 32px 0;
            font-size: 12px;
            color: var(--muted);
        }

        @media (max-width: 768px) {
            h1 { font-size: 36px; }
            .experiments-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="eyebrow">AI Engineering Research Lab</div>
        <h1>Experiment <span class="highlight">Hub</span></h1>
        <p class="subtitle">
            Explore AI model evaluation, performance benchmarking, and behavior analysis through interactive experiments.
        </p>
    </div>

    <div class="experiments-grid">
        <a href="/ai-judge" class="experiment-card card-1">
            <div class="card-header">
                <span class="card-icon">⚖️</span>
                <h2 class="card-title">AI as a Judge</h2>
                <p class="card-subtitle">Evaluation Framework</p>
            </div>
            <div class="card-body">
                <p class="card-description">
                    Explore three AI evaluation modes: self-evaluation, reference comparison, and head-to-head judging.
                </p>
                <ul class="features-list">
                    <li>Self Evaluation (1-5 scoring)</li>
                    <li>Reference Comparison (match detection)</li>
                    <li>Head-to-Head (A vs B)</li>
                    <li>Burmese language support</li>
                </ul>
                <div class="launch-btn">🚀 Launch Experiment</div>
            </div>
        </a>

        <a href="/speed-benchmark" class="experiment-card card-2">
            <div class="card-header">
                <span class="card-icon">🏁</span>
                <h2 class="card-title">Speed Benchmark</h2>
                <p class="card-subtitle">Performance Testing</p>
            </div>
            <div class="card-body">
                <p class="card-description">
                    Compare response speed across GPT models. Race Nano, Mini, and full-size models.
                </p>
                <ul class="features-list">
                    <li>GPT-4.1 Nano (~4B params)</li>
                    <li>GPT-4.1 Mini (~13B params)</li>
                    <li>GPT-4.1 (~175B params)</li>
                    <li>Real-time rankings & metrics</li>
                </ul>
                <div class="launch-btn">🚀 Launch Experiment</div>
            </div>
        </a>

        <a href="/temperature" class="experiment-card card-3">
            <div class="card-header">
                <span class="card-icon">🌡️</span>
                <h2 class="card-title">Temperature Effect</h2>
                <p class="card-subtitle">Consistency Testing</p>
            </div>
            <div class="card-body">
                <p class="card-description">
                    Test how temperature affects output consistency. Observe deterministic vs creative behavior.
                </p>
                <ul class="features-list">
                    <li>Temperature 0 (Deterministic)</li>
                    <li>Temperature 0.7 (Balanced)</li>
                    <li>Temperature 1.0 (Creative)</li>
                    <li>Side-by-side comparison</li>
                </ul>
                <div class="launch-btn">🚀 Launch Experiment</div>
            </div>
        </a>
    </div>

    <div class="info-section">
        <h3 class="info-title">📚 About These Experiments</h3>
        <p class="info-text">
            This experiment hub provides hands-on tools for understanding AI model behavior and performance. Each experiment is designed to demonstrate key concepts in AI engineering: evaluation methodologies, performance benchmarking, and output consistency.
        </p>
        <br>
        <p class="info-text">
            <strong>Model:</strong> {{ model_name }} | <strong>Server:</strong> All experiments integrated on port 5000
        </p>
    </div>

    <div class="footer">
        <p><strong>AI Engineering Experiment Lab</strong></p>
    </div>
</div>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, model_name=model)

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎯 AI ENGINEERING EXPERIMENT LAB - UNIFIED SERVER")
    print("="*70)
    print("\n📖 Open your browser: http://127.0.0.1:5000")
    print("\nAvailable Routes:")
    print("  🏠 Home Page           → http://127.0.0.1:5000/")
    print("  ⚖️  AI as a Judge       → http://127.0.0.1:5000/ai-judge")
    print("  🏁 Speed Benchmark     → http://127.0.0.1:5000/speed-benchmark")
    print("  🌡️  Temperature Effect  → http://127.0.0.1:5000/temperature")
    print("\n✅ All experiments running on one server with Flask Blueprints!")
    print("\n" + "="*70 + "\n")
    app.run(debug=True, port=5000)
