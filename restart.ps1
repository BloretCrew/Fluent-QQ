# 停止正在运行的 Fluent-QQ 进程
Stop-Process -Name "Fluent-QQ" -Force -ErrorAction SilentlyContinue

# 等待一段时间确保进程完全终止
# Start-Sleep -Seconds 1

# 启动新的 Fluent-QQ 实例
Start-Process -FilePath "Fluent-QQ.exe"