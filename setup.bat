::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: SOME USEFUL VB SCRIPTS:
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: VBSCRIPT TO Automatically check & get admin rights V2
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
@echo off
CLS
ECHO.
ECHO =============================
ECHO Running Admin shell
ECHO =============================

:init
setlocal DisableDelayedExpansion
set "batchPath=%~0"
for %%k in (%0) do set batchName=%%~nk
set "vbsGetPrivileges=%temp%\OEgetPriv_%batchName%.vbs"
setlocal EnableDelayedExpansion

:checkPrivileges
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto gotPrivileges ) else ( goto getPrivileges )

:getPrivileges
if '%1'=='ELEV' (echo ELEV & shift /1 & goto gotPrivileges)
ECHO.
ECHO **************************************
ECHO Invoking UAC for Privilege Escalation
ECHO **************************************

ECHO Set UAC = CreateObject^("Shell.Application"^) > "%vbsGetPrivileges%"
ECHO args = "ELEV " >> "%vbsGetPrivileges%"
ECHO For Each strArg in WScript.Arguments >> "%vbsGetPrivileges%"
ECHO args = args ^& strArg ^& " "  >> "%vbsGetPrivileges%"
ECHO Next >> "%vbsGetPrivileges%"
ECHO UAC.ShellExecute "!batchPath!", args, "", "runas", 1 >> "%vbsGetPrivileges%"
"%SystemRoot%\System32\WScript.exe" "%vbsGetPrivileges%" %*
exit /B

:gotPrivileges
setlocal & pushd .
cd /d %~dp0
if '%1'=='ELEV' (del "%vbsGetPrivileges%" 1>nul 2>nul  &  shift /1)
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: VBSCRIPT TO CREATE SOFT LINKS
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

set SCRIPT=create_shortcut.vbs
set EXECUTABLE=sms.exe
set PROGRAM_NAME=Student Management System
set INSTALL_PATH=C:\Program Files\SMS by Skylight

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%

echo sLinkFile = "%USERPROFILE%\Desktop\%PROGRAM_NAME%.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%INSTALL_PATH%\%EXECUTABLE%" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

echo sLinkFile_2 = "%USERPROFILE%\OneDrive\Desktop\%PROGRAM_NAME%.lnk" >> %SCRIPT%
echo Set oLink_2 = oWS.CreateShortcut(sLinkFile_2) >> %SCRIPT%
echo oLink_2.TargetPath = "%INSTALL_PATH%\%EXECUTABLE%" >> %SCRIPT%
echo oLink_2.Save >> %SCRIPT%

::oLink.Arguments
::oLink.Description
::oLink.HotKey
::oLink.IconLocation
::oLink.WindowStyle
::oLink.WorkingDirectory


::MOVE skylight_sms skylight_sms.zip
cscript /nologo create_shortcut.vbs
DEL create_shortcut.vbs

::start program
"%INSTALL_PATH%\%EXECUTABLE%"
:::::::::::::::::::::::::::::::::::::::::



:::::::::::::::::::::::::::::::::::::::::
:: first stab at an updater
:::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::
:: HELPFUL TOKEN
:: To get to dir of running batch script
:: cd /d %~dp0
:::::::::::::::::::::::::::::::::::::::::

@ECHO OFF
CLS
CD /d %USERPROFILE%

:::::::::::::::::::::::::::::::::::::::::
:: KILL sms.exe
:::::::::::::::::::::::::::::::::::::::::
ECHO stopping sms.exe ...
TASKKILL /F /IM sms.exe /T


:::::::::::::::::::::::::::::::::::::::::
:: BACKUP PREVIOUS VERSION
:::::::::::::::::::::::::::::::::::::::::
ECHO creating backup sms-bak\ ...
MKDIR %USERPROFILE%\sms-bak
move /Y sms sms-bak

ECHO recreating sms\
MKDIR %USERPROFILE%\sms


:::::::::::::::::::::::::::::::::::::::::::::
:: CScript to unzip files
:::::::::::::::::::::::::::::::::::::::::::::
ECHO creating cscript to unzip archive ...
REM This script upzip's files...

    > j_unzip.vbs ECHO '
    >> j_unzip.vbs ECHO ' UnZip a file script
    >> j_unzip.vbs ECHO '
    >> j_unzip.vbs ECHO ' It's a mess, I know!!!
    >> j_unzip.vbs ECHO '
    >> j_unzip.vbs ECHO.
    >> j_unzip.vbs ECHO ' Dim ArgObj, var1, var2
    >> j_unzip.vbs ECHO Set ArgObj = WScript.Arguments
    >> j_unzip.vbs ECHO.
    >> j_unzip.vbs ECHO If (Wscript.Arguments.Count ^> 0) Then
    >> j_unzip.vbs ECHO. var1 = ArgObj(0)
    >> j_unzip.vbs ECHO Else
    >> j_unzip.vbs ECHO. var1 = ""
    >> j_unzip.vbs ECHO End if
    >> j_unzip.vbs ECHO.
    >> j_unzip.vbs ECHO If (Wscript.Arguments.Count ^> 1) Then
    >> j_unzip.vbs ECHO. var2 = ArgObj(1)
    >> j_unzip.vbs ECHO Else
    >> j_unzip.vbs ECHO. var2 = ""
    >> j_unzip.vbs ECHO End if
    >> j_unzip.vbs ECHO.
    >> j_unzip.vbs ECHO If var1 = "" then
    >> j_unzip.vbs ECHO. strFileZIP = "example.zip"
    >> j_unzip.vbs ECHO Else
    >> j_unzip.vbs ECHO. strFileZIP = var1
    >> j_unzip.vbs ECHO End if
    >> j_unzip.vbs ECHO.
    >> j_unzip.vbs ECHO 'The location of the zip file.
    >> j_unzip.vbs ECHO REM Set WshShell = CreateObject("Wscript.Shell")
    >> j_unzip.vbs ECHO REM CurDir = WshShell.ExpandEnvironmentStrings("%%cd%%")
    >> j_unzip.vbs ECHO Dim sCurPath
    >> j_unzip.vbs ECHO sCurPath = CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(".")
    >> j_unzip.vbs ECHO strZipFile = sCurPath ^& "\" ^& strFileZIP
    >> j_unzip.vbs ECHO 'The folder the contents should be extracted to.
    >> j_unzip.vbs ECHO outFolder = sCurPath ^& "\"
    >> j_unzip.vbs ECHO.
    >> j_unzip.vbs ECHO If var2 = "" then
    >> j_unzip.vbs ECHO. outFolder = outFolder
    >> j_unzip.vbs ECHO Else
    >> j_unzip.vbs ECHO. outFolder = sCurPath ^& "\" ^& var2 ^& "\"
    >> j_unzip.vbs ECHO End if
    >> j_unzip.vbs ECHO.
    >> j_unzip.vbs ECHO. WScript.Echo ( "Extracting file " ^& strFileZIP)
    >> j_unzip.vbs ECHO.
    >> j_unzip.vbs ECHO Set objShell = CreateObject( "Shell.Application" )
    >> j_unzip.vbs ECHO Set objSource = objShell.NameSpace(strZipFile).Items()
    >> j_unzip.vbs ECHO Set objTarget = objShell.NameSpace(outFolder)
    >> j_unzip.vbs ECHO intOptions = 256
    >> j_unzip.vbs ECHO objTarget.CopyHere objSource, intOptions
    >> j_unzip.vbs ECHO.
    >> j_unzip.vbs ECHO. WScript.Echo ( "Extracted." )
    >> j_unzip.vbs ECHO.

:::::::::::::::::::::::::::::::::::::::::
:: UNZIP SMS.EXE
:::::::::::::::::::::::::::::::::::::::::
ECHO extracting sms.exe ...
CSCRIPT /B %USERPROFILE%\j_unzip.vbs sms.zip sms


:::::::::::::::::::::::::::::::::::::::::
:: CLEAN-UP
:::::::::::::::::::::::::::::::::::::::::
ECHO removing temporary files ...
DEL %USERPROFILE%\j_unzip.vbs
DEL %USERPROFILE%\sms.zip


:::::::::::::::::::::::::::::::::::::::::
:: START sms.exe
:::::::::::::::::::::::::::::::::::::::::
ECHO restarting sms.exe ...
START %USERPROFILE%\sms\sms.exe

