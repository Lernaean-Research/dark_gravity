param(
  [Parameter(Mandatory=$true)][string]$DocxPath,
  [string]$ArxivDir = "arxiv",
  [string]$OutBody = "sections/99_pandoc_body.tex",
  [string]$MediaDir = "figures/pandoc_media"
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'ensure_pandoc.ps1')

if(-not (Test-Path -LiteralPath $DocxPath)){
  throw "DOCX not found: $DocxPath"
}
if(-not (Test-Path -LiteralPath $ArxivDir)){
  throw "arXiv dir not found: $ArxivDir"
}

try {
  $pandocExe = Ensure-Pandoc
} catch {
  throw "pandoc not available: $($_.Exception.Message)"
}

Push-Location $ArxivDir
try {
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutBody) | Out-Null
  New-Item -ItemType Directory -Force -Path $MediaDir | Out-Null

  # Ensure bibliography is available inside arxiv/ for packaging
  if(-not (Test-Path -LiteralPath "references.bib") -and (Test-Path -LiteralPath "..\references.bib")){
    Copy-Item -Force -LiteralPath "..\references.bib" -Destination "references.bib"
  }

  Write-Host "Generating arXiv LaTeX body via pandoc" -ForegroundColor Cyan
  Write-Host "  DOCX:  $DocxPath"
  Write-Host "  BODY:  $ArxivDir/$OutBody"
  Write-Host "  MEDIA: $ArxivDir/$MediaDir"

  # Create a LaTeX fragment (no standalone preamble) and avoid hard-wrapping lines.
  & $pandocExe "..\$DocxPath" -o $OutBody --extract-media=$MediaDir --wrap=none

  Write-Host "Done. main.tex will include sections/99_pandoc_body.tex automatically." -ForegroundColor Green
}
finally {
  Pop-Location
}
