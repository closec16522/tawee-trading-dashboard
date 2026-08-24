$df = [System.IO.File]::ReadAllText('Dockerfile')
$dc = [System.IO.File]::ReadAllText('docker-compose.yml')

$sh1 = "cat << 'EOF' | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/Dockerfile > /dev/null`n$df`nEOF`necho DF_OK"
[System.IO.File]::WriteAllText("push_df.sh", $sh1)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m push_df.sh superuser@192.168.0.11

$sh2 = "cat << 'EOF' | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/docker-compose.yml > /dev/null`n$dc`nEOF`necho DC_OK"
[System.IO.File]::WriteAllText("push_dc.sh", $sh2)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m push_dc.sh superuser@192.168.0.11

$b64Index = [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('index.html'))
$chunkSize = 50000
$totalLen = $b64Index.Length

$clearSh = "echo NUTza067668141 | sudo -S rm -f /tmp/idx_b64.txt"
[System.IO.File]::WriteAllText("push_clear.sh", $clearSh)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m push_clear.sh superuser@192.168.0.11

Write-Host "Uploading index.html to NAS..."

for ($i = 0; $i -lt $totalLen; $i += $chunkSize) {
    $len = [Math]::Min($chunkSize, $totalLen - $i)
    $part = $b64Index.Substring($i, $len)
    
    $chunkSh = "cat << 'EOF' | echo NUTza067668141 | sudo -S tee -a /tmp/idx_b64.txt > /dev/null`n$part`nEOF"
    [System.IO.File]::WriteAllText("push_chunk.sh", $chunkSh)
    & .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m push_chunk.sh superuser@192.168.0.11
    Write-Host "Uploaded chunk $([Math]::Floor($i / $chunkSize) + 1) / $([Math]::Ceiling($totalLen / $chunkSize))"
}

$decodeSh = "echo NUTza067668141 | sudo -S base64 -d /tmp/idx_b64.txt | echo NUTza067668141 | sudo -S tee /volume1/docker/tawee_trading_intelligence/index.html > /dev/null`n" +
            "echo NUTza067668141 | sudo -S rm -f /tmp/idx_b64.txt`n" +
            "echo ALL_FILES_PUSHED_SUCCESSFULLY"
[System.IO.File]::WriteAllText("push_decode.sh", $decodeSh)
& .\plink.exe -batch -hostkey 'SHA256:qhnc+VcD08Y08Ped5zSY/9HCzXd80uLTMthIH7TOz3E' -ssh -pw NUTza067668141 -m push_decode.sh superuser@192.168.0.11
