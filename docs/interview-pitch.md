# Как рассказывать о проекте на интервью

Сделал lab-проект под Validation DS: проверка classic ML и LLM-решений.

В Python-части реализованы baseline logistic regression и challenger gradient boosting, расчёт ROC-AUC, Gini, KS, Precision/Recall/F1, backtest по историческим периодам и PSI/drift monitoring.

Отдельно добавил LLM evaluation: оценку релевантности, фактологичности, полноты и риска галлюцинаций на тестовых кейсах.

Blazor UI читает generated CSV-отчёты из папки reports и показывает результаты в виде dashboard. Проект демонстрирует подход не только к построению модели, но и к независимой проверке, мониторингу и подготовке validation report.
