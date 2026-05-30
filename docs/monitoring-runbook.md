# Runbook мониторинга модели

## Что контролируем

- ROC-AUC / Gini / KS
- Default rate
- PSI по признакам
- Долю high-risk LLM-ответов

## Что делать при ухудшении качества

1. Проверить свежие данные.
2. Проверить drift признаков.
3. Сравнить качество по периодам.
4. Поднять вопрос о recalibration/retraining.
5. Подготовить validation note для команды.

## Что делать при high-risk LLM ответах

1. Зафиксировать кейс.
2. Проверить ожидаемые факты.
3. Передать ответ на human review.
4. Обновить golden dataset / prompt / guardrails.
