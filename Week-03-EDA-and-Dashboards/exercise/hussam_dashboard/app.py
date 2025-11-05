from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="MovieLens Dashboard (Week 3)", layout="wide")


@st.cache_data(ttl=3600)
def load_movie_ratings() -> pd.DataFrame:
    f"""Load the movie ratings dataset from the Week 3 data folder.

    The app is located at: Week-03-EDA-and-Dashboards/exercise/name_dashboard/app.py
    The data lives at:      Week-03-EDA-and-Dashboards/data/movie_ratings.csv
    """
    data_path = Path(__file__).resolve().parents[2] / "data" / "movie_ratings.csv"
    df = pd.read_csv(data_path)
    return df


def render_header() -> None:
    st.title("MovieLens Dashboard")
    st.caption("Week 3 — EDA and Dashboards")


def render_sidebar(df: Optional[pd.DataFrame]) -> dict:
    with st.sidebar:
        st.header("Controls")
        show_raw = st.toggle("Show raw data preview", value=False)

        controls = {"show_raw": show_raw}
        return controls


def main() -> None:
    render_header()

    # Load data
    try:
        df = load_movie_ratings()
    except FileNotFoundError:
        st.error(
            "Could not find data file at ../data/movie_ratings.csv. "
            "Verify the project layout matches the course repo."
        )
        return

    controls = render_sidebar(df)

    if controls.get("show_raw"):
        with st.expander("Raw data (first 50 rows)", expanded=False):
            st.dataframe(df.head(50), use_container_width=True)

    # Tabs per question (outline only for now)
    tabs = st.tabs(
        [
            "Q1: Genre breakdown",
            "Q2: Avg rating by genre",
            "Q3: Avg rating by release year",
            "Q4: Top movies by ratings (placeholder)",
        ]
    )

    with tabs[0]:
        st.subheader("Q1: What's the breakdown of genres for the movies that were rated?")
        st.caption("Pie chart of rating counts by pre-exploded 'genres'.")

        # Controls for grouping small slices
        min_pct = st.slider(
            "Group slices under this percentage into 'Other'",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.5,
            help="Genres contributing less than this percent will be grouped as 'Other'.",
        )

        # Aggregate counts by genre (data is already pre-exploded)
        genre_counts = (
            df.groupby("genres", dropna=False)
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

        total = genre_counts["count"].sum()
        genre_counts["pct"] = 100 * genre_counts["count"] / max(total, 1)

        # Group small categories into 'Other'
        major = genre_counts[genre_counts["pct"] >= min_pct].copy()
        minor = genre_counts[genre_counts["pct"] < min_pct]
        if not minor.empty:
            other_row = pd.DataFrame({
                "genres": ["Other"],
                "count": [int(minor["count"].sum())],
                "pct": [minor["pct"].sum()],
            })
            display_df = pd.concat([major, other_row], ignore_index=True)
        else:
            display_df = major

        fig = px.pie(
            display_df,
            names="genres",
            values="count",
            title="Composition of Ratings by Genre",
            hole=0.0,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("Q2: Which genres have the highest viewer satisfaction?")
        st.caption("Interactive bar chart of mean rating by genre (pre-exploded 'genres').")

        col1, col2 = st.columns([1, 1])
        with col1:
            min_count = st.number_input(
                "Minimum number of ratings per genre",
                min_value=0,
                max_value=10000,
                value=50,
                step=10,
                help="Filter out genres with too few ratings to reduce noise.",
            )
        with col2:
            sort_order = st.radio(
                "Sort by mean rating",
                options=["Descending", "Ascending"],
                horizontal=True,
            )

        # Compute mean rating and counts per genre
        genre_stats = (
            df.groupby("genres", dropna=False)
            .agg(mean_rating=("rating", "mean"), n_ratings=("rating", "size"))
            .reset_index()
        )
        filtered = genre_stats[genre_stats["n_ratings"] >= min_count].copy()
        ascending = sort_order == "Ascending"
        filtered = filtered.sort_values("mean_rating", ascending=ascending)

        fig2 = px.bar(
            filtered,
            x="genres",
            y="mean_rating",
            hover_data={"n_ratings": True, "mean_rating": ":.2f"},
            title="Average Rating by Genre",
        )
        fig2.update_layout(xaxis_title="Genre", yaxis_title="Average Rating (1–5)")
        st.plotly_chart(fig2, use_container_width=True)

    with tabs[2]:
        st.subheader("Q3: How does mean rating change across movie release years?")
        st.caption("Interactive line chart of mean rating by release year.")

        # Controls
        min_year, max_year = int(df["year"].min()), int(df["year"].max())
        year_range = st.slider(
            "Year range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1,
        )
        col1, col2 = st.columns([1, 1])
        with col1:
            min_count_year = st.number_input(
                "Minimum ratings per year",
                min_value=0,
                max_value=100000,
                value=50,
                step=10,
            )
        with col2:
            smooth_window = st.slider(
                "Rolling mean window (years)", min_value=1, max_value=9, value=1, step=1
            )

        # Aggregate by year
        year_stats = (
            df.groupby("year", dropna=False)
            .agg(mean_rating=("rating", "mean"), n_ratings=("rating", "size"))
            .reset_index()
        )
        # Filter by selected range and min count
        lo, hi = year_range
        mask = (year_stats["year"] >= lo) & (year_stats["year"] <= hi)
        year_filtered = year_stats[mask & (year_stats["n_ratings"] >= min_count_year)].copy()
        year_filtered = year_filtered.sort_values("year")

        # Optional smoothing
        if smooth_window and smooth_window > 1 and not year_filtered.empty:
            year_filtered["mean_rating_smoothed"] = (
                year_filtered["mean_rating"].rolling(window=smooth_window, center=True).mean()
            )
        else:
            year_filtered["mean_rating_smoothed"] = year_filtered["mean_rating"]

        fig3 = px.line(
            year_filtered,
            x="year",
            y="mean_rating_smoothed",
            hover_data={"n_ratings": True, "mean_rating": ":.2f"},
            title="Movie Release Year vs Average Rating",
        )
        fig3.update_layout(xaxis_title="Movie Release Year", yaxis_title="Average Rating")
        st.plotly_chart(fig3, use_container_width=True)

    with tabs[3]:
        st.subheader("Q4: Top movies by average rating (interactive)")
        st.caption("Horizontal bar chart of top movies; size = number of ratings.")

        col1, col2 = st.columns([1, 1])
        with col1:
            min_ratings_movie = st.number_input(
                "Minimum number of ratings per movie",
                min_value=1,
                max_value=100000,
                value=50,
                step=10,
            )
        with col2:
            top_n = st.slider("Top N movies", min_value=3, max_value=25, value=5, step=1)

        movie_stats = (
            df.groupby(["movie_id", "title"], dropna=False)
            .agg(mean_rating=("rating", "mean"), n_ratings=("rating", "size"))
            .reset_index()
        )
        movie_filtered = movie_stats[movie_stats["n_ratings"] >= min_ratings_movie].copy()
        top_movies = movie_filtered.sort_values(
            ["mean_rating", "n_ratings"], ascending=[False, False]
        ).head(top_n)

        # Plot horizontal bar where bar length is mean rating; marker size encodes n_ratings
        fig4 = px.bar(
            top_movies,
            y="title",
            x="mean_rating",
            orientation="h",
            hover_data={"n_ratings": True, "mean_rating": ":.2f"},
            title=f"Top {top_n} Movies by Average Rating (min {min_ratings_movie} ratings)",
        )
        fig4.update_layout(xaxis_title="Average Rating (1–5)", yaxis_title="Movie Title")
        st.plotly_chart(fig4, use_container_width=True)


if __name__ == "__main__":
    main()

