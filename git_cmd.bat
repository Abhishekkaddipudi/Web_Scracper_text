@echo off
setlocal enabledelayedexpansion

echo Extracting commit message from novel_title.txt...

REM Read the first line of the file
set "commit_message="
for /f "usebackq delims=" %%i in ("novel_title.txt") do (
    set "commit_message=%%i"
    goto commit_done
)

:commit_done
if "%commit_message%"=="" (
    echo ❌ No commit message found in novel_title.txt
    pause
    exit /b 1
)

echo Commit message: %commit_message%

echo Adding files...
git add .

echo Committing changes...
git commit -m "%commit_message%"

echo Pushing to the remote repository...
git push

echo Done!
pause
