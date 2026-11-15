@echo off
title AutoPrice AI Dashboard
echo ============================================================
echo Starting AutoPrice AI - Car Pricing & Q1 Demand Forecaster
echo ============================================================

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" run_app.py
) else (
    py run_app.py 2>nul || python run_app.py
)

pause
