-- Схема демонстрационной БД для validation DS lab.
-- Таблица заявок хранит исторические признаки и целевую переменную дефолта.
CREATE TABLE scoring_applications (
    application_id VARCHAR(32) PRIMARY KEY,
    period VARCHAR(7) NOT NULL,
    age INT NOT NULL,
    monthly_income NUMERIC(14,2) NOT NULL,
    credit_history_months INT NOT NULL,
    debt_to_income NUMERIC(6,4) NOT NULL,
    delinquencies_12m INT NOT NULL,
    previous_defaults INT NOT NULL,
    recent_inquiries INT NOT NULL,
    product_type VARCHAR(32) NOT NULL,
    channel VARCHAR(32) NOT NULL,
    target_default_90d INT NOT NULL
);

-- Таблица результатов валидационных запусков по моделям.
CREATE TABLE model_validation_runs (
    run_id SERIAL PRIMARY KEY,
    run_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model_name VARCHAR(128) NOT NULL,
    roc_auc NUMERIC(8,4),
    gini NUMERIC(8,4),
    ks NUMERIC(8,4),
    precision_value NUMERIC(8,4),
    recall_value NUMERIC(8,4),
    f1_value NUMERIC(8,4),
    validation_comment TEXT
);

-- Таблица мониторинга drift по признакам через PSI.
CREATE TABLE feature_drift_monitoring (
    id SERIAL PRIMARY KEY,
    run_id INT REFERENCES model_validation_runs(run_id),
    feature_name VARCHAR(128) NOT NULL,
    psi NUMERIC(8,4) NOT NULL,
    drift_status VARCHAR(32) NOT NULL
);
