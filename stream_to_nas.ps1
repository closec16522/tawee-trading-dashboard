$b64 = (Get-Content -Path 'index_b64.txt' -Raw).Trim()
$chunkSize = 50000
$totalLen = $b64.Length

$clearSh = "echo NUTza067668141 | sudo -S rm -f /tmp/b64.txt"
[System.IO.File]::WriteAllText("cmd_clear.sh", $clearSh)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_clear.sh superuser@192.168.0.11

Write-Host "Streaming chunks to NAS..."

for ($i = 0; $i -lt $totalLen; $i += $chunkSize) {
    $len = [Math]::Min($chunkSize, $totalLen - $i)
    $part = $b64.Substring($i, $len)
    
    $chunkSh = "cat << 'EOF' | echo NUTza067668141 | sudo -S tee -a /tmp/b64.txt > /dev/null`n$part`nEOF"
    [System.IO.File]::WriteAllText("cmd_chunk.sh", $chunkSh)
    & .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_chunk.sh superuser@192.168.0.11
    Write-Host "Uploaded chunk $([Math]::Floor($i / $chunkSize) + 1) / $([Math]::Ceiling($totalLen / $chunkSize))"
}

$decodeSh = "echo NUTza067668141 | sudo -S base64 -d /tmp/b64.txt | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/index.html > /dev/null`necho INDEX_DECODED_OK"
[System.IO.File]::WriteAllText("cmd_decode.sh", $decodeSh)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_decode.sh superuser@192.168.0.11
