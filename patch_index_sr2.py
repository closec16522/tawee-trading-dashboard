import os
import re

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """                          } else {
                              window._patternLabel.textContent = `AI Pattern: None Detected`;
                          }
                          
                          // Support & Resistance Lines
                          if (data.sr_lines && data.sr_lines.length > 0) {
                              data.sr_lines.forEach(sr => {
                                  newSeries.createPriceLine({
                                      price: sr.price,
                                      color: sr.type === 'support' ? '#10b981' : '#ef4444',
                                      lineWidth: 2,
                                      lineStyle: LightweightCharts.LineStyle.Dashed,
                                      axisLabelVisible: true,
                                      title: sr.type === 'support' ? `Sup ${sr.price}` : `Res ${sr.price}`,
                                  });
                              });
                          }"""

content = re.sub(
    r'\} else \{\s*window\._patternLabel\.textContent = `AI Pattern: None Detected`;\s*\}',
    replacement,
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched index.html successfully.")
