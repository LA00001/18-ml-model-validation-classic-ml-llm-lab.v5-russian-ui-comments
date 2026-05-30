"""Полный validation DS-сценарий для проекта 18.

Скрипт демонстрирует независимую проверку скоринговой ML-модели:
- загрузка исторических данных;
- обучение baseline и challenger-моделей;
- расчёт ROC-AUC, Gini, KS, precision/recall/F1;
- backtest качества модели по временным периодам;
- PSI/drift monitoring по признакам;
- сохранение результатов в папку reports для Blazor UI.

Важно: этот файл использует pandas/sklearn. Если установка зависимостей неудобна,
можно запустить lite-режим без pip: python src/run_validation_lite.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Корень проекта: .../18-ml-model-validation-classic-ml-llm-lab...
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "synthetic_credit_scoring.csv"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Целевая переменная: факт дефолта в горизонте 90 дней.
TARGET = "target_default_90d"

# Числовые признаки синтетической скоринговой выборки.
NUMERIC_FEATURES = [
    "age",
    "monthly_income",
    "credit_history_months",
    "debt_to_income",
    "delinquencies_12m",
    "previous_defaults",
    "recent_inquiries",
]

# Категориальные признаки: тип продукта и канал подачи заявки.
CATEGORICAL_FEATURES = ["product_type", "channel"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def ks_statistic(y_true: Iterable[int], y_score: Iterable[float]) -> float:
    """Считаем KS-статистику: максимальный разрыв между кумулятивными долями bad/good."""
    frame = pd.DataFrame({"y": y_true, "score": y_score}).sort_values("score")
    events = (frame["y"] == 1).sum()
    non_events = (frame["y"] == 0).sum()
    if events == 0 or non_events == 0:
        return 0.0
    frame["cum_events"] = (frame["y"] == 1).cumsum() / events
    frame["cum_non_events"] = (frame["y"] == 0).cumsum() / non_events
    return float((frame["cum_events"] - frame["cum_non_events"]).abs().max())


def psi(expected: pd.Series, actual: pd.Series, buckets: int = 10) -> float:
    """Считаем PSI: насколько распределение признака изменилось между train и holdout."""
    breakpoints = np.unique(np.quantile(expected, np.linspace(0, 1, buckets + 1)))
    if len(breakpoints) < 3:
        return 0.0
    expected_counts = pd.cut(expected, bins=breakpoints, include_lowest=True).value_counts(normalize=True)
    actual_counts = pd.cut(actual, bins=breakpoints, include_lowest=True).value_counts(normalize=True)
    aligned = pd.concat([expected_counts, actual_counts], axis=1).fillna(0.0001)
    aligned.columns = ["expected", "actual"]
    aligned = aligned.replace(0, 0.0001)
    return float(((aligned["actual"] - aligned["expected"]) * np.log(aligned["actual"] / aligned["expected"])).sum())


def make_preprocessor() -> ColumnTransformer:
    """Готовим признаки: числовые стандартизируем, категориальные кодируем через one-hot."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def build_models() -> dict[str, Pipeline]:
    """Создаём baseline и challenger-модели для сравнения в рамках validation."""
    return {
        "baseline_logistic_regression": Pipeline(
            steps=[
                ("prep", make_preprocessor()),
                ("model", LogisticRegression(max_iter=500, class_weight="balanced", random_state=18)),
            ]
        ),
        "challenger_gradient_boosting": Pipeline(
            steps=[
                ("prep", make_preprocessor()),
                ("model", GradientBoostingClassifier(random_state=18)),
            ]
        ),
    }


def evaluate_model(name: str, model: Pipeline, x_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float | str]:
    """Считаем ключевые метрики качества модели на holdout-периоде."""
    scores = model.predict_proba(x_test)[:, 1]
    y_pred = (scores >= 0.5).astype(int)
    auc = roc_auc_score(y_test, scores)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary", zero_division=0)
    return {
        "model": name,
        "roc_auc": round(float(auc), 4),
        "gini": round(float(2 * auc - 1), 4),
        "ks": round(ks_statistic(y_test, scores), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
    }


def main() -> None:
    """Запускаем полный pipeline: train/holdout, метрики, backtest, PSI и отчёт."""
    data = pd.read_csv(DATA_PATH).sort_values("period")

    # Train: январь-август 2025. Holdout/backtest: сентябрь-декабрь 2025.
    train = data[data["period"] <= "2025-08"].copy()
    holdout = data[data["period"] > "2025-08"].copy()

    x_train = train[FEATURES]
    y_train = train[TARGET]
    x_holdout = holdout[FEATURES]
    y_holdout = holdout[TARGET]

    metrics = []
    models = build_models()
    fitted_models = {}
    for name, model in models.items():
        # Здесь происходит реальное обучение sklearn-моделей.
        model.fit(x_train, y_train)
        fitted_models[name] = model
        metrics.append(evaluate_model(name, model, x_holdout, y_holdout))

    metrics_df = pd.DataFrame(metrics)
    metrics_df.to_csv(REPORTS_DIR / "model_metrics_generated.csv", index=False)

    # Для демонстрации backtest используем challenger-модель.
    challenger = fitted_models["challenger_gradient_boosting"]
    backtest_rows = []
    for period, frame in holdout.groupby("period"):
        scores = challenger.predict_proba(frame[FEATURES])[:, 1]
        auc = roc_auc_score(frame[TARGET], scores) if frame[TARGET].nunique() > 1 else np.nan
        backtest_rows.append(
            {
                "period": period,
                "applications": len(frame),
                "default_rate": round(float(frame[TARGET].mean()), 4),
                "roc_auc": round(float(auc), 4) if not np.isnan(auc) else "not_enough_classes",
                "gini": round(float(2 * auc - 1), 4) if not np.isnan(auc) else "not_enough_classes",
                "ks": round(ks_statistic(frame[TARGET], scores), 4),
            }
        )
    pd.DataFrame(backtest_rows).to_csv(REPORTS_DIR / "backtest_results_generated.csv", index=False)

    # PSI считаем по каждому числовому признаку между train и holdout.
    psi_rows = []
    for feature in NUMERIC_FEATURES:
        value = psi(train[feature], holdout[feature])
        psi_rows.append(
            {
                "feature": feature,
                "psi": round(value, 4),
                "status": "critical" if value >= 0.25 else "watch" if value >= 0.1 else "ok",
            }
        )
    pd.DataFrame(psi_rows).to_csv(REPORTS_DIR / "psi_results_generated.csv", index=False)

    # Используем to_string, чтобы не требовать дополнительный пакет tabulate.
    summary = [
        "# Сгенерированное резюме по валидации модели",
        "",
        "## Метрики моделей",
        metrics_df.to_string(index=False),
        "",
        "## Интерпретация",
        "Baseline проще интерпретировать. Challenger может улучшить качество, но требует проверки стабильности, объяснимости и мониторинга drift.",
    ]
    (REPORTS_DIR / "validation_summary_generated.md").write_text("\n".join(summary), encoding="utf-8")
    print("Артефакты валидации сохранены в", REPORTS_DIR)


if __name__ == "__main__":
    main()
