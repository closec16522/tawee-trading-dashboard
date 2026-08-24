
 = (Get-Content -Path 'index_b64.txt' -Raw).Trim()

$initSh = "rm -f /tmp/b64_index.txt"
[System.IO.File]::WriteAllText("cmd_init.sh", $initSh)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_init.sh superuser@192.168.0.11

Write-Host "Streaming index.html chunks..."

 = 50000
 = .Length

for ( = 0;  -lt ;  += ) {
     = [Math]::Min(,  - )
     = .Substring(, )
    
    $chunkSh = "cat << 'EOF' >> /tmp/b64_index.txt`n`nEOF"
    [System.IO.File]::WriteAllText("cmd_chunk.sh", $chunkSh)
    & .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_chunk.sh superuser@192.168.0.11
    Write-Host "Uploaded chunk  / "
}

$decodeSh = "base64 -d /tmp/b64_index.txt > /tmp/index.html`n" +
            "echo NUTza067668141 | sudo -S cp /tmp/index.html /volume1/docker/tawee_trading_intelligence/index.html`n" +
            "echo NUTza067668141 | sudo -S chown 1000:1000 /volume1/docker/tawee_trading_intelligence/index.html`n" +
            "rm -f /tmp/b64_index.txt /tmp/index.html`n" +
            "echo DEPLOYMENT_FILES_WRITTEN"
[System.IO.File]::WriteAllText("cmd_decode.sh", $decodeSh)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m cmd_decode.sh superuser@192.168.0.11
