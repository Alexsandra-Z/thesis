# Streamlit-приложение

from pathlib import Path

import streamlit as st

from utils.load_data import load_app_data
from utils.filters import (
    TARGET_LABELS,
    MODEL_LABELS,
    SPEC_LABELS,
    get_filtered_metrics,
    get_option_list,
)
from utils.plots import plot_forecast, plot_errors


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"

st.set_page_config(
    page_title="Прогнозирование рынка недвижимости",
    page_icon="🏙️",
    layout="wide",
)

# Стили приложения
st.markdown(
    """
    <style>
    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 6px;
        line-height: 1.35;
        color: #ffffff;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 16px;
        margin-bottom: 22px;
    }

    .info-box {
        padding: 16px 18px;
        border-radius: 12px;
        background: #f6f8fb;
        border: 1px solid #e5e8ef;
        margin-bottom: 14px;
        color: #1f2937;
    }

    .info-box * {
        color: #1f2937 !important;
    }

    .info-box b {
        font-weight: 700;
        color: #111827 !important;
    }

    div[data-testid="stMetric"] {
        padding: 6px 0px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Подписи для версий данных
VERSION_LABELS = {
    "level": "Уровни",
    "growth": "Лог-приросты",
}


def get_label(value, mapping=None):
    if mapping is None:
        mapping = {}

    return mapping.get(value, value)


def get_best_model_text(final_results, target, data_version):
    filtered = final_results[
        (final_results["target"] == target)
        & (final_results["data_version"] == data_version)
    ].copy()

    if filtered.empty:
        return "Нет данных"

    best_row = filtered.sort_values("RMSE").iloc[0]

    model_text = get_label(best_row["model"], MODEL_LABELS)
    spec_text = get_label(best_row["specification"], SPEC_LABELS)

    return f"{model_text}<br>{spec_text}<br>RMSE = {best_row['RMSE']:.3f}"


# Заголовок приложения
st.markdown(
    '<div class="main-title">Прогнозирование ценовых показателей первичного рынка недвижимости</div>',
    unsafe_allow_html=True,
)

# Загрузка CSV-файлов
app_data = load_app_data(DATA_DIR)

final_results = app_data["final_results"]
best_models_level = app_data["best_models_level"]
monthly_errors_level = app_data["monthly_errors_level"]
forecasts = app_data["forecasts"]

if final_results.empty:
    st.error("Файлы с результатами моделей не найдены")
    st.stop()

# Боковая панель
st.sidebar.header("Параметры")

available_targets = get_option_list(final_results, "target")

if len(available_targets) == 0:
    st.error("В таблице результатов нет целевых показателей")
    st.stop()

target = st.sidebar.selectbox(
    "Показатель",
    options=available_targets,
    format_func=lambda x: get_label(x, TARGET_LABELS),
)

available_versions = get_option_list(
    final_results[final_results["target"] == target],
    "data_version",
)

if len(available_versions) == 0:
    st.error("Для выбранного показателя нет версий данных")
    st.stop()

version_index = available_versions.index("level") if "level" in available_versions else 0

data_version = st.sidebar.selectbox(
    "Данные",
    options=available_versions,
    index=version_index,
    format_func=lambda x: get_label(x, VERSION_LABELS),
)

filtered_for_target = final_results[
    (final_results["target"] == target)
    & (final_results["data_version"] == data_version)
].copy()

available_models = get_option_list(filtered_for_target, "model")

if len(available_models) == 0:
    st.error("Для выбранного показателя нет моделей")
    st.stop()

model = st.sidebar.selectbox(
    "Модель",
    options=available_models,
    format_func=lambda x: get_label(x, MODEL_LABELS),
)

filtered_for_model = filtered_for_target[
    filtered_for_target["model"] == model
].copy()

available_specs = get_option_list(filtered_for_model, "specification")

if len(available_specs) == 0:
    st.error("Для выбранной модели нет спецификаций")
    st.stop()

specification = st.sidebar.selectbox(
    "Спецификация",
    options=available_specs,
    format_func=lambda x: get_label(x, SPEC_LABELS),
)

# Выбранные метрики
selected_metrics = get_filtered_metrics(
    final_results=final_results,
    target=target,
    model=model,
    specification=specification,
    data_version=data_version,
)

if selected_metrics.empty:
    st.warning("Для выбранной комбинации нет результатов")
    st.stop()

selected_row = selected_metrics.iloc[0]

# Верхний информационный блок
left, right = st.columns([2, 1])

with left:
    st.markdown(
        f"""
        <div class="info-box">
            <b>Показатель:</b> {get_label(target, TARGET_LABELS)}<br>
            <b>Модель:</b> {get_label(model, MODEL_LABELS)}<br>
            <b>Спецификация:</b> {get_label(specification, SPEC_LABELS)}<br>
            <b>Данные:</b> {get_label(data_version, VERSION_LABELS)}
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    best_title = (
        "Лучшая модель в уровнях"
        if data_version == "level"
        else "Лучшая модель в лог-приростах"
    )

    best_text = get_best_model_text(
        final_results=final_results,
        target=target,
        data_version=data_version,
    )

    st.markdown(
        f"""
        <div class="info-box">
            <b>{best_title}</b><br>
            {best_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

# Карточки метрик
metric_cols = st.columns(4)

metric_cols[0].metric("MAE", f"{selected_row['MAE']:.3f}")
metric_cols[1].metric("RMSE", f"{selected_row['RMSE']:.3f}")
metric_cols[2].metric("SMAPE", f"{selected_row['SMAPE']:.2f}%")
metric_cols[3].metric("MedAE", f"{selected_row['MedAE']:.3f}")

# Основные вкладки
tab_forecast, tab_tables, tab_compare = st.tabs(
    [
        "Прогноз",
        "Таблицы",
        "Сравнение",
    ]
)

# Вкладка прогноза
with tab_forecast:
    st.subheader("Фактические значения и прогноз")

    fig = plot_forecast(
        forecasts=forecasts,
        monthly_errors=monthly_errors_level,
        target=target,
        model=model,
        specification=specification,
        data_version=data_version,
    )

    if fig is None:
        st.info("Для этой модели нет прогноза")
    else:
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Ошибки прогноза")

    err_fig = plot_errors(
        forecasts=forecasts,
        monthly_errors=monthly_errors_level,
        target=target,
        model=model,
        specification=specification,
        data_version=data_version,
    )

    if err_fig is None:
        st.info("Нет данных для графика ошибок")
    else:
        st.plotly_chart(err_fig, use_container_width=True)

# Вкладка таблиц
with tab_tables:
    st.subheader("Помесячный прогноз")

    table = monthly_errors_level.copy()

    if not table.empty:
        table = table[
            (table["target"] == target)
            & (table["model"] == model)
            & (table["specification"] == specification)
        ].copy()

        if "data_version" in table.columns:
            table = table[table["data_version"] == data_version].copy()

    if table.empty:
        st.info("Помесячная таблица доступна только для сохранённых моделей")
    else:
        show_cols = [
            "date",
            "actual",
            "forecast",
            "error",
            "abs_error",
        ]

        show_cols = [col for col in show_cols if col in table.columns]

        st.dataframe(
            table[show_cols].reset_index(drop=True),
            use_container_width=True,
        )

    st.subheader("Лучшие модели в уровнях")

    if best_models_level.empty:
        st.info("Файл с лучшими моделями не найден")
    else:
        st.dataframe(
            best_models_level.reset_index(drop=True),
            use_container_width=True,
        )

# Вкладка сравнения
with tab_compare:
    st.subheader("Сравнение моделей")

    compare_df = final_results[
        (final_results["target"] == target)
        & (final_results["data_version"] == data_version)
    ].copy()

    if compare_df.empty:
        st.info("Нет данных для сравнения")
    else:
        compare_df = compare_df.sort_values("RMSE").reset_index(drop=True)

        st.dataframe(
            compare_df,
            use_container_width=True,
        )