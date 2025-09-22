import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="🎬 MovieLens Dashboard")

# --- Load & Clean Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("Week-03-EDA-and-Dashboards/data/movie_ratings.csv")
    df['genres'] = df['genres'].str.split('|')
    df = df.explode('genres')
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")
all_genres = sorted(df['genres'].unique())
selected_genres = st.sidebar.multiselect("Select Genres", all_genres, default=all_genres[:5])

year_min, year_max = int(df['year'].min()), int(df['year'].max())
selected_years = st.sidebar.slider("Select Release Year Range", year_min, year_max, (1990, 2000))

age_min, age_max = int(df['age'].min()), int(df['age'].max())
selected_ages = st.sidebar.slider("Select Viewer Age Range", age_min, age_max, (18, 60))

# --- Apply Filters ---
filtered_df = df[
    (df['genres'].isin(selected_genres)) &
    (df['year'] >= selected_years[0]) &
    (df['year'] <= selected_years[1]) &
    (df['age'] >= selected_ages[0]) &
    (df['age'] <= selected_ages[1])
]

# --- Title ---
st.title("🎥 MovieLens Ratings Dashboard")
st.markdown("Explore viewer ratings, genre trends, and age-based insights from the MovieLens dataset.")

# --- Q1: Genre Breakdown ---
with st.container():
    st.subheader("📊 1. Breakdown of Genres for Rated Movies")
    genre_counts = filtered_df['genres'].value_counts().reset_index()
    genre_counts.columns = ['Genre', 'Rating Count']
    fig1, ax1 = plt.subplots()
    sns.barplot(data=genre_counts, y="Genre", x="Rating Count", palette="viridis", ax=ax1)
    ax1.set_xlabel("Number of Ratings")
    ax1.set_ylabel("Genre")
    st.pyplot(fig1)
    st.markdown("**Insight:** Comedy, Drama, and Action dominate viewer attention, reflecting mainstream popularity.")

# --- Q2: Highest Viewer Satisfaction by Genre ---
with st.container():
    st.subheader("🌟 2. Genres with Highest Viewer Satisfaction")
    fig2, ax2 = plt.subplots()
    sns.violinplot(data=filtered_df, x="genres", y="rating", palette="Set2", ax=ax2)
    ax2.set_ylabel("Viewer Rating (1–5)")
    ax2.set_xlabel("Genre")
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    st.pyplot(fig2)
    st.markdown("**Insight:** Genres like Documentary and Animation often show higher median ratings and tighter distributions.")

# --- Q3: Mean Rating Across Release Years ---
with st.container():
    st.subheader("📈 3. Mean Rating Across Movie Release Years")
    yearly_avg = filtered_df.groupby("year")["rating"].mean().reset_index()
    fig3, ax3 = plt.subplots()
    sns.lineplot(data=yearly_avg, x="year", y="rating", ax=ax3)
    ax3.set_ylabel("Mean Rating")
    ax3.set_xlabel("Release Year")
    st.pyplot(fig3)
    st.markdown("**Insight:** Older films tend to have slightly higher average ratings, possibly due to nostalgic bias or selective viewing.")

# --- Q4: Top 5 Best-Rated Movies (≥50 and ≥150 Ratings) ---
with st.container():
    st.subheader("🏆 4. Top 5 Best-Rated Movies")
    movie_stats = filtered_df.groupby("title").agg({"rating": ["mean", "count"]})
    movie_stats.columns = ["mean_rating", "rating_count"]
    top_50 = movie_stats[movie_stats["rating_count"] >= 50].sort_values("mean_rating", ascending=False).head(5)
    top_150 = movie_stats[movie_stats["rating_count"] >= 150].sort_values("mean_rating", ascending=False).head(5)
    st.markdown("**Movies with ≥50 Ratings**")
    st.dataframe(top_50.style.highlight_max("mean_rating", color="lightgreen"))
    
    st.markdown("**Movies with ≥150 Ratings**")
    st.dataframe(top_150.style.highlight_max("mean_rating", color="lightblue"))
    
    st.markdown("**Insight:** Filtering by rating count avoids flukes and highlights consistently loved films.")

# --- Q5: Rating vs Age for Selected Genres with Chart Toggle ---
with st.container():
    st.subheader("👥 5. Rating vs Age for Selected Genres")

    chart_type = st.sidebar.radio("Choose Chart Type for Genre-Age Analysis", ["Line Plot", "Heatmap"])

    genre_subset = filtered_df[filtered_df['genres'].isin(selected_genres)]

    if chart_type == "Line Plot":
        g = sns.FacetGrid(genre_subset, col="genres", col_wrap=2, height=4)
        g.map(sns.lineplot, "age", "rating")
        st.pyplot(g.fig)
        st.markdown("**Insight:** Line plots show how ratings shift across continuous age — older viewers tend to rate Drama and Romance higher, while younger viewers lean toward Comedy and Action.")

    elif chart_type == "Heatmap":
        genre_subset['age_bin'] = pd.cut(genre_subset['age'], bins=[10, 20, 30, 40, 50, 60, 70], labels=["10s", "20s", "30s", "40s", "50s", "60s"])
        pivot = genre_subset.pivot_table(index="genres", columns="age_bin", values="rating", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.heatmap(pivot, annot=True, cmap="coolwarm", ax=ax)
        ax.set_xlabel("Viewer Age Group")
        ax.set_ylabel("Genre")
        st.pyplot(fig)
        st.markdown("**Insight:** Heatmaps reveal which genre-age combinations have the highest satisfaction — e.g., Romance in 40s, Comedy in 20s.")


# --- Q6: Ratings Volume vs Mean Rating per Genre ---
with st.container():
    st.subheader("📉 6. Ratings Volume vs Mean Rating per Genre")
    genre_stats = filtered_df.groupby("genres").agg({"rating": ["mean", "count"]})
    genre_stats.columns = ["mean_rating", "rating_count"]
    fig6, ax6 = plt.subplots()
    sns.scatterplot(data=genre_stats, x="rating_count", y="mean_rating", ax=ax6)
    ax6.set_xlabel("Number of Ratings")
    ax6.set_ylabel("Mean Rating")
    st.pyplot(fig6)
    st.markdown("**Insight:** No strong correlation — some niche genres have high ratings despite low volume.")

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ by Patience · Powered by Streamlit · Dataset: movie_ratings_EC.csv")
