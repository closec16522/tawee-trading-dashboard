import json
import os
import argparse

JOURNAL_PATH = os.path.join(os.path.dirname(__file__), "journal.json")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset.jsonl")

def generate_dataset():
    if not os.path.exists(JOURNAL_PATH):
        print(f"Error: {JOURNAL_PATH} not found.")
        return

    with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
        try:
            journal_data = json.load(f)
        except Exception as e:
            print(f"Error reading journal: {e}")
            return

    if not journal_data:
        print("Journal is empty. No data to process.")
        return

    print(f"Found {len(journal_data)} trade records. Generating dataset...")
    
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        for trade in journal_data:
            # Skip invalid records
            if not all(k in trade for k in ("symbol", "type", "entry", "exit", "profit", "insight")):
                continue
                
            instruction = "You are an expert quantitative AI trader. Analyze the following trade details and provide a professional trading insight."
            input_text = f"Symbol: {trade['symbol']}, Type: {trade['type']}, Entry: {trade['entry']}, Exit: {trade['exit']}, Profit: ${trade['profit']}, Date: {trade.get('date', 'Unknown')}"
            output_text = trade['insight']
            
            # Alpaca format
            record = {
                "instruction": instruction,
                "input": input_text,
                "output": output_text
            }
            
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✅ Dataset generated successfully at: {DATASET_PATH}")
    print("\n--- Next Steps for Local Fine-Tuning ---")
    print("To fine-tune Llama3 on this dataset using Unsloth (recommended for 8GB+ VRAM GPUs):")
    print("1. Install Unsloth in a Jupyter Notebook or Python environment with CUDA.")
    print("2. Load the 'dataset.jsonl' file.")
    print("3. Use the following snippet to train:")
    print('''
from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. Load Model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/llama-3-8b-Instruct-bnb-4bit",
    max_seq_length = 2048,
    dtype = None,
    load_in_4bit = True,
)

# 2. Add LoRA Adapters
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# 3. Train Model
# ... Add your dataset loading logic here ...

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = 2048,
    dataset_num_proc = 2,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60,
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

trainer_stats = trainer.train()

# 4. Save to Ollama Format (GGUF)
model.save_pretrained_gguf("model", tokenizer, quantization_method = "q4_k_m")
print("Model saved to GGUF format! You can now run it in Ollama.")
    ''')

if __name__ == "__main__":
    generate_dataset()
