import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix window.renderSignalAlerts
js_code = r'''      window.renderSignalAlerts = function(history) {
          const dashCont = document.getElementById("dash-signals-container");
          const tradeCont = document.getElementById("trade-signals-container");
          const notifList = document.querySelector("#notif-menu .notif-list");
          const notifCount = document.querySelector("#notif-menu .notif-sub-count");
          const bellBadge = document.querySelector(".bell-badge");
          
          if (!history || history.length === 0) {
              const emptyMsg = <div style="color:var(--text-muted); font-size:12px; padding:10px; text-align:center;">ไม่พบสัญญาณเทรดในรอบนี้</div>;
              if (dashCont) dashCont.innerHTML = emptyMsg;
              if (tradeCont) tradeCont.innerHTML = emptyMsg;
              if (notifList) notifList.innerHTML = <div style="color:var(--text-muted); font-size:12px; padding:10px; text-align:center;">ไม่มีประวัติสัญญาณ</div>;
              if (notifCount) notifCount.innerText = "0 สัญญาณเข้าเกณฑ์";
              if (bellBadge) bellBadge.style.display = 'none';
              return;
          }
          
          let dashHtml = "";
          let tradeHtml = "";
          let notifHtml = "";
          
          // Use only top 4 for alerts
          const topSignals = history.slice(0, 4);
          
          topSignals.forEach(sig => {
              const isBuy = sig.type === "BUY";
              const color = isBuy ? "#10b981" : "#ef4444";
              const dirLabel = isBuy ? "▲ BUY ฝั่งขาขึ้น" : "▼ SELL ฝั่งขาลง";
              const badgeClass = isBuy ? "buy" : "sell";
              const badgeLabel = isBuy ? "▲ BUY สัญญาณ" : "▼ SELL สัญญาณ";
              
              dashHtml += <div class="signal-row-item" style="padding:10px 14px; background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.06); border-radius:8px;">
                <span class="signal-pair-name" style="font-weight:800; color:#fff;"></span>
                <span class="signal-status-label" style="color:;"></span>
                <span style="font-size:11px; color:#60a5fa; font-weight:700;">Entry  • Conf %</span>
              </div>;
              
              const notifBadgeReal = isBuy ? "▲ BUY ซื้อ" : "▼ SELL ขาย";
              
              const commonNotifHtml = <div class="notif-item" onclick="window.selectNotifItem('', event)" style="cursor:pointer; padding:8px 10px; background:rgba(255,255,255,0.015); border:1px solid rgba(255,255,255,0.03); border-radius:8px; display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
                <span class="notif-badge " style="font-size:10.5px; padding:3px 8px;"></span>
                <div class="notif-info" style="flex:1; margin-left:12px;">
                  <div class="notif-pair" style="font-weight:700; font-size:13px; color:#fff; margin-bottom:2px;"></div>
                  <div class="notif-details" style="font-size:10.5px; color:#94a3b8;">เข้า  · SL  · TP </div>
                </div>
                <span class="notif-prob" style="font-size:13px; font-weight:700; color:#60a5fa;">%</span>
              </div>;
              
              tradeHtml += commonNotifHtml;
              notifHtml += commonNotifHtml;
          });
          
          if (dashCont) dashCont.innerHTML = dashHtml;
          if (tradeCont) tradeCont.innerHTML = tradeHtml;
          if (notifList) notifList.innerHTML = notifHtml;
          
          const countText = ${topSignals.length} สัญญาณเข้าเกณฑ์;
          if (notifCount) notifCount.innerText = countText;
          if (bellBadge) {
              bellBadge.innerText = topSignals.length;
              bellBadge.style.display = 'flex';
          }
      };'''

# Replace from window.renderSignalAlerts to the end of it
pattern1 = re.compile(r'window\.renderSignalAlerts = function\(history\) \{.*?\};\n', re.DOTALL)
content = pattern1.sub(js_code + '\n', content)

# Fix window.renderSignalsTable
js_code_table = r'''        window.renderSignalsTable = function(history) {
            window.signalsHistory = history;
            const now = Date.now() / 1000;
            const cutoff = now - (window.activeDaysFilter * 86400);
            
            const filtered = history.filter(item => item.timestamp >= cutoff);
            
            const subTitle = document.getElementById('signals-count-subtitle');
            if (subTitle) {
                subTitle.textContent = ${filtered.length} รายการ · รวม re-check ต่อเนื่องเป็น 1 สัญญาณ;
            }
            
            renderRows(filtered);
        };'''

pattern2 = re.compile(r'window\.renderSignalsTable = function\(history\) \{.*?        \};', re.DOTALL)
content = pattern2.sub(js_code_table, content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("JS syntax patched")