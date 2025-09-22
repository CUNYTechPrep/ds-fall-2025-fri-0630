import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from data_cleaning import clean_movie_ratings

st.set_page_config(page_title="🎬 MovieLens Dashboard")
st.title("🎬 MovieLens Ratings Dashboard")

@st.cache_data
def load_data():
    return clean_movie_ratings('Week-03-EDA-and-Dashboards/data/movie_ratings.csv')
    

df = load_data()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    selected_genres = st.multiselect("Genres", sorted(df['genres'].unique()), default=['Drama', 'Comedy'])
    min_ratings = st.slider("Minimum Ratings", 0, 500, 50)
    selected_occupations = st.multiselect("Occupation", sorted(df['occupation'].unique()), default=sorted(df['occupation'].unique()))
    selected_genders = st.multiselect("Gender", ['M', 'F'], default=['M', 'F'])

filtered_df = df[
    df['genres'].isin(selected_genres) &
    df['occupation'].isin(selected_occupations) &
    df['gender'].isin(selected_genders)
]

# Top metrics
st.markdown("### 📊 Overview")
col1, col2, col3 = st.columns(3)
col1.metric("🎞️ Unique Movies", df['title'].nunique())
col2.metric("👤 Unique Users", df['user_id'].nunique())
col3.metric("⭐ Avg Rating", round(df['rating'].mean(), 2))

# Genre Breakdown + Viewer Satisfaction
st.markdown("### 🎭 Genre Insights")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Genre Distribution")
    genre_counts = filtered_df['genres'].value_counts()
    st.bar_chart(genre_counts)
with col2:
    st.subheader("Viewer Satisfaction")
    genre_ratings = filtered_df.groupby('genres')['rating'].agg(['mean', 'count'])
    genre_ratings = genre_ratings[genre_ratings['count'] >= min_ratings].sort_values('mean', ascending=False)
    st.dataframe(genre_ratings)

# Ratings Over Time + Top Movies
st.markdown("### 🕰️ Ratings Over Time")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Mean Rating by Release Year")
    yearly_ratings = filtered_df.groupby('year')['rating'].mean()
    fig, ax = plt.subplots()
    yearly_ratings.plot(ax=ax)
    ax.set_ylim(1, 5)
    st.pyplot(fig)
with col2:
    st.subheader("Top-Rated Movies")
    movie_stats = filtered_df.groupby('title')['rating'].agg(['mean', 'count'])
    top_movies = movie_stats[movie_stats['count'] >= min_ratings].sort_values('mean', ascending=False).head(5)
    st.dataframe(top_movies)

# Age vs Rating + Occupation Distribution
st.markdown("### 👥 Viewer Demographics")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Rating vs Age by Genre")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=filtered_df, x='age', y='rating', hue='genres', estimator='mean', ax=ax)
    ax.set_ylim(1, 5)
    st.pyplot(fig)
with col2:
    st.subheader("Rating by Occupation")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=filtered_df, x='occupation', y='rating')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)

# Gender Ratings + Movie Age
st.markdown("### 🧠 Viewer Behavior")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gender Differences")
    gender_ratings = filtered_df.groupby('gender')['rating'].mean()
    st.bar_chart(gender_ratings)

with col2:
    st.subheader("Rating vs Movie Age")
    filtered_df['movie_age'] = filtered_df['rating_year'] - filtered_df['year']
    age_bins = pd.cut(filtered_df['movie_age'], bins=10)
    age_rating = filtered_df.groupby(age_bins)['rating'].mean()
    age_rating.index = age_rating.index.astype(str)  # ✅ Convert intervals to strings
    st.bar_chart(age_rating)

# Heatmap
st.markdown("### 🔥 Cross-Demographic Heatmap")

# 🔄 Toggle between heatmap views
heatmap_view = st.radio("Choose heatmap view:", ["Static", "Interactive"], horizontal=True)

# 📊 Create pivot table
pivot = df.pivot_table(index='age_group', columns='gender', values='rating', aggfunc='mean')
pivot = pivot.sort_index().fillna(0)

# 🔥 Render heatmap
if heatmap_view == "Static":
    st.subheader("🔥 Static Heatmap")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(pivot, annot=True, cmap='YlGnBu', fmt=".2f", linewidths=0.5, cbar_kws={'label': 'Avg Rating'})
    ax.set_title("Average Rating by Age Group and Gender")
    ax.set_xlabel("Gender")
    ax.set_ylabel("Age Group")
    st.pyplot(fig)

else:
    st.subheader("🔥 Interactive Heatmap")
    heatmap_df = pivot.reset_index().melt(id_vars='age_group', var_name='gender', value_name='avg_rating')
    chart = alt.Chart(heatmap_df).mark_rect().encode(
        x=alt.X('gender:N', title='Gender'),
        y=alt.Y('age_group:N', title='Age Group'),
        color=alt.Color('avg_rating:Q', scale=alt.Scale(scheme='yellowgreenblue'), title='Avg Rating'),
        tooltip=['age_group', 'gender', 'avg_rating']
    ).properties(title="Average Rating by Age Group and Gender")

    st.altair_chart(chart, use_container_width=True)

# 🧠 Insight Panel
with st.expander("🧠 Insights"):
    st.markdown(f"""
    - Highest average ratings: **{pivot.max().idxmax()} in {pivot.idxmax().max()}**
    - Lowest ratings: **{pivot.min().idxmin()} in {pivot.idxmin().min()}**
    - Gender divergence most visible in: **{pivot.apply(lambda row: abs(row['M'] - row['F']), axis=1).idxmax()}**
    """)
