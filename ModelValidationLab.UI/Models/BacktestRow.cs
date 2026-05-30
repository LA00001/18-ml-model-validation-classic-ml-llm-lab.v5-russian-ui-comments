namespace ModelValidationLab.UI.Models;

// Строка backtest-отчёта: качество модели на отдельном историческом периоде.
public sealed record BacktestRow(string Period, double RocAuc, double Gini, double DefaultRate, string Status);
