Set objShell = CreateObject("WScript.Shell")
objShell.Run "powershell -Command Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser", 0, True
objShell.Run "powershell -ExecutionPolicy Bypass -Command {""& {python manage.py create_backup}""}", 0, True
