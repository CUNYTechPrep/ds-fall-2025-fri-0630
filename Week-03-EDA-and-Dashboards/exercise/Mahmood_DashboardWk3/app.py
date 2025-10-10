import streamlit as st
import pandas as pd
from pathlib import Path
import os
import importlib.util

try:
    import plotly.express as px
except ImportError as e:
    st.error(f"Failed to import Plotly: {e}. Install with `pip install plotly`.")
    st.stop()
# Detect statsmodels without importing to avoid unresolved-import warnings
HAS_SM = importlib.util.find_spec("statsmodels") is not None

st.set_page_config(page_title="🎬 MovieLens Dashboard", page_icon="🎬", layout="wide")

@st.cache_data
def load_movies() -> pd.DataFrame:
    script_dir = Path(os.path.dirname(__file__)).resolve()
    # Support either app root or data/ subfolder
    candidates = [
        script_dir / "movie_ratings.csv",
        script_dir / "data" / "movie_ratings.csv",
        script_dir / "movie_ratings_EC.csv",
        script_dir / "data" / "movie_ratings_EC.csv",
    ]
    df = None
    for p in candidates:
        if p.exists():
            df = pd.read_csv(p)
            break
    if df is None:
        st.error("movie_ratings.csv not found. Place it in app folder or data/ subfolder.")
        return pd.DataFrame()
    # Normalize and coerce
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    for c in ["rating", "age", "year", "rating_year"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "genres" in df.columns:
        df["genres"] = df["genres"].fillna("")
    return df

st.title("🎬 MovieLens Data Analysis")
st.caption("Interactive dashboard answering the Week 3 questions.")

df = load_movies()
if df.empty:
    st.stop()

# Build filter controls
with st.sidebar:
    st.header("Filters")
    age_min = int(df["age"].min()) if "age" in df.columns and df["age"].notna().any() else 0
    age_max = int(df["age"].max()) if "age" in df.columns and df["age"].notna().any() else 100
    sel_age = st.slider("Age", min_value=age_min, max_value=age_max, value=(age_min, age_max)) if age_min < age_max else None

    genders = sorted([g for g in df.get("gender", pd.Series()).dropna().unique().tolist()]) if "gender" in df.columns else []
    sel_gender = st.multiselect("Gender", genders, default=genders)

    occupations = sorted([o for o in df.get("occupation", pd.Series()).dropna().unique().tolist()]) if "occupation" in df.columns else []
    sel_occ = st.multiselect("Occupation", occupations, default=occupations[:10] if len(occupations) > 10 else occupations)

    years = sorted(df.get("year", pd.Series()).dropna().unique().tolist()) if "year" in df.columns else []
    if years:
        y_min, y_max = int(min(years)), int(max(years))
        sel_year = st.slider("Release year", min_value=y_min, max_value=y_max, value=(y_min, y_max))
    else:
        sel_year = None

    # Genre selection from exploded unique list
    genre_pool = sorted(set(g.strip() for s in df.get("genres", pd.Series([""])).astype(str) for g in s.split("|") if g.strip()))
    sel_genres = st.multiselect("Genres (any)", genre_pool)

# Filtering
mask = pd.Series(True, index=df.index)
if sel_age is not None and "age" in df.columns:
    a1, a2 = sel_age
    mask &= df["age"].between(a1, a2)
if sel_gender and "gender" in df.columns:
    mask &= df["gender"].isin(sel_gender)
if sel_occ and "occupation" in df.columns:
    mask &= df["occupation"].isin(sel_occ)
if sel_year is not None and "year" in df.columns:
    y1, y2 = sel_year
    mask &= df["year"].between(y1, y2)
if sel_genres and "genres" in df.columns:
    mask &= df["genres"].astype(str).apply(lambda s: any(g in s.split("|") for g in sel_genres))

fdf = df[mask].copy()

st.markdown("---")

# Q1: Genre breakdown (explode genres and count)
st.subheader("Q1. Genre breakdown of rated movies")
if not fdf.empty and "genres" in fdf.columns:
    gdf = fdf.assign(genres=fdf["genres"].astype(str).str.split("|")).explode("genres")
    gdf = gdf[gdf["genres"].str.len() > 0]
    genre_counts = gdf["genres"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]
    if not genre_counts.empty:
        fig = px.bar(genre_counts, x="genre", y="count", title="Genre Count (Filtered)")
        st.plotly_chart(fig, width='stretch')
    st.dataframe(genre_counts.head(50), width='content')
else:
    st.info("No genre data available after filters.")

st.markdown("---")

# Q2: Highest viewer satisfaction by genre (mean rating with min N)
st.subheader("Q2. Highest-rated genres")
min_n = st.slider("Minimum ratings per genre", 10, 300, 50, step=10)
if not fdf.empty and {"genres", "rating"}.issubset(fdf.columns):
    gdf2 = fdf.assign(genres=fdf["genres"].astype(str).str.split("|")).explode("genres")
    gdf2 = gdf2[gdf2["genres"].str.len() > 0]
    genre_stats = (
        gdf2.groupby("genres")["rating"]
        .agg(count="count", mean="mean")
        .reset_index()
        .query("count >= @min_n")
        .sort_values(["mean", "count"], ascending=[False, False])
    )
    if not genre_stats.empty:
        fig2 = px.bar(genre_stats, x="genres", y="mean", hover_data=["count"], title=f"Mean Rating by Genre (n>={min_n})", range_y=[1,5])
        st.plotly_chart(fig2, width='stretch')
    st.dataframe(genre_stats, width='content')
else:
    st.info("Ratings/genres not available.")

st.markdown("---")

# Q3: Mean rating over release years
st.subheader("Q3. Mean rating across movie release years")
if not fdf.empty and {"year", "rating"}.issubset(fdf.columns):
    year_stats = (
        fdf.dropna(subset=["year", "rating"]).groupby("year")["rating"].mean().reset_index()
        .sort_values("year")
    )
    if not year_stats.empty:
        fig3 = px.line(year_stats, x="year", y="rating", title="Mean Rating by Release Year")
        st.plotly_chart(fig3, width='stretch')
    st.dataframe(year_stats.tail(100), width='content')
else:
    st.info("Year/rating not available.")

st.markdown("---")

# Q4: Best-rated movies with thresholds
st.subheader("Q4. Best-rated movies with minimum rating counts")
if not fdf.empty and {"title", "rating"}.issubset(fdf.columns):
    movie_stats = (
        fdf.groupby("title")["rating"].agg(count="count", mean="mean").reset_index()
    )
    top50 = movie_stats.query("count >= 50").sort_values(["mean", "count"], ascending=[False, False]).head(20)
    top150 = movie_stats.query("count >= 150").sort_values(["mean", "count"], ascending=[False, False]).head(20)
    st.write("Top movies (n ≥ 50)")
    st.dataframe(top50, width='content')
    st.write("Top movies (n ≥ 150)")
    st.dataframe(top150, width='content')
else:
    st.info("Missing title or rating column.")

st.markdown("---")

# Extra Credit: rating vs age per selected genres
with st.expander("Extra Credit: Rating vs Age by Genre"):
    if not fdf.empty and {"genres", "rating", "age"}.issubset(fdf.columns):
        ec_genres = st.multiselect("Pick genres", genre_pool[:10], default=genre_pool[:4] if len(genre_pool) >= 4 else genre_pool)
        if ec_genres:
            eg = fdf.assign(genres=fdf["genres"].astype(str).str.split("|")).explode("genres")
            eg = eg[eg["genres"].isin(ec_genres)].dropna(subset=["age", "rating"])
            if not eg.empty:
                trend = "ols" if HAS_SM else None
                fig4 = px.scatter(eg, x="age", y="rating", color="genres", trendline=trend, opacity=0.3, title="Rating vs Age by Genre")
                st.plotly_chart(fig4, width='stretch')
            st.dataframe(
                eg.groupby(["genres"]).agg(n=("rating","count"), mean=("rating","mean")).reset_index(),
                width='content'
            )
        else:
            st.info("Select at least one genre.")
    else:
        st.info("Need genres, rating, and age columns.")

# Extra Credit: volume vs mean rating per genre
with st.expander("Extra Credit: Volume vs Mean Rating per Genre"):
    if not fdf.empty and {"genres", "rating"}.issubset(fdf.columns):
        gg = fdf.assign(genres=fdf["genres"].astype(str).str.split("|")).explode("genres")
        gg = gg[gg["genres"].str.len() > 0]
        gstats = gg.groupby("genres")["rating"].agg(count="count", mean="mean").reset_index()
        if not gstats.empty:
            trend2 = "ols" if HAS_SM else None
            fig5 = px.scatter(gstats, x="count", y="mean", text="genres", trendline=trend2, title="Ratings Volume vs Mean Rating (Genre)", range_y=[1,5])
            fig5.update_traces(textposition="top center")
            st.plotly_chart(fig5, width='stretch')
        st.dataframe(gstats.sort_values("count", ascending=False), width='content')
    else:
        st.info("Ratings/genres not available.")

# Extra Credit: show how to clean movie_ratings_EC.csv
with st.expander("Extra Credit: Clean raw genres from movie_ratings_EC.csv"):
    st.caption("Demo snippet to explode and clean genres from raw CSV if provided.")
    st.code(
        """
import pandas as pd

# Load the original EC file (place it under data/)
raw = pd.read_csv('movie_ratings_EC.csv')
raw['genres'] = raw['genres'].fillna('')

# Explode pipe-separated genres into rows
df_clean = raw.assign(genres=raw['genres'].str.split('|')).explode('genres')
df_clean = df_clean[df_clean['genres'].str.len() > 0]
""".strip(),
        language='python'
    )

st.markdown("---")
st.caption("Built with Streamlit + Plotly. Use sidebar to adjust filters.")


