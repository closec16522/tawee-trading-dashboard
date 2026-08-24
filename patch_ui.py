import codecs
import re

with codecs.open('index.html', 'r', 'utf-8') as f:
    content = f.read()

# Replace hardcoded SL Multiplier in Best Params box
content = re.sub(
    r'<div style="font-size: 11px; color: #f59e0b;">Best SL Multiplier</div>\s*<div style="font-size: 18px; font-weight: bold; color: #fff;">\$\{data\.best_params\.sl_multiplier\}x</div>',
    r'<div style="font-size: 11px; color: #f59e0b;">Best Strategy Params (CrossSMA)</div>\n                    <div style="font-size: 14px; font-weight: bold; color: #fff;">F: ${data.best_params.fast}, S: ${data.best_params.slow}</div>',
    content
)

# Replace table headers
content = re.sub(
    r'<th>SL Mult</th>\s*<th>R:R Ratio</th>',
    r'<th>Fast SMA</th>\n                        <th>Slow SMA</th>',
    content
)

# Replace table row data
content = re.sub(
    r'<td>\$\{item\.params\.sl_multiplier\}</td>\s*<td>\$\{item\.params\.rr_ratio\}</td>',
    r'<td>${item.params.fast}</td>\n                        <td>${item.params.slow}</td>',
    content
)

# Also fix the training simulation to look like MCP Server
# Find startAiTraining and replace its logic
training_logic = """
      function startAiTraining() {
        const btn = document.getElementById("btn-start-training");
        if (btn.disabled) return;
        
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner" style="width:14px;height:14px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;display:inline-block;animation:spin 1s linear infinite;"></span> Running AI-Trader MCP...`;
        
        const term = document.getElementById("training-terminal");
        term.innerHTML = "[System] Initializing AI-Trader MCP Server...\\n";
        
        let step = 0;
        const maxSteps = 20;
        
        const interval = setInterval(() => {
          step++;
          
          if (step === 2) {
             term.innerHTML += "[MCP] Connected to Claude Desktop.\\n";
             term.innerHTML += "[Claude] Requesting backtest for CrossSMAStrategy...\\n";
          }
          if (step === 4) {
             term.innerHTML += "[MCP] Generating YAML config...\\n";
             term.innerHTML += "[MCP] Executing Backtrader Engine (ai-trader)...\\n";
          }
          
          if (step > 4 && step < maxSteps) {
             const loss = Math.max(0.1, 2.0 - (step/maxSteps)*1.8 + (Math.random()*0.2)).toFixed(4);
             term.innerHTML += `[Backtrader] Eval step ${step}: Sharpe Ratio improving... Loss=${loss}\\n`;
             if (trainingChart) {
                trainingChart.data.labels.push(step);
                trainingChart.data.datasets[0].data.push(loss);
                trainingChart.update();
             }
          }
          
          if (step >= maxSteps) {
             clearInterval(interval);
             term.innerHTML += "[MCP] Optimization complete. Best YAML config saved.\\n";
             term.innerHTML += "[System] AI-Trader execution finished.\\n";
             btn.disabled = false;
             btn.innerHTML = "Start AI Optimization (Simulate)";
          }
          term.scrollTop = term.scrollHeight;
        }, 800);
      }
"""
# We'll just replace the whole function
content = re.sub(
    r'function startAiTraining\(\) \{.*?\}(?=\s*function|\s*</script>)',
    training_logic.strip(),
    content,
    flags=re.DOTALL
)


with codecs.open('index.html', 'w', 'utf-8') as f:
    f.write(content)