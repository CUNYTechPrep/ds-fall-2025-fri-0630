import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="🎬 MovieLens Dashboard", layout="wide")
st.title("🎬 MovieLens Ratings Dashboard")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv('/workspaces/ds-fall-2025-fri-0630/Week-03-EDA-and-Dashboards/data/movie_ratings.csv')
    df.columns = df.columns.str.replace(' ', '_').str.lower()
    df['genres'] = df['genres'].str.split('|')
    df = df.explode('genres')
    return df

df = load_data()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    selected_genres = st.multiselect("Select Genres", sorted(df['genres'].unique()), default=['Drama', 'Comedy', 'Action', 'Sci-Fi'])
    min_ratings = st.slider("Minimum Ratings", 0, 500, 50)
    selected_occupations = st.multiselect("Occupation", sorted(df['occupation'].unique()), default=sorted(df['occupation'].unique()))
    selected_genders = st.multiselect("Gender", ['M', 'F'], default=['M', 'F'])

# Apply filters
filtered_df = df[
    df['genres'].isin(selected_genres) &
    df['occupation'].isin(selected_occupations) &
    df['gender'].isin(selected_genders)
]

# Section containers
with st.container():
    st.subheader("📊 Genre Breakdown")
    with st.expander("View genre distribution"):
        genre_counts = filtered_df['genres'].value_counts()
        st.bar_chart(genre_counts)

with st.container():
    st.subheader("⭐ Viewer Satisfaction by Genre")
    with st.expander("Explore average ratings per genre"):
        genre_ratings = filtered_df.groupby('genres')['rating'].agg(['mean', 'count'])
        genre_ratings = genre_ratings[genre_ratings['count'] >= min_ratings].sort_values('mean', ascending=False)
        st.dataframe(genre_ratings)

with st.container():
    st.subheader("📈 Mean Rating Over Time")
    with st.expander("See how ratings evolve by release year"):
        yearly_ratings = filtered_df.groupby('year')['rating'].mean()
        fig, ax = plt.subplots()
        yearly_ratings.plot(ax=ax)
        ax.set_ylim(1, 5)
        ax.set_title("Mean Rating by Release Year")
        st.pyplot(fig)

with st.container():
    st.subheader("🎬 Top-Rated Movies")
    with st.expander("Top movies with enough ratings"):
        movie_stats = filtered_df.groupby('title')['rating'].agg(['mean', 'count'])
        top_movies = movie_stats[movie_stats['count'] >= min_ratings].sort_values('mean', ascending=False).head(5)
        st.dataframe(top_movies)

with st.container():
    st.subheader("📈 Rating vs Age by Genre")
    with st.expander("How age affects ratings across genres"):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=filtered_df, x='age', y='rating', hue='genres', estimator='mean', ax=ax)
        ax.set_title("Average Rating by Age for Selected Genres")
        ax.set_ylabel("Mean Rating")
        ax.set_xlabel("Viewer Age")
        ax.set_ylim(1, 5)
        ax.grid(True)
        st.pyplot(fig)

with st.container():
    st.subheader("👔 Rating Distribution by Occupation")
    with st.expander("Compare how different jobs rate movies"):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=filtered_df, x='occupation', y='rating')
        ax.set_title("Rating Distribution by Occupation")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)

with st.container():
    st.subheader("👩‍🦰👨 Gender Differences in Ratings")
    with st.expander("Average ratings by gender"):
        gender_ratings = filtered_df.groupby('gender')['rating'].mean()
        st.bar_chart(gender_ratings)

with st.container():
    st.subheader("🕰️ Ratings Over Time")
    with st.expander("How viewer ratings changed over the years"):
        yearly = filtered_df.groupby('rating_year')['rating'].mean()
        fig, ax = plt.subplots()
        yearly.plot(ax=ax)
        ax.set_title("Average Rating Over Time")
        st.pyplot(fig)

with st.container():
    st.subheader("📅 Genre Popularity Over Decades")
    with st.expander("Which genres dominated each decade"):
        genre_decade = filtered_df.groupby(['decade', 'genres']).size().unstack().fillna(0)
        st.line_chart(genre_decade)

with st.container():
    st.subheader("📉 Rating vs Movie Age")
    with st.expander("Do older movies get better ratings?"):
        filtered_df['movie_age'] = filtered_df['rating_year'] - filtered_df['year']
        age_bins = pd.cut(filtered_df['movie_age'], bins=10)
        age_rating = filtered_df.groupby(age_bins)['rating'].mean()
        st.bar_chart(age_rating)

with st.container():
    st.subheader("🔥 Heatmap: Ratings by Age and Gender")
    with st.expander("Cross-tab of age and gender rating behavior"):
        pivot = filtered_df.pivot_table(index='age', columns='gender', values='rating', aggfunc='mean')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot, annot=True, cmap='coolwarm')
        st.pyplot(fig)
