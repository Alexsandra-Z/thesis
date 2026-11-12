# ============================================
# Вспомогательный код для экспорта результатов из ноутбука
# ============================================
# Запускается в ноутбуке после расчета final_results_level,
# final_results_growth, best_models_level, monthly_errors_level_df.

import os
import pandas as pd

os.makedirs("data", exist_ok=True)

final_results_level.to_csv("data/final_model_results_level.csv", index=False)
final_results_growth.to_csv("data/final_model_results_growth.csv", index=False)
best_models_level.to_csv("data/best_models_level.csv", index=False)
monthly_errors_level_df.to_csv("data/monthly_errors_level.csv", index=False)

# Если в ноутбуке есть словарь forecasts и data_versions,
# можно дополнительно собрать forecasts.csv для графика train/test/forecast.
# Ожидается, что ключ forecasts имеет вид:
# (target, model, specification, data_version) -> pd.Series прогноза

forecast_rows = []

try:
    for key, pred in forecasts.items():
        target, model, specification, data_version = key
        data = data_versions[data_version]
        series = data[target].dropna()

        train_series = series.iloc[:-TEST_SIZE]
        test_series = series.iloc[-TEST_SIZE:]

        for date, value in train_series.items():
            forecast_rows.append({
                "date": date,
                "target": target,
                "model": model,
                "specification": specification,
                "data_version": data_version,
                "split": "train",
                "value": value,
            })

        for date, value in test_series.items():
            forecast_rows.append({
                "date": date,
                "target": target,
                "model": model,
                "specification": specification,
                "data_version": data_version,
                "split": "test",
                "value": value,
            })

        for date, value in pred.items():
            forecast_rows.append({
                "date": date,
                "target": target,
                "model": model,
                "specification": specification,
                "data_version": data_version,
                "split": "forecast",
                "value": value,
            })

    forecasts_df = pd.DataFrame(forecast_rows)
    forecasts_df.to_csv("data/forecasts.csv", index=False)
    print("forecasts.csv сохранен")

except Exception as e:
    print("forecasts.csv не создан:", e)

print("Экспорт завершен")
