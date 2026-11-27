from dash import Dash, dcc, html
import plotly.graph_objects as go

from main import build_market_snapshot, load_instruments


def create_dashboard(snapshot):
    instrument = snapshot["instrument"]
    benchmark = snapshot["benchmark"]
    figure = go.Figure()
    for asset, key, color in (
        (instrument, "instrument_base_100", "#176b64"),
        (benchmark, "benchmark_base_100", "#596cca"),
    ):
        series = snapshot[key]
        figure.add_scatter(
            x=[row["date"] for row in series],
            y=[row["value"] for row in series],
            mode="lines",
            name=asset["ticker"],
            line={"color": color, "width": 3},
        )

    figure.update_layout(
        title="Instrument vs Benchmark",
        xaxis_title="Date",
        yaxis_title="Base 100",
        template="plotly_white",
        hovermode="x unified",
        legend={"orientation": "h"},
        margin={"l": 56, "r": 24, "t": 60, "b": 50},
    )

    indicators = (
        ("Instrument return", f"{snapshot['instrument_return']:+.2f}%"),
        ("Benchmark return", f"{snapshot['benchmark_return']:+.2f}%"),
        ("Relative performance", f"{snapshot['relative_performance']:+.2f} pp"),
    )
    app = Dash(__name__, title="MarketPulse")
    app.layout = html.Main(
        [
            html.H1("MarketPulse", style={"margin": "0 0 12px"}),
            html.P(
                f"{snapshot['provider']} · {snapshot['access_mode']} · "
                f"Lookback: {snapshot['lookback']} · Interval: {snapshot['interval']}"
            ),
            html.P(
                f"{instrument['ticker']} — {instrument['name']} vs "
                f"{benchmark['ticker']} — {benchmark['name']}"
            ),
            html.Div(
                [
                    html.Div(
                        [html.Div(label), html.Strong(value, style={"fontSize": "1.7rem"})],
                        style={
                            "flex": "1 1 180px",
                            "background": "#eef3f6",
                            "borderRadius": "8px",
                            "padding": "14px 18px",
                        },
                    )
                    for label, value in indicators
                ],
                style={"display": "flex", "flexWrap": "wrap", "gap": "12px"},
            ),
            dcc.Graph(figure=figure, config={"displayModeBar": False}),
        ],
        style={
            "maxWidth": "1080px",
            "margin": "0 auto",
            "padding": "24px",
            "fontFamily": "system-ui, sans-serif",
            "color": "#172938",
        },
    )
    return app


if __name__ == "__main__":
    assets = load_instruments()
    snapshot = build_market_snapshot(assets["instrument"], assets["benchmark"])
    create_dashboard(snapshot).run(debug=False)
