$b64 = (Get-Content -Path 'index_b64.txt' -Raw).Trim()
$content = "cat << 'EOF' | base64 -d | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/index.html > /dev/null`n$b64`nEOF`necho INDEX_HTML_DECODED_FULLY"
[System.IO.File]::WriteAllText("remote_write_index.sh", $content)
Write-Host "remote_write_index.sh generated."
