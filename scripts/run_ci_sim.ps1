Push-Location agentic-honeypot
$p = Start-Process -FilePath python -ArgumentList '-m','uvicorn','src.main:app','--host','127.0.0.1','--port','8000' -PassThru
Write-Output "uvicorn pid=$($p.Id)"
$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch { }
    Start-Sleep -Seconds 1
}
if (-not $ok) { Write-Output 'Health check failed after timeout' }
Pop-Location
if ($ok) {
    python -m pytest -q
} else {
    Write-Output 'Skipping tests due to failed health check'
}
if ($p -and -not $p.HasExited) {
    $p.Kill()
    Write-Output "Stopped uvicorn pid=$($p.Id)"
} else {
    Write-Output 'uvicorn process not found or already exited'
}
