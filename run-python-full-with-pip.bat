@echo off
REM Полный режим: создаёт виртуальное окружение, ставит pandas/sklearn и запускает validation DS pipeline.
REM Если интернет или pip дают сбой, используйте run-python-lite-no-pip.bat.
cd /d "%~dp0python"
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install --timeout 120 --retries 10 -r requirements.txt
python src\run_validation.py
python src\llm_evaluation_stub.py
echo.
echo Готово. Отчёты сохранены в папке reports. Теперь можно открыть Blazor UI и нажать кнопку.
pause
