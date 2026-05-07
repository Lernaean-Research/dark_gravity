param(
  [switch]$Clean
)

$ErrorActionPreference = 'Stop'

Push-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Pop-Location | Out-Null

$root = Resolve-Path (Join-Path $PSScriptRoot '..')
Push-Location $root
try {
  if ($Clean) {
    if (Test-Path 'build') { Remove-Item -Recurse -Force 'build' }
  }
  latexmk -pdf -interaction=nonstopmode main.tex
} finally {
  Pop-Location
}
