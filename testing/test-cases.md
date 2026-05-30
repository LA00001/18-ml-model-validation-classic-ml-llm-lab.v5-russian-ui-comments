# Тест-кейсы

## TC-01. Запуск полного Python-режима

Шаги:
1. Запустить `run-python-full-with-pip.bat`.
2. Проверить появление generated CSV в `reports`.

Ожидаемый результат: CSV-отчёты созданы без ошибок.

## TC-02. Запуск lite-режима

Шаги:
1. Запустить `run-python-lite-no-pip.bat`.
2. Проверить generated CSV.

Ожидаемый результат: отчёты созданы без установки зависимостей.

## TC-03. Проверка UI

Шаги:
1. Открыть solution в Visual Studio.
2. Запустить UI.
3. Нажать кнопку.

Ожидаемый результат: UI показывает generated CSV reports, а не fallback-данные.
