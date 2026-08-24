import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add logic for Active Signals and AI Analysis
global_funcs = '''
        window.renderDashSignals = function(history) {
            const container = document.getElementById("dash-signals-container");
            if(!container) return;
            const activeSigs = history.filter(s => s.status === "ACTIVE" || s.status === "PENDING" || (s.result && s.result.toLowerCase().includes('wait')));
            
            if(activeSigs.length === 0) {
                container.innerHTML = '<div style="color:var(--text-muted); font-size:12px; grid-column: 1 / -1;">ไม่มีสัญญาณที่กำลัง Active</div>';
                return;
            }
            
            let html = "";
            activeSigs.slice(0, 3).forEach(s => {
                const sideColor = (s.type || s.side) === "BUY" ? "#10b981" : "#ef4444";
                const sideText = (s.type || s.side) === "BUY" ? "▲ BUY ฝั่งขาขึ้น" : "▼ SELL ฝั่งขาลง";
                html += <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:10px 14px; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:12px; color:#fff;"></b>
                    <span style="font-size:11px; font-weight:700; color:;"></span>
                    <span style="font-size:10px; color:var(--text-muted);">Entry  • Conf %</span>
                </div>;
            });
            container.innerHTML = html;
        };
        
        window.updateDashAiAnalysis = function(history) {
            // Find most recent signal to populate AI Analysis card
            if(!history || history.length === 0) return;
            const recent = history[0];
            
            const elSym = document.getElementById('ai-analysis-symbol');
            const elBias = document.getElementById('ai-analysis-bias');
            const elBullL = document.getElementById('ai-bullish-label');
            const elBearL = document.getElementById('ai-bearish-label');
            const elBullB = document.getElementById('ai-bullish-bar');
            const elNeuT = document.getElementById('ai-neu-text');
            const elMain = document.getElementById('ai-analysis-main');
            const elStruct = document.getElementById('ai-analysis-struct');
            const elRec = document.getElementById('ai-analysis-rec');
            
            if(elSym) elSym.textContent = recent.symbol;
            
            let isBuy = (recent.type || recent.side) === "BUY";
            let conf = parseInt(recent.confidence || 80);
            
            if(elBias) elBias.textContent = isBuy ? "เอนขาขึ้น (Bullish)" : "เอนขาลง (Bearish)";
            
            let bullPct = isBuy ? conf : (100 - conf - 10);
            let bearPct = isBuy ? (100 - conf - 10) : conf;
            if(bullPct < 0) bullPct = 0;
            if(bearPct < 0) bearPct = 0;
            let neuPct = 100 - bullPct - bearPct;
            
            if (elBullL) elBullL.textContent = Bullish %;
            if (elBearL) elBearL.textContent = Bearish %;
            if (elBullB) elBullB.style.width = ${bullPct}%;
            if (elNeuT) elNeuT.textContent = = %;
            
            if (elMain) elMain.textContent = ${isBuy ? 'Bullish' : 'Bearish'} % ();
            if (elStruct) elStruct.textContent = recent.reason || พบสัญญาณ  ในตลาด;
            if (elRec) elRec.textContent = แนะนำให้เปิดออเดอร์  แถวราคา ;
        };
'''
content = content.replace('window.renderSignalsTable = function(history) {', global_funcs + '\n        window.renderSignalsTable = function(history) {')

hook_logic = '''
                if (window.renderDashSignals) window.renderDashSignals(data.signal_history);
                if (window.updateDashAiAnalysis) window.updateDashAiAnalysis(data.signal_history);
'''
content = content.replace('if (window.renderSignalAlerts) window.renderSignalAlerts(data.signal_history);', 'if (window.renderSignalAlerts) window.renderSignalAlerts(data.signal_history);\n' + hook_logic)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Active Signals & AI Analysis patched.")
