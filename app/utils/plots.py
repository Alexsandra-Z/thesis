# ============================================
# Графики
# ============================================

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def _filter_forecasts(forecasts, target, model, specification, data_version):
    if forecasts.empty:
        return pd.DataFrame()

    required = {"date", "target", "model", "specification", "data_version", "split", "value"}
    if not required.issubset(set(forecasts.columns)):
        return pd.DataFrame()

    return forecasts[
        (forecasts["target"] == target)
        & (forecasts["model"] == model)
        & (forecasts["specification"].astype(str) == str(specification))
        & (forecasts["data_version"] == data_version)
    ].copy()


def _filter_monthly_errors(monthly_errors, target, model, specification, data_version):
    if monthly_errors.empty:
        return pd.DataFrame()

    required = {"date", "target", "model", "specification", "actual", "forecast"}
    if not required.issubset(set(monthly_errors.columns)):
        return pd.DataFrame()

    df = monthly_errors[
        (monthly_errors["target"] == target)
        & (monthly_errors["model"] == model)
        & (monthly_errors["specification"].astype(str) == str(specification))
    ].copy()

    if "data_version" in df.columns:
        df = df[df["data_version"] == data_version]

    return df


def plot_forecast(forecasts, monthly_errors, target, model, specification, data_version):
    """строит train/test/forecast, если есть forecasts.csv; иначе test/forecast."""

    fc = _filter_forecasts(forecasts, target, model, specification, data_version)

    fig = go.Figure()

    if not fc.empty:
        for split, name in [("train", "train"), ("test", "test"), ("forecast", "forecast")]:
            part = fc[fc["split"] == split]
            if part.empty:
                continue

            fig.add_trace(
                go.Scatter(
                    x=part["date"],
                    y=part["value"],
                    mode="lines+markers" if split != "train" else "lines",
                    name=name,
                )
            )

        fig.update_layout(
            height=520,
            xaxis_title="Дата",
            yaxis_title=target,
            legend_title="Ряд",
            hovermode="x unified",
        )
        return fig

    me = _filter_monthly_errors(monthly_errors, target, model, specification, data_version)
    if me.empty:
        return None

    fig.add_trace(
        go.Scatter(
            x=me["date"],
            y=me["actual"],
            mode="lines+markers",
            name="test",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=me["date"],
            y=me["forecast"],
            mode="lines+markers",
            name="forecast",
        )
    )

    fig.update_layout(
        height=520,
        xaxis_title="Дата",
        yaxis_title=target,
        legend_title="Ряд",
        hovermode="x unified",
    )
    return fig


def plot_errors(forecasts, monthly_errors, target, model, specification, data_version):
    me = _filter_monthly_errors(monthly_errors, target, model, specification, data_version)

    if me.empty:
        fc = _filter_forecasts(forecasts, target, model, specification, data_version)
        if fc.empty:
            return None

        test = fc[fc["split"] == "test"][["date", "value"]].rename(columns={"value": "actual"})
        pred = fc[fc["split"] == "forecast"][["date", "value"]].rename(columns={"value": "forecast"})
        me = pd.merge(test, pred, on="date", how="inner")

    if me.empty:
        return None

    me = me.copy()
    if "error" not in me.columns:
        me["error"] = me["actual"] - me["forecast"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=me["date"],
            y=me["error"],
            name="error",
        )
    )
    fig.add_hline(y=0, line_dash="dash")
    fig.update_layout(
        height=360,
        xaxis_title="Дата",
        yaxis_title="Ошибка",
        hovermode="x unified",
    )
    return fig


def plot_metric_comparison(compare_df):
    df = compare_df.copy()
    df["model_spec"] = df["model"].astype(str) + " | " + df["specification"].astype(str)
    df = df.sort_values("RMSE")

    fig = px.bar(
        df,
        x="model_spec",
        y="RMSE",
        hover_data=["MAE", "SMAPE"],
        labels={"model_spec": "Модель / спецификация", "RMSE": "RMSE"},
    )
    fig.update_layout(
        height=460,
        xaxis_tickangle=-35,
    )
    return fig
