namespace ModelValidationLab.UI.Models;

// Метрики одной ML-модели: baseline или challenger.
public sealed record ModelMetric(
    string ModelName,
    double RocAuc,
    double Gini,
    double Ks,
    double Precision,
    double Recall,
    double F1,
    string Comment);
