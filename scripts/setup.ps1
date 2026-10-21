$ErrorActionPreference = 'Stop'
$Project = 'D:\VenuFinAI'
Set-Location $Project
if (-not (Test-Path '.venv')) { python -m venv .venv }
& '.\.venv\Scripts\python.exe' -m pip install --upgrade pip
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
Set-Location (Join-Path $Project 'frontend')
npm install
Set-Location $Project
if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
& '.\.venv\Scripts\python.exe' -m alembic upgrade head
Write-Host 'Base setup complete. Optional semantic embeddings can be installed with:'
Write-Host '  .\.venv\Scripts\python.exe -m pip install -r requirements-embeddings.txt'
Write-Host 'Edit .env locally for authorized provider credentials. Do not paste secrets into chat.'
