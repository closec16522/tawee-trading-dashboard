import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# 1. Add Navigation Link
nav_html = """<li id="nav-training" onclick="switchTab('training')"><span class="icon">🧠</span> Local AI Training</li>"""
if "nav-training" not in content:
    content = content.replace(
        '<li id="nav-backtest" onclick="switchTab(\'backtest\')"><span class="icon">🧪</span> Data Backtest</li>',
        '<li id="nav-backtest" onclick="switchTab(\'backtest\')"><span class="icon">🧪</span> Data Backtest</li>\n                    ' + nav_html
    )

# 2. Add Training View HTML
training_view_html = """
        <div id="view-training" class="view">
            <div class="header-container">
                <div>
                    <h2>🧠 Local AI Training (Simulation)</h2>
                    <p>Fine-tune Llama 3 8B with Unsloth and LoRA adapters using your local trading journal data.</p>
                </div>
                <div>
                    <button class="btn btn-primary" id="btn-start-training" onclick="startAiTraining()">🚀 Start Training (Simulate)</button>
                </div>
            </div>

            <div class="card" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3>Training Progress <span id="training-status-badge" style="font-size: 12px; padding: 3px 8px; border-radius: 12px; background: rgba(255,255,255,0.1); margin-left: 10px;">IDLE</span></h3>
                    <div id="training-metrics" style="font-size: 14px; color: #a1a1aa;">Epoch: <span id="train-epoch">0</span>/3 | Step: <span id="train-step">0</span>/0 | Loss: <span id="train-loss">N/A</span></div>
                </div>
                <div style="width: 100%; height: 10px; background: rgba(255,255,255,0.05); border-radius: 5px; overflow: hidden; margin-top: 15px;">
                    <div id="training-progress-bar" style="width: 0%; height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6); transition: width 0.3s ease;"></div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="card" style="height: 400px; display: flex; flex-direction: column;">
                    <h3>📉 Loss Performance Curve</h3>
                    <div style="flex-grow: 1; position: relative;">
                        <canvas id="trainingLossChart"></canvas>
                    </div>
                </div>
                
                <div class="card" style="height: 400px; display: flex; flex-direction: column;">
                    <h3>💻 Terminal Console Log</h3>
                    <div id="training-console" style="flex-grow: 1; background: #0f172a; border-radius: 8px; padding: 15px; font-family: 'Courier New', Courier, monospace; font-size: 13px; color: #10b981; overflow-y: auto; border: 1px solid #334155;">
                        <div style="color: #64748b;">[System] Ready to start fine-tuning process.</div>
                        <div style="color: #64748b;">[System] Awaiting user command...</div>
                    </div>
                </div>
            </div>
        </div>
"""
if "view-training" not in content:
    # Insert before the closing </main>
    main_end = content.find("</main>")
    if main_end != -1:
        content = content[:main_end] + training_view_html + content[main_end:]

# 3. Add JavaScript
js_code = """
// --- Training UI Logic ---
let trainingChart = null;
let trainingPollingInterval = null;
let lossData = [];
let labelsData = [];

function initTrainingChart() {
    const ctx = document.getElementById('trainingLossChart');
    if (!ctx) return;
    
    if (trainingChart) {
        trainingChart.destroy();
    }
    
    trainingChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labelsData,
            datasets: [{
                label: 'Training Loss',
                data: lossData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                pointRadius: 1,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, title: { display: true, text: 'Loss' } },
                x: { grid: { display: false }, title: { display: true, text: 'Step' } }
            },
            plugins: { legend: { display: false } },
            animation: false
        }
    });
}

function startAiTraining() {
    const btn = document.getElementById('btn-start-training');
    btn.disabled = true;
    btn.innerHTML = '⏳ Initializing...';
    
    fetch(`http://${gwHost}:19000/api/training/start`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            btn.innerHTML = '⚙️ Training in Progress...';
            document.getElementById('training-status-badge').innerText = 'TRAINING';
            document.getElementById('training-status-badge').style.background = 'rgba(59, 130, 246, 0.2)';
            document.getElementById('training-status-badge').style.color = '#60a5fa';
            
            // Reset Chart
            lossData = [];
            labelsData = [];
            initTrainingChart();
            
            // Start Polling
            if (trainingPollingInterval) clearInterval(trainingPollingInterval);
            trainingPollingInterval = setInterval(pollTrainingStatus, 1000);
        })
        .catch(err => {
            console.error('Training Error:', err);
            btn.disabled = false;
            btn.innerHTML = '🚀 Start Training (Simulate)';
            alert('Failed to start training: ' + err.message);
        });
}

function pollTrainingStatus() {
    fetch(`http://${gwHost}:19000/api/training/status`)
        .then(res => res.json())
        .then(data => {
            // Update Metrics
            document.getElementById('train-epoch').innerText = data.current_epoch;
            document.getElementById('train-step').innerText = data.current_step;
            document.getElementById('train-loss').innerText = data.loss.toFixed(4);
            
            // Update Progress
            const progress = (data.current_step / data.total_steps) * 100;
            document.getElementById('training-progress-bar').style.width = `${progress}%`;
            
            // Update Chart
            if (data.is_training || data.current_step >= data.total_steps) {
                if (labelsData.length === 0 || labelsData[labelsData.length - 1] !== data.current_step) {
                    labelsData.push(data.current_step);
                    lossData.push(data.loss);
                    if (trainingChart) trainingChart.update();
                }
            }
            
            // Update Console
            const consoleDiv = document.getElementById('training-console');
            consoleDiv.innerHTML = '';
            data.logs.forEach(log => {
                consoleDiv.innerHTML += `<div><span style="color: #64748b;">[${log.time}]</span> ${log.msg}</div>`;
            });
            consoleDiv.scrollTop = consoleDiv.scrollHeight;
            
            // Handle Completion
            if (!data.is_training && data.current_step >= data.total_steps && data.total_steps > 0) {
                clearInterval(trainingPollingInterval);
                const btn = document.getElementById('btn-start-training');
                btn.disabled = false;
                btn.innerHTML = '✅ Training Complete';
                document.getElementById('training-status-badge').innerText = 'COMPLETED';
                document.getElementById('training-status-badge').style.background = 'rgba(16, 185, 129, 0.2)';
                document.getElementById('training-status-badge').style.color = '#34d399';
            }
        })
        .catch(err => console.error(err));
}

// Hook into switchTab
const originalSwitchTab = switchTab;
switchTab = function(tabId) {
    originalSwitchTab(tabId);
    if (tabId === 'training') {
        setTimeout(() => {
            if (!trainingChart) initTrainingChart();
        }, 100);
    }
};
"""
if "startAiTraining()" not in content:
    # Insert before the closing </script>
    script_end = content.rfind("</script>")
    if script_end != -1:
        content = content[:script_end] + js_code + "\n" + content[script_end:]

with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)
print("index.html patched with AI Training Simulation UI.")
