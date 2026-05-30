"""Lite-режим валидации для проекта 18.

Этот файл не требует внешних зависимостей: используется только стандартная библиотека Python.
Назначение:
- создать такие же CSV-отчёты, которые читает Blazor UI;
- обойти проблемы с pip/pandas/sklearn на Windows или Python 3.14;
- оставить полный pandas/sklearn pipeline в run_validation.py для более богатого варианта.

Запуск из папки python:
    python src/run_validation_lite.py
    python src/llm_evaluation_lite.py
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "synthetic_credit_scoring.csv"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

NUMERIC_FEATURES = [
    "age",
    "monthly_income",
    "credit_history_months",
    "debt_to_income",
    "delinquencies_12m",
    "previous_defaults",
    "recent_inquiries",
]


def sigmoid(x: float) -> float:
    """Сигмоида переводит скоринговую сумму в вероятность дефолта."""
    return 1.0 / (1.0 + math.exp(-max(min(x, 35), -35)))


def read_rows() -> list[dict[str, str]]:
    """Читаем синтетическую скоринговую выборку."""
    with DATA.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def f(row: dict[str, str], name: str) -> float:
    """Безопасно приводим строковое значение признака к float."""
    return float(row[name])


def baseline_score(row: dict[str, str]) -> float:
    """Прозрачная baseline-модель в стиле скоринговой карты."""
    z = -2.25
    z += 3.20 * f(row, "debt_to_income")
    z += 0.55 * f(row, "delinquencies_12m")
    z += 1.05 * f(row, "previous_defaults")
    z += 0.18 * f(row, "recent_inquiries")
    z -= 0.000010 * f(row, "monthly_income")
    z -= 0.006 * f(row, "credit_history_months")
    z += 0.004 * max(0.0, 24.0 - f(row, "age"))
    return sigmoid(z)


def challenger_score(row: dict[str, str]) -> float:
    """Challenger-модель добавляет простые нелинейные правила, имитируя boosted-tree подход."""
    score = baseline_score(row)
    nonlinear = 0.0
    if f(row, "debt_to_income") > 0.55:
        nonlinear += 0.11
    if f(row, "recent_inquiries") >= 3:
        nonlinear += 0.07
    if f(row, "credit_history_months") < 12:
        nonlinear += 0.06
    if row.get("channel") == "web" and row.get("product_type") == "credit_card":
        nonlinear += 0.03
    if f(row, "monthly_income") > 120000 and f(row, "debt_to_income") < 0.25:
        nonlinear -= 0.05
    return min(max(score + nonlinear, 0.001), 0.999)


def auc_score(y: list[int], scores: list[float]) -> float:
    """Считаем ROC-AUC через ранги, включая обработку равных score."""
    pairs = sorted(zip(scores, y), key=lambda x: x[0])
    n_pos = sum(y)
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    rank_sum_pos = 0.0
    i = 0
    while i < len(pairs):
        j = i
        while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        positives_in_tie = sum(label for _, label in pairs[i:j+1])
        rank_sum_pos += positives_in_tie * avg_rank
        i = j + 1
    return (rank_sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def ks_score(y: list[int], scores: list[float]) -> float:
    """Считаем KS: максимальный разрыв между накопленными good/bad."""
    pairs = sorted(zip(scores, y), key=lambda x: x[0], reverse=True)
    total_pos = sum(y)
    total_neg = len(y) - total_pos
    if total_pos == 0 or total_neg == 0:
        return 0.0
    cum_pos = cum_neg = 0
    best = 0.0
    for _, label in pairs:
        if label == 1:
            cum_pos += 1
        else:
            cum_neg += 1
        best = max(best, abs(cum_pos / total_pos - cum_neg / total_neg))
    return best


def classification_metrics(y: list[int], scores: list[float], threshold: float = 0.30) -> tuple[float, float, float]:
    """Считаем precision, recall и F1 на заданном пороге."""
    preds = [1 if score >= threshold else 0 for score in scores]
    tp = sum(1 for actual, pred in zip(y, preds) if actual == 1 and pred == 1)
    fp = sum(1 for actual, pred in zip(y, preds) if actual == 0 and pred == 1)
    fn = sum(1 for actual, pred in zip(y, preds) if actual == 1 and pred == 0)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def model_metrics(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Сравниваем baseline и challenger по ключевым метрикам."""
    y = [int(row["target_default_90d"]) for row in rows]
    result = []
    for name, scorer in [
        ("baseline_scorecard_lite", baseline_score),
        ("challenger_nonlinear_lite", challenger_score),
    ]:
        scores = [scorer(row) for row in rows]
        auc = auc_score(y, scores)
        precision, recall, f1 = classification_metrics(y, scores)
        result.append({
            "model": name,
            "roc_auc": auc,
            "gini": 2 * auc - 1,
            "ks": ks_score(y, scores),
            "precision": precision,
            "recall": recall,
            "f1": f1,
        })
    return result


def backtest(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Проверяем качество challenger-модели отдельно по каждому историческому периоду."""
    by_period: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_period[row["period"]].append(row)
    result = []
    for period in sorted(by_period):
        part = by_period[period]
        y = [int(row["target_default_90d"]) for row in part]
        scores = [challenger_score(row) for row in part]
        auc = auc_score(y, scores)
        result.append({
            "period": period,
            "applications": len(part),
            "default_rate": sum(y) / len(y) if y else 0.0,
            "roc_auc": auc,
            "gini": 2 * auc - 1,
            "ks": ks_score(y, scores),
        })
    return result


def quantile_edges(values: list[float], bins: int = 10) -> list[float]:
    """Границы бинов для PSI строим по квантилям expected-периода."""
    sorted_values = sorted(values)
    edges = []
    for i in range(1, bins):
        idx = int(len(sorted_values) * i / bins)
        edges.append(sorted_values[min(idx, len(sorted_values) - 1)])
    return edges


def bucket(value: float, edges: list[float]) -> int:
    """Определяем номер бина для значения признака."""
    for i, edge in enumerate(edges):
        if value <= edge:
            return i
    return len(edges)


def psi(expected: list[float], actual: list[float], bins: int = 10) -> float:
    """PSI показывает сдвиг распределения признака между expected и actual."""
    edges = quantile_edges(expected, bins)
    eps = 1e-6
    total_expected = len(expected)
    total_actual = len(actual)
    score = 0.0
    for b in range(bins):
        expected_pct = sum(1 for value in expected if bucket(value, edges) == b) / total_expected if total_expected else eps
        actual_pct = sum(1 for value in actual if bucket(value, edges) == b) / total_actual if total_actual else eps
        expected_pct = max(expected_pct, eps)
        actual_pct = max(actual_pct, eps)
        score += (actual_pct - expected_pct) * math.log(actual_pct / expected_pct)
    return score


def psi_results(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Формируем PSI-таблицу по числовым признакам."""
    expected = [row for row in rows if row["period"] in {"2025-01", "2025-02", "2025-03"}]
    actual = [row for row in rows if row["period"] in {"2025-10", "2025-11", "2025-12"}]
    result = []
    for feature in NUMERIC_FEATURES:
        value = psi([f(row, feature) for row in expected], [f(row, feature) for row in actual])
        status = "critical" if value >= 0.25 else "watch" if value >= 0.10 else "ok"
        result.append({"feature": feature, "psi": value, "status": status})
    return sorted(result, key=lambda x: x["psi"], reverse=True)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Сохраняем отчёт в CSV, который потом читает Blazor UI."""
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: (f"{value:.6f}" if isinstance(value, float) else value) for key, value in row.items()})


def main() -> None:
    """Генерируем validation/backtest/PSI отчёты без pandas/sklearn."""
    rows = read_rows()
    write_csv(REPORTS / "model_metrics_generated.csv", ["model", "roc_auc", "gini", "ks", "precision", "recall", "f1"], model_metrics(rows))
    write_csv(REPORTS / "backtest_results_generated.csv", ["period", "applications", "default_rate", "roc_auc", "gini", "ks"], backtest(rows))
    write_csv(REPORTS / "psi_results_generated.csv", ["feature", "psi", "status"], psi_results(rows))
    print(f"Сгенерированы validation-отчёты в папке: {REPORTS}")
    print("- model_metrics_generated.csv")
    print("- backtest_results_generated.csv")
    print("- psi_results_generated.csv")


if __name__ == "__main__":
    main()
