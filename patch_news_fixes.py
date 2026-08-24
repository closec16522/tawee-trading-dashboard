import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

init_js = """
      // Initialize News from localStorage
      const cachedNews = localStorage.getItem('kpiNews');
      if (cachedNews) {
         try {
             window._kpiNews = JSON.parse(cachedNews);
             // Dispatch it synthetically
             setTimeout(() => {
                 if (window.handleWsMessage) {
                     window.handleWsMessage({type: 'NEWS_UPDATE', ...window._kpiNews});
                 }
             }, 500);
         } catch(e) {}
      }
"""
content = content.replace("// Initialize KPIs from localStorage", init_js + "\n      // Initialize KPIs from localStorage")

news_old = """            if (data.type === "NEWS_UPDATE") {"""
news_new = """            if (data.type === "NEWS_UPDATE") {
                 localStorage.setItem('kpiNews', JSON.stringify(data));
                 window._kpiNews = data;"""

content = content.replace(news_old, news_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("News persistence applied.")
