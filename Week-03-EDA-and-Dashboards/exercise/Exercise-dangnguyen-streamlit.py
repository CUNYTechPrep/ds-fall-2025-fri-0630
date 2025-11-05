from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(layout="wide", page_title="MovieLens Ratings Dashboard")


@st.cache_data
def load_data(filepath):
    """
    Loads the MovieLens ratings data from a CSV file.
    """
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{filepath}' was not found. Please make sure it's in the same folder as the script.")
        return None

# --- Main Application ---
movie_data = load_data('movie_ratings.csv')

st.title("🎬 MovieLens 200k Ratings Analysis")
st.markdown("This dashboard explores the MovieLens dataset to uncover insights about movie genres, ratings, and trends over time.")

if movie_data is not None:
    
    # --- Question 1: Genre Breakdown ---
    st.header("1. What is the breakdown of movie genres?")
    st.markdown("This chart shows the total number of ratings given to movies in each genre.")
    
    genres_df = movie_data.dropna(subset=['genres']).copy()
    genres_df['genres'] = genres_df['genres'].str.split('|')
    exploded_genres = genres_df.explode('genres')
    
    genre_counts = exploded_genres['genres'].value_counts()
    
    fig1 = px.bar(
        genre_counts,
        x=genre_counts.index,
        y=genre_counts.values,
        title="Total Ratings per Genre",
        labels={'x': 'Genre', 'y': 'Number of Ratings'}
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- Question 2: Highest Rated Genres ---
    st.header("2. Which genres have the highest viewer satisfaction?")
    st.markdown("This chart displays the average rating for each genre, sorted from highest to lowest.")
    
    avg_genre_ratings = exploded_genres.groupby('genres')['rating'].mean().sort_values(ascending=False)
    
    fig2 = px.bar(
        avg_genre_ratings,
        x=avg_genre_ratings.values,
        y=avg_genre_ratings.index,
        orientation='h',
        title="Average Rating by Genre",
        labels={'x': 'Average Rating (1-5)', 'y': 'Genre'}
    )
    fig2.update_layout(yaxis={'categoryorder':'total ascending'}) 
    st.plotly_chart(fig2, use_container_width=True)

    # --- Question 3: Mean Rating Across Release Years ---
    st.header("3. How does mean rating change across movie release years?")
    st.markdown("This line chart illustrates the trend of average movie ratings based on their release year.")
    
    yearly_ratings = movie_data.dropna(subset=['year']).copy()
    yearly_ratings['year'] = yearly_ratings['year'].astype(int)
    avg_rating_by_year = yearly_ratings.groupby('year')['rating'].mean().reset_index()

    fig3 = px.line(
        avg_rating_by_year,
        x='year',
        y='rating',
        title='Average Movie Rating by Release Year',
        labels={'year': 'Release Year', 'rating': 'Average Rating'}
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # --- Question 4: Best-Rated Movies with Minimum Ratings ---
    st.header("4. What are the best-rated movies?")
    st.markdown("To find the best movies, we calculate the average rating and the total number of ratings for each title. This avoids rewarding movies with a single 5-star rating.")

    movie_stats = movie_data.groupby('title')['rating'].agg(['count', 'mean']).reset_index()

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 5 (at least 50 ratings)")
        # Filter for movies with at least 50 ratings, then sort by mean rating.
        top_50 = movie_stats[movie_stats['count'] >= 50].sort_values('mean', ascending=False).head(5)
        st.dataframe(top_50.reset_index(drop=True))

    with col2:
        st.subheader("Top 5 (at least 150 ratings)")
        # Filter for movies with at least 150 ratings, then sort by mean rating.
        top_150 = movie_stats[movie_stats['count'] >= 150].sort_values('mean', ascending=False).head(5)
        st.dataframe(top_150.reset_index(drop=True))
