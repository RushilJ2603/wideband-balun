# Turns off Windows power throttling (efficiency mode) for running openEMS
# processes, which otherwise run on the efficiency cores at low clock when
# started from a terminal without a window.
#   powershell -File no_throttle.ps1
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class Throttle {
    [StructLayout(LayoutKind.Sequential)]
    public struct State { public uint Version; public uint ControlMask; public uint StateMask; }
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool SetProcessInformation(IntPtr h, int cls, ref State s, int size);
}
"@
foreach ($p in Get-Process openEMS -ErrorAction SilentlyContinue) {
    $s = New-Object Throttle+State
    $s.Version = 1
    $s.ControlMask = 1
    $s.StateMask = 0
    $ok = [Throttle]::SetProcessInformation($p.Handle, 4, [ref]$s, 12)
    Write-Output "openEMS $($p.Id): throttling off = $ok"
}
