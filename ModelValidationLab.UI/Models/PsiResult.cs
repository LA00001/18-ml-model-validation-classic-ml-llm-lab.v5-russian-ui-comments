namespace ModelValidationLab.UI.Models;

// PSI показывает, насколько распределение признака изменилось между обучающим и контрольным периодом.
public sealed record PsiResult(string Feature, double Psi, string Status);
