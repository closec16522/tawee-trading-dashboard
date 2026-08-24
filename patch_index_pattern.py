import os

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """                              window._patternSeries = chart.addLineSeries({
                                  color: '#eab308',
                                  lineWidth: 3,
                                  lineStyle: LightweightCharts.LineStyle.Solid,
                                  lastValueVisible: false,
                                  priceLineVisible: false
                              });
                              window._patternSeries.setData(data.pattern_points);"""

new_code = """                              window._patternSeries = chart.addLineSeries({
                                  color: '#eab308',
                                  lineWidth: 3,
                                  lineStyle: LightweightCharts.LineStyle.Solid,
                                  lastValueVisible: false,
                                  priceLineVisible: false
                              });
                              try {
                                  window._patternSeries.setData(data.pattern_points);
                              } catch(e) {
                                  console.error("Pattern Series Error:", e);
                              }"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched index.html successfully.")
else:
    print("Could not find the target code in index.html.")
