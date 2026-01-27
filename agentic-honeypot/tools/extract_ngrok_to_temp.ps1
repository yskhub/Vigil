$zip = "D:\Vigil\ngrok-v3-stable-windows-amd64 (1).zip"
$dest = "C:\Temp\ngrok"
Write-Host "Extracting `"$zip`" to `"$dest`"..."
New-Item -ItemType Directory -Path $dest -Force | Out-Null
try {
    Unblock-File -Path $zip -ErrorAction SilentlyContinue
    Expand-Archive -Path $zip -DestinationPath $dest -Force
    Write-Host "Extraction complete. Contents:"
    Get-ChildItem -Path $dest -Recurse | Select-Object FullName,Length | Format-Table -AutoSize
} catch {
    Write-Error "Extraction failed: $_"
    exit 1
}
