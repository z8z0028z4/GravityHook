@echo off
REM GravityHook Installation Script for Windows
REM Usage: install.bat C:\path\to\target\project

setlocal enabledelayedexpansion

echo.
echo ================================================
echo   GravityHook Installer (Windows)
echo ================================================
echo.

REM Check if target directory is provided
if "%~1"=="" (
    set /p TARGET_DIR="Enter target project directory: "
) else (
    set TARGET_DIR=%~1
)

REM Remove trailing backslash if present
if "!TARGET_DIR:~-1!"=="\" set TARGET_DIR=!TARGET_DIR:~0,-1!

REM Validate target directory
if not exist "!TARGET_DIR!" (
    echo.
    echo Directory does not exist: !TARGET_DIR!
    set /p CREATE_DIR="Create it? (y/n): "
    if /i "!CREATE_DIR!"=="y" (
        mkdir "!TARGET_DIR!"
        echo [OK] Created directory: !TARGET_DIR!
    ) else (
        echo Installation cancelled.
        exit /b 1
    )
)

set AGENT_DIR=!TARGET_DIR!\.agent

echo.
echo Target project: !TARGET_DIR!
echo Installing GravityHook to: !AGENT_DIR!
echo.

REM Create .agent directory structure
echo Creating directory structure...
if not exist "!AGENT_DIR!" mkdir "!AGENT_DIR!"
if not exist "!AGENT_DIR!\rules" mkdir "!AGENT_DIR!\rules"
if not exist "!AGENT_DIR!\workflows" mkdir "!AGENT_DIR!\workflows"
if not exist "!AGENT_DIR!\skills" mkdir "!AGENT_DIR!\skills"
echo [OK] Created .agent\ directories
echo.

REM Get script directory (where install.bat is located)
set SCRIPT_DIR=%~dp0
REM Remove trailing backslash
if "!SCRIPT_DIR:~-1!"=="\" set SCRIPT_DIR=!SCRIPT_DIR:~0,-1!

REM Copy templates
echo Copying templates...

if not exist "!AGENT_DIR!\MISSION_STATE.md" (
    copy "!SCRIPT_DIR!\templates\MISSION_STATE.md" "!AGENT_DIR!\" >nul
    echo [OK] Copied MISSION_STATE.md
) else (
    echo [WARN] MISSION_STATE.md already exists, skipping
)

if not exist "!AGENT_DIR!\vibe_check.md" (
    copy "!SCRIPT_DIR!\templates\vibe_check.md" "!AGENT_DIR!\" >nul
    echo [OK] Copied vibe_check.md
) else (
    echo [WARN] vibe_check.md already exists, skipping
)

if not exist "!AGENT_DIR!\rules\claw_rules.md" (
    copy "!SCRIPT_DIR!\templates\claw_rules.md" "!AGENT_DIR!\rules\" >nul
    echo [OK] Copied claw_rules.md to .agent\rules\
) else (
    echo [WARN] claw_rules.md already exists, skipping
)

if not exist "!AGENT_DIR!\skills\SKILL_INDEX.md" (
    copy "!SCRIPT_DIR!\templates\SKILL_INDEX.md" "!AGENT_DIR!\skills\" >nul
    echo [OK] Copied SKILL_INDEX.md to .agent\skills\
) else (
    echo [WARN] SKILL_INDEX.md already exists, skipping
)

echo.
echo [INFO] SYSTEM_PROMPT.md is available in GravityHook\templates\
echo [INFO] Copy its content to your OpenClaw Project's Custom Instructions

REM Copy Python logic modules (optional)
echo.
set /p COPY_LOGIC="Copy Python logic modules to project? (y/n): "
if /i "!COPY_LOGIC!"=="y" (
    if not exist "!TARGET_DIR!\gravityhook_logic" mkdir "!TARGET_DIR!\gravityhook_logic"
    xcopy /E /I /Y "!SCRIPT_DIR!\logic" "!TARGET_DIR!\gravityhook_logic" >nul
    echo [OK] Copied Python modules to gravityhook_logic\
    
    REM Copy requirements.txt
    if not exist "!TARGET_DIR!\requirements.txt" (
        copy "!SCRIPT_DIR!\requirements.txt" "!TARGET_DIR!\" >nul
        echo [OK] Copied requirements.txt
    ) else (
        echo [WARN] requirements.txt exists. Add these dependencies:
        type "!SCRIPT_DIR!\requirements.txt"
    )
)

REM Summary
echo.
echo ========================================
echo  GravityHook installed successfully!
echo ========================================
echo.
echo Created structure:
echo   !AGENT_DIR!\
echo   ├── MISSION_STATE.md
echo   ├── vibe_check.md
echo   ├── rules\
echo   │   └── claw_rules.md
echo   ├── workflows\
echo   └── skills\
echo.
echo Next steps:
echo 1. Customize .agent\rules\claw_rules.md for your project
echo 2. Update .agent\MISSION_STATE.md with your current mission
echo 3. Edit .agent\vibe_check.md to add project-specific checks
echo.
echo For OpenClaw integration, see: !SCRIPT_DIR!\SKILL_MANIFEST.md
echo.
echo Happy coding! 🚀
echo.

pause
