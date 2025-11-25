' elevate.vbs
' Launches a command with elevated privileges.
'
' Usage:
'     cscript elevate.vbs "path\\to\\command.exe" "arg1" "arg2"

Set objArgs = WScript.Arguments
command = objArgs(0)
args = ""

If objArgs.Count > 1 Then
    For i = 1 To objArgs.Count - 1
        args = args & " """ & objArgs(i) & """"
    Next
End If

Set objShellApp = CreateObject("Shell.Application")
objShellApp.ShellExecute command, args, "", "runas", 1
