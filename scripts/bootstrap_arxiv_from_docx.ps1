param(
  [string]$DocxPath = "",
  [string]$ArxivDir = "arxiv",
  [string]$BodyTex = "sections/99_pandoc_body.tex",
  [string]$MediaDir = "figures/pandoc_media",
  [string]$PandocPath = ""
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'ensure_pandoc.ps1')

if(-not $DocxPath){
  $manifestPath = Join-Path $ArxivDir 'SOURCE_MANIFEST.json'
  if(-not (Test-Path -LiteralPath $manifestPath)){
    throw "DocxPath not provided and manifest not found: $manifestPath"
  }
  $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
  $DocxPath = $manifest.source_of_truth.docx_path
}

if(-not (Test-Path -LiteralPath $DocxPath)){
  throw "DOCX not found: $DocxPath"
}

$docxAbsPath = (Resolve-Path -LiteralPath $DocxPath).Path

$pandocExe = $null
if($PandocPath -and (Test-Path -LiteralPath $PandocPath)){
  $pandocExe = (Resolve-Path -LiteralPath $PandocPath).Path
} else {
  $pandocExe = Ensure-Pandoc
}

if(-not (Test-Path -LiteralPath $ArxivDir)){
  throw "ArxivDir not found: $ArxivDir"
}

Push-Location $ArxivDir
try {
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $BodyTex) | Out-Null
  New-Item -ItemType Directory -Force -Path $MediaDir | Out-Null

  Write-Host "Using pandoc: $pandocExe" -ForegroundColor DarkGray
  Write-Host "Converting DOCX -> LaTeX body (committed)" -ForegroundColor Cyan
  Write-Host "  DOCX:  $DocxPath"
  Write-Host "  TEX:   $ArxivDir/$BodyTex"
  Write-Host "  MEDIA: $ArxivDir/$MediaDir"

  & $pandocExe $docxAbsPath -f docx -t latex -o $BodyTex --extract-media=$MediaDir --wrap=none

  # Minimal normalization pass for a couple of known Pandoc unicode artifacts in math mode.
  # Keep this list short and surgical; the goal is stable compilation, not re-authoring.
  $body = Get-Content -LiteralPath $BodyTex -Raw -Encoding utf8
  $body = $body.Replace('{\overset{ˉ}{T}}_{\mu\nu}', '\overline{T}_{\mu\nu}')
  $body = $body.Replace('Tʳᵉˢᵖ_{\mu\nu}', 'T^{resp}_{\mu\nu}')
  $body = $body.Replace('T̄', '\ensuremath{\overline{T}}')

  # Unicode superscript-minus sequences commonly show up in units (e.g., m⁻², s⁻¹).
  # Normalize them to TeX-safe math exponents.
  $body = $body.Replace('⁻¹', '\ensuremath{^{-1}}')
  $body = $body.Replace('⁻²', '\ensuremath{^{-2}}')
  $body = $body.Replace('⁻³', '\ensuremath{^{-3}}')
  $body = $body.Replace('⁻⁴', '\ensuremath{^{-4}}')
  $body = $body.Replace('⁻⁵', '\ensuremath{^{-5}}')

  # Scientific notation sometimes appears as 10¹⁹ (unicode superscripts).
  # Convert 10ⁿ -> \ensuremath{10^{n}}.
  $supDigits = @{
    '⁰' = '0'
    '¹' = '1'
    '²' = '2'
    '³' = '3'
    '⁴' = '4'
    '⁵' = '5'
    '⁶' = '6'
    '⁷' = '7'
    '⁸' = '8'
    '⁹' = '9'
  }
  $body = [regex]::Replace($body, '10([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', {
    param($m)
    $digits = -join ($m.Groups[1].Value.ToCharArray() | ForEach-Object { $supDigits[[string]$_] })
    "\ensuremath{10^{${digits}}}"
  })
  Set-Content -LiteralPath $BodyTex -Value $body -Encoding utf8
}
finally {
  Pop-Location
}

Write-Host "Done. main.tex will auto-include $BodyTex if present." -ForegroundColor Green

