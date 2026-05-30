namespace ModelValidationLab.UI.Models;

// Агрегированный результат, который Blazor UI получает из generated CSV или fallback-демо.
public sealed class ModelValidationResult
{
    public required IReadOnlyList<ModelMetric> ModelMetrics { get; init; }
    public required IReadOnlyList<BacktestRow> Backtest { get; init; }
    public required IReadOnlyList<PsiResult> PsiResults { get; init; }
    public required IReadOnlyList<LlmEvaluationRow> LlmEvaluations { get; init; }
    public required IReadOnlyList<string> Recommendations { get; init; }

    // Описание источника данных: generated CSV reports или встроенные демо-данные.
    public string SourceDescription { get; init; } = "встроенный демонстрационный сценарий";

    public double BestRocAuc => ModelMetrics.Max(x => x.RocAuc);
    public double BestGini => ModelMetrics.Max(x => x.Gini);
    public int PsiWatchFeatures => PsiResults.Count(x => x.Status is "watch" or "critical");
    public int HighRiskLlmCases => LlmEvaluations.Count(x => x.HallucinationRisk == "high");
}
