[CmdletBinding()]
param(
    [switch]$Recreate,
    [switch]$SkipSmokeTest,
    [string]$Python = "py"
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Write-Info([string]$msg) { Write-Host "[setup] $msg" }

$repoRoot = Split-Path -Parent $PSCommandPath | Split-Path -Parent
Set-Location $repoRoot

$venvDir = Join-Path $repoRoot '.venv'
$venvPython = Join-Path $venvDir 'Scripts/python.exe'
$req = Join-Path $repoRoot 'requirements.txt'

if (-not (Test-Path $req)) {
    throw "requirements.txt not found at $req"
}

if ($Recreate -and (Test-Path $venvDir)) {
    Write-Info "Removing existing .venv (Recreate)"
    Remove-Item -Recurse -Force $venvDir
}

if (-not (Test-Path $venvPython)) {
    Write-Info "Creating virtual environment at .venv"

    $venvCmd = @($Python, '-m', 'venv', '.venv')
    try {
        & $venvCmd[0] $venvCmd[1..($venvCmd.Length-1)]
    }
    catch {
        Write-Info "Failed using '$Python'. Falling back to 'python'."
        & python -m venv .venv
    }
}

if (-not (Test-Path $venvPython)) {
    throw "Virtualenv created but python not found at $venvPython"
}

# Occasionally, interrupted pip upgrades can leave behind stray `~ip*` directories
# that trigger "Ignoring invalid distribution" warnings.
$badPipGlobs = @(
    Join-Path $venvDir 'Lib/site-packages/~ip*'
)
foreach ($globPath in $badPipGlobs) {
    $matches = Get-ChildItem -Path $globPath -ErrorAction SilentlyContinue
    if ($matches) {
        Write-Info "Removing stray pip leftovers: $globPath"
        Remove-Item -Recurse -Force $globPath
    }
}

Write-Info "Upgrading pip tooling"
& $venvPython -m pip install --upgrade pip setuptools wheel

Write-Info "Installing requirements.txt"
& $venvPython -m pip install -r $req

if (-not $SkipSmokeTest) {
    Write-Info "Smoke test: importing key packages"
    & $venvPython -c "import sys; import numpy, matplotlib, astropy, astroquery; print('python',sys.executable); print('numpy',numpy.__version__); print('matplotlib',matplotlib.__version__); print('astropy',astropy.__version__); print('astroquery',astroquery.__version__)"
}

Write-Info "Done. Use this interpreter for all commands: $venvPython"
Write-Info "(Optional) Activate in your shell: .\.venv\Scripts\Activate.ps1"
