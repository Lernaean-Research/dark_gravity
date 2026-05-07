$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$arxivDir = Resolve-Path (Join-Path $PSScriptRoot '..')

# Ensure we have a .bbl (arXiv is happiest when you include it)
Push-Location $arxivDir
try {
  latexmk -pdf -interaction=nonstopmode main.tex
  $bbl = Join-Path $arxivDir 'build\main.bbl'
  if (!(Test-Path $bbl)) {
    throw "Expected .bbl not found at $bbl"
  }

  $staging = Join-Path $arxivDir 'build\_arxiv_upload_staging'
  if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
  New-Item -ItemType Directory -Path $staging | Out-Null

  Copy-Item -Force (Join-Path $arxivDir 'main.tex') $staging
  Copy-Item -Force (Join-Path $arxivDir 'preamble.tex') $staging
  Copy-Item -Force (Join-Path $arxivDir 'macros.tex') $staging
  Copy-Item -Force (Join-Path $arxivDir 'references.bib') $staging

  Copy-Item -Recurse -Force (Join-Path $arxivDir 'sections') (Join-Path $staging 'sections')
  Copy-Item -Recurse -Force (Join-Path $arxivDir 'figures') (Join-Path $staging 'figures')

  # Place .bbl at top-level with main.tex
  Copy-Item -Force $bbl (Join-Path $staging 'main.bbl')

  $zipPath = Join-Path $repoRoot 'arxiv_robust_upload.zip'
  if (Test-Path $zipPath) { Remove-Item -Force $zipPath }

  Compress-Archive -Path (Join-Path $staging '*') -DestinationPath $zipPath
  Write-Host "Wrote $zipPath"
} finally {
  Pop-Location
}
