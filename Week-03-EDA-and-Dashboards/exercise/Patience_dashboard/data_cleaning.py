filepath='/workspaces/ds-fall-2025-fri-0630/Week-03-EDA-and-Dashboards/data/movie_ratings.csv'

def clean_movie_ratings(filepath):
    import pandas as pd

    df = pd.read_csv(filepath)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Handle missing values
    df = df.dropna(subset=['rating', 'year'])
    if 'age' in df.columns:
        df['age'] = df['age'].fillna(df['age'].median())
    if 'occupation' in df.columns:
        df['occupation'] = df['occupation'].fillna('Unknown')

    # Convert types
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Explode genres
    if 'genres' in df.columns:
        df['genres'] = df['genres'].str.split('|')
        df = df.explode('genres')

    # Clean categories
    if 'occupation' in df.columns:
        df['occupation'] = df['occupation'].str.title().str.strip()
    if 'gender' in df.columns:
        df['gender'] = df['gender'].str.upper().str.strip()

    # Derived columns
    if 'timestamp' in df.columns:
        df['rating_year'] = df['timestamp'].dt.year
    df['movie_age'] = df['rating_year'] - df['year']
    df['decade'] = (df['year'] // 10) * 10
    df['age_group'] = pd.cut(df['age'], bins=[10, 20, 30, 40, 50, 60, 70, 80], labels=[
        '10s', '20s', '30s', '40s', '50s', '60s', '70s'
    ])

    # Filter outliers
    df = df[(df['age'] >= 10) & (df['age'] <= 100)]
    df = df[(df['rating'] >= 0.5) & (df['rating'] <= 5)]

    # Drop duplicates
    df = df.drop_duplicates()

    return df
