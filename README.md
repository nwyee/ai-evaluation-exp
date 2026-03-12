# AI Engineering Evaluation Experiments

A unified web application for exploring and evaluating AI model behaviors, capabilities, and performance characteristics. Built with Flask Blueprints for modularity and scalability.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run the unified application
python app.py

# 4. Open browser
# Visit: http://127.0.0.1:5000/
```

---

## 📁 Project Structure

```
ai-evaluation-exp/
├── 🚀 app.py                    # Main unified Flask application
├── 📁 blueprints/               # Modular experiment components
│   ├── __init__.py
│   ├── ai_judge_blueprint.py
│   ├── speed_benchmark_blueprint.py
│   └── temperature_blueprint.py
├── 📁 standalones/              # Original standalone versions (optional)
│   ├── model_speed_benchmark.py
├── 📁 cli/                      # Command-line tools
│   ├── ai-as-a-judge.py
│   ├── check-bpb.py
│   └── check-ppl.py
├── 📄 requirements.txt
├── 📄 .env.example
└── 📄 README.md
```

---

## 🎯 Experiments

### Web Experiments (Integrated)

All three web experiments are accessible through the unified `app.py` with a beautiful landing page:

#### 1. ⚖️ AI as a Judge (`/ai-judge`)

Explore three AI evaluation methodologies:

- **Self Evaluation** — AI scores its own answers (1-5 scale)
- **Reference Comparison** — Compare against ground truth (match/no match)
- **Head-to-Head** — Pairwise ranking (A vs B winner)

**Features:**
- Generate AI answers in Burmese language
- Real-time scoring with reasoning
- Preset question templates
- JSON-based evaluation results

**URL:** http://127.0.0.1:5000/ai-judge

---

#### 2. 🏁 Speed Benchmark (`/speed-benchmark`)

Compare response speed and performance across GPT model sizes:

**Models:**
- 🚀 GPT-4.1 Nano (~4B parameters) — Fastest, cost-efficient
- ⚖️ GPT-4.1 Mini (~13B parameters) — Balanced performance
- 🧠 GPT-4.1 (~175B parameters) — Most powerful

**Metrics:**
- Total response time (milliseconds)
- Output token count
- Estimated cost per query
- Speed rankings with visual comparison

**Features:**
- Real-time race visualization
- Ranking system (🥇🥈🥉)
- Cost-performance analysis
- Burmese language prompts

**URL:** http://127.0.0.1:5000/speed-benchmark

---

#### 3. 🌡️ Temperature Experiment (`/temperature`)

Test how temperature affects output consistency and creativity:

**Temperature Settings:**
- **T=0.0 (🧊 Deterministic)** — Produces identical outputs
- **T=0.7 (⚖️ Balanced)** — Moderate variation
- **T=1.0 (🎲 Creative)** — Maximum diversity

**Experimental Design:**
- Run identical prompts twice at each temperature
- Compare outputs with similarity scoring
- Detect exact matches vs variations
- Side-by-side comparison view

**Features:**
- Automatic similarity calculation
- Exact match detection
- Visual comparison interface
- Summary insights

**URL:** http://127.0.0.1:5000/temperature

---

### CLI Tools

#### AI-as-a-Judge CLI (`cli/ai-as-a-judge.py`)

Command-line version with interactive menu for:
- Self evaluation (1-5 scoring)
- Reference comparison (True/False)
- Head-to-head battles (A vs B)

**Usage:**
```bash
python cli/ai-as-a-judge.py
```

---

#### Perplexity Check (`cli/check-ppl.py`)

Compare perplexity scores across different text types and models.

**Text Types Tested:**
- Simple/Natural language
- Technical content
- Random/Nonsensical text
- Burmese (Myanmar) language
- Code snippets
- News articles

**Models Compared:**
- GPT-2 (~124M parameters)
- GPT-2 Large (~355M parameters)

**Output:** Table showing perplexity scores for each text type and model

**Usage:**
```bash
python cli/check-ppl.py
```

**Interpretation:**
- Lower perplexity = better model understanding
- Higher perplexity = text is surprising/out-of-domain

---

#### BPB Check (`cli/check-bpb.py`)

Measure perplexity in bits-per-byte (BPB) for text evaluation.

**Formula:**
```
BPB = (cross_entropy / ln(2)) * (num_tokens / num_bytes)
```

**Usage:**
```bash
python cli/check-bpb.py
```

**Use Cases:**
- Language model quality assessment
- Model compression effectiveness
- Text difficulty measurement

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# API Configuration
PROXY_API_KEY=your-api-key-here
OPENAI_API_KEY=your-openai-key-here
PROXY_BASE_URL=https://your-proxy-url (optional)
MODEL_NAME=gpt-4.1-mini
MAX_TOKENS=1000
```

**Priority Order:**
1. `PROXY_API_KEY` (checked first)
2. `OPENAI_API_KEY` (fallback)

**Available Models:**
- `gpt-4.1-nano` — Fast, cost-efficient
- `gpt-4.1-mini` — Balanced (recommended)
- `gpt-4.1` — Most powerful

---

## 📦 Installation

### 1. Clone Repository

```bash
cd ai-evaluation-exp
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API key and configuration
```

---

## 🎮 Usage

### Running the Unified Web Application

```bash
python app.py
```

**Access Points:**
- 🏠 **Home:** http://127.0.0.1:5000/
- ⚖️ **AI Judge:** http://127.0.0.1:5000/ai-judge
- 🏁 **Speed Benchmark:** http://127.0.0.1:5000/speed-benchmark
- 🌡️ **Temperature:** http://127.0.0.1:5000/temperature

### Running CLI Tools

```bash
# AI evaluation CLI
python cli/ai-as-a-judge.py

# Perplexity comparison
python cli/check-ppl.py

# Bits-per-byte check
python cli/check-bpb.py
```

### Running Standalone Versions (Optional)

```bash
# Individual web apps (run on different ports)
python standalones/model_speed_benchmark.py         # Port 5003
```

---

## 🏗️ Architecture

### Flask Blueprints Structure

The application uses **Flask Blueprints** for modular organization:

```python
# Main app (app.py)
app = Flask(__name__)
app.register_blueprint(ai_judge_bp)
app.register_blueprint(speed_benchmark_bp)
app.register_blueprint(temperature_bp)

# Each blueprint (e.g., blueprints/ai_judge_blueprint.py)
ai_judge_bp = Blueprint('ai_judge', __name__, url_prefix='/ai-judge')
```

**Benefits:**
- ✅ Modular: Each experiment in its own file
- ✅ Scalable: Easy to add new experiments
- ✅ No Conflicts: Separate URL namespaces
- ✅ Shared Resources: Single OpenAI client
- ✅ Navigation: "Back to Home" on all pages

**Shared Configuration:**
All blueprints access shared resources via `app.config`:
- `app.config['OPENAI_CLIENT']` — OpenAI client instance
- `app.config['MODEL_NAME']` — Default model name

---

## 📊 Output Formats

### Self Evaluation
```json
{
  "score": 4,
  "reasoning": "The answer is accurate and well-structured..."
}
```

### Reference Comparison
```json
{
  "match": true,
  "reasoning": "Generated answer conveys the same core meaning..."
}
```

### Head-to-Head
```json
{
  "winner": "A",
  "reasoning": "Answer A provides more comprehensive coverage..."
}
```

### Speed Benchmark
```json
{
  "text": "Model response text...",
  "time": 1250,
  "tokens": 45,
  "cost": "0.04"
}
```

---

## 🔍 Key Metrics

### Speed Benchmark
- **Total Time:** End-to-end response latency (ms)
- **Token Count:** Number of output tokens generated
- **Estimated Cost:** Calculated from token pricing (cents)

### Temperature Experiment
- **Consistency:** Percentage match between runs
- **Exact Match:** Binary indicator of identical outputs
- **Similarity Score:** Ratio-based comparison (0-1)

### Perplexity
- **Cross Entropy:** Information loss (nats/token)
- **BPB:** Normalized bits per byte
- **Lower is Better:** Indicates better model understanding

---

## 🛠️ Dependencies

```
flask==3.0.0                  # Web framework
openai==1.57.0               # OpenAI API client
python-dotenv==1.0.0         # Environment management
requests==2.31.0             # HTTP requests
anthropic >= 0.39            # Anthropic API support
httpx == 0.27.2              # Async HTTP client
transformers                 # HuggingFace (for BPB/PPL)
torch                        # Deep learning (for BPB/PPL)
```

---

## 🚨 Troubleshooting

### "API Key not set" Error
- Ensure `.env` exists in project root
- Verify `PROXY_API_KEY` or `OPENAI_API_KEY` is set
- Check the value is not empty

### Port Already in Use
- Change port in `app.py` (default: 5000)
- Or stop the process using that port:
  ```bash
  lsof -ti:5000 | xargs kill -9
  ```

### Model Not Found
- Verify `MODEL_NAME` in `.env` is valid
- Check API credentials and permissions
- Ensure model is available in your account

### Import Errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

---

## 🎨 Language Support

- **English:** Full interface and documentation
- **Burmese (Myanmar):** Question presets and UI text
- **Unicode Emojis:** Visual indicators throughout

---

## 📚 Evaluation Best Practices

### For AI Judge
- Use clear, specific questions
- Provide balanced reference answers
- Test with multiple models
- Consider temperature effects on consistency

### For Speed Benchmarking
- Run multiple times for reliable averages
- Consider network latency
- Test under consistent conditions
- Account for model queue times

### For Temperature Experiments
- Use standardized prompts
- Run sufficient iterations (>3)
- Consider task-specific requirements
- Document findings

---

## 🔮 Future Enhancements

- Token cost comparison dashboard
- Streaming response time measurement
- Multi-model evaluation matrices
- Historical data tracking
- CSV/JSON export functionality
- Advanced statistical analysis
- Batch evaluation processing

---

## 🤝 Contributing

To add a new experiment:

1. Create blueprint: `blueprints/new_experiment_blueprint.py`
2. Register in `app.py`: `app.register_blueprint(new_exp_bp)`
3. Add card to home page template
4. Update this README

---

## 📄 License

This project is part of the AI Engineering Evaluation initiative.

---

## 📞 Support

For questions or issues:
- Check the code documentation
- Review the Architecture section above for technical details
- Consult inline comments in each file

---

**Version:** 2.0 (Flask Blueprints Architecture)
**Last Updated:** 2026-03-12
**Main App:** `app.py`
