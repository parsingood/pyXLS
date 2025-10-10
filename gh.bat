@echo off
chcp 65001

cd /d C:\ivanm\pyXLS

:: Пита потребителя за описание на промените
set /p msg=Въведи описание на промените: 

git add .
git commit -m "%msg%"
git push

echo.
echo ✅ Промените са качени успешно в GitHub!
pause
