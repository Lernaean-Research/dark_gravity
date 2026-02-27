param(
  [ValidateSet('None','User','Machine')][string]$Persist = 'None',
  [switch]$PrintVersion
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-PandocExe {
  [CmdletBinding()]
  param()

  # 1) PATH (fast)
  $cmd = Get-Command pandoc -ErrorAction SilentlyContinue
  if ($cmd -and $cmd.Source -and (Test-Path -LiteralPath $cmd.Source)) {
    return (Resolve-Path -LiteralPath $cmd.Source).Path
  }

  # 2) Windows uninstall registry (reliable)
  $keys = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
  )
  $apps = foreach ($k in $keys) { Get-ItemProperty $k -ErrorAction SilentlyContinue }
  $pandoc = $apps |
    Where-Object { $_.DisplayName -match '^Pandoc(\s|$)' -or $_.DisplayName -match '^Pandoc\b' } |
    Sort-Object { $_.DisplayVersion } -Descending |
    Select-Object -First 1
  if ($pandoc -and $pandoc.InstallLocation) {
    $exe = Join-Path $pandoc.InstallLocation 'pandoc.exe'
    if (Test-Path -LiteralPath $exe) {
      return (Resolve-Path -LiteralPath $exe).Path
    }
  }

  # 3) Common locations
  $candidates = @(
    Join-Path $env:LOCALAPPDATA 'Pandoc\pandoc.exe',
    'C:\Program Files\Pandoc\pandoc.exe',
    'C:\Program Files (x86)\Pandoc\pandoc.exe'
  )
  foreach ($p in $candidates) {
    if ($p -and (Test-Path -LiteralPath $p)) {
      return (Resolve-Path -LiteralPath $p).Path
    }
  }

  return $null
}

function Add-ToPath {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory=$true)][string]$Dir,
    [Parameter(Mandatory=$true)][ValidateSet('User','Machine')][string]$Scope
  )

  $current = [Environment]::GetEnvironmentVariable('Path', $Scope)
  if ($null -eq $current) { $current = '' }
  $parts = $current -split ';' | Where-Object { $_ -and $_.Trim() -ne '' }
  if ($parts -contains $Dir) { return $false }
  [Environment]::SetEnvironmentVariable('Path', (($parts + $Dir) -join ';'), $Scope)
  return $true
}

function Ensure-Pandoc {
  [CmdletBinding()]
  param(
    [ValidateSet('None','User','Machine')][string]$Persist = 'None'
  )

  $pandocExe = Get-PandocExe
  if (-not $pandocExe) {
    throw "pandoc.exe not found. Install Pandoc (e.g., winget install JohnMacFarlane.Pandoc) and reopen the terminal."
  }

  # Always harden the current session.
  $pandocDir = Split-Path -Parent $pandocExe
  $pathParts = ($env:Path -split ';') | Where-Object { $_ -and $_.Trim() -ne '' }
  if (-not ($pathParts -contains $pandocDir)) {
    $env:Path = ($env:Path.TrimEnd(';') + ';' + $pandocDir)
  }

  if ($Persist -ne 'None') {
    if ($Persist -eq 'Machine') {
      [void](Add-ToPath -Dir $pandocDir -Scope 'Machine')
    } elseif ($Persist -eq 'User') {
      [void](Add-ToPath -Dir $pandocDir -Scope 'User')
    }
  }

  return $pandocExe
}

# If run directly (not dot-sourced), behave like a small utility.
if ($MyInvocation.InvocationName -ne '.') {
  $exe = Ensure-Pandoc -Persist $Persist
  Write-Host "pandoc resolved to: $exe" -ForegroundColor DarkGray
  if ($PrintVersion) {
    & $exe --version | Select-Object -First 3 | ForEach-Object { Write-Host $_ }
  }
}
