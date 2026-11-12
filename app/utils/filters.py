# ============================================
# Подписи и фильтрация таблиц
# ============================================

TARGET_LABELS = {
    "price_sqm": "Средняя цена 1 кв. м",
    "price_index_economy": "Индекс цен эконом/комфорт",
    "price_index_business": "Индекс цен бизнес",
}

MODEL_LABELS = {
    "naive": "Наивная модель",
    "seasonal_naive": "Сезонная наивная модель",
    "SARIMA": "SARIMA",
    "VAR": "VAR",
    "Ridge": "Ridge",
}

SPEC_LABELS = {
    "-": "без факторов",
    "macro_raw": "ипотечно-макроэкономическая, сырые признаки",
    "market_raw": "рыночная, сырые признаки",
    "mixed_raw": "смешанная, сырые признаки",
    "macro_derived": "ипотечно-макроэкономическая, производные признаки",
    "market_derived": "рыночная, производные признаки",
    "mixed_derived": "смешанная, производные признаки",
}


def get_option_list(df, column):
    if df.empty or column not in df.columns:
        return []

    values = df[column].dropna().astype(str).unique().tolist()
    return sorted(values)


def get_filtered_metrics(final_results, target, model, specification, data_version):
    return final_results[
        (final_results["target"] == target)
        & (final_results["model"] == model)
        & (final_results["specification"].astype(str) == str(specification))
        & (final_results["data_version"] == data_version)
    ].copy()


def get_best_model_text(best_models_level, target):
    if best_models_level.empty:
        return "нет данных"

    row = best_models_level[best_models_level["target"] == target]
    if row.empty:
        return "нет данных"

    row = row.iloc[0]
    model = MODEL_LABELS.get(row["model"], row["model"])
    spec = SPEC_LABELS.get(str(row["specification"]), row["specification"])
    rmse = row["RMSE"]

    return f"{model}<br><span class='small-caption'>{spec}, RMSE = {rmse:.3f}</span>"
