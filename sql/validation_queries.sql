-- 1. Доля дефолтов по историческим периодам.
SELECT
    period,
    COUNT(*) AS applications,
    AVG(target_default_90d::NUMERIC) AS default_rate
FROM scoring_applications
GROUP BY period
ORDER BY period;

-- 2. Риск по сегментам: продукт и канал подачи заявки.
SELECT
    product_type,
    channel,
    COUNT(*) AS applications,
    AVG(target_default_90d::NUMERIC) AS default_rate,
    AVG(debt_to_income) AS avg_dti
FROM scoring_applications
GROUP BY product_type, channel
ORDER BY default_rate DESC;

-- 3. Сравнение запусков валидации моделей.
SELECT
    model_name,
    roc_auc,
    gini,
    ks,
    precision_value,
    recall_value,
    f1_value,
    validation_comment
FROM model_validation_runs
ORDER BY roc_auc DESC;

-- 4. Алерты drift monitoring по PSI.
SELECT
    feature_name,
    psi,
    drift_status
FROM feature_drift_monitoring
WHERE drift_status IN ('watch', 'critical')
ORDER BY psi DESC;
