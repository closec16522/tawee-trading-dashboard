import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

toolbar_html = """<div id="chartview" style="display:none; flex-direction:column; height:100%;">
  <div style="padding:8px 16px; background:#0f172a; border-bottom:1px solid #1e293b; display:flex; gap:12px; align-items:center;">
    <span style="color:#a78bfa; font-weight:800; font-size:14px;">🤖 AI Fib Analysis</span>
    <input type="text" id="lw-symbol" value="XAUUSD" style="background:#1e293b; border:1px solid rgba(255,255,255,0.1); color:#fff; padding:4px 8px; border-radius:4px; font-weight:700; width:100px; outline:none;" />
    <select id="lw-timeframe" style="background:#1e293b; border:1px solid rgba(255,255,255,0.1); color:#fff; padding:4px 8px; border-radius:4px; outline:none;">
      <option value="5">M5</option>
      <option value="15">M15</option>
      <option value="30">M30</option>
      <option value="60" selected>H1</option>
      <option value="240">H4</option>
      <option value="D">D1</option>
    </select>
    <button id="lw-reload" style="background:#3b82f6; color:#fff; border:none; padding:4px 12px; border-radius:4px; font-size:12px; font-weight:700; cursor:pointer;">Analyze / Reload</button>
  </div>
  <div id="tv_chart" style="flex:1; width:100%; position:relative;"></div>
</div>"""

if '🤖 AI Fib Analysis' not in content:
    content = content.replace('<div id="chartview" style="display:none;"><div id="tv_chart" style="width:100%;height:100%;"></div></div>', toolbar_html)
    content = content.replace('if (chartview) chartview.style.display = v === "chart" ? "block" : "none";', 'if (chartview) chartview.style.display = v === "chart" ? "flex" : "none";')

init_tv_new = """const initTV = async () => {
          const tvContainer = root.querySelector("#tv_chart");
          if (!tvContainer) return;
          if (typeof LightweightCharts === "undefined") {
            tvContainer.innerHTML = '<div style="color:#7c889f;padding:20px">LightweightCharts not loaded.</div>';
            return;
          }
          
          if(tvWidget) return; // Already initialized chart instance

          tvContainer.innerHTML = "";
          const chart = LightweightCharts.createChart(tvContainer, {
              width: tvContainer.clientWidth,
              height: tvContainer.clientHeight,
              layout: { background: { type: 'solid', color: '#0c1020' }, textColor: '#cbd5e1' },
              grid: { vertLines: { color: 'rgba(255,255,255,0.05)' }, horzLines: { color: 'rgba(255,255,255,0.05)' } },
              crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
              timeScale: { timeVisible: true, secondsVisible: false }
          });
          tvWidget = chart; // Store chart instance

          const handleResize = () => {
              if(tvContainer.clientWidth > 0 && tvContainer.clientHeight > 0) {
                 chart.applyOptions({ width: tvContainer.clientWidth, height: tvContainer.clientHeight });
              }
          };
          window.addEventListener('resize', handleResize);

          const candlestickSeries = chart.addCandlestickSeries({
              upColor: '#10b981', downColor: '#ef4444', borderVisible: false, wickUpColor: '#10b981', wickDownColor: '#ef4444'
          });
          
          window._lwLoadData = async (series) => {
              const symInput = root.querySelector('#lw-symbol');
              const tfInput = root.querySelector('#lw-timeframe');
              if(!symInput || !tfInput) return series;
              
              const cleanSymbol = symInput.value.split(':').pop().toUpperCase();
              
              try {
                  const res = await fetch(`http://127.0.0.1:19000/api/history?symbol=${cleanSymbol}&timeframe=${tfInput.value}&count=200`);
                  if(res.ok) {
                      const data = await res.json();
                      if(data.data && data.data.length > 0) {
                          
                          chart.removeSeries(series);
                          const newSeries = chart.addCandlestickSeries({
                              upColor: '#10b981', downColor: '#ef4444', borderVisible: false, wickUpColor: '#10b981', wickDownColor: '#ef4444'
                          });
                          newSeries.setData(data.data);
                          
                          // Fibonacci Calculation
                          let maxHigh = -Infinity;
                          let minLow = Infinity;
                          data.data.forEach(d => {
                              if (d.high > maxHigh) maxHigh = d.high;
                              if (d.low < minLow) minLow = d.low;
                          });
                          
                          if (maxHigh !== -Infinity && minLow !== Infinity) {
                              const diff = maxHigh - minLow;
                              const levels = [
                                  { ratio: 1.0, color: '#ef4444', name: '1 (0%)' },
                                  { ratio: 0.786, color: '#f59e0b', name: '0.786 (21.4%)' },
                                  { ratio: 0.618, color: '#10b981', name: '0.618 (38.2%)' },
                                  { ratio: 0.5, color: '#3b82f6', name: '0.5 (50%)' },
                                  { ratio: 0.382, color: '#10b981', name: '0.382 (61.8%)' },
                                  { ratio: 0.236, color: '#f59e0b', name: '0.236 (76.4%)' },
                                  { ratio: 0.0, color: '#ef4444', name: '0 (100%)' }
                              ];
                              
                              levels.forEach(lvl => {
                                  const price = minLow + (diff * lvl.ratio);
                                  newSeries.createPriceLine({
                                      price: price,
                                      color: lvl.color,
                                      lineWidth: 1,
                                      lineStyle: LightweightCharts.LineStyle.Dashed,
                                      axisLabelVisible: true,
                                      title: `Fib ${lvl.name}`
                                  });
                              });
                          }
                          chart.timeScale().fitContent();
                          return newSeries;
                      }
                  }
              } catch(e) { console.error(e); }
              return series;
          };

          let currentSeries = candlestickSeries;
          root.querySelector('#lw-reload').addEventListener('click', async () => {
              currentSeries = await window._lwLoadData(currentSeries);
          });
          
          currentSeries = await window._lwLoadData(currentSeries);
          setTimeout(handleResize, 100);
        };"""

pattern = r'const initTV = \(\) => \{.*?\n        \};'
match = re.search(pattern, content, re.DOTALL)
if match:
    content = content[:match.start()] + init_tv_new + content[match.end():]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched initTV in index.html successfully.")
else:
    print("Could not find const initTV with regex.")
