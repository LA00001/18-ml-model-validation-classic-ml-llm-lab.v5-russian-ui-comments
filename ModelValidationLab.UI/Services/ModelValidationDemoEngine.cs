using System.Globalization;
using ModelValidationLab.UI.Models;

namespace ModelValidationLab.UI.Services;

// Демо-движок для UI.
// Сначала он пытается прочитать generated CSV-отчёты, которые создали Python-скрипты.
// Если отчётов нет, используется встроенный fallback-сценарий, чтобы UI всё равно открывался.
public sealed class ModelValidationDemoEngine
{
    private readonly IWebHostEnvironment _environment;

    public ModelValidationDemoEngine(IWebHostEnvironment environment)
    {
        _environment = environment;
    }

    // Главный метод сценария: UI вызывает его после нажатия кнопки.
    public ModelValidationResult Run()
    {
        var fromReports = TryLoadFromGeneratedReports();
        return fromReports ?? RunEmbeddedDemoScenario();
    }

    // Пробуем загрузить результаты полного или lite Python-расчёта из папки reports.
    private ModelValidationResult? TryLoadFromGeneratedReports()
    {
        var reportsDir = FindReportsDirectory();
        if (reportsDir is null)
        {
            return null;
        }

        var metricsPath = Path.Combine(reportsDir, "model_metrics_generated.csv");
        var backtestPath = Path.Combine(reportsDir, "backtest_results_generated.csv");
        var psiPath = Path.Combine(reportsDir, "psi_results_generated.csv");
        var llmPath = Path.Combine(reportsDir, "llm_eval_results_generated.csv");

        if (!File.Exists(metricsPath) || !File.Exists(backtestPath) || !File.Exists(psiPath) || !File.Exists(llmPath))
        {
            return null;
        }

        try
        {
            var metrics = LoadModelMetrics(metricsPath);
            var backtest = LoadBacktest(backtestPath);
            var psi = LoadPsi(psiPath);
            var llm = LoadLlm(llmPath);

            if (metrics.Count == 0 || backtest.Count == 0 || psi.Count == 0 || llm.Count == 0)
            {
                return null;
            }

            return new ModelValidationResult
            {
                ModelMetrics = metrics,
                Backtest = backtest,
                PsiResults = psi,
                LlmEvaluations = llm,
                SourceDescription = $"сгенерированные CSV-отчёты из папки {reportsDir}",
                Recommendations = BuildRecommendations(metrics, backtest, psi, llm)
            };
        }
        catch
        {
            // Для демонстрационного проекта не падаем в UI, а возвращаем fallback-сценарий.
            return null;
        }
    }

    // Ищем reports рядом с решением, внутри UI-проекта или через bin-папку Visual Studio.
    private string? FindReportsDirectory()
    {
        var candidates = new[]
        {
            Path.GetFullPath(Path.Combine(_environment.ContentRootPath, "..", "reports")),
            Path.GetFullPath(Path.Combine(_environment.ContentRootPath, "reports")),
            Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "reports"))
        };

        return candidates.FirstOrDefault(path => File.Exists(Path.Combine(path, "model_metrics_generated.csv")));
    }

    // Читаем таблицу model_metrics_generated.csv.
    private static List<ModelMetric> LoadModelMetrics(string path)
    {
        var rows = new List<ModelMetric>();
        foreach (var columns in ReadCsvRows(path))
        {
            var modelName = columns[0];
            var comment = modelName.Contains("challenger", StringComparison.OrdinalIgnoreCase)
                ? "Challenger-модель рассчитана Python/sklearn pipeline; перед внедрением нужны объяснимость, проверка drift и контроль стабильности."
                : "Baseline-модель рассчитана Python/sklearn pipeline; это понятная отправная точка для независимой валидации.";

            rows.Add(new ModelMetric(
                modelName,
                ParseDouble(columns[1]),
                ParseDouble(columns[2]),
                ParseDouble(columns[3]),
                ParseDouble(columns[4]),
                ParseDouble(columns[5]),
                ParseDouble(columns[6]),
                comment));
        }
        return rows;
    }

    // Читаем backtest_results_generated.csv и присваиваем статус по ROC-AUC.
    private static List<BacktestRow> LoadBacktest(string path)
    {
        var rows = new List<BacktestRow>();
        foreach (var columns in ReadCsvRows(path))
        {
            if (!double.TryParse(columns[3], NumberStyles.Any, CultureInfo.InvariantCulture, out var rocAuc))
            {
                continue;
            }

            var status = rocAuc < 0.70 ? "critical" : rocAuc < 0.75 ? "watch" : "ok";
            rows.Add(new BacktestRow(
                columns[0],
                rocAuc,
                ParseDouble(columns[4]),
                ParseDouble(columns[2]),
                status));
        }
        return rows;
    }

    // Читаем psi_results_generated.csv: признаки, PSI и статус drift.
    private static List<PsiResult> LoadPsi(string path)
    {
        var rows = new List<PsiResult>();
        foreach (var columns in ReadCsvRows(path))
        {
            rows.Add(new PsiResult(columns[0], ParseDouble(columns[1]), columns[2]));
        }
        return rows;
    }

    // Читаем llm_eval_results_generated.csv: оценки ответов LLM.
    private static List<LlmEvaluationRow> LoadLlm(string path)
    {
        var rows = new List<LlmEvaluationRow>();
        foreach (var columns in ReadCsvRows(path))
        {
            rows.Add(new LlmEvaluationRow(
                columns[0],
                ParseDouble(columns[2]),
                ParseDouble(columns[3]),
                ParseDouble(columns[4]),
                columns[5]));
        }
        return rows;
    }

    // Формируем выводы validation DS на русском языке.
    private static List<string> BuildRecommendations(
        IReadOnlyList<ModelMetric> metrics,
        IReadOnlyList<BacktestRow> backtest,
        IReadOnlyList<PsiResult> psi,
        IReadOnlyList<LlmEvaluationRow> llm)
    {
        var best = metrics.OrderByDescending(x => x.RocAuc).First();
        var watchFeatures = psi.Where(x => x.Status is "watch" or "critical").Select(x => FeatureRu(x.Feature)).ToList();
        var lateWatch = backtest.Count(x => x.Status is "watch" or "critical");
        var highRiskLlm = llm.Count(x => x.HallucinationRisk == "high");

        return new List<string>
        {
            $"Лучшая модель по ROC-AUC: {ModelRu(best.ModelName)}; валидация должна проверить не только качество, но и стабильность, интерпретируемость и применимость бизнес-правил.",
            watchFeatures.Count > 0
                ? $"PSI/drift требует внимания по признакам: {string.Join(", ", watchFeatures)}; нужен регулярный мониторинг и пороги алертов."
                : "PSI/drift не показывает отклонений уровня наблюдения; регулярный мониторинг всё равно нужен.",
            lateWatch > 0
                ? $"Backtest нашёл {lateWatch} период(а/ов) со статусом наблюдение/критично; качество модели нужно контролировать по временным срезам."
                : "Backtest по историческим периодам выглядит стабильным, но нужен контроль на новых периодах.",
            highRiskLlm > 0
                ? $"Оценка LLM нашла {highRiskLlm} кейс(а/ов) высокого риска; ответы LLM для отчёта по валидации должны проходить ручную проверку."
                : "Оценка LLM не нашла high-risk кейсов, но production-подход требует эталонного набора данных и ручной проверки.",
            "Для production-подхода нужны карточка модели, отчёт по валидации, проверка challenger-модели, пороги качества, алерты и регламент пересмотра модели."
        };
    }

    // Минимальный CSV-reader достаточен для наших простых generated-файлов без запятых внутри значений.
    private static IEnumerable<string[]> ReadCsvRows(string path)
    {
        return File.ReadLines(path)
            .Skip(1)
            .Where(line => !string.IsNullOrWhiteSpace(line))
            .Select(line => line.Split(','));
    }

    private static double ParseDouble(string value)
    {
        return double.Parse(value, NumberStyles.Any, CultureInfo.InvariantCulture);
    }

    // Русские названия моделей для выводов.
    private static string ModelRu(string modelName) => modelName switch
    {
        "baseline_logistic_regression" => "baseline: логистическая регрессия",
        "challenger_gradient_boosting" => "challenger: градиентный бустинг",
        "baseline_scorecard_lite" => "baseline: скоринговая карта lite",
        "challenger_nonlinear_lite" => "challenger: нелинейная lite-модель",
        _ => modelName
    };

    // Русские названия признаков для выводов.
    private static string FeatureRu(string feature) => feature switch
    {
        "age" => "возраст",
        "monthly_income" => "ежемесячный доход",
        "credit_history_months" => "длина кредитной истории",
        "debt_to_income" => "долговая нагрузка",
        "delinquencies_12m" => "просрочки за 12 месяцев",
        "previous_defaults" => "предыдущие дефолты",
        "recent_inquiries" => "недавние кредитные запросы",
        _ => feature
    };

    // Fallback-сценарий нужен, если Python-отчёты ещё не сгенерированы.
    private static ModelValidationResult RunEmbeddedDemoScenario()
    {
        var metrics = new List<ModelMetric>
        {
            new("baseline_logistic_regression", 0.742, 0.484, 0.382, 0.410, 0.615, 0.492, "Интерпретируемый baseline для независимой валидации."),
            new("challenger_gradient_boosting", 0.781, 0.562, 0.431, 0.455, 0.654, 0.536, "Качество выше, но нужны объяснимость и проверки drift.")
        };

        var backtest = new List<BacktestRow>
        {
            new("2025-07", 0.782, 0.564, 0.092, "ok"),
            new("2025-08", 0.771, 0.542, 0.101, "ok"),
            new("2025-09", 0.748, 0.496, 0.118, "watch"),
            new("2025-10", 0.736, 0.472, 0.126, "watch"),
            new("2025-11", 0.714, 0.428, 0.139, "watch"),
            new("2025-12", 0.703, 0.406, 0.151, "watch")
        };

        var psi = new List<PsiResult>
        {
            new("debt_to_income", 0.213, "watch"),
            new("recent_inquiries", 0.184, "watch"),
            new("delinquencies_12m", 0.097, "ok"),
            new("monthly_income", 0.061, "ok"),
            new("credit_history_months", 0.044, "ok")
        };

        var llm = new List<LlmEvaluationRow>
        {
            new("LLM-001", 0.90, 0.95, 0.88, "low"),
            new("LLM-002", 0.87, 0.92, 0.80, "low"),
            new("LLM-003", 0.20, 0.10, 0.15, "high"),
            new("LLM-004", 0.93, 0.90, 0.91, "low"),
            new("LLM-005", 0.35, 0.05, 0.20, "high")
        };

        var recommendations = new List<string>
        {
            "Challenger-модель показывает качество выше baseline, но требует объяснимости и проверки стабильности.",
            "Есть drift уровня наблюдения по долговой нагрузке и недавним кредитным запросам; нужен регулярный PSI-мониторинг.",
            "Backtest показывает снижение качества на поздних периодах; рекомендуется ежемесячный мониторинг качества модели.",
            "LLM можно использовать для черновиков отчётов, но ответы высокого риска должны проходить ручную проверку.",
            "Для production-подхода нужны карточка модели, отчёт по валидации, пороги, алерты и регламент пересмотра модели."
        };

        return new ModelValidationResult
        {
            ModelMetrics = metrics,
            Backtest = backtest,
            PsiResults = psi,
            LlmEvaluations = llm,
            Recommendations = recommendations,
            SourceDescription = "встроенные демонстрационные данные; сгенерированные CSV-отчёты не найдены"
        };
    }
}
