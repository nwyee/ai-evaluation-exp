import warnings
from transformers import AutoModelForCausalLM, AutoTokenizer, logging as hf_logging
import torch

warnings.filterwarnings("ignore")
hf_logging.set_verbosity_error()

def get_perplexity(text, model_name, tokenizer, model):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )
    
    with torch.no_grad():
        labels = inputs["input_ids"].clone()
        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            labels=labels
        )
        loss = outputs.loss
        if torch.isnan(loss) or torch.isinf(loss):
            return None
        return torch.exp(loss).item()

# Different text types
texts = {
    "Simple"     : "The cat sat on the mat.",
    "Technical"  : "Artificial intelligence is transforming the way software engineers work.",
    "Random"     : "Purple elephant dances quantum blockchain universe.",
    "Burmese"    : "မင်္ဂလာပါ၊ ကျွန်တော် AI လေ့လာနေပါတယ်။",
    "Code"       : "def hello(): print('Hello World')",
    "News"       : "The president signed the bill into law yesterday.",
}

models = [
    "gpt2",
    "gpt2-large",
]


# Load models once and reuse
loaded_models = {}
for model_name in models:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()
    loaded_models[model_name] = (tokenizer, model)

print("=" * 200)
print(f"{'Text Type':12} | {'gpt2':>10} | {'gpt2-large':>12} | {'Text':>100}")
print("=" * 200)


for text_type, text in texts.items():
    results = []
    for model_name in models:
        tokenizer, model = loaded_models[model_name]
        ppl = get_perplexity(text, model_name, tokenizer, model)
        results.append(f"{ppl:>10.2f}" if ppl else f"{'Error':>10}")
    
    print(f"{text_type:12} | {results[0]} | {results[1]:>12} | {text[:100]:>100}")

print("=" * 200)f