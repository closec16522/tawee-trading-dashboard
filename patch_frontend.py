import os

path = 'index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find connectMT5Gateway();
target = 'connectMT5Gateway();'
replacement = '''connectMT5Gateway();

// --- 🚀 INSTANT JOURNAL LOAD (Phase 1 Fix) ---
setTimeout(() => {
    const apiHost = new URLSearchParams(window.location.search).get('gw') || '192.168.0.41';
    fetch(`http://${apiHost}:19000/api/signal_history`)
        .then(res => res.json())
        .then(data => {
            if (data && data.length > 0) {
                window.signalsHistory = data;
                if (window.renderSignalsTable) window.renderSignalsTable(data);
                console.log("✅ Successfully loaded past Journal entries!");
            }
        }).catch(err => console.error("Error loading journal:", err));
}, 1000);
'''

if target in content and '// --- 🚀 INSTANT JOURNAL LOAD' not in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Frontend Journal patch applied!")
else:
    print("Patch already applied or target not found.")
