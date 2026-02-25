param(
  [string]$SourceToyModels = "D:\#Documents\#Publication\Spacetime_Mechanics\toy_models",
  [string]$DestToyModels = "$(Join-Path $PSScriptRoot '..\toy_models')",
  [int]$MaxBytes = 5000000
)

$wantExt = @(
  '.py','.md','.tex','.ps1','.ipynb',
  '.txt','.csv','.tsv',
  '.json','.yml','.yaml','.toml','.bib','.ini'
)

if(-not (Test-Path -LiteralPath $SourceToyModels)){
  throw "SourceToyModels not found: $SourceToyModels"
}
if(-not (Test-Path -LiteralPath $DestToyModels)){
  throw "DestToyModels not found: $DestToyModels"
}

Write-Host "Syncing methodology/provenance files" -ForegroundColor Cyan
Write-Host "  From: $SourceToyModels"
Write-Host "  To:   $DestToyModels"
Write-Host "  Max:  $MaxBytes bytes"

$copied = 0
$skippedLarge = 0

Get-ChildItem -LiteralPath $SourceToyModels -File -Recurse -Force |
  Where-Object { $_.FullName -notmatch '\\__pycache__\\' } |
  ForEach-Object {
    $rel = $_.FullName.Substring($SourceToyModels.Length).TrimStart('\\')
    $ext = [IO.Path]::GetExtension($_.Name).ToLowerInvariant()
    if(-not ($wantExt -contains $ext)) { return }
    if($_.Length -gt $MaxBytes) { $script:skippedLarge++; return }

    $dst = Join-Path $DestToyModels $rel
    if(Test-Path -LiteralPath $dst) { return }

    $dir = Split-Path -Parent $dst
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Copy-Item -LiteralPath $_.FullName -Destination $dst -Force
    $script:copied++
  }

Write-Host "Copied: $copied" -ForegroundColor Green
Write-Host "Skipped (too large): $skippedLarge" -ForegroundColor Yellow
