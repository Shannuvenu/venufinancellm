$ErrorActionPreference = 'Stop'
$Project = 'D:\VenuFinAI'
if (-not (Test-Path (Join-Path $Project '.venv\Scripts\python.exe'))) { throw 'Run scripts\setup.ps1 first.' }
if (-not (Test-Path (Join-Path $Project 'frontend\node_modules'))) { throw 'Run scripts\setup.ps1 first.' }
if (-not (Test-Path (Join-Path $Project '.env'))) { Copy-Item (Join-Path $Project '.env.example') (Join-Path $Project '.env') }
& (Join-Path $Project '.venv\Scripts\python.exe') -m alembic upgrade head
$backend = Start-Process -FilePath (Join-Path $Project '.venv\Scripts\python.exe') -ArgumentList '-m','uvicorn','app.main:app','--app-dir',(Join-Path $Project 'backend'),'--host','127.0.0.1','--port','8000' -WorkingDirectory $Project -WindowStyle Hidden -PassThru
$frontend = Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev' -WorkingDirectory (Join-Path $Project 'frontend') -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 3
Write-Host 'VenuFin AI is starting at http://127.0.0.1:3000'
Write-Host 'API reference: http://127.0.0.1:8000/docs'
Write-Host "Backend process: $($backend.Id) | Frontend process: $($frontend.Id)"
Start-Process 'http://127.0.0.1:3000'
