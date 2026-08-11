@echo off
cd /d "%~dp0"

REM Find Conda
if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat"
) else if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
    call "%USERPROFILE%\anaconda3\Scripts\activate.bat"
) else (
    echo.
    echo ERROR: Could not find Miniconda or Anaconda.
    echo Please install Miniconda or Anaconda first.
    echo.
    pause
    exit /b 1
)

REM Initialize Conda
call conda activate base

REM Check for Mamba
where mamba >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Mamba is not installed. Installing it now...
    echo.

    conda install -n base -c conda-forge mamba -y

    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install Mamba.
        pause
        exit /b 1
    )
)

REM Create environment
echo.
echo Creating environment...
mamba env create -f env.yaml

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to create the environment.
    pause
    exit /b 1
)

echo.
echo Environment created successfully!
pause