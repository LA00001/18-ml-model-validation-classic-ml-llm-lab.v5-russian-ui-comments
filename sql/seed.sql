-- Демо-данные для таблиц validation DS.
-- Полная синтетическая выборка лежит отдельно в data/synthetic_credit_scoring.csv.
INSERT INTO model_validation_runs
(model_name, roc_auc, gini, ks, precision_value, recall_value, f1_value, validation_comment)
VALUES
('baseline_logistic_regression', 0.7420, 0.4840, 0.3820, 0.4100, 0.6150, 0.4920, 'Интерпретируемая baseline-модель'),
('challenger_gradient_boosting', 0.7810, 0.5620, 0.4310, 0.4550, 0.6540, 0.5360, 'Challenger-модель показывает качество выше, но требует explainability checks');

INSERT INTO feature_drift_monitoring (run_id, feature_name, psi, drift_status)
VALUES
(2, 'debt_to_income', 0.2130, 'watch'),
(2, 'recent_inquiries', 0.1840, 'watch'),
(2, 'monthly_income', 0.0610, 'ok');
