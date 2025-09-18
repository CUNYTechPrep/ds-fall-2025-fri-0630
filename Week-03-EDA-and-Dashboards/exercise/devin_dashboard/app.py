import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Movie Dashboard", layout="wide")

st.sidebar.header("Movie Dashboard Controls")

try:
    df = pd.read_csv("../../data/movie_ratings.csv")
except:
    st.error("No file found at ../../data/movie_ratings.csv")
    st.stop()

df = df.drop_duplicates().dropna()

show_raw = st.sidebar.checkbox("Show raw data")

age_min = int(df['age'].min())
age_max = int(df['age'].max())
age_range = st.sidebar.slider("Age range", age_min, age_max, (age_min, age_max))

genders = df['gender'].unique().tolist()
selected_genders = st.sidebar.multiselect("Pick genders", genders, default=genders)

jobs = df['occupation'].unique().tolist()
selected_jobs = st.sidebar.multiselect("Pick jobs", jobs, default=jobs)

filtered_df = df[
    (df['age'] >= age_range[0]) &
    (df['age'] <= age_range[1]) &
    (df['gender'].isin(selected_genders)) &
    (df['occupation'].isin(selected_jobs))
]

if filtered_df.empty:
    st.warning("No data matches these filters.")
    st.stop()

if show_raw:
    st.subheader("Raw Data Sample")
    st.dataframe(filtered_df.head(50))

tab1, tab2, tab3, tab4 = st.tabs(["Genres", "Avg Genre", "Year Ratings", "Top Movies"])

with tab1:
    st.subheader("Genres Overview")
    min_pct = st.slider("Group small genres into 'Other' %", 0.0, 10.0, 2.0, 0.5)
    
    genre_counts = filtered_df.groupby("genres").size().reset_index(name="count")
    total_count = genre_counts["count"].sum()
    genre_counts["pct"] = 100 * genre_counts["count"] / total_count
    
    main_genres = genre_counts[genre_counts["pct"] >= min_pct]
    small_genres = genre_counts[genre_counts["pct"] < min_pct]
    
    if not small_genres.empty:
        other_row = pd.DataFrame({"genres":["Other"], "count":[small_genres["count"].sum()]})
        chart_data = pd.concat([main_genres, other_row])
    else:
        chart_data = main_genres
    
    pie_chart = px.pie(chart_data, names="genres", values="count")
    pie_chart.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(pie_chart, use_container_width=True)

with tab2:
    st.subheader("Average Rating by Genre")
    min_ratings = st.number_input("Min ratings per genre", 0, 10000, 50, 10)
    sort_order = st.radio("Sort order", ["Descending","Ascending"])
    
    genre_stats = filtered_df.groupby("genres").agg({"rating":"mean","age":"size"}).reset_index()
    genre_stats.rename(columns={"age":"num_ratings"}, inplace=True)
    genre_stats = genre_stats[genre_stats["num_ratings"] >= min_ratings]
    
    ascending = True if sort_order=="Ascending" else False
    genre_stats = genre_stats.sort_values("rating", ascending=ascending)
    
    bar_chart = px.bar(genre_stats, x="genres", y="rating", hover_data=["num_ratings"])
    bar_chart.update_layout(xaxis_title="Genre", yaxis_title="Avg Rating")
    st.plotly_chart(bar_chart, use_container_width=True)

with tab3:
    st.subheader("Ratings by Year")
    min_year_ratings = st.number_input("Min ratings per year", 0, 100000, 50, 10)
    rolling_window = st.slider("Rolling mean window", 1, 9, 1)
    
    year_min = int(filtered_df["year"].min())
    year_max = int(filtered_df["year"].max())
    year_range = st.slider("Year range", year_min, year_max, (year_min, year_max))
    
    year_stats = filtered_df.groupby("year").agg({"rating":"mean","age":"size"}).reset_index()
    year_stats.rename(columns={"age":"num_ratings"}, inplace=True)
    
    year_stats = year_stats[
        (year_stats["year"] >= year_range[0]) &
        (year_stats["year"] <= year_range[1]) &
        (year_stats["num_ratings"] >= min_year_ratings)
    ].sort_values("year")
    
    if rolling_window > 1:
        year_stats["rating_smooth"] = year_stats["rating"].rolling(rolling_window, center=True).mean()
    else:
        year_stats["rating_smooth"] = year_stats["rating"]
    
    line_chart = px.line(year_stats, x="year", y="rating_smooth", markers=True, hover_data=["num_ratings","rating"])
    line_chart.update_layout(xaxis_title="Year", yaxis_title="Avg Rating")
    st.plotly_chart(line_chart, use_container_width=True)

with tab4:
    st.subheader("Top Movies")
    min_movie_ratings = st.number_input("Min ratings per movie", 1, 100000, 50, 10)
    top_n = st.slider("Top N movies", 3, 25, 5)
    
    movie_stats = filtered_df.groupby(["movie_id","title"]).agg({"rating":"mean","age":"size"}).reset_index()
    movie_stats.rename(columns={"age":"num_ratings"}, inplace=True)
    movie_stats = movie_stats[movie_stats["num_ratings"] >= min_movie_ratings]
    
    top_movies = movie_stats.sort_values(["rating","num_ratings"], ascending=[False,False]).head(top_n)
    
    bar_chart_movies = px.bar(top_movies, y="title", x="rating", orientation="h", hover_data=["num_ratings"])
    bar_chart_movies.update_layout(xaxis_title="Avg Rating", yaxis_title="Movie")
    st.plotly_chart(bar_chart_movies, use_container_width=True)
