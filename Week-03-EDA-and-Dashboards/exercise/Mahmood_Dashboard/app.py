import streamlit as st
import pandas as pd
try:
    import plotly.express as px
except ImportError as e:
    st.error(
        f"Failed to import Plotly: {e}. Install with `pip install plotly` or add `plotly` to requirements.")
    st.stop()
from pathlib import Path
from io import StringIO
import os

st.set_page_config(page_title="Population Dashboard", page_icon="📈", layout="wide")

SAMPLE_CSV = """Country,Year,Population
United States,2010,309349689
United States,2015,320738994
United States,2020,331002651
India,2010,1234281170
India,2015,1310152403
India,2020,1380004385
China,2010,1340968737
China,2015,1376048943
China,2020,1439323776
Brazil,2010,195713635
Brazil,2015,204471769
Brazil,2020,212559417
Nigeria,2010,159424742
Nigeria,2015,181137448
Nigeria,2020,206139589
"""

@st.cache_data
def load_data(uploaded_file=None):
    """Load user-uploaded CSV or fall back to local file, then to built-in sample."""
    # 1) If user uploads a CSV, use it.
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return _basic_cleanup(df)

    # 2) If local sample exists, use it. Resolve relative to this file for robustness.
    script_dir = Path(os.path.dirname(__file__)).resolve()
    df_path = (script_dir / "data" / "sample_population.csv")
    if df_path.exists():
        df = pd.read_csv(df_path)
        return _basic_cleanup(df)

    # 3) Fallback to built-in sample string.
    st.warning("`data/sample_population.csv` not found — using built-in sample data.")
    df = pd.read_csv(StringIO(SAMPLE_CSV))
    return _basic_cleanup(df)

def _basic_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize column names
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    # Coerce common columns if present
    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    if "Population" in df.columns:
        df["Population"] = pd.to_numeric(df["Population"], errors="coerce")
    return df

st.title("📈 Population Dashboard")
st.write(
    "Upload your own CSV (with columns like `Country`, `Year`, `Population`) "
    "or explore the sample dataset to get started."
)

with st.sidebar:
    st.header("Controls")
    uploaded = st.file_uploader("Upload CSV", type=["csv"]
    )
    st.markdown("**Expected columns**: `Country`, `Year`, `Population`")
    st.caption("Tip: Keep column names simple; capitalization doesn’t matter.")

df = load_data(uploaded)

# Build filter options defensively
countries = (
    sorted(df["Country"].dropna().unique().tolist())
    if "Country" in df.columns else []
)
if "Year" in df.columns and df["Year"].notna().any():
    # Guard against NaNs in Year when casting to int
    year_min_val = pd.to_numeric(df["Year"], errors="coerce").min()
    year_max_val = pd.to_numeric(df["Year"], errors="coerce").max()
    if pd.notna(year_min_val) and pd.notna(year_max_val):
        year_min, year_max = int(year_min_val), int(year_max_val)
    else:
        year_min = year_max = None
else:
    year_min = year_max = None

with st.sidebar:
    sel_countries = st.multiselect(
        "Select countries",
        countries,
        default=(countries[:5] if len(countries) >= 5 else countries),
    )
    if year_min is not None and year_max is not None:
        sel_years = st.slider(
            "Year range",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max),
            step=1,
        )
    else:
        sel_years = None

# Apply filters
# Ensure mask aligns to df.index to avoid index alignment issues
mask = pd.Series(True, index=df.index) if not df.empty else pd.Series([], dtype=bool)
if not df.empty:
    if sel_countries and "Country" in df.columns:
        mask &= df["Country"].isin(sel_countries)
    if sel_years and "Year" in df.columns:
        y1, y2 = sel_years
        mask &= df["Year"].between(y1, y2)

fdf = df[mask].dropna(subset=["Population"]) if not df.empty and "Population" in df.columns else pd.DataFrame()

# KPIs
col1, col2, col3 = st.columns(3)
if not fdf.empty and "Year" in fdf.columns and "Country" in fdf.columns:
    # Guard: coerce Year and drop NaNs before max
    year_series = pd.to_numeric(fdf["Year"], errors="coerce").dropna()
    if not year_series.empty:
        latest_year = int(year_series.max())
    else:
        latest_year = None
    if latest_year is not None:
        latest_df = fdf[pd.to_numeric(fdf["Year"], errors="coerce") == latest_year]
        total_pop = latest_df["Population"].sum()
        n_countries = latest_df["Country"].nunique()
        avg_pop = latest_df["Population"].mean()

        col1.metric("Total Population (latest year)", f"{total_pop:,.0f}")
        col2.metric("Countries (latest year)", f"{n_countries}")
        col3.metric("Avg. Population (latest year)", f"{avg_pop:,.0f}")
    else:
        col1.write("No valid years in data.")
        col2.write("")
        col3.write("")
else:
    col1.write("No data after filters; adjust selections.")

st.markdown("---")


# Line chart: population over time
if not fdf.empty and {"Year", "Population", "Country"}.issubset(fdf.columns):
    plot_df = fdf.copy()
    plot_df["Year"] = pd.to_numeric(plot_df["Year"], errors="coerce")
    plot_df = plot_df.dropna(subset=["Year", "Population"])  # ensure clean plotting
    if not plot_df.empty:
        fig = px.line(
            plot_df, x="Year", y="Population", color="Country", markers=True,
            title="Population Over Time"
        )
        st.plotly_chart(fig, width='stretch')

# Bar chart: latest year comparison
if not fdf.empty and "Country" in fdf.columns and "Year" in fdf.columns:
    year_series = pd.to_numeric(fdf["Year"], errors="coerce").dropna()
    if not year_series.empty:
        latest_year = int(year_series.max())
    else:
        latest_year = None
    latest_df = fdf[pd.to_numeric(fdf["Year"], errors="coerce") == latest_year].sort_values("Population", ascending=False) if latest_year is not None else pd.DataFrame()
    if not latest_df.empty:
        fig2 = px.bar(
            latest_df, x="Country", y="Population",
            title=f"Population by Country (Year {latest_year})"
        )
        st.plotly_chart(fig2, width='stretch')

# Raw data preview
with st.expander("Preview Data"):
    st.dataframe(fdf.head(200), width='stretch')

