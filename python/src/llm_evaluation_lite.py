"""Lite-режим оценки LLM для проекта 18.

Файл не требует внешних зависимостей и использует только стандартную библиотеку Python.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "llm_evaluation_cases.csv"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

# Плохие маркеры: слишком уверенные утверждения без подтверждения.
BAD_MARKERS = ["идеальна", "никогда не ошибается", "аудит не нужен", "без проверки", "всегда правильно"]

# Хорошие маркеры: термины, которые ожидаются в корректном validation-ответе.
GOOD_MARKERS = ["roc-auc", "gini", "ks", "psi", "monitoring", "drift", "backtest", "challenger", "baseline", "pd", "risk", "метрик"]


def score_case(row: dict[str, str]) -> dict[str, object]:
    """Считаем rule-based оценки одного LLM-ответа."""
    answer = row["candidate_answer"].lower()
    expected = [item.strip().lower() for item in row["expected_facts"].split(",")]
    found = sum(1 for fact in expected if fact and fact in answer)
    relevance = min(0.99, 0.25 + 0.15 * found)
    factuality = min(0.99, 0.30 + 0.14 * found)
    completeness = min(0.99, 0.20 + 0.16 * found)

    if any(marker in answer for marker in BAD_MARKERS) or row.get("label") == "bad":
        relevance = min(relevance, 0.35)
        factuality = min(factuality, 0.20)
        completeness = min(completeness, 0.35)
        risk = "high"
    elif found >= max(2, len(expected) // 2):
        risk = "low"
    else:
        risk = "watch"

    return {
        "case_id": row["case_id"],
        "prompt_type": row["prompt_type"],
        "relevance": relevance,
        "factuality": factuality,
        "completeness": completeness,
        "hallucination_risk": risk,
    }


def main() -> None:
    """Генерируем CSV-отчёт по оценке LLM-ответов."""
    with DATA.open("r", encoding="utf-8-sig", newline="") as f:
        rows = [score_case(row) for row in csv.DictReader(f)]
    out = REPORTS / "llm_eval_results_generated.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "prompt_type", "relevance", "factuality", "completeness", "hallucination_risk"])
        writer.writeheader()
        for row in rows:
            writer.writerow({key: (f"{value:.6f}" if isinstance(value, float) else value) for key, value in row.items()})
    print(f"Сгенерирован отчёт по LLM-оценке: {out}")


if __name__ == "__main__":
    main()
