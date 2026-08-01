' Taskbar Pets — Silent Launcher (No Command Prompt Window)
Set WshShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath
WshShell.Run "pythonw """ & strPath & "\main.py""", 0, False
