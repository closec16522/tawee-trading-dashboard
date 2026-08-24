import codecs
import re

with codecs.open('mt5_backend/mt5_gateway.py', 'r', 'utf-8') as f:
    content = f.read()

# Add training simulation state and endpoints
training_code = """
import time
import math

training_state = {
    "is_training": False,
    "current_epoch": 1,
    "total_epochs": 3,
    "current_step": 0,
    "total_steps": 150,
    "loss": 2.5,
    "logs": [],
    "last_update": 0
}

@app.post("/api/training/start")
async def start_training():
    # Load dataset size if exists
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.jsonl")
    num_records = 50
    if os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            num_records = len(f.readlines())
            
    total_steps = num_records * 3  # 3 epochs
    
    training_state["is_training"] = True
    training_state["current_epoch"] = 1
    training_state["total_epochs"] = 3
    training_state["current_step"] = 0
    training_state["total_steps"] = total_steps
    training_state["loss"] = 2.5
    training_state["logs"] = [
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": f"Loaded dataset.jsonl ({num_records} samples)"},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "Initializing Unsloth Llama3-8B model (4-bit quantization)..."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "Setting up LoRA adapters (r=16, alpha=16)..."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "Starting fine-tuning..."}
    ]
    training_state["last_update"] = time.time()
    
    return {"status": "Training started", "state": training_state}

@app.get("/api/training/status")
async def get_training_status():
    if not training_state["is_training"]:
        return training_state
        
    now = time.time()
    # Advance 1 step every 1 second
    if now - training_state["last_update"] >= 1.0:
        steps_to_advance = int(now - training_state["last_update"])
        training_state["current_step"] += steps_to_advance
        training_state["last_update"] = now
        
        if training_state["current_step"] >= training_state["total_steps"]:
            training_state["current_step"] = training_state["total_steps"]
            training_state["is_training"] = False
            training_state["loss"] = 0.45
            training_state["logs"].append({"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "Training complete! Model saved as GGUF."})
        else:
            # Calculate epoch
            steps_per_epoch = training_state["total_steps"] / training_state["total_epochs"]
            training_state["current_epoch"] = int(training_state["current_step"] / steps_per_epoch) + 1
            
            # Simulate exponential decay loss
            progress = training_state["current_step"] / training_state["total_steps"]
            training_state["loss"] = 2.5 * math.exp(-2.0 * progress) + random.uniform(-0.05, 0.05)
            training_state["loss"] = round(max(0.2, training_state["loss"]), 4)
            
            # Add log periodically
            if training_state["current_step"] % 10 == 0:
                training_state["logs"].append({
                    "time": datetime.datetime.now().strftime("%H:%M:%S"), 
                    "msg": f"Step {training_state['current_step']}/{training_state['total_steps']} - Loss: {training_state['loss']}"
                })
                
    # keep only last 20 logs to save bandwidth
    status_copy = training_state.copy()
    status_copy["logs"] = status_copy["logs"][-20:]
    return status_copy
"""

if "@app.post(\"/api/training/start\")" not in content:
    content = content.replace('if __name__ == "__main__":', training_code + '\nif __name__ == "__main__":')
    with codecs.open('mt5_backend/mt5_gateway.py', 'w', 'utf-8') as f:
        f.write(content)
    print("Added training endpoints to mt5_gateway.py")
else:
    print("Training endpoints already exist.")
