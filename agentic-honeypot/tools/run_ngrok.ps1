<#
Simple ngrok helper (PowerShell).
Requirements: ngrok CLI installed and `ngrok authtoken <token>` configured.
Usage: .\run_ngrok.ps1 -Port 8000
#>
param(
    [int]$Port = 8000,
    [string]$Region = "us"
)

Write-Host "Starting ngrok for port $Port (region=$Region)..."
if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Error "ngrok CLI not found. Install from https://ngrok.com/download and configure your authtoken."
    exit 1
}

$proc = Start-Process -NoNewWindow -PassThru -FilePath ngrok -ArgumentList "http", "--region=$Region", "$Port"
Write-Host "ngrok started (PID $($proc.Id)). Waiting for public URL..."
Start-Sleep -Seconds 2
try {
    $api = Invoke-RestMethod http://127.0.0.1:4040/api/tunnels -ErrorAction Stop
    $public = $api.tunnels[0].public_url
    Write-Host "Public URL: $public"
} catch {
    Write-Warning "Could not fetch ngrok tunnels immediately. Check http://127.0.0.1:4040/status for details."
}

Write-Host "To stop: Stop-Process -Id $($proc.Id)"
