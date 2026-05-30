using ModelValidationLab.UI.Services;

var builder = WebApplication.CreateBuilder(args);

// Подключаем Razor Pages и Blazor Server для демонстрационного UI.
builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();

// Демо-движок читает generated CSV-отчёты из папки reports.
builder.Services.AddSingleton<ModelValidationDemoEngine>();

var app = builder.Build();

// В production-режиме включаем стандартную страницу ошибок и HSTS.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();

app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();
