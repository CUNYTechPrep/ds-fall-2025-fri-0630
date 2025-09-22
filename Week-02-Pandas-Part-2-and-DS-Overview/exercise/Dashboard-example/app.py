import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="🥗 Food & Fitness Dashboard")

# --- Load & Clean Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("Week-02-Pandas-Part-2-and-DS-Overview/data/food_cleaned.csv")
    df['calories_day'] = pd.to_numeric(df['calories_day'], errors='coerce')
    df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
    df['Gender'] = df['Gender'].map({1: "Female", 2: "Male"})
    df = df.dropna(subset=['calories_day', 'weight', 'Gender'])
    df['calories_per_kg'] = df['calories_day'] / df['weight']
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")
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

x_col = "calories_per_kg" if normalize else "calories_day"
x_label = "Calories per kg" if normalize else "Calories per Day"

# --- Title ---
st.title("🥗 Food & Fitness Dashboard")
st.markdown("Explore calorie intake and weight patterns across genders.")

# --- Summary Stats ---
with st.container():
    st.subheader("📊 Summary Statistics")
    col1, col2 = st.columns(2)
    col1.metric("Average Calories", f"{filtered_df['calories_day'].mean():,.0f}")
    col2.metric("Calories per kg", f"{filtered_df['calories_per_kg'].mean():.1f}")
    st.markdown("**Insight:** These metrics give a quick snapshot of overall intake and body mass. Normalized calories help compare across body types.")

# --- Scatter Plot: Calories vs Weight ---
with st.container():
    st.subheader("⚖️ Calories vs Weight")
    fig1, ax1 = plt.subplots()
    sns.scatterplot(data=filtered_df, x=x_col, y="weight", hue="Gender", ax=ax1)
    ax1.set_xlabel(x_label)
    ax1.set_ylabel("Weight (kg)")
    st.pyplot(fig1)
    st.markdown("**Insight:** This plot shows how calorie intake relates to body weight. Look for clusters or outliers by gender.")

# --- Violin Plot: Calorie Distribution by Gender ---
with st.container():
    st.subheader("🎻 Calorie Distribution by Gender")
    fig2, ax2 = plt.subplots()
    sns.violinplot(data=filtered_df, x="Gender", y=x_col, palette="Set2", ax=ax2)
    ax2.set_ylabel(x_label)
    st.pyplot(fig2)
    st.markdown("**Insight:** Violin plots reveal the shape of intake distribution. Wider sections show where most data points lie.")

# --- Swarm Plot: Individual Intake Points ---
with st.container():
    st.subheader("🐝 Individual Calorie Points by Gender")
    fig3, ax3 = plt.subplots()
    sns.swarmplot(data=filtered_df, x="Gender", y=x_col, size=4, ax=ax3)
    ax3.set_ylabel(x_label)
    st.pyplot(fig3)
    st.markdown("**Insight:** Swarm plots highlight individual variation. You can spot outliers and clusters by gender.")

# --- Correlation Matrix ---
with st.container():
    st.subheader("🧠 Correlation Matrix")
    corr = filtered_df[['calories_day', 'weight', 'calories_per_kg']].corr()
    st.dataframe(corr.style.background_gradient(cmap="coolwarm"))
    st.markdown("**Insight:** This matrix shows how strongly variables relate. A high correlation between calories and weight may indicate consistent intake patterns.")

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ by Patience · Powered by Streamlit")
