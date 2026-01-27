$zip = "D:\Vigil\ngrok-v3-stable-windows-amd64 (1).zip"
$dest = "D:\Vigil\agentic-honeypot\tools\ngrok"
Write-Host "Extracting `"$zip`" to `"$dest`"..."
New-Item -ItemType Directory -Path $dest -Force | Out-Null
try {
    Unblock-File -Path $zip -ErrorAction SilentlyContinue
    Expand-Archive -Path $zip -DestinationPath $dest -Force
    Write-Host "Extraction complete. Contents:"
    Get-ChildItem -Path $dest | Select-Object Name,Length | Format-Table -AutoSize
} catch {
    Write-Error "Extraction failed: $_"
    exit 1
}
