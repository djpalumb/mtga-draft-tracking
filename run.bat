@echo off
cd /d "%~dp0"

call conda activate mtga

python -m src.app.main_application