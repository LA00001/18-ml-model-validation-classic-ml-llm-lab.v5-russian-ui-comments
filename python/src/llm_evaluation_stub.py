"""Полная демо-оценка LLM-ответов для validation DS.

Скрипт не вызывает внешний LLM API. Он показывает логику контроля ответов:
- релевантность ожидаемым фактам;
- полнота ответа;
- фактологичность;
- риск галлюцинации;
- сохранение структурированного отчёта для Blazor UI.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "llm_evaluation_cases.csv"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Маркеры потенциальной галлюцинации: чрезмерно уверенные или неподтверждённые утверждения.
RISK_TERMS = ["идеальна", "никогда не ошибается", "внедрена в промышленную", "одобрена регулятором"]


def score_case(expected_facts: str, answer: str) -> dict[str, float | str]:
    """Считаем простые rule-based оценки LLM-ответа для демонстрации validation-подхода."""
    expected_tokens = {token.strip().lower() for token in expected_facts.replace('/', ',').split(',') if token.strip()}
    answer_lower = answer.lower()
    hits = sum(1 for token in expected_tokens if token in answer_lower)
    relevance = hits / max(len(expected_tokens), 1)
    hallucination_hits = sum(1 for term in RISK_TERMS if term in answer_lower)
    hallucination_risk = "high" if hallucination_hits else "low"
    factuality = 0.2 if hallucination_hits else min(0.95, 0.65 + relevance * 0.3)
    completeness = min(0.95, 0.45 + relevance * 0.5)
    return {
        "relevance": round(relevance, 3),
        "factuality": round(factuality, 3),
        "completeness": round(completeness, 3),
        "hallucination_risk": hallucination_risk,
    }


def main() -> None:
    """Читаем тестовые LLM-кейсы, считаем оценки и сохраняем generated CSV/Markdown."""
    cases = pd.read_csv(DATA_PATH)
    rows = []
    for _, row in cases.iterrows():
        scores = score_case(row["expected_facts"], row["candidate_answer"])
        rows.append({"case_id": row["case_id"], "prompt_type": row["prompt_type"], **scores})
    result = pd.DataFrame(rows)
    result.to_csv(REPORTS_DIR / "llm_eval_results_generated.csv", index=False)

    # Используем to_string, чтобы не требовать пакет tabulate.
    report = [
        "# Сгенерированный отчёт по оценке LLM-ответов",
        "",
        "Этот отчёт демонстрирует лёгкий rule-based слой проверки LLM-ответов.",
        "В production-подходе его можно расширить через ручную проверку, эталонный набор данных и проверки model-as-a-judge.",
        "",
        result.to_string(index=False),
    ]
    (REPORTS_DIR / "llm_eval_report_generated.md").write_text("\n".join(report), encoding="utf-8")
    print("Артефакты оценки LLM сохранены в", REPORTS_DIR)


if __name__ == "__main__":
    main()
