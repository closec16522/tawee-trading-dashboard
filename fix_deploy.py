import codecs
path = 'master_deploy.ps1'
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

old_chunk = "cat << 'EOF' | echo NUTza067668141 | sudo -S tee -a /tmp/b64_index.txt > /dev/null\\n$part\\nEOF"
new_chunk = "cat << 'EOF' >> /tmp/b64_index.txt\\n$part\\nEOF"
content = content.replace(old_chunk, new_chunk)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)
