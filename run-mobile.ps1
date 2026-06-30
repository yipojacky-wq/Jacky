param(
  [int]$Port = 8010
)

$ErrorActionPreference = "Stop"

$ip = Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object {
    $_.IPAddress -notlike "127.*" -and
    $_.IPAddress -notlike "169.254.*" -and
    $_.PrefixOrigin -ne "WellKnown"
  } |
  Select-Object -First 1 -ExpandProperty IPAddress

if (-not $ip) {
  Write-Host "Could not detect a LAN IPv4 address. Start manually with: uvicorn app.main:app --host 0.0.0.0 --port $Port"
  exit 1
}

Write-Host ""
Write-Host "Disclosure Completion AI MVP mobile/LAN server"
Write-Host "Local URL:  http://127.0.0.1:$Port"
Write-Host "Phone URL:  http://$ip`:$Port"
Write-Host ""
Write-Host "Keep this terminal open. Connect your phone to the same Wi-Fi, then open the Phone URL."
Write-Host ""

uvicorn app.main:app --host 0.0.0.0 --port $Port
