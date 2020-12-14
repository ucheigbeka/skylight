@ECHO OFF
ECHO.
:::::::::::::::::::::::::::::::::::::::::
:: PRINT DATE & TIME, CD TO USER_HOME
:::::::::::::::::::::::::::::::::::::::::
ECHO %date:~0,2%/%date:~3,2%/%date:~-4%, %time:~0,2%:%time:~3,2%:%time:~6,2%
CD /D %USERPROFILE%

:::::::::::::::::::::::::::::::::::::::::
:: KILL sms.exe
:::::::::::::::::::::::::::::::::::::::::
ECHO stopping sms.exe ...
TASKKILL /F /IM sms.exe

:::::::::::::::::::::::::::::::::::::::::
:: REMOVE OLD sms DIR
:::::::::::::::::::::::::::::::::::::::::
ECHO removing sms\
RMDIR /S /Q sms

:::::::::::::::::::::::::::::::::::::::::
:: ERROR CHECKING 1
:::::::::::::::::::::::::::::::::::::::::
ECHO find sms ...
DIR | FINDSTR sms

:::::::::::::::::::::::::::::::::::::::::
:: MOVE sms_temp TO sms
:::::::::::::::::::::::::::::::::::::::::
ECHO moving sms_temp\ to sms\
MOVE /Y sms_temp sms

ECHO cd to sms ...
CD /d %USERPROFILE%\sms

:::::::::::::::::::::::::::::::::::::::::
:: ERROR CHECKING 2
:::::::::::::::::::::::::::::::::::::::::
ECHO find sms.exe ...
DIR | FINDSTR sms.exe

:::::::::::::::::::::::::::::::::::::::::
:: START sms.exe
:::::::::::::::::::::::::::::::::::::::::
ECHO restarting sms.exe ...
START sms.exe
