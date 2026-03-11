# AI Engineering Evaluation Experiments

A comprehensive laboratory for exploring and evaluating AI model behaviors, capabilities, and performance characteristics. This project contains multiple experimental tools designed to measure AI engineering metrics through practical, interactive web-based interfaces.

## Overview

This repository contains six Python-based experiments focused on understanding AI models' evaluation, speed, consistency, and perplexity:

1. **AI-as-a-Judge** — Evaluation framework with three modes
2. **AI Judge Web** — Web-based judge with Burmese language support
3. **GPT Speed Benchmark** — Model performance comparison tool
4. **Temperature Experiment** — Testing output consistency at different temperatures
5. **Perplexity Check** — Multi-text type perplexity comparison
6. **BPB Check** — Bits-per-byte perplexity measurement

---

## Project Structure

```
ai-evaluation-exp/
├── ai-as-a-judge.py              # CLI-based evaluation tool
├── ai_judge_web.py               # Flask web interface for evaluation
├── gpt_speed_benchmark.py         # Performance benchmarking tool
├── temperature_experiment.py      # Temperature consistency testing
├── check-ppl.py                  # Perplexity comparison across text types
├── check-bpb.py                  # Bits-per-byte perplexity measurement
├── requirements.txt              # Python dependencies
├── .env.example                  # Configuration template
└── README.md                     # This file
```

---

## Experiments

### 1. AI-as-a-Judge (`ai-as-a-judge.py`)

**Purpose:** Interactive CLI tool for practicing AI evaluation with three distinct modes.

**Evaluation Modes:**
- **Self Evaluation:** AI scores a single answer on a 1-5 scale
- **Reference Comparison:** Compare generated answer against reference (True/False match)
- **Head-to-Head:** Two answers compete; AI determines the winner (A or B)

**Features:**
- Pre-configured sample questions across multiple categories
- Custom input support
- JSON-formatted evaluation results with reasoning
- Temperature set to 0.3 for consistent, deterministic evaluation

**Sample Categories:**
- Geography
- Biology
- Health
- Technology
- History
- Astronomy
- Physics
- Environment
- Programming
- Earth Science

**Usage:**
```bash
python ai-as-a-judge.py
```

Follow the interactive menu to select evaluation mode and questions.

---

### 2. AI Judge Web (`ai_judge_web.py`)

**Purpose:** Web-based interface for AI evaluation with support for Burmese language.

**Features:**
- Single-page web application built with Flask
- Three evaluation tabs (Self, Reference, Head-to-Head)
- Burmese language preset questions
- Beautiful, responsive UI with modern design
- Real-time evaluation results with reasoning

**Preset Question Examples (Burmese):**
- 🥗 ကျန်းမာရေး (Health tips)
- 😴 အိပ်ရေး (Sleep advice)
- 🍜 မနက်စာ (Breakfast recommendations)
- 💧 ရေသောက် (Water intake)
- 🏃 လေ့ကျင့်ခန်း (Exercise routines)

**Server:**
```bash
python ai_judge_web.py
```
Open browser to: `http://localhost:5000`

**API Endpoints:**
- `POST /api/generate_self` — Generate answer for self evaluation
- `POST /api/judge_self` — Score an answer (1-5)
- `POST /api/generate_ref` — Generate answer for reference comparison
- `POST /api/judge_ref` — Compare with reference (match/no match)
- `POST /api/generate_h2h` — Generate both answers for head-to-head
- `POST /api/judge_h2h` — Determine winner (A or B)

---

### 3. GPT Speed Benchmark (`gpt_speed_benchmark.py`)

**Purpose:** Benchmark and compare response speed across different GPT model sizes.

**Models Compared:**
- 🚀 GPT-4.1 Nano (~4B parameters) — Fastest, cost-efficient
- ⚖️ GPT-4.1 Mini (~13B parameters) — Balanced performance
- 🧠 GPT-4.1 (~175B parameters) — Most powerful

**Metrics Measured:**
- Total response time (milliseconds)
- Output token count
- Estimated cost (in cents)
- Speed comparison visualization with rankings

**Features:**
- Real-time race visualization
- Ranking system (🥇🥈🥉)
- Cost estimation per query
- Burmese language prompts
- Preset question templates

**Server:**
```bash
python gpt_speed_benchmark.py
```
Open browser to: `http://localhost:5003`

**Use Cases:**
- Identify fastest model for time-sensitive applications
- Calculate cost-performance trade-offs
- Understand speed variations under different conditions
- Find optimal model for specific latency requirements

---

### 4. Temperature Experiment (`temperature_experiment.py`)

**Purpose:** Explore how temperature parameter affects output consistency and creativity.

**Temperature Settings Tested:**
- **T=0.0 (🧊 Deterministic):** Should produce identical output across runs
- **T=0.7 (⚖️ Balanced):** Moderate variation; suitable for most applications
- **T=1.0 (🎲 Creative):** Maximum variation; useful for creative tasks

**Experimental Design:**
Each temperature setting is run twice with identical prompts to measure consistency:
- Exact matching indicates deterministic behavior
- Similarity percentage shows variation level
- Visual comparison of outputs side-by-side

**Features:**
- Run both executions with real-time progress tracking
- Compare outputs with similarity scoring
- Automatic detection of exact matches
- Preset question templates
- Summary insights about temperature effects

**Server:**
```bash
python temperature_experiment.py
```
Open browser to: `http://localhost:5001`

**Key Findings You'll Observe:**
- T=0 should always produce identical results
- T=0.7 produces varied but related outputs
- T=1.0 shows maximum diversity in responses

---

### 5. Perplexity Check (`check-ppl.py`)

**Purpose:** Compare perplexity scores across different text types and model sizes.

**Experiment Design:**
Measures how well different language models predict various types of text:
- Simple/Natural text
- Technical text
- Random/Nonsensical text
- Burmese (Myanmar) language
- Code snippets
- News articles

**Models Compared:**
- GPT-2 (~124M parameters)
- GPT-2 Large (~355M parameters)

**Metrics:**
- **Perplexity Score:** How "surprised" the model is by the text (lower = better)
- **Cross-entropy Loss:** Calculated and exponentiated to perplexity
- **Model-to-Model Comparison:** Direct comparison of model performance

**Features:**
- Batch processing of multiple text types
- Side-by-side model comparison
- Error handling for invalid/problematic inputs
- Truncation support for long texts (max 512 tokens)
- Attention mask handling for proper evaluation

**Output:**
```
Text Type     | gpt2       | gpt2-large | Text
──────────────────────────────────────────────
Simple        |      45.32 |      38.21 | The cat sat on the mat.
Technical     |      89.45 |      72.13 | Artificial intelligence is transforming...
Random        |    2145.67 |    1923.45 | Purple elephant dances quantum...
Burmese       |     156.78 |     134.56 | မင်္ဂလာပါ၊ ကျွန်တော်...
Code          |     234.56 |     198.34 | def hello(): print('Hello World')
News          |      62.34 |      51.23 | The president signed the bill...
```

**Usage:**
```bash
python check-ppl.py
```

**Interpretation:**
- Lower perplexity = model finds text more predictable (understands it better)
- Higher perplexity = text is "surprising" to the model (novel/random/out-of-domain)
- GPT-2 Large typically has lower perplexity than GPT-2

**Use Cases:**
- Language model quality comparison
- Text domain analysis
- Out-of-domain detection
- Model capability assessment
- Multilingual text evaluation

---

### 6. BPB Check (`check-bpb.py`)

**Purpose:** Measure perplexity in bits-per-byte (BPB) for text evaluation.

**Calculation Process:**
1. Tokenizes input text using the model
2. Computes cross-entropy (in nats per token)
3. Converts to bits using logarithm base 2
4. Normalizes to bits per byte

**Formula:**
```
BPB = (cross_entropy / ln(2)) * (num_tokens / num_bytes)
```

**Use Cases:**
- Language model quality assessment
- Comparison of model compression effectiveness
- Text difficulty measurement
- Model perplexity benchmarking

**Default Model:** GPT-2 (can be modified)

**Usage:**
```bash
python check-bpb.py
```

---

## Installation

### 1. Clone or Download Repository
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

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
PROXY_API_KEY=your-api-key
PROXY_BASE_URL=your-base-url-or-leave-empty
MODEL_NAME=your-model-name
MAX_TOKENS=1000
```

---

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PROXY_API_KEY` | Your OpenAI or proxy API key | `sk-...` |
| `OPENAI_API_KEY` | Alternative: Direct OpenAI API key | `sk-...` |
| `PROXY_BASE_URL` | Optional proxy URL | `https://api.example.com/v1` |
| `MODEL_NAME` | Model identifier to use | `gpt-4.1-mini` |
| `MAX_TOKENS` | Maximum tokens in responses | `1000` |

**Priority Order for API Keys:**
1. `PROXY_API_KEY` (checked first)
2. `OPENAI_API_KEY` (fallback)

**File Search:** The scripts search for `.env` in:
1. Current directory
2. Parent directory
3. Grandparent directory

---

## Dependencies

```
flask==3.0.0                  # Web framework for Flask apps
openai==1.57.0               # OpenAI API client
python-dotenv==1.0.0         # Environment variable management
requests==2.31.0             # HTTP requests
anthropic >= 0.39            # Anthropic API support
httpx == 0.27.2              # Async HTTP client
transformers                 # For BPB calculation (hugging face)
torch                        # Deep learning (for BPB calculation)
```

---

## Usage Examples

### Running Self-Evaluation (CLI)
```bash
python ai-as-a-judge.py
# Select option 1 from menu
# Choose a sample question or enter custom
# View 1-5 score with reasoning
```

### Running Web-Based Judge
```bash
python ai_judge_web.py
# Open http://localhost:5000
# Select evaluation mode (Self/Reference/Head-to-Head)
# Fill in question and optionally generate AI answers
# Click Judge/Compare/Battle to get results
```

### Speed Benchmarking
```bash
python gpt_speed_benchmark.py
# Open http://localhost:5003
# Select preset question or enter custom
# Click "Start Race!" to compare all three models
# View rankings, timings, and cost estimates
```

### Temperature Testing
```bash
python temperature_experiment.py
# Open http://localhost:5001
# Enter a question
# Click "Run with all 3 temperatures"
# Observe consistency differences across T=0, T=0.7, T=1.0
```

### Comparing Perplexity Across Text Types
```bash
python check-ppl.py
# Compares GPT-2 and GPT-2 Large on multiple text types
# Shows perplexity scores in table format
# Outputs: Simple, Technical, Random, Burmese, Code, News
```

### Measuring Bits-Per-Byte Perplexity
```bash
python check-bpb.py
# Runs with default text: "The quick brown fox jumps over the lazy dog."
# Displays cross-entropy and BPB metrics
```

---

## Output Formats

### Self Evaluation Output
```json
{
  "score": 4,
  "reasoning": "The answer is accurate and well-structured, covering all major points with clear explanations."
}
```

### Reference Comparison Output
```json
{
  "match": true,
  "reasoning": "The generated answer conveys the same core meaning as the reference, though with slightly different wording."
}
```

### Head-to-Head Output
```json
{
  "winner": "A",
  "reasoning": "Answer A provides more comprehensive coverage with better organization and clarity."
}
```

### Speed Benchmark Output
```json
{
  "text": "Model response text...",
  "time": 1250,
  "tokens": 45,
  "cost": "0.04"
}
```

---

## Architecture

### CLI Application (ai-as-a-judge.py)
- Simple menu-driven interface
- Deterministic evaluation (temperature=0.3)
- Local data processing
- No web server required

### Web Applications
- **Framework:** Flask
- **Frontend:** Vanilla JavaScript, HTML/CSS
- **Styling:** Custom CSS with design variables
- **Real-time Updates:** Async fetch API calls
- **Language Support:** Burmese (Myanmar) with emoji indicators

---

## Key Metrics

### Speed Benchmark Metrics
- **Total Time:** End-to-end response latency
- **Token Count:** Number of output tokens generated
- **Estimated Cost:** Calculated from token pricing

### Temperature Metrics
- **Consistency:** Percentage match between runs
- **Exact Match:** Binary indicator of identical outputs
- **Similarity Score:** Ratio-based comparison (0-1)

### Perplexity Metrics
- **Cross Entropy:** Information loss in nats/token
- **BPB:** Normalized bits per byte for comparison

---

## Troubleshooting

### "API Key not set" Error
- Ensure `.env` file exists in project directory
- Check that `PROXY_API_KEY` or `OPENAI_API_KEY` is configured
- Verify the environment variable is not empty

### Port Already in Use
- Change port in Flask apps (default ports: 5000, 5001, 5003)
- Or stop the process using that port

### Model Not Found
- Verify `MODEL_NAME` is valid for your API
- Check API credentials and access permissions
- Ensure the model is available in your account

### Timeout Errors
- Increase `MAX_TOKENS` if needed
- Check network connection to API
- Verify API service is operational

---

## Evaluation Best Practices

### For AI Judge Evaluation
- Use clear, specific questions for better scoring
- Provide balanced reference answers for comparison
- Test with multiple models to understand variations
- Consider temperature effects on consistency

### For Speed Benchmarking
- Run multiple times for reliable averages
- Consider network latency factors
- Test under consistent load conditions
- Account for model queue times

### For Temperature Experiments
- Use standardized prompts for fair comparison
- Run sufficient iterations (>3) for statistical validity
- Consider task-specific temperature requirements
- Document findings for reproducibility

---

## Language Support

The web applications support:
- **English:** Full interface and documentation
- **Burmese (Myanmar):** Question presets and user interface text
- **Unicode Emojis:** Visual indicators for different modes and metrics

---

## Future Enhancements

Potential additions for this evaluation suite:
- Token cost comparison across models
- Streaming response time measurement
- Multi-model evaluation matrices
- Historical data tracking and visualization
- Export results to CSV/JSON
- Advanced statistical analysis
- Batch evaluation processing

---

## License

This project is part of the AI Engineering Evaluation initiative.

---

## Support & Contact

For questions or issues regarding these experiments, refer to the code documentation and comments within each Python file.

**Key Components:**
- Evaluation prompts and logic
- API integration patterns
- Web UI best practices
- Measurement methodologies

---

## Related Concepts

### AI Evaluation
- Self-evaluation: AI judges its own outputs
- Reference-based: Comparison against ground truth
- Pairwise ranking: Relative quality assessment

### Model Performance
- Latency: Time to first token and total response time
- Throughput: Tokens generated per second
- Cost efficiency: Output quality per dollar spent

### Output Consistency
- Temperature effect: Deterministic vs. creative outputs
- Reproducibility: Exact vs. similar responses
- Entropy: Information content measurement

### Perplexity Metrics
- Cross-entropy: Prediction error measurement
- Bits-per-byte: Normalized compression metric
- Model quality: Lower is better

---

**Last Updated:** 2026-03-11
**Version:** 1.0