from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import warnings

warnings.filterwarnings("ignore")

def get_bpb(text, model_name="gpt2"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])

        # Cross entropy (nats per token - natural logarithm)
        cross_entropy = outputs.loss.item()

        print(f"Cross Entropy (nats/token): {cross_entropy:.4f}")

        # tokens to bytes conversion
        num_tokens = inputs["input_ids"].shape[1]
        num_bytes = len(text.encode("utf-8"))

        # BPB calculation: convert nats/token to bits/byte
        # 1. cross_entropy is in nats per token
        # 2. divide by ln(2) to convert nats to bits
        # 3. multiply by (num_tokens / num_bytes) to get bits per byte
        import math
        bpb = (cross_entropy / math.log(2.0)) * (num_tokens / num_bytes)

    return bpb

text = "The quick brown fox jumps over the lazy dog."
bpb = get_bpb(text)
print(f"BPB: {bpb:.4f}")