# Quick environment check before a timed assessment (Windows / PowerShell)
# JavaScript (Node.js) stack for Toptal prep
Write-Host "=== Toptal prep - Node.js environment ===" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

function Show-Cmd {
    param([string]$Name, [string]$Command)
    Write-Host ""
    Write-Host "[$Name]" -ForegroundColor Yellow
    try {
        Invoke-Expression $Command 2>&1 | ForEach-Object { Write-Host $_ }
    } catch {
        Write-Host "(not found or error)" -ForegroundColor Red
    }
}

Show-Cmd "Node" "node --version"
Show-Cmd "npm" "npm --version"

Write-Host ""
Write-Host "Done. Install Node LTS if missing: https://nodejs.org/" -ForegroundColor Green
