"""PSET 5: interactive explorer for the World Happiness Report 2025 rankings."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_FILE = Path(__file__).parent / "world_happiness_2025.csv"

SCORE = "Happiness score"
RANK = "Happiness rank"
COUNTRY = "Country"
FACTORS = [
    "GDP per capita",
    "Social support",
    "Healthy life expectancy",
    "Freedom to make life choices",
    "Generosity",
    "Perceptions of corruption",
]
DEFAULT_COUNTRY = "Mongolia"

HIGHLIGHT = "#2a78d6"
CONTEXT = "#898781"
INK = "#52514e"
TITLE_INK = "#0b0b0b"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)


def in_sentence(factor: str) -> str:
    """Lowercase a factor name for use mid-sentence, keeping the acronym GDP."""
    return factor if factor.startswith("GDP") else factor.lower()


def style_chart(fig, title: str):
    axis = dict(
        gridcolor=GRID,
        linecolor=BASELINE,
        zeroline=False,
        tickfont_color=INK,
        automargin=True,
        title_standoff=12,
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=TITLE_INK), x=0),
        font=dict(family='system-ui, -apple-system, "Segoe UI", sans-serif', color=INK),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        margin=dict(l=10, r=30, t=80, b=10),
        hoverlabel=dict(bgcolor="white", font_color=TITLE_INK),
    )
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    return fig


def scatter_chart(data: pd.DataFrame, factor: str, country: str):
    plot_data = data.dropna(subset=[factor])
    selected = plot_data[plot_data[COUNTRY] == country]
    others = plot_data[plot_data[COUNTRY] != country]

    hover_data = {factor: ":.3f", SCORE: ":.3f", RANK: True}
    fig = px.scatter(
        others,
        x=factor,
        y=SCORE,
        hover_name=COUNTRY,
        hover_data=hover_data,
        color_discrete_sequence=[CONTEXT],
    )
    fig.update_traces(
        name="Other countries",
        showlegend=True,
        marker=dict(size=8, opacity=0.65, line=dict(width=1, color=SURFACE)),
    )

    # The selected country goes on top, labeled directly on the chart.
    if not selected.empty:
        row = selected.iloc[0]
        fig.add_scatter(
            x=[row[factor]],
            y=[row[SCORE]],
            mode="markers+text",
            name=country,
            text=[f"<b>{country}</b>"],
            textposition="top center",
            textfont=dict(color=TITLE_INK, size=13),
            cliponaxis=False,
            marker=dict(size=14, color=HIGHLIGHT, line=dict(width=2, color=SURFACE)),
            hovertemplate=(
                f"<b>{country}</b><br>{factor}: %{{x:.3f}}<br>"
                f"{SCORE}: %{{y:.3f}}<br>{RANK}: {row[RANK]}<extra></extra>"
            ),
        )

    fig.update_layout(
        height=520,
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.0, x=0),
    )
    fig.update_xaxes(title=f"{factor} (contribution to score)")
    fig.update_yaxes(title=f"{SCORE} (0 to 10)")
    return style_chart(fig, f"{factor} and happiness across countries")


def ranking_chart(data: pd.DataFrame, factor: str, country: str, top_n: int):
    ranked = data.dropna(subset=[factor]).copy()
    ranked["Factor rank"] = ranked[factor].rank(ascending=False, method="min").astype(int)
    ranked = ranked.sort_values([factor, COUNTRY], ascending=[False, True])

    # Keep the selected country visible even when it falls outside the top N.
    shown = ranked[ranked.index.isin(ranked.index[:top_n]) | (ranked[COUNTRY] == country)].copy()
    shown["Label"] = "#" + shown["Factor rank"].astype(str) + " " + shown[COUNTRY]
    shown["Series"] = shown[COUNTRY].eq(country).map({True: country, False: "Other"})

    fig = px.bar(
        shown,
        x=factor,
        y="Label",
        orientation="h",
        color="Series",
        color_discrete_map={country: HIGHLIGHT, "Other": CONTEXT},
        hover_name=COUNTRY,
        hover_data={factor: ":.3f", "Factor rank": True, "Label": False, "Series": False},
    )
    fig.update_traces(marker_cornerradius=4)
    fig.update_layout(
        height=520,
        bargap=0.25,
        showlegend=False,
    )
    fig.update_yaxes(
        title=None,
        showgrid=False,
        categoryorder="array",
        categoryarray=shown["Label"].tolist()[::-1],
    )
    fig.update_xaxes(title=f"{factor} (contribution to score)", rangemode="tozero")
    return style_chart(fig, f"Top {top_n} countries by {in_sentence(factor)}")


st.set_page_config(page_title="World Happiness 2025", page_icon="🌍", layout="wide")

happiness = load_data()
total = len(happiness)

st.title("World Happiness Explorer 2025")
st.write(
    f"Compare {total} countries from the "
    "[World Happiness Report 2025](https://worldhappiness.report/ed/2025/). "
    "Pick a factor and a country to see how they relate to happiness."
)

factor_col, country_col, top_col = st.columns([1.2, 1.2, 1])

factor = factor_col.selectbox("Factor", FACTORS)

countries = sorted(happiness[COUNTRY])
country = country_col.selectbox(
    "Country to highlight", countries, index=countries.index(DEFAULT_COUNTRY)
)

top_n = top_col.slider("Countries in ranking", min_value=5, max_value=25, value=10)

row = happiness[happiness[COUNTRY] == country].iloc[0]
has_factor = pd.notna(row[factor])

tile_1, tile_2, tile_3 = st.columns(3)
tile_1.metric(f"{country}: happiness rank", f"#{row[RANK]} of {total}")
tile_2.metric(f"{country}: happiness score", f"{row[SCORE]:.3f}")
if has_factor:
    factor_values = happiness[factor].dropna()
    factor_rank = int((factor_values > row[factor]).sum()) + 1
    tile_3.metric(
        f"{country}: {in_sentence(factor)}",
        f"{row[factor]:.3f}",
        f"#{factor_rank} of {len(factor_values)}",
        delta_color="off",
        delta_arrow="off",
    )
else:
    tile_3.metric(f"{country}: {in_sentence(factor)}", "No data")

left, right = st.columns([1.25, 1])
left.plotly_chart(scatter_chart(happiness, factor, country), width="stretch", theme=None)
right.plotly_chart(ranking_chart(happiness, factor, country, top_n), width="stretch", theme=None)

if not has_factor:
    st.warning(f"The report has no {in_sentence(factor)} value for {country}, so it isn't plotted.")

correlation = happiness[factor].corr(happiness[SCORE])
st.write(f"**Correlation between {in_sentence(factor)} and happiness score:** {correlation:.2f}")

st.caption(
    "Happiness score is a 2022-2024 average of people's own 0-10 ratings of their lives. "
    "Factor values are not raw measurements: they estimate how much each factor contributes "
    "to a country's score, so GDP per capita here is not a dollar amount."
)

if factor == "Perceptions of corruption":
    st.caption("For this factor, a higher value means people perceive **less** corruption.")

with st.expander("See the data as a table"):
    st.dataframe(
        happiness[[RANK, COUNTRY, SCORE, *FACTORS]],
        width="stretch",
        hide_index=True,
    )
