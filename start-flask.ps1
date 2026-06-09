# Start the IdentityHub Flask Application
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  IdentityHub Python - SSL Startup' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan

# 1. Look for Python
$PYTHON_EXE = ''
$possiblePaths = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    'python',
    'py'
)
foreach ($path in $possiblePaths) {
    if (Test-Path $path) { $PYTHON_EXE = $path; break }
    if (Get-Command $path -ErrorAction SilentlyContinue) { $PYTHON_EXE = $path; break }
}

if (-not $PYTHON_EXE) {
    Write-Host 'Error: Python not found.' -ForegroundColor Red
    exit
}

# 2. Install Dependencies
Write-Host '1. Ensuring dependencies are installed...' -ForegroundColor Green
& $PYTHON_EXE -m pip install Flask Authlib requests pyOpenSSL --quiet

# 3. Launch App
Write-Host '2. Starting Flask Server...' -ForegroundColor Cyan
Write-Host '   Visit: https://localhost:7284' -ForegroundColor White

# Launch browser in 3 seconds
Start-Job -ScriptBlock { Start-Sleep -Seconds 3; Start-Process 'https://localhost:7284' } | Out-Null

# Start Flask (Blocks until Ctrl+C)
& $PYTHON_EXE app.py
