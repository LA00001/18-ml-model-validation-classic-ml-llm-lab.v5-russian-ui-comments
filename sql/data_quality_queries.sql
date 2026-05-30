-- Проверки качества данных для скоринговой выборки.

-- 1. Критичные пропуски: без этих полей нельзя корректно валидировать модель.
SELECT COUNT(*) AS missing_critical_values
FROM scoring_applications
WHERE application_id IS NULL
   OR period IS NULL
   OR debt_to_income IS NULL
   OR target_default_90d IS NULL;

-- 2. Значения долговой нагрузки вне допустимого диапазона.
SELECT application_id, debt_to_income
FROM scoring_applications
WHERE debt_to_income < 0 OR debt_to_income > 1;

-- 3. Периоды, где нет bad/good классов: на таких срезах ROC-AUC может быть некорректной.
SELECT
    period,
    SUM(target_default_90d) AS defaults,
    COUNT(*) - SUM(target_default_90d) AS non_defaults,
    COUNT(*) AS total
FROM scoring_applications
GROUP BY period
HAVING SUM(target_default_90d) = 0 OR COUNT(*) - SUM(target_default_90d) = 0;
