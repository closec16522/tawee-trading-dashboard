$bytes = [System.IO.File]::ReadAllBytes('index.html')
$b64 = [System.Convert]::ToBase64String($bytes)
[System.IO.File]::WriteAllText('index_b64.txt', $b64)
Write-Host "Base64 text file written successfully. Size: $($b64.Length)"
