# Спецификация dashboard

## KPI-блок

- Лучшая ROC-AUC
- Лучший Gini
- Количество признаков с PSI watch/critical
- Количество LLM-кейсов высокого риска

## Таблицы

1. Сравнение baseline и challenger.
2. Backtest по историческим периодам.
3. PSI / drift monitoring.
4. Оценка LLM-ответов.
5. Выводы validation DS.

## Источник данных

Dashboard читает generated CSV из папки `reports`.
