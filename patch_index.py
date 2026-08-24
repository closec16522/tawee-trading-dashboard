import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Add AI Meeting room HTML inside getCommandCenterHTML(), after the <div class="stage">...</div>
old_stage_end = """                    <div id="chartview" style="display:none;"><div id="tv_chart" style="width:100%;height:100%;"></div></div>
                    
                  </div>"""

new_stage_end = """                    <div id="chartview" style="display:none;"><div id="tv_chart" style="width:100%;height:100%;"></div></div>
                    
                  </div>
                  
                  <!-- AI Meeting Room Chat Log -->
                  <div class="ai-meeting-room" id="ai-meeting-room">
                    <div class="ai-meeting-header">?? AI Team Meeting Room - Live Protocol</div>
                    <div class="ai-meeting-log" id="ai-meeting-log">
                        <div class="ai-msg system-msg">[SYSTEM] Connecting to Multi-Agent Protocol...</div>
                        <div class="ai-msg system-msg">[SYSTEM] Connection Established. Listening to Agents.</div>
                    </div>
                  </div>"""

html = html.replace(old_stage_end, new_stage_end)

# Add CSS for the meeting room and responsiveness. I'll append it before </style> or inside a <style> block.
css_to_add = """
/* AI Meeting Room Styles */
.ai-meeting-room {
    margin-top: 15px;
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    height: 250px;
    overflow: hidden;
}
.ai-meeting-header {
    background: #1e293b;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: bold;
    color: #94a3b8;
    border-bottom: 1px solid #334155;
    display: flex;
    align-items: center;
    gap: 8px;
}
.ai-meeting-log {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-family: 'Fira Code', monospace;
    font-size: 12px;
}
.ai-msg {
    padding: 6px 10px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.03);
    border-left: 3px solid #64748b;
    animation: fadeIn 0.3s ease-out;
}
.ai-msg.system-msg { border-left-color: #64748b; color: #94a3b8; }
.ai-msg.market-analyst { border-left-color: #3b82f6; color: #bfdbfe; }
.ai-msg.smc-strategist { border-left-color: #f59e0b; color: #fde68a; }
.ai-msg.trade-executor { border-left-color: #10b981; color: #a7f3d0; }
.ai-msg.portfolio-manager { border-left-color: #8b5cf6; color: #ddd6fe; }
.ai-msg.supervisor-ai { border-left-color: #eab308; color: #fef08a; }
.ai-msg.news-analyst { border-left-color: #ef4444; color: #fecaca; }
.ai-msg.trade-journal { border-left-color: #ec4899; color: #fbcfe8; }
.ai-msg b { color: #fff; }

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .stage {
        height: 300px !important; /* Scale down canvas container on mobile */
    }
    #office {
        width: 100% !important;
        height: auto !important;
        object-fit: contain;
    }
    .stats {
        flex-wrap: wrap;
    }
    .ai-meeting-room {
        height: 200px;
    }
}
"""
if "/* AI Meeting Room Styles */" not in html:
    html = html.replace("</style>", css_to_add + "\n</style>")


# Add TradingView studies
old_tv_options1 = """              "container_id": "tradingview_embed_canvas",
              "hide_side_toolbar": false,
              "studies": [
                "RSI@tv-basicstudies",
                "MASimple@tv-basicstudies"
              ]"""
new_tv_options1 = """              "container_id": "tradingview_embed_canvas",
              "hide_side_toolbar": false,
              "studies": [
                "RSI@tv-basicstudies",
                "MASimple@tv-basicstudies",
                "MACD@tv-basicstudies"
              ]"""
html = html.replace(old_tv_options1, new_tv_options1)

old_tv_options2 = """              "container_id": "trading_tv_embed",
              "hide_side_toolbar": false,
              "studies": [
                "RSI@tv-basicstudies",
                "MASimple@tv-basicstudies"
              ]"""
new_tv_options2 = """              "container_id": "trading_tv_embed",
              "hide_side_toolbar": false,
              "studies": [
                "RSI@tv-basicstudies",
                "MASimple@tv-basicstudies",
                "MACD@tv-basicstudies"
              ]"""
html = html.replace(old_tv_options2, new_tv_options2)

old_tv_options3 = """            locale: "en",
            allow_symbol_change: true,
            hide_side_toolbar: false
          });"""
new_tv_options3 = """            locale: "en",
            allow_symbol_change: true,
            hide_side_toolbar: false,
            studies: [
                "RSI@tv-basicstudies",
                "MASimple@tv-basicstudies",
                "MACD@tv-basicstudies"
            ]
          });"""
html = html.replace(old_tv_options3, new_tv_options3)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Patched index.html with AI Meeting Room and TV studies.")
