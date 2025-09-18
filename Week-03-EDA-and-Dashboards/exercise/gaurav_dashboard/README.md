# Movie Ratings Dashboard

This is a lightweight Streamlit dashboard for visualizing movie ratings data.  
It provides four interactive visualizations selectable via a sidebar.

## Project layout
Everything lives and runs inside this directory to keep things simple.
- App: `app.py`
- Data (relative path expected by the app): `data/movie_ratings.csv`
- Local deps: `requirements.txt`
- Streamlit config: `.streamlit/config.toml` (optional)

## Deployed app
- URL: <your-deployment-url-here>

## Setup
1. Create and activate a virtual environment (recommended).
2. Install dependencies:
```bash
pip install -r requirements.txt

Visualizations
Counts by genre – bar chart of the most common genres
Average rating by genre – bar chart of mean ratings across genres
Average rating by year – line chart of rating trends over time
Top rated movies – table of best-rated movies with a minimum ratings slider
Deployment
All deployment assets are in this folder.
Render (recommended)
Create a new Web Service from your GitHub repo
Root Directory: path/to/dashboard
Build Command: pip install -r requirements.txt
Start Command: sh -c "streamlit run app.py --server.address 0.0.0.0 --server.port $PORT"
Streamlit Community Cloud
Create a new app pointing to your repo
Main file path: path/to/dashboard/app.py
Dependencies: auto-detected via requirements.txt