import pandas as pd
import streamlit as st 
import altair as alt

# load dataset
df = pd.read_csv('data/movie_ratings.csv')

def make_genre_bar(data, indep_var='Genre', dep_var='Count', horizontal=True, height=400):
    # normalize input to a DataFrame with columns [indep_var, dep_var]
    if isinstance(data, pd.Series):
        _df = data.reset_index()
        _df.columns = [indep_var, dep_var]
    else:
        _df = data.copy()

    if horizontal:
        chart = (
            alt.Chart(_df)
               .mark_bar()
               .encode(
                   x=alt.X(f'{dep_var}:Q', title=dep_var),
                   y=alt.Y(f'{indep_var}:N', sort='-x', title=indep_var),
                   tooltip=[alt.Tooltip(f'{indep_var}:N'), alt.Tooltip(f'{dep_var}:Q', format='.2f')]
               )
               .properties(height=height)
        )
    else:
        chart = (
            alt.Chart(_df)
               .mark_bar()
               .encode(
                   x=alt.X(f'{indep_var}:N',
                           sort=alt.EncodingSortField(field=dep_var, op='identity', order='descending'),
                           title=indep_var),
                   y=alt.Y(f'{dep_var}:Q', title=dep_var),
                   tooltip=[alt.Tooltip(f'{indep_var}:N'), alt.Tooltip(f'{dep_var}:Q', format='.2f')]
               )
               .properties(height=height)
        )
    return chart

# clean
df = df.dropna(subset=['rating', 'genres', 'year', 'title'])

# Page title
st.set_page_config(page_title="Movie Dashboard (Week 3)", layout="wide")

# Sidebar
st.sidebar.title("Views")
view = st.sidebar.selectbox(
    "Choose a visualization",
    [
        "Counts by genre",
        "Average rating by genre",
        "Average rating by year",
        "Top rated movies (min ratings)"
    ]
)

# Render chosen visualization
if view == "Counts by genre":
    st.subheader("Counts by genre")
    counts = df['genres'].value_counts().sort_values(ascending=False)
    st.altair_chart(make_genre_bar(counts, indep_var='Genre', dep_var='Count'),
                    use_container_width=True)

elif view == "Average rating by genre":
    st.subheader("Average rating by genre")
    mean_by_genre = df.groupby('genres')['rating'].mean().sort_values(ascending=False)
    st.altair_chart(make_genre_bar(mean_by_genre, indep_var='Genre', dep_var='Average Rating'),
                    use_container_width=True)

elif view == "Average rating by year":
    st.subheader("Average rating by year")
    ratings_year_df = (
        df.groupby('year', as_index=False)['rating'].mean()
          .rename(columns={'rating': 'avg_rating'})
    )
    st.altair_chart(
        alt.Chart(ratings_year_df).mark_line(point=True).encode(
            x=alt.X('year:O', title='Year'),   # change to 'year:Q' if numeric year
            y=alt.Y('avg_rating:Q', title='Average Rating'),
            tooltip=['year', alt.Tooltip('avg_rating:Q', format='.2f')]
        ).properties(height=350),
        use_container_width=True
    )

else:  # "Top rated movies (min ratings)"
    st.subheader("Top rated movies with at least X ratings")
    # slider in sidebar so it stays visible while scrolling
    min_r = st.sidebar.slider("Minimum number of ratings", 1, 500, 50, step=10)

    movie_stats = (
        df.groupby(['movie_id', 'title'], as_index=False)['rating']
          .agg(num_ratings='size', avg_rating='mean')
    )

    def top_n(min_ratings, n=5):
        return (
            movie_stats.query("num_ratings >= @min_ratings")
            .sort_values(['avg_rating', 'num_ratings'], ascending=[False, False])
            .assign(avg_rating=lambda d: d['avg_rating'].round(2))
            .head(n)
        )

    st.dataframe(top_n(min_r))