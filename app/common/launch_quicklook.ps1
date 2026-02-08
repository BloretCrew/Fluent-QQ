function Launch-QuickLook {
    param (
        [string]$TargetFile
    )

    $ErrorActionPreference = "Stop"
    $logFile = "$env:TEMP\QuickLookLaunch.log"

    try {
        $pkg = Get-AppxPackage *QuickLook*
        if ($null -eq $pkg) {
            throw "QuickLook 未安装或包名不匹配，请确认已正确安装 Microsoft Store 版本"
        }
        
        # In case multiple versions/architectures are found, pick the first one
        if ($pkg -is [array]) {
            $pkg = $pkg | Select-Object -First 1
        }

        $qlPath = $pkg.InstallLocation + "\Package\QuickLook.exe"

        if (-not (Test-Path $qlPath)) {
            # Log this specific issue but throw generic or specific error
            throw "QuickLook executable not found at: $qlPath"
        }

        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "$timestamp INFO: Resolved QuickLook path: $qlPath" | Out-File -FilePath $logFile -Append -Encoding utf8

        if (-not [string]::IsNullOrEmpty($TargetFile)) {
            "$timestamp INFO: Previewing file: $TargetFile" | Out-File -FilePath $logFile -Append -Encoding utf8
            & $qlPath $TargetFile
        } else {
            "$timestamp INFO: Launching QuickLook (no file)" | Out-File -FilePath $logFile -Append -Encoding utf8
            & $qlPath
        }

    } catch {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "$timestamp ERROR: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
        Write-Error $_
        exit 1
    }
}

# Execute function with arguments passed to script
Launch-QuickLook -TargetFile $args[0]
