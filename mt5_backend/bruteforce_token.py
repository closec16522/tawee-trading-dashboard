import requests
import itertools

# Base token with placeholders
# 8899582441:AAFvY4Ab23ilqc{A}{B}BBue5zo{C}8RbmmJAVAA{D}

A_opts = ['0', 'O', 'o']
B_opts = ['1', 'l', 'I', 'L']
C_opts = ['1', 'l', 'I']
D_opts = ['I', 'l', '1']

found = False
for a in A_opts:
    for b in B_opts:
        for c in C_opts:
            for d in D_opts:
                t = f"8899582441:AAFvY4Ab23ilqc{a}{b}BBue5zo{c}8RbmmJAVAA{d}"
                url = f"https://api.telegram.org/bot{t}/getMe"
                r = requests.get(url)
                if r.status_code == 200:
                    print(f"VALID TOKEN FOUND: {t}")
                    found = True
                    break
            if found: break
        if found: break
    if found: break

if not found:
    print("No valid token found in combinations.")
