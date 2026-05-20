@echo off

pip install -r requirements.txt

pip install pyinstaller

python -m PyInstaller main.py ^
 --noconsole ^
 --onefile ^
 --icon=icon.ico ^
 --name SmartHomeBrowser

python -m PyInstaller show_browser.py ^
 --noconsole ^
 --onefile ^
 --name ShowBrowser

pause