import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

old_agent_update = """                   if (data.agent_id && typeof speechBubbles !== 'undefined') {
                   if (!speechBubbles[data.agent_id]) speechBubbles[data.agent_id] = [];
                   
                   let txt = data.status;
                   if (data.activity) txt = data.activity;
                   
                   // Keep only last 3 messages to rotate
                   speechBubbles[data.agent_id].unshift(txt);"""

new_agent_update = """                   if (data.agent_id && typeof speechBubbles !== 'undefined') {
                   if (!speechBubbles[data.agent_id]) speechBubbles[data.agent_id] = [];
                   
                   let txt = data.status;
                   if (data.activity) txt = data.activity;
                   
                   // Keep only last 3 messages to rotate
                   speechBubbles[data.agent_id].unshift(txt);
                   
                   // Add to AI Meeting Room Chat Log
                   const logContainer = document.getElementById("ai-meeting-log");
                   if (logContainer) {
                       const msgDiv = document.createElement("div");
                       const agentClass = data.agent_id.replace("_", "-");
                       msgDiv.className = `ai-msg ${agentClass}`;
                       
                       const agentNameMap = {
                           "market_analyst": "Market Analyst",
                           "smc_strategist": "SMC Strategist",
                           "trade_executor": "Trade Executor",
                           "portfolio_manager": "Portfolio Manager",
                           "supervisor_ai": "Supervisor AI",
                           "news_analyst": "News Analyst",
                           "trade_journal": "Trade Journal"
                       };
                       const readableName = agentNameMap[data.agent_id] || data.agent_id.toUpperCase();
                       
                       msgDiv.innerHTML = `<b>[${readableName}]</b> ${txt}`;
                       logContainer.appendChild(msgDiv);
                       logContainer.scrollTop = logContainer.scrollHeight;
                       
                       // Keep max 50 messages
                       if (logContainer.children.length > 50) {
                           logContainer.removeChild(logContainer.firstChild);
                       }
                   }"""

html = html.replace(old_agent_update, new_agent_update)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Patched websocket AGENT_UPDATE for meeting room logs.")
