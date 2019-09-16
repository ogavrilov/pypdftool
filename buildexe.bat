REM We use Python 3.7.3 & PyInstaller 3.4
REM --------------------------------------------------------------------------------
REM Change Current Directory to the location of this batch file
cd /d %~dp0
REM Checking and delete service files and folders
if exist "pypdftool.exe" del "pypdftool.exe"
if exist "dist/*.*" rd "dist" /s /Q
if exist "__pycache__/*.*" rd "__pycache__" /s /Q
if exist "build/*.*" rd "build" /s /Q
REM Assembly of one executable file
pyinstaller pypdftool.py --noconsole --onefile
REM Сopy the executable to the root directory
echo Expect a few seconds to complete all operations...
sleep 3
if exist "dist\pypdftool.exe" copy dist\pypdftool.exe pypdftool.exe
REM Checking and delete service files and folders
if exist "pypdftool.spec" del "pypdftool.spec"
if exist "__pycache__/*.*" rd "__pycache__" /s /Q
if exist "build/*.*" rd "build" /s /Q
if exist "dist/*.*" rd "dist" /s /Q