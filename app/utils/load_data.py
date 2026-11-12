# ============================================
# Загрузка данных
# ============================================

from pathlib import Path
import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp1251")


def _prepare_dates(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "date" not in df.columns:
        return df

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def load_app_data(data_dir: Path) -> dict:
    """Читает все CSV-файлы, которые использует интерфейс"""

    final_level = _read_csv(data_dir / "final_model_results_level.csv")
    final_growth = _read_csv(data_dir / "final_model_results_growth.csv")

    # Если итоговый файл уже общий, тоже поддерживаем
    final_all = _read_csv(data_dir / "final_model_results.csv")

    if not final_all.empty:
        final_results = final_all.copy()
    else:
        parts = []
        if not final_level.empty:
            final_level = final_level.copy()
            if "data_version" not in final_level.columns:
                final_level["data_version"] = "level"
            parts.append(final_level)

        if not final_growth.empty:
            final_growth = final_growth.copy()
            if "data_version" not in final_growth.columns:
                final_growth["data_version"] = "growth"
            parts.append(final_growth)

        final_results = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

    best_models_level = _read_csv(data_dir / "best_models_level.csv")
    monthly_errors_level = _prepare_dates(_read_csv(data_dir / "monthly_errors_level.csv"))
    forecasts = _prepare_dates(_read_csv(data_dir / "forecasts.csv"))

    # Приводим specification к строке, чтобы '-' не превращался в NaN
    for frame in [final_results, best_models_level, monthly_errors_level, forecasts]:
        if not frame.empty and "specification" in frame.columns:
            frame["specification"] = frame["specification"].fillna("-").astype(str)

    return {
        "final_results": final_results,
        "best_models_level": best_models_level,
        "monthly_errors_level": monthly_errors_level,
        "forecasts": forecasts,
    }
