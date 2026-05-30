# Пример резюме по валидации модели

## Интерпретация

Challenger-модель показывает качество выше baseline, но перед использованием нужны дополнительные проверки: интерпретируемость, стабильность и drift monitoring. Baseline остаётся полезной как понятный benchmark.

## Основные выводы

- Challenger улучшает ROC-AUC относительно baseline.
- PSI показывает watch-level drift по `debt_to_income` и `recent_inquiries`.
- Поздние периоды требуют мониторинга, потому что default rate растёт.
- LLM-ответы высокого риска должны проходить ручную проверку.

## Рекомендации

1. Оставить baseline logistic regression как интерпретируемый benchmark.
2. Использовать challenger только вместе с объяснимость и drift monitoring.
3. Настроить monthly backtest и PSI-алерты.
4. Добавить ручную проверку для LLM-generated отчётов.
