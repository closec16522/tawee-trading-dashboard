import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add to initDashboardLogic
init_acc = """
      // Initialize Account info from localStorage
      const cachedAcc = localStorage.getItem('kpiAccount');
      if (cachedAcc) {
         try {
             window._kpiAccount = JSON.parse(cachedAcc);
         } catch(e) {}
      }
"""
content = content.replace("// Initialize KPIs from localStorage", init_acc + "\n      // Initialize KPIs from localStorage")

# Add to MT5_UPDATE websocket handler
mt5_old = """               if(data.account) {
                  window._kpiAccount = data.account;"""

mt5_new = """               if(data.account) {
                  window._kpiAccount = data.account;
                  localStorage.setItem('kpiAccount', JSON.stringify(data.account));"""
content = content.replace(mt5_old, mt5_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Account persistence applied.")
