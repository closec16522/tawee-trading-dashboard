import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

init_js = """
      // Initialize AI Analysis from localStorage
      const cachedAi = localStorage.getItem('aiAnalysisStr');
      if (cachedAi) {
         try {
             window.aiDict = JSON.parse(cachedAi);
             setTimeout(() => {
                 if (window.updateDashAiAnalysis && window.signalsHistory) {
                     window.updateDashAiAnalysis(window.signalsHistory);
                 }
             }, 600);
         } catch(e) {}
      }
"""
content = re.sub(r'const cachedAi = localStorage\.getItem\(\'aiAnalysisStr\'\);.*?catch\(e\) \{\}\n\s*\}', init_js.strip(), content, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("AI cache dispatch applied.")
