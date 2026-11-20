# Opens a .pptx in PowerPoint and writes a PDF next to it.
#   powershell -File export_pdf.ps1 <path to .pptx>
param([string]$Path)
$full = (Resolve-Path $Path).Path
$pdf = [System.IO.Path]::ChangeExtension($full, ".pdf")
$pp = New-Object -ComObject PowerPoint.Application
try {
    $p = $pp.Presentations.Open($full, $true, $false, $false)
    $p.SaveAs($pdf, 32)
    $p.Close()
} finally {
    $pp.Quit()
}
Write-Output "wrote $pdf"
