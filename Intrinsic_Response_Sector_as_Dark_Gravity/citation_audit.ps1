# Extract all BibTeX keys from references.bib
$bib_keys = @()
Select-String -Path references.bib -Pattern "^@\w+\{([^,]+)" | ForEach-Object {
    $bib_keys += $_.Matches[0].Groups[1].Value
}
$bib_keys = $bib_keys | Sort-Object -Unique

# Extract all citation keys from manuscript_overleaf.tex
$tex_keys = @()
Select-String -Path manuscript_overleaf.tex -Pattern "\\cite[pt]*\{([^}]+)\}" | ForEach-Object {
    $citations = $_.Matches.Groups[1].Value
    $citations -split ',' | ForEach-Object {
        $tex_keys += $_.Trim()
    }
}
$tex_keys = $tex_keys | Sort-Object -Unique

# Find missing keys (in .tex but not in .bib)
$missing_in_bib = @()
foreach ($key in $tex_keys) {
    if ($bib_keys -notcontains $key) {
        $missing_in_bib += $key
    }
}

# Find unused keys (in .bib but not in .tex)
$unused_in_bib = @()
foreach ($key in $bib_keys) {
    if ($tex_keys -notcontains $key) {
        $unused_in_bib += $key
    }
}

# Output reports
Write-Output "=== CITATION AUDIT REPORT ===" | Tee-Object -FilePath citation_audit_report.txt
Write-Output "" | Tee-Object -FilePath citation_audit_report.txt -Append
Write-Output "Total BibTeX entries in references.bib: $($bib_keys.Count)" | Tee-Object -FilePath citation_audit_report.txt -Append
Write-Output "Total unique citations in manuscript_overleaf.tex: $($tex_keys.Count)" | Tee-Object -FilePath citation_audit_report.txt -Append
Write-Output "" | Tee-Object -FilePath citation_audit_report.txt -Append

if ($missing_in_bib.Count -gt 0) {
    Write-Output "=== MISSING IN .BIB (cited in .tex but not in .bib) ===" | Tee-Object -FilePath citation_audit_report.txt -Append
    $missing_in_bib | Tee-Object -FilePath citation_audit_report.txt -Append
} else {
    Write-Output "✓ No missing references - all citations have corresponding .bib entries" | Tee-Object -FilePath citation_audit_report.txt -Append
}

Write-Output "" | Tee-Object -FilePath citation_audit_report.txt -Append

if ($unused_in_bib.Count -gt 0) {
    Write-Output "=== UNUSED IN .TEX (52 - $($tex_keys.Count) = $($unused_in_bib.Count) unused) ===" | Tee-Object -FilePath citation_audit_report.txt -Append
    $unused_in_bib | Tee-Object -FilePath citation_audit_report.txt -Append
}

Write-Output "" | Tee-Object -FilePath citation_audit_report.txt -Append
Write-Output "=== SECTION 9 CITATIONS ONLY ===" | Tee-Object -FilePath citation_audit_report.txt -Append

# Extract Section 9 content
$section9_start = (Select-String -Path manuscript_overleaf.tex -Pattern "\\section\{Discussion\}" | Select-Object -First 1).LineNumber
$section10_start = (Select-String -Path manuscript_overleaf.tex -Pattern "\\section\{Conclusion\}" | Select-Object -First 1).LineNumber

# Extract lines in Section 9
$section9_content = Get-Content manuscript_overleaf.tex | Select-Object -Index (($section9_start - 1)..($section10_start - 2))

# Extract citations from Section 9
$section9_citations = @()
$section9_content | ForEach-Object {
    if ($_ -match "\\cite[pt]*\{([^}]+)\}") {
        $citations = $matches[1]
        $citations -split ',' | ForEach-Object {
            $section9_citations += $_.Trim()
        }
    }
}
$section9_citations = $section9_citations | Sort-Object -Unique

Write-Output "Citation keys in Section 9:" | Tee-Object -FilePath citation_audit_report.txt -Append
$section9_citations | Tee-Object -FilePath citation_audit_report.txt -Append
Write-Output "Total unique citations in Section 9: $($section9_citations.Count)" | Tee-Object -FilePath citation_audit_report.txt -Append
