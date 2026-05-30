"""Минимальная утилита для напоминания о назначении датасета.

Основной синтетический датасет уже лежит в data/synthetic_credit_scoring.csv.
В проекте он используется как исторические данные для validation/backtest.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "synthetic_credit_scoring.csv"

if __name__ == "__main__":
    print(f"Синтетический скоринговый датасет уже подготовлен: {DATA_PATH}")
