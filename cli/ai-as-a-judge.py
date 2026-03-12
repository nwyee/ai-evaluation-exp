"""
AI-as-a-Judge Practice Program

Three evaluation modes:
1. Self Evaluation: AI scores a single answer (1-5 scale)
2. Reference Comparison: Compare generated answer against reference (True/False)
3. Head-to-Head: Two answers compete, AI picks winner (A or B)
"""

import os
import json
import sys
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# Load .env from current directory or parent directories
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

# ─── Evaluation Prompts ────────────────────────────────────────────

SELF_EVAL_PROMPT = """You are an expert AI evaluator. Evaluate the quality of the answer for the given question.

Question: {question}
Answer: {answer}

Respond ONLY in this exact JSON format (no markdown, no extra text):
{{"score": <number 1-5>, "reasoning": "<2-3 sentences explaining the score>"}}

Scoring:
1 = Very bad (completely wrong or irrelevant)
2 = Poor (major issues)
3 = Acceptable (partially correct)
4 = Good (mostly correct with minor issues)
5 = Excellent (accurate, clear, complete)"""

REFERENCE_EVAL_PROMPT = """You are an expert AI evaluator. Compare the generated answer against the reference answer.

Question: {question}
Reference Answer: {reference}
Generated Answer: {generated}

Evaluate if the generated answer is factually correct and covers the key points from the reference.

Respond ONLY in this exact JSON format (no markdown, no extra text):
{{"match": <true or false>, "reasoning": "<2-3 sentences explaining why>"}}

Match criteria:
- true = Generated answer is accurate and covers key points
- false = Generated answer has errors or misses key information"""

HEAD_TO_HEAD_PROMPT = """You are an expert AI evaluator. Compare two answers to the same question and decide which one is better.

Question: {question}
Answer A: {answer_a}
Answer B: {answer_b}

Respond ONLY in this exact JSON format (no markdown, no extra text):
{{"winner": "<A or B>", "reasoning": "<2-3 sentences explaining why>"}}

Evaluation criteria:
- Accuracy and correctness
- Clarity and completeness
- Relevance to the question
- Overall helpfulness"""

# ─── Sample Questions & Answers ────────────────────────────────────

SAMPLE_DATA = {
    "self_eval": [
        {
            "question": "What is the capital of France?",
            "answer": "The capital of France is Paris, which is located in the north-central part of the country along the Seine River.",
            "category": "Geography"
        },
        {
            "question": "Explain how photosynthesis works",
            "answer": "Photosynthesis is a process where plants use sunlight to make food. It happens in two stages: light-dependent reactions in the thylakoids and light-independent reactions (Calvin cycle) in the stroma. Plants take in CO2 and water, and produce glucose and oxygen.",
            "category": "Biology"
        },
        {
            "question": "What are the benefits of regular exercise?",
            "answer": "Exercise improves health through better cardiovascular fitness, stronger muscles, weight management, mental health benefits, and longer lifespan.",
            "category": "Health"
        },
        {
            "question": "How does blockchain technology work?",
            "answer": "Blockchain is like a shared ledger that nobody controls. Bad answer.",
            "category": "Technology"
        },
    ],
    "reference_eval": [
        {
            "question": "What year did World War II end?",
            "reference": "World War II ended in 1945. Germany surrendered on May 7, 1945 (V-E Day), and Japan surrendered on September 2, 1945 (V-J Day).",
            "generated": "WWII ended in 1945, with Germany surrendering in May and Japan in September.",
            "category": "History"
        },
        {
            "question": "What is the largest planet in our solar system?",
            "reference": "Jupiter is the largest planet in our solar system. It has a mass more than twice that of all other planets combined.",
            "generated": "Jupiter is the biggest planet, and it's very large with lots of moons.",
            "category": "Astronomy"
        },
        {
            "question": "Explain Newton's First Law of Motion",
            "reference": "An object at rest stays at rest, and an object in motion stays in motion unless acted upon by an external force.",
            "generated": "Newton's First Law says things move because of force. Gravity and friction affect motion.",
            "category": "Physics"
        },
    ],
    "head_to_head": [
        {
            "question": "What are the main causes of climate change?",
            "answer_a": "Climate change is primarily caused by the emission of greenhouse gases like CO2 and methane from human activities such as burning fossil fuels, deforestation, and industrial processes. These gases trap heat in the atmosphere.",
            "answer_b": "Climate change happens because of natural cycles. The sun gets hotter and colder. Also, maybe volcanoes.",
            "category": "Environment"
        },
        {
            "question": "How do you learn a new programming language effectively?",
            "answer_a": "Build projects while learning syntax. Start with fundamentals, practice daily, and gradually take on more complex challenges. Read other people's code and participate in communities.",
            "answer_b": "Read the entire documentation first, then memorize all the syntax rules before writing any code.",
            "category": "Programming"
        },
        {
            "question": "Describe the water cycle",
            "answer_a": "Water evaporates from oceans and lakes into water vapor, condenses into clouds, and falls as precipitation. It then flows through rivers back to the ocean.",
            "answer_b": "The water cycle involves evaporation where water turns into clouds, then it rains, and water goes back to the ocean. There's also something about groundwater.",
            "category": "Earth Science"
        },
    ]
}

# ─── Evaluation Functions ──────────────────────────────────────────

def evaluate_self(question: str, answer: str) -> dict:
    """Tab 1: Self Evaluation - Score a single answer (1-5)"""
    prompt = SELF_EVAL_PROMPT.format(question=question, answer=answer)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert AI evaluator. Always respond in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except json.JSONDecodeError:
        return {"score": 0, "reasoning": "Error parsing evaluation"}

def evaluate_reference(question: str, reference: str, generated: str) -> dict:
    """Tab 2: Reference Comparison - True/False match"""
    prompt = REFERENCE_EVAL_PROMPT.format(
        question=question,
        reference=reference,
        generated=generated
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert AI evaluator. Always respond in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except json.JSONDecodeError:
        return {"match": False, "reasoning": "Error parsing evaluation"}

def evaluate_head_to_head(question: str, answer_a: str, answer_b: str) -> dict:
    """Tab 3: Head-to-Head - Pick winner (A or B)"""
    prompt = HEAD_TO_HEAD_PROMPT.format(
        question=question,
        answer_a=answer_a,
        answer_b=answer_b
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert AI evaluator. Always respond in valid JSON format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except json.JSONDecodeError:
        return {"winner": "A", "reasoning": "Error parsing evaluation"}

# ─── UI Functions ─────────────────────────────────────────────────

def display_header():
    """Display main menu header"""
    print("\n" + "="*70)
    print("AI-AS-A-JUDGE — EVALUATION PRACTICE PROGRAM")
    print("="*70)
    print("\nChoose an evaluation mode:\n")
    print("  1️⃣  Self Evaluation     - AI scores a single answer (1-5)")
    print("  2️⃣  Reference Compare   - Compare against reference (True/False)")
    print("  3️⃣  Head-to-Head        - Two answers compete (A or B wins)")
    print("  4️⃣  Exit\n")

def tab_self_evaluation():
    """Tab 1: Self Evaluation"""
    print("\n" + "─"*70)
    print("TAB 1: SELF EVALUATION")
    print("─"*70)
    print("\nSample questions available:")
    for i, item in enumerate(SAMPLE_DATA["self_eval"], 1):
        print(f"  {i}. [{item['category']}] {item['question']}")

    choice = input("\nSelect sample (1-4) or enter custom (0): ").strip()

    if choice == "0":
        question = input("\nEnter question: ").strip()
        answer = input("Enter answer: ").strip()
    elif choice in ["1", "2", "3", "4"]:
        item = SAMPLE_DATA["self_eval"][int(choice) - 1]
        question = item["question"]
        answer = item["answer"]
    else:
        print("❌ Invalid choice")
        return

    print("\n⏳ Evaluating...")
    result = evaluate_self(question, answer)

    print(f"\n✅ RESULT:")
    print(f"   Question: {question}")
    print(f"   Answer: {answer}")
    print(f"   Score: {result['score']}/5 ⭐")
    print(f"   Reasoning: {result['reasoning']}")

def tab_reference_comparison():
    """Tab 2: Reference Comparison"""
    print("\n" + "─"*70)
    print("TAB 2: REFERENCE COMPARISON")
    print("─"*70)
    print("\nSample questions available:")
    for i, item in enumerate(SAMPLE_DATA["reference_eval"], 1):
        print(f"  {i}. [{item['category']}] {item['question']}")

    choice = input("\nSelect sample (1-3) or enter custom (0): ").strip()

    if choice == "0":
        question = input("\nEnter question: ").strip()
        reference = input("Enter reference answer: ").strip()
        generated = input("Enter generated answer: ").strip()
    elif choice in ["1", "2", "3"]:
        item = SAMPLE_DATA["reference_eval"][int(choice) - 1]
        question = item["question"]
        reference = item["reference"]
        generated = item["generated"]
    else:
        print("❌ Invalid choice")
        return

    print("\n⏳ Comparing...")
    result = evaluate_reference(question, reference, generated)

    match_status = "✅ MATCH" if result['match'] else "❌ NO MATCH"
    print(f"\n{match_status}:")
    print(f"   Question: {question}")
    print(f"   Reference: {reference}")
    print(f"   Generated: {generated}")
    print(f"   Match: {result['match']}")
    print(f"   Reasoning: {result['reasoning']}")

def tab_head_to_head():
    """Tab 3: Head-to-Head"""
    print("\n" + "─"*70)
    print("TAB 3: HEAD-TO-HEAD COMPARISON")
    print("─"*70)
    print("\nSample questions available:")
    for i, item in enumerate(SAMPLE_DATA["head_to_head"], 1):
        print(f"  {i}. [{item['category']}] {item['question']}")

    choice = input("\nSelect sample (1-3) or enter custom (0): ").strip()

    if choice == "0":
        question = input("\nEnter question: ").strip()
        answer_a = input("Enter answer A: ").strip()
        answer_b = input("Enter answer B: ").strip()
    elif choice in ["1", "2", "3"]:
        item = SAMPLE_DATA["head_to_head"][int(choice) - 1]
        question = item["question"]
        answer_a = item["answer_a"]
        answer_b = item["answer_b"]
    else:
        print("❌ Invalid choice")
        return

    print("\n⏳ Battling...")
    result = evaluate_head_to_head(question, answer_a, answer_b)

    winner = result['winner'].upper()
    print(f"\n🏆 WINNER: {winner}")
    print(f"   Question: {question}")
    print(f"   Answer A: {answer_a}")
    print(f"   Answer B: {answer_b}")
    print(f"   Winner: {winner}")
    print(f"   Reasoning: {result['reasoning']}")

def main():
    """Main menu loop"""
    print("\n" + "="*70)
    print("WELCOME TO AI-AS-A-JUDGE PRACTICE")
    print("="*70)

    while True:
        try:
            display_header()
            choice = input("Enter choice (1-4): ").strip()

            if choice == "1":
                tab_self_evaluation()
            elif choice == "2":
                tab_reference_comparison()
            elif choice == "3":
                tab_head_to_head()
            elif choice == "4":
                print("\n👋 Goodbye!\n")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.\n")
        except EOFError:
            print("\n👋 Goodbye!\n")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
