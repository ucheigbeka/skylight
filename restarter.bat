@ECHO OFF
ECHO.
ECHO %date:~0,2%/%date:~3,2%/%date:~-4%, %time:~0,2%:%time:~3,2%:%time:~6,2%
CD /d %USERPROFILE%

:::::::::::::::::::::::::::::::::::::::::
:: KILL sms.exe
:::::::::::::::::::::::::::::::::::::::::
ECHO stopping sms.exe ...
TASKKILL /F /IM sms.exe


:::::::::::::::::::::::::::::::::::::::::
:: BACKUP PREVIOUS VERSION
:::::::::::::::::::::::::::::::::::::::::
ECHO removing sms\
RMDIR /S /Q sms

ECHO recreating sms\
MOVE /Y sms_temp sms


:::::::::::::::::::::::::::::::::::::::::
:: START sms.exe
:::::::::::::::::::::::::::::::::::::::::
ECHO restarting sms.exe ...
START %USERPROFILE%\sms\sms.exe