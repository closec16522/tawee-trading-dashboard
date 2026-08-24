import re

# Fix mt5_gateway.py
gw_file = 'mt5_backend/mt5_gateway.py'
with open(gw_file, 'r', encoding='utf-8') as f:
    gw_code = f.read()

# Extract the endpoint code
endpoint_match = re.search(r'(@app\.get\("/api/track_record"\).*?)(?=if __name__|$)', gw_code, re.DOTALL)
if endpoint_match:
    endpoint_code = endpoint_match.group(1).strip()
    # Remove it from the end
    gw_code = gw_code.replace(endpoint_code, "")
    
    # Re-insert before if __name__ == "__main__":
    gw_code = gw_code.replace('if __name__ == "__main__":', endpoint_code + '\n\nif __name__ == "__main__":')
    
    with open(gw_file, 'w', encoding='utf-8') as f:
        f.write(gw_code)
    print("Fixed mt5_gateway.py route position")

# Fix index.html fetch URL
html_file = 'index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace("fetch('/api/track_record')", "fetch(`http://${window.location.hostname || '127.0.0.1'}:19000/api/track_record`)")

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed index.html fetch URL")
