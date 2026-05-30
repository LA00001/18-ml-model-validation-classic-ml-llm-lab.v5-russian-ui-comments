@echo off
REM Lite-режим: не ставит зависимости и не требует интернета.
REM Генерирует CSV-отчёты стандартной библиотекой Python.
cd /d "%~dp0python"
python src\run_validation_lite.py
python src\llm_evaluation_lite.py
echo.
echo Готово. Lite-отчёты сохранены в папке reports. Теперь можно открыть Blazor UI и нажать кнопку.
pause
