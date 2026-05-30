namespace ModelValidationLab.UI.Models;

// Строка оценки LLM-ответа: релевантность, фактологичность, полнота и риск галлюцинации.
public sealed record LlmEvaluationRow(string CaseId, double Relevance, double Factuality, double Completeness, string HallucinationRisk);
