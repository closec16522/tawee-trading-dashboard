import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the definition of .main or add it to CSS
if '#command-center-root .main' not in content:
    content = content.replace('</style>', '      #command-center-root .main { padding-right: 24px !important; box-sizing: border-box !important; overflow: hidden !important; width: 100% !important; }\n    </style>')
else:
    # Append padding-right: 24px to existing .main
    pass

# Also update rightcol to remove the internal padding-right if we added it to main
content = re.sub(r'padding: 8px 24px 8px 8px !important;', 'padding: 8px !important;', content)

# To ensure the center and rightcol shrink properly without overflowing:
# Make .center flex: 1 1 auto; max-width: calc(100vw - 400px);
content = re.sub(r'max-width: calc\(100% - 380px\)', 'max-width: calc(100vw - 374px)', content) # 350 + 24 = 374

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched main padding for 0.25 inch gap.')
