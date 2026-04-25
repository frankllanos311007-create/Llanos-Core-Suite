Set WshShell = CreateObject("WScript.Shell")
' Obtener la ruta del directorio donde está este script
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' Comando para ejecutar el monitor de forma oculta
strCommand = "python """ & strPath & "\monitor.py"""
WshShell.Run strCommand, 0, False
