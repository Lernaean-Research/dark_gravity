param(
  [string]$ArxivDir = "arxiv",
  [string]$ZipPath = "arxiv_submission.zip"
)

$ErrorActionPreference = 'Stop'

if(-not (Test-Path -LiteralPath $ArxivDir)){
  throw "Not found: $ArxivDir"
}

Push-Location $ArxivDir

try {
  $tmp = Join-Path $PWD "_package_tmp"
  if(Test-Path -LiteralPath $tmp){ Remove-Item -Recurse -Force -LiteralPath $tmp }
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null

  Copy-Item -Force -LiteralPath "main.tex" -Destination (Join-Path $tmp "main.tex")
  Copy-Item -Recurse -Force -LiteralPath "sections" -Destination (Join-Path $tmp "sections")
  Copy-Item -Recurse -Force -LiteralPath "figures" -Destination (Join-Path $tmp "figures")

  # arXiv bib is project-local only (no fallback to repo-root bib).
  if(-not (Test-Path -LiteralPath "references.bib")){
    throw "Missing arXiv bibliography: $ArxivDir/references.bib"
  }
  Copy-Item -Force -LiteralPath "references.bib" -Destination (Join-Path $tmp "references.bib")

  if(Test-Path -LiteralPath "build"){
    Write-Host "Note: build/ exists but is not packaged." -ForegroundColor DarkGray
  }

  $zipFull = Join-Path (Resolve-Path ..) $ZipPath
  if(Test-Path -LiteralPath $zipFull){ Remove-Item -Force -LiteralPath $zipFull }

  Write-Host "Creating zip: $zipFull" -ForegroundColor Cyan
  Compress-Archive -Path (Join-Path $tmp '*') -DestinationPath $zipFull

  Remove-Item -Recurse -Force -LiteralPath $tmp
  Write-Host "Done." -ForegroundColor Green
}
finally {
  Pop-Location
}
