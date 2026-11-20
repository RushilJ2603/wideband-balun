# Opens a .docx in Word, updates the table of contents and other fields,
# saves it and writes a PDF next to it.
#   powershell -File export_pdf.ps1 <path to .docx>
param([string]$Path)
$full = (Resolve-Path $Path).Path
$pdf = [System.IO.Path]::ChangeExtension($full, ".pdf")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($full)
    foreach ($t in $doc.TablesOfContents) { $t.Update() }
    $doc.Fields.Update() | Out-Null
    $doc.Save()
    $doc.SaveAs([ref]$pdf, [ref]17)
    $doc.Close()
} finally {
    $word.Quit()
}
Write-Output "wrote $pdf"
