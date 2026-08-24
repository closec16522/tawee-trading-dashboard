$b64Dockerfile = [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('Dockerfile'))
$b64Compose = [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('docker-compose.yml'))
$b64Index = (Get-Content -Path 'index_b64.txt' -Raw).Trim()

$initSh = "echo '$b64Dockerfile' | base64 -d | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/Dockerfile > /dev/null`n" +
          "echo '$b64Compose' | base64 -d | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/docker-compose.yml > /dev/null`n" +
          "echo NUTza067668141 | sudo -S rm -f /tmp/b64_index.txt"

[System.IO.File]::WriteAllText("cmd_init.sh", $initSh)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_init.sh superuser@192.168.0.11

Write-Host "Streaming index.html chunks..."

$chunkSize = 50000
$totalLen = $b64Index.Length

for ($i = 0; $i -lt $totalLen; $i += $chunkSize) {
    $len = [Math]::Min($chunkSize, $totalLen - $i)
    $part = $b64Index.Substring($i, $len)
    
    $chunkSh = "cat << 'EOF' | echo NUTza067668141 | sudo -S tee -a /tmp/b64_index.txt > /dev/null`n$part`nEOF"
    [System.IO.File]::WriteAllText("cmd_chunk.sh", $chunkSh)
    & .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_chunk.sh superuser@192.168.0.11
    Write-Host "Uploaded chunk $([Math]::Floor($i / $chunkSize) + 1) / $([Math]::Ceiling($totalLen / $chunkSize))"
}

$decodeSh = "echo NUTza067668141 | sudo -S base64 -d /tmp/b64_index.txt | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/index.html > /dev/null`n" +
            "echo NUTza067668141 | sudo -S rm -f /tmp/b64_index.txt`n" +
            "echo DEPLOYMENT_FILES_WRITTEN"
[System.IO.File]::WriteAllText("cmd_decode.sh", $decodeSh)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_decode.sh superuser@192.168.0.11
