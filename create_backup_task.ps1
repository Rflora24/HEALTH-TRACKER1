$Action = New-ScheduledTaskAction -Execute "python" -Argument "manage.py create_backup"
$Trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName "Health Project Backup" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force
