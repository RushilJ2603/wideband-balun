# Opens a .pptx in PowerPoint, saves it again as a PowerPoint file and
# writes a PDF next to it.
#   powershell -File export_pdf.ps1 <path to .pptx>
param([string]$Path)
$full = (Resolve-Path $Path).Path
$pdf = [System.IO.Path]::ChangeExtension($full, ".pdf")
$tmp = [System.IO.Path]::ChangeExtension($full, ".saved.pptx")
$pp = New-Object -ComObject PowerPoint.Application
try {
    $p = $pp.Presentations.Open($full, $false, $false, $false)
    $p.SaveAs($tmp, 24)
    $p.SaveAs($pdf, 32)
    $p.Close()
} finally {
    $pp.Quit()
}
Move-Item -Force $tmp $full
Write-Output "wrote $pdf"
