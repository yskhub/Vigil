$ngrok = Join-Path $PSScriptRoot 'ngrok\ngrok.exe'
if (-not (Test-Path $ngrok)) {
    Write-Error "ngrok not found at $ngrok"
    exit 1
}
Write-Host "Starting ngrok from $ngrok (http 8000)..."
Start-Process -FilePath $ngrok -ArgumentList 'http','8000' -WorkingDirectory (Split-Path $ngrok) -NoNewWindow -PassThru | ForEach-Object { Write-Host "Started ngrok PID $($_.Id)" }
Start-Sleep -Seconds 2
try {
    $api = Invoke-RestMethod -Uri http://127.0.0.1:4040/api/tunnels -ErrorAction Stop
    $public = $api.tunnels[0].public_url
    Write-Host "Public URL: $public"
} catch {
    Write-Warning "ngrok started but API endpoint not available yet. Check http://127.0.0.1:4040/status"
}
