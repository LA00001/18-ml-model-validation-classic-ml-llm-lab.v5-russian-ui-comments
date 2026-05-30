# Сгенерированный отчёт по оценке LLM-ответов

Этот отчёт демонстрирует лёгкий rule-based слой проверки LLM-ответов.
В production-подходе его можно расширить через ручную проверку, эталонный набор данных и проверки model-as-a-judge.

case_id         prompt_type  relevance  factuality  completeness hallucination_risk
LLM-001       model_summary       0.50       0.800         0.700                low
LLM-002    risk_explanation       0.25       0.725         0.575                low
LLM-003    auditor_response       0.00       0.200         0.450               high
LLM-004   validation_report       0.80       0.890         0.850                low
LLM-005 hallucination_check       0.00       0.200         0.450               high