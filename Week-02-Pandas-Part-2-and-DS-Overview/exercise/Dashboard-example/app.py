import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="Food & Fitness Dashboard", layout="wide")

# --- Load & Clean Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("/workspaces/ds-fall-2025-fri-0630/Week-02-Pandas-Part-2-and-DS-Overview/data/food_cleaned.csv")
    df['calories_day'] = pd.to_numeric(df['calories_day'], errors='coerce')
    df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
    df['Gender'] = pd.to_numeric(df['Gender'], errors='coerce')

    # Map numeric gender codes to labels
    gender_map = {1: "Female", 2: "Male"}
    df['Gender'] = df['Gender'].map(gender_map)

    df = df.dropna(subset=['calories_day', 'weight', 'Gender'])
    df['calories_per_kg'] = df['calories_day'] / df['weight']
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
gender_options = df['Gender'].unique()
selected_gender = st.sidebar.multiselect("Select Gender", gender_options, default=gender_options)

weight_min, weight_max = int(df['weight'].min()), int(df['weight'].max())
selected_weight = st.sidebar.slider("Select Weight Range (kg)", weight_min, weight_max, (weight_min, weight_max))

normalize = st.sidebar.checkbox("Normalize Calories by Weight")

# --- Apply Filters ---
filtered_df = df[
    (df['Gender'].isin(selected_gender)) &
    (df['weight'] >= selected_weight[0]) &
    (df['weight'] <= selected_weight[1])
]

# --- Title ---
st.title("🥗 Food & Fitness Dashboard")
st.markdown("Explore calorie intake and weight patterns across genders.")

# --- Summary Stats ---
with st.container():
    st.subheader("📊 Summary Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Calories/Day", f"{filtered_df['calories_day'].mean():,.0f}")
    col2.metric("Average Weight", f"{filtered_df['weight'].mean():,.1f} kg")
    col3.metric("Calories per kg", f"{filtered_df['calories_per_kg'].mean():.1f}")

# --- Scatter Plot ---
with st.container():
    st.subheader("⚖️ Calories vs Weight")
    fig1, ax1 = plt.subplots()
    x_col = "calories_per_kg" if normalize else "calories_day"
    sns.scatterplot(data=filtered_df, x=x_col, y="weight", hue="Gender", ax=ax1)
    ax1.set_xlabel("Calories per Day" if not normalize else "Calories per kg")
    ax1.set_ylabel("Weight (kg)")
    st.pyplot(fig1)

# --- Violin Plot ---
with st.container():
    st.subheader("🎻 Calorie Distribution by Gender")
    fig2, ax2 = plt.subplots()
    sns.violinplot(data=filtered_df, x="Gender", y=x_col, palette="Set2", ax=ax2)
    ax2.set_ylabel("Calories per Day" if not normalize else "Calories per kg")
    st.pyplot(fig2)

# --- Correlation Matrix ---
with st.container():
    st.subheader("🧠 Correlation Matrix")
    corr = filtered_df[['calories_day', 'weight', 'calories_per_kg']].corr()
    st.dataframe(corr.style.background_gradient(cmap="coolwarm"))

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ by Patience · Powered by Streamlit")
