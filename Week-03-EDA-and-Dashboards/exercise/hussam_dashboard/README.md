# MovieLens Dashboard (Week 3)

This is a lightweight Streamlit scaffold for the Week 3 dashboard exercise. It provides an outline with tabs for Questions 1–4 and a cached data loader.

## Project layout
Everything lives and runs inside this directory to avoid merge conflicts in PRs.
- App: `app.py`
- Data (relative path expected by the app): `../../data/movie_ratings.csv`
- Local deps: `requirements.txt`
- Streamlit config: `.streamlit/config.toml`

## Deployed app
- URL: https://hussam-exercise3-dashboard.streamlit.app/

## Setup
1. Create and activate a virtual environment (recommended).
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Run locally
From this directory:
```bash
streamlit run app.py
```

## Next steps
- Q1: explode `genres` and plot rating-count pie chart
- Q2: explode `genres`, compute mean rating by genre, plot bar chart
- Q3: compute mean rating by `year`, plot line chart
- Q4: add min ratings threshold control and show top movies table

## Deployment
All deployment assets are co-located in this folder.

### Render (recommended)
- Create a new Web Service from your GitHub repo
- Root Directory: `Week-03-EDA-and-Dashboards/exercise/name_dashboard`
- Build Command: `pip install -r requirements.txt`
- Start Command: `sh -c "streamlit run app.py --server.address 0.0.0.0 --server.port $PORT"`

### Streamlit Community Cloud
- Create a new app pointing to your fork
- Main file path: `Week-03-EDA-and-Dashboards/exercise/name_dashboard/app.py`
- Dependencies: auto-detected via this folder's `requirements.txt`
