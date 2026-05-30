# 18 ML Model Validation Classic ML / LLM Lab

Лабораторный проект под вакансию **Junior/Middle Data Scientist (Classic ML / LLM)** в направлении Validation DS.

## КАКАЯ МОДЕЛЬ ML?

В проекте реализована проверка двух ML-моделей для скоринговой задачи: baseline-модели на основе логистической регрессии и challenger-модели на основе градиентного бустинга деревьев решений. Обе модели собраны в `sklearn Pipeline`, где сначала выполняется предобработка числовых и категориальных признаков, а затем применяется ML-алгоритм для бинарной классификации кредитного дефолта.

Baseline-модель называется `baseline_logistic_regression`. Это логистическая регрессия (`LogisticRegression`) в составе `sklearn Pipeline` с предобработкой признаков. Она используется как более простая и интерпретируемая отправная точка для сравнения качества.

Challenger-модель называется `challenger_gradient_boosting`. Это модель градиентного бустинга деревьев решений (`GradientBoostingClassifier`) в составе `sklearn Pipeline` с такой же предобработкой признаков. Она используется как более сложный альтернативный подход, который можно сравнить с baseline-моделью по качеству, стабильности и применимости.

Обучение моделей происходит в строке `model.fit(x_train, y_train)`: модель получает обучающие признаки `x_train` и правильные ответы `y_train`, после чего учится находить связь между параметрами клиента и фактом дефолта. После обучения объект модели сохраняется в словарь `fitted_models` через строку `fitted_models[name] = model`. Это позволяет дальше использовать уже обученную модель для расчёта метрик качества, проверки на holdout-выборке и backtest по историческим периодам.

Для оценки качества моделей рассчитываются ROC-AUC, Gini, KS, Precision, Recall и F1. Дополнительно выполняется backtest по историческим периодам и PSI/drift monitoring для проверки стабильности входных признаков. Такой подход имитирует validation DS-процесс: модель не просто обучается, а затем проверяется на исторических данных, сравнивается с альтернативным решением и анализируется с точки зрения качества, устойчивости и рисков использования.

## ЧТО ПОКАЗЫВАЕТ?

Проект показывает полный демонстрационный сценарий независимой проверки ML/LLM-решений:

- обучение baseline-модели и challenger-модели;
- расчёт ROC-AUC, Gini, KS, Precision, Recall, F1;
- backtest качества модели по историческим периодам;
- PSI/drift monitoring по признакам;
- rule-based оценка ответов LLM по релевантности, фактологичности, полноте и риску галлюцинаций;
- Blazor UI, который читает сгенерированные CSV-отчёты из папки `reports`.

## Как запускать

### Вариант 1. Полный Python/sklearn-режим

```bat
run-python-full-with-pip.bat
```

Или вручную:

```bat
cd python
python -m venv .venv
.venv\Scripts ctivate
pip install --timeout 120 --retries 10 -r requirements.txt
python src
un_validation.py
python src\llm_evaluation_stub.py
```

### Вариант 2. Lite-режим без pip

```bat
run-python-lite-no-pip.bat
```

Lite-режим не ставит зависимости и подходит, если на машине проблемы с PyPI, pandas или sklearn.

## Как работает UI

Blazor UI не обучает модель в момент нажатия кнопки. Логика такая:

```text
Python-скрипты → пересчитывают CSV в reports → Blazor UI читает сгенерированные CSV → браузер показывает отчёт
```

Открывать solution:

```text
ModelValidationLab.UI\ModelValidationLab.UI.sln
```

Ожидаемый адрес:

```text
https://localhost:61818
```

## Что важно для рекрутера

Проект демонстрирует не просто построение модели, а именно **validation-подход**:

- сравнение baseline и challenger;
- проверка модели на исторических периодах;
- контроль drift через PSI;
- интерпретация метрик качества;
- проверка LLM-ответов на риск галлюцинаций;
- подготовка отчётов для model validation / model risk / monitoring.

## Короткое описание

Classic ML / LLM validation lab: Python/pandas/sklearn, baseline logistic regression, challenger gradient boosting, ROC-AUC/Gini/KS/F1, backtest по историческим периодам, PSI/drift monitoring, LLM evaluation, сгенерированные CSV-отчёты и Blazor UI для демонстрации результатов.


## ИСТОРИЯ
### 1 ai-operations-ui-demo.zip — простой Blazor UI
### 2 topic-knowledge-base-demo.zip — справочник тем 101–115
### 3 docx-generator-demo.zip — отдельная генерация DOCX
### 4 workflow-pipeline-demo.zip — конвейер в консольном варианте
### 5 generated-files-api-demo.zip — API для выдачи файлов
### 6 ai-document-workflow-demo.zip — главный полный MVP с UI + конвейером
### 7 ai-document-workflow-devops-lab.zip — расширенная версия MVP с DevOps-обвязкой: health-check endpoints, Docker, Jenkinsfile, GitHub Actions CI и примеры AI infrastructure lab
### 8 ai-infra-kafka-s3-vault-dropapp-lab.zip — отдельный инфраструктурный lab: ASP.NET Core API + Redpanda/Kafka-compatible broker + MinIO/S3-compatible storage + HashiCorp Vault + dropapp-style manifest
### 9 ai-document-workflow-kafka-s3-vault-lab.zip — связка логики AI Document Workflow из проекта 6 с инфраструктурой Kafka/S3/Vault
### 10 ai-document-workflow-devops-ops-lab.zip — DevOps/Ops версия под Jenkins, Ansible, Groovy, Kafka, S3, Vault, Istio, dropapp-style, ИФТ/ПСИ и production-сопровождение
### 11 ai-document-workflow-observability-support-lab.zip — observability/support версия под сопровождение ПО: Prometheus, Grafana, Alertmanager, /metrics, healthz/readyz, readiness-проверки Kafka/S3/Vault, dashboard panels, alert rules, incident snapshot и runbook для диагностики инцидентов
### 12 ai-document-workflow-postgresql-support-lab.zip — PostgreSQL/support версия под сопровождение БД: PostgreSQL 16, Adminer, SQL schema/seed scripts, диагностические SQL-запросы, JOIN/GROUP BY/CTE, индексы, VIEW, PL/pgSQL functions, document health, incident diagnostics, release health и API endpoints для проверки состояния данных
### 13 ai-document-workflow-mvp-postgresql-support-lab.zip — гибрид проекта 6 и 12: главный MVP с UI + document workflow pipeline, объединённый с PostgreSQL/support-слоем для сопровождения БД: Docker Compose, PostgreSQL 16, Adminer, SQL schema/seed scripts, индексы, VIEW, PL/pgSQL functions, diagnostic SQL queries, document health, incident diagnostics, release health, /healthz, /readyz, /metrics, Prometheus, Grafana и Alertmanager
### 14 ai-document-workflow-business-data-analytics-lab.zip — Аналитический Blazor UI lab под роль аналитика: Visual Studio solution, запуск сценария анализа городских обращений, KPI по SLA/категориям/районам, BPMN/UML, business requirements, ТЗ, API/OpenAPI, SQL, Python ETL, dashboard spec и ML data preparation.
### 15-mortgage-vba-excel-sql-dashboard-lab.v2-blazor-ui-sln.zip — Excel/VBA/SQL lab под автоматизацию ипотечной отчётности: Visual Studio solution, Blazor UI для запуска сценария, ипотечный калькулятор, импорт CSV/SQL-выгрузок, VBA-модули, расчёт платежей/PTI/LTV, dashboard, data quality checks и регулярные отчёты.
### 16-ai-document-workflow-itil-change-management-lab.v1-html-ui-sln — ITIL/ITSM Change Management lab под инженера внедрения: Visual Studio solution, HTML UI с кнопкой формирования календаря изменений, ЗНИ/RFC, оценка рисков, поиск конфликтов, CAB checklist, планы внедрения и отката, связь с incident/problem management, KPI и SQL-отчётность.
### 17-ai-document-workflow-itsm-incident-analytics-lab.v2-blazor-ui-sln — ITSM Incident Analytics lab под роль аналитика в ITSM-системе: Blazor UI для анализа технологических инцидентов, KPI по SLA/MTTR/impact/root cause, контроль качества данных ITSM, аудит мероприятий, SQL-отчётность, RCA, dashboard spec и management report.
### 18-ml-model-validation-classic-ml-llm-lab.v5-russian-ui-comments.zip — Classic ML / LLM validation DS lab: Python pandas/sklearn, baseline logistic regression, challenger gradient boosting, ROC-AUC/Gini/KS/F1, backtest по историческим периодам, PSI/drift monitoring, LLM evaluation, generated CSV reports и Blazor UI-витрина.

## License

Copyright (c) 2026 Андрей / LA00001

All rights reserved.

This repository is provided for portfolio and demonstration purposes only.
Copying, redistribution, modification, sublicensing, commercial use, or publication
of the source code is not permitted without prior written permission from the author.

---

Авторское право (c) 2026 Андрей / LA00001

Все права защищены.

Данный репозиторий предоставлен только для демонстрации в портфолио.
Копирование, распространение, изменение, сублицензирование, коммерческое использование
или публикация исходного кода не допускаются без предварительного письменного разрешения автора.
