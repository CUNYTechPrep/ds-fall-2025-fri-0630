from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Hamzah's Movie Dashboard", layout="wide")


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    """Load the movie ratings CSV from the data folder."""
    data_path = Path(__file__).resolve().parents[2] / "data" / "movie_ratings.csv"
    return pd.read_csv(data_path)


def show_header():
    st.title("Hamzah's MovieLens Dashboard")
    st.caption("Week 3 — EDA and Interactive Charts")


def sidebar_controls(df: Optional[pd.DataFrame]) -> dict:
    with st.sidebar:
        st.header("Options")
        show_raw = st.toggle("Preview Raw Data", value=False)
    return {"show_raw": show_raw}


def main():
    show_header()

    # Load dataset
    try:
        df = load_data()
    except FileNotFoundError:
        st.error("Cannot find the data file. Check that movie_ratings.csv exists in the data folder.")
        return

    controls = sidebar_controls(df)

    if controls.get("show_raw"):
        with st.expander("Raw Data Preview (first 50 rows)"):
            st.dataframe(df.head(50), use_container_width=True)

    # Tabs
    tabs = st.tabs([
        "Q1: Genre Pie Chart",
        "Q2: Average Rating by Genre",
        "Q3: Rating Trend by Year",
        "Q4: Top Rated Movies"
    ])

    # --- Q1: Genre Breakdown ---
    with tabs[0]:
        st.subheader("Q1: How popular are the different genres?")
        st.caption("Pie chart showing count of ratings per genre.")

        min_pct = st.slider(
            "Combine small genres into 'Other' if below (%)",
            0.0, 10.0, 2.0, 0.5
        )

        # Aggregate
        genre_counts = df.groupby("genres").size().reset_index(name="count")
        genre_counts["pct"] = 100 * genre_counts["count"] / genre_counts["count"].sum()

        major = genre_counts[genre_counts["pct"] >= min_pct]
        minor = genre_counts[genre_counts["pct"] < min_pct]
        if not minor.empty:
            other_row = pd.DataFrame({
                "genres": ["Other"],
                "count": [minor["count"].sum()],
                "pct": [minor["pct"].sum()]
            })
            display_df = pd.concat([major, other_row], ignore_index=True)
        else:
            display_df = major

        fig = px.pie(
            display_df,
            names="genres",
            values="count",
            title="Genre Distribution of Movie Ratings",
            hole=0.1
        )
        fig.update_traces(textposition="inside", textinfo="label+percent")
        st.plotly_chart(fig, use_container_width=True)

    # --- Q2: Avg Rating by Genre ---
    with tabs[1]:
        st.subheader("Q2: Which genres get the highest ratings?")
        st.caption("Bar chart of mean ratings per genre.")

        col1, col2 = st.columns(2)
        with col1:
            min_ratings = st.number_input("Min ratings per genre", 0, 10000, 50, 10)
        with col2:
            sort_order = st.radio("Sort ratings", ["High → Low", "Low → High"], horizontal=True)

        genre_stats = df.groupby("genres").agg(
            avg_rating=("rating", "mean"),
            num_ratings=("rating", "size")
        ).reset_index()
        filtered = genre_stats[genre_stats["num_ratings"] >= min_ratings]
        ascending = sort_order == "Low → High"
        filtered = filtered.sort_values("avg_rating", ascending=ascending)

        fig2 = px.bar(
            filtered,
            x="genres",
            y="avg_rating",
            hover_data={"num_ratings": True, "avg_rating": ":.2f"},
            title="Average Ratings by Genre"
        )
        fig2.update_layout(xaxis_title="Genre", yaxis_title="Avg Rating (1–5)")
        st.plotly_chart(fig2, use_container_width=True)

    # --- Q3: Avg Rating by Year ---
    with tabs[2]:
        st.subheader("Q3: How do ratings change over years?")
        st.caption("Line chart of average rating per release year.")

        min_year, max_year = int(df["year"].min()), int(df["year"].max())
        year_range = st.slider("Select Year Range", min_year, max_year, (min_year, max_year))
        min_count_year = st.number_input("Min ratings per year", 0, 100000, 50, 10)
        smooth_window = st.slider("Smoothing window (years)", 1, 9, 1)

        year_stats = df.groupby("year").agg(
            avg_rating=("rating", "mean"),
            n_ratings=("rating", "size")
        ).reset_index()
        mask = (year_stats["year"] >= year_range[0]) & (year_stats["year"] <= year_range[1])
        year_filtered = year_stats[mask & (year_stats["n_ratings"] >= min_count_year)]

        if smooth_window > 1 and not year_filtered.empty:
            year_filtered["avg_smoothed"] = year_filtered["avg_rating"].rolling(window=smooth_window, center=True).mean()
        else:
            year_filtered["avg_smoothed"] = year_filtered["avg_rating"]

        fig3 = px.line(
            year_filtered,
            x="year",
            y="avg_smoothed",
            hover_data={"n_ratings": True, "avg_rating": ":.2f"},
            title="Average Rating Trend by Year"
        )
        fig3.update_layout(xaxis_title="Year", yaxis_title="Avg Rating")
        st.plotly_chart(fig3, use_container_width=True)

    # --- Q4: Top Movies ---
    with tabs[3]:
        st.subheader("Q4: Highest Rated Movies")
        st.caption("Top N movies with minimum number of ratings.")

        col1, col2 = st.columns(2)
        with col1:
            min_movie_ratings = st.number_input("Min ratings per movie", 1, 100000, 50, 10)
        with col2:
            top_n = st.slider("Show Top N Movies", 3, 25, 5)

        movie_stats = df.groupby(["movie_id", "title"]).agg(
            avg_rating=("rating", "mean"),
            n_ratings=("rating", "size")
        ).reset_index()
        filtered_movies = movie_stats[movie_stats["n_ratings"] >= min_movie_ratings]
        top_movies = filtered_movies.sort_values(
            ["avg_rating", "n_ratings"], ascending=[False, False]
        ).head(top_n)

        fig4 = px.bar(
            top_movies,
            y="title",
            x="avg_rating",
            orientation="h",
            hover_data={"n_ratings": True, "avg_rating": ":.2f"},
            title=f"Top {top_n} Movies (Min {min_movie_ratings} Ratings)"
        )
        fig4.update_layout(xaxis_title="Avg Rating", yaxis_title="Movie Title")
        st.plotly_chart(fig4, use_container_width=True)


if __name__ == "__main__":
    main()
