param(
  [string]$LinksDir = "toy_models/out_cluster_fetch/bullet_cluster",
  [string]$OutRoot = "toy_models/data/bullet_cluster/raw/heasarc",
  [string[]]$OnlyObsIds = @(),
  [ValidateSet("chanmaster","xmmmaster")]
  [string[]]$OnlyCatalogs = @(),
  [switch]$DoDownload,
  [bool]$DryRun = $true
)

$ErrorActionPreference = "Stop"

# Avoid AWS CLI trying IMDS (can cause delays on desktops)
$env:AWS_EC2_METADATA_DISABLED = "true"

function Resolve-AwsCli {
  $cmd = Get-Command aws -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }

  $candidates = @(
    "$env:ProgramFiles\Amazon\AWSCLIV2\aws.exe",
    "$env:LocalAppData\Programs\Amazon\AWSCLIV2\aws.exe"
  )
  foreach ($p in $candidates) {
    if (Test-Path $p) { return $p }
  }

  throw "AWS CLI not found. Install AWS CLI v2 or ensure aws.exe is on PATH."
}

function Get-ObsIdFromS3Path([string]$s3) {
  # expects trailing /<obsid>/
  $s = $s3.TrimEnd('/')
  return ($s.Split('/') | Select-Object -Last 1)
}

function Invoke-Sync([string]$awsExe, [string]$s3, [string]$dest) {
  New-Item -ItemType Directory -Force -Path $dest | Out-Null

  $args = @("s3", "sync", $s3, $dest, "--no-sign-request")
  if ($DryRun) { $args += "--dryrun" }

  $cmdLine = "& `"$awsExe`" " + ($args | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' '
  Write-Host $cmdLine

  if ($DoDownload) {
    & $awsExe @args
  }
}

$awsExe = Resolve-AwsCli
Write-Host "Using AWS CLI: $awsExe"
Write-Host "LinksDir: $LinksDir"
Write-Host "OutRoot:  $OutRoot"
if ($OnlyObsIds.Count -gt 0) { Write-Host "OnlyObsIds: $($OnlyObsIds -join ', ')" }
if ($OnlyCatalogs.Count -gt 0) { Write-Host "OnlyCatalogs: $($OnlyCatalogs -join ', ')" }
Write-Host "DoDownload: $DoDownload  DryRun: $DryRun"

$chanLinks = Join-Path $LinksDir "chanmaster_links.csv"
$xmmLinks = Join-Path $LinksDir "xmmmaster_links.csv"

if (!(Test-Path $chanLinks)) { throw "Missing: $chanLinks" }
if (!(Test-Path $xmmLinks)) { throw "Missing: $xmmLinks" }

$rows = @()
$rows += Import-Csv $chanLinks
$rows += Import-Csv $xmmLinks

foreach ($r in $rows) {
  $s3 = [string]$r.aws
  if ([string]::IsNullOrWhiteSpace($s3)) { continue }

  $obsid = Get-ObsIdFromS3Path $s3
  $cat = ([string]$r.catalog).ToLowerInvariant()

  if ($OnlyCatalogs.Count -gt 0 -and ($OnlyCatalogs -notcontains $cat)) { continue }
  if ($OnlyObsIds.Count -gt 0 -and ($OnlyObsIds -notcontains $obsid)) { continue }

  if ($cat -eq "chanmaster") {
    $dest = Join-Path $OutRoot (Join-Path "chandra" $obsid)
  } elseif ($cat -eq "xmmmaster") {
    $dest = Join-Path $OutRoot (Join-Path "xmm" $obsid)
  } else {
    $dest = Join-Path $OutRoot (Join-Path $cat $obsid)
  }

  Invoke-Sync $awsExe $s3 $dest
}

Write-Host "Done."
Write-Host "Tip: re-run with -DoDownload -DryRun:$false to actually download."