import codecs

with codecs.open('mt5_backend/mt5_gateway.py', 'r', 'utf-8') as f:
    content = f.read()

# Replace the simulated training logic in mt5_gateway.py with real subprocess logic
old_training_logic = """training_state = {
    "is_training": False,
    "current_epoch": 0,
    "total_epochs": 3,
    "current_step": 0,
    "total_steps": 30,
    "loss": 0.0,
    "logs": [],
    "last_update": 0
}

@app.post("/api/training/start")
async def start_training():
    if training_state["is_training"]:
        return {"status": "Already training", "state": training_state}
        
    training_state["is_training"] = True
    training_state["current_epoch"] = 1
    training_state["total_epochs"] = 3
    training_state["current_step"] = 0
    # Simulate longer training for local Llama
    total_steps = 30 
    training_state["total_steps"] = total_steps
    training_state["loss"] = 2.5
    training_state["logs"] = [
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "[System] Initializing AI-Trader MCP Server..."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "[MCP] Connected to Claude Desktop."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "[Claude] Requesting backtest for CrossSMAStrategy..."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "[MCP] Generating YAML config..."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "[MCP] Executing Backtrader Engine (ai-trader)..."}
    ]
    training_state["last_update"] = time.time()
    
    return {"status": "Training started", "state": training_state}

@app.get("/api/training/status")
async def get_training_status():
    if not training_state["is_training"]:
        return training_state
        
    now = time.time()
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
            steps_per_epoch = training_state["total_steps"] / training_state["total_epochs"]
            training_state["current_epoch"] = int(training_state["current_step"] / steps_per_epoch) + 1
            
            # Simulate exponentially decaying loss curve
            progress = training_state["current_step"] / training_state["total_steps"]
            import math
            import random
            training_state["loss"] = 2.5 * math.exp(-2.0 * progress) + random.uniform(-0.05, 0.05)
            training_state["loss"] = round(max(0.2, training_state["loss"]), 4)
            
            if training_state["current_step"] % 10 == 0:
                training_state["logs"].append({
                    "time": datetime.datetime.now().strftime("%H:%M:%S"), 
                    "msg": f"Step {training_state['current_step']}/{training_state['total_steps']} - Loss: {training_state['loss']}"
                })
                
    status_copy = training_state.copy()
    status_copy["logs"] = status_copy["logs"][-20:] # Keep log short for frontend
    return status_copy"""

new_training_logic = """import subprocess
import threading
import math
import random

training_state = {
    "is_training": False,
    "current_epoch": 0,
    "total_epochs": 3,
    "current_step": 0,
    "total_steps": 30,
    "loss": 0.0,
    "logs": [],
    "last_update": 0
}

def training_thread_func():
    global training_state
    try:
        # Run the train_lora.py script
        process = subprocess.Popen(
            [sys.executable, "train_lora.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        for line in process.stdout:
            line = line.strip()
            if line:
                training_state["logs"].append({"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": line})
                
                # Parse Loss if available
                if "Loss:" in line:
                    try:
                        loss_str = line.split("Loss:")[1].split("|")[0].strip()
                        training_state["loss"] = float(loss_str)
                    except:
                        pass
                
                # Parse Step/Epoch if available
                if "Step " in line and "/" in line:
                    try:
                        step_part = line.split("Step ")[1].split("/")[0].strip()
                        training_state["current_step"] = int(step_part)
                    except:
                        pass
                
                training_state["last_update"] = time.time()
                
        process.wait()
        training_state["logs"].append({"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "[System] Training process exited."})
    except Exception as e:
        training_state["logs"].append({"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": f"Error: {e}"})
    finally:
        training_state["is_training"] = False
        training_state["current_step"] = training_state["total_steps"]

@app.post("/api/training/start")
async def start_training():
    if training_state["is_training"]:
        return {"status": "Already training", "state": training_state}
        
    training_state["is_training"] = True
    training_state["current_epoch"] = 1
    training_state["total_epochs"] = 3
    training_state["current_step"] = 0
    training_state["total_steps"] = 30
    training_state["loss"] = 2.5
    training_state["logs"] = [
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "msg": "[System] Initializing Real GPU Training on RTX 3060..."}
    ]
    training_state["last_update"] = time.time()
    
    # Start background thread
    t = threading.Thread(target=training_thread_func)
    t.daemon = True
    t.start()
    
    return {"status": "Training started", "state": training_state}

@app.get("/api/training/status")
async def get_training_status():
    status_copy = training_state.copy()
    status_copy["logs"] = status_copy["logs"][-30:] # Return last 30 logs
    return status_copy"""

if 'training_thread_func' not in content:
    content = content.replace(old_training_logic, new_training_logic)
    with codecs.open('mt5_backend/mt5_gateway.py', 'w', 'utf-8') as f:
        f.write(content)
    print("mt5_gateway.py patched with real training subprocess.")
else:
    print("Already patched.")