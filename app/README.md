# Streamlit-приложение для демонстрации прогнозных моделей

Приложение показывает готовые результаты моделирования по трем целевым показателям:

- `price_sqm` — средняя стоимость 1 кв. м;
- `price_index_economy` — индекс цен эконом/комфорт;
- `price_index_business` — индекс цен бизнес.

Интерфейс не обучает модели заново. Он читает готовые CSV-файлы из папки `data/` и показывает метрики, графики прогнозов и помесячные ошибки.

## Структура проекта

```text
real_estate_app/
├── app.py
├── data/
│   ├── final_model_results_level.csv
│   ├── final_model_results_growth.csv
│   ├── best_models_level.csv
│   ├── monthly_errors_level.csv
│   └── forecasts.csv              # необязательный, но нужен для train/test/forecast
├── utils/
│   ├── load_data.py
│   ├── plots.py
│   └── filters.py
├── requirements.txt
└── run_app.bat
```

## Как запустить в VS Code

1. Распаковать архив.
2. Открыть папку `real_estate_app` в VS Code.
3. Открыть терминал в VS Code.
4. Установить зависимости:

```bash
pip install -r requirements.txt
```

5. Запустить приложение:

```bash
streamlit run app.py
```

После запуска откроется браузер с интерфейсом.

## Какие файлы нужно заменить на свои

Положи свои файлы в папку `data/` с такими названиями:

- `final_model_results_level.csv`
- `final_model_results_growth.csv` — необязательно
- `best_models_level.csv`
- `monthly_errors_level.csv`
- `forecasts.csv` — желательно, если нужен полный график train/test/forecast

## Формат final_model_results_level.csv

Обязательные столбцы:

```text
target,model,specification,data_version,MAE,RMSE,SMAPE
```

## Формат best_models_level.csv

Обязательные столбцы:

```text
target,model,specification,data_version,MAE,RMSE,SMAPE
```

## Формат monthly_errors_level.csv

Обязательные столбцы:

```text
date,target,model,specification,data_version,actual,forecast,error,abs_error
```

Этот файл используется для таблицы помесячных ошибок и графика ошибок.

## Формат forecasts.csv

Необязательный, но полезный файл для большого графика train/test/forecast.

Обязательные столбцы:

```text
date,target,model,specification,data_version,split,value
```

Где `split` принимает значения:

- `train`
- `test`
- `forecast`

Если `forecasts.csv` отсутствует, приложение построит только test/forecast по `monthly_errors_level.csv` для лучших моделей.
