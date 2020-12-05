@ECHO OFF
CLS
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