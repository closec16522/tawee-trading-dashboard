import os

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix chart crash in initCommandCenterLogic
old_handle_resize_1 = """        const handleResize = () => {
          chart.applyOptions({
            width: chartContainer.clientWidth,
            height: chartContainer.clientHeight
          });
        };"""

new_handle_resize_1 = """        const handleResize = () => {
          if (!document.body.contains(chartContainer)) return;
          if (chartContainer.clientWidth > 0 && chartContainer.clientHeight > 0) {
              chart.applyOptions({
                width: chartContainer.clientWidth,
                height: chartContainer.clientHeight
              });
          }
        };"""

content = content.replace(old_handle_resize_1, new_handle_resize_1)

# 2. Fix chart crash in initTV
old_handle_resize_2 = """          const handleResize = () => {
              if(tvContainer.clientWidth > 0 && tvContainer.clientHeight > 0) {
                 chart.applyOptions({ width: tvContainer.clientWidth, height: tvContainer.clientHeight });
              }
          };"""

new_handle_resize_2 = """          const handleResize = () => {
              if (!document.body.contains(tvContainer)) return;
              if(tvContainer.clientWidth > 0 && tvContainer.clientHeight > 0) {
                 chart.applyOptions({ width: tvContainer.clientWidth, height: tvContainer.clientHeight });
              }
          };"""

content = content.replace(old_handle_resize_2, new_handle_resize_2)

# 3. Add initNewsLogic
old_init_news = """      function initNewsLogic() {}"""

new_init_news = """      function initNewsLogic() {
        const fetchNews = async () => {
            try {
                const res = await fetch(`http://${host}:19000/api/news_status`);
                if(res.ok) {
                    const data = await res.json();
                    
                    const timeEl = document.getElementById("news-update-time");
                    if (timeEl) timeEl.innerText = new Date().toLocaleTimeString();
                    
                    const sumEl = document.getElementById("news-summary-text");
                    if (sumEl && data.summary_text) sumEl.innerText = data.summary_text;
                    
                    const grid = document.getElementById("news-pairs-grid");
                    if (grid && data.pairs) {
                        grid.innerHTML = data.pairs.map(p => `
                            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.04); border-radius:8px; padding:12px;">
                                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                    <span style="font-weight:700; color:#cbd5e1;">${p.symbol}</span>
                                    <span style="font-size:11px; padding:2px 8px; border-radius:12px; background:${p.color}20; color:${p.color}; border:1px solid ${p.color}40;">${p.impact}</span>
                                </div>
                                <div style="font-size:12px; color:#94a3b8;">${p.text}</div>
                            </div>
                        `).join("");
                    }
                }
            } catch(e) {
                console.error("Failed to load news status", e);
            }
        };
        fetchNews();
      }"""

content = content.replace(old_init_news, new_init_news)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched index.html")
