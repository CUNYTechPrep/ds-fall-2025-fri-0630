import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from salary_cleaning import clean_salary

st.set_page_config(page_title="💼 Salary Insights", layout="wide")
st.title("💼 Salary Insights Dashboard")

# Load and clean data
@st.cache_data
def load_data():
    return clean_salary('/workspaces/ds-fall-2025-fri-0630/Week-02-Pandas-Part-2-and-DS-Overview/exercise/salary_cleaned.csv')
   
df = load_data()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    industries = st.multiselect("Industry", df['industry'].dropna().unique(), default=df['industry'].dropna().unique())
    titles = st.multiselect("Job Title", df['title'].dropna().unique(), default=df['title'].dropna().unique())
    education = st.multiselect("Education", df['highest_education_completed'].dropna().unique())
    genders = st.multiselect("Gender", df['gender'].dropna().unique())
    races = st.multiselect("Race", df['race'].dropna().unique())

filtered_df = df[
    df['industry'].isin(industries) &
    df['title'].isin(titles)
]
if education:
    filtered_df = filtered_df[filtered_df['highest_education_completed'].isin(education)]
if genders:
    filtered_df = filtered_df[filtered_df['gender'].isin(genders)]
if races:
    filtered_df = filtered_df[filtered_df['race'].isin(races)]

# Top metrics
st.markdown("### 📊 Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Median Salary", f"${filtered_df['salary'].median():,.0f}")
col2.metric("Median Bonus", f"${filtered_df['additional_compensation'].median():,.0f}")
col3.metric("Avg YOE", round(filtered_df['total_yoe'].mean(), 1))
col4.metric("Top Industry", filtered_df['industry'].mode()[0] if not filtered_df.empty else "N/A")

# Salary Distribution
st.markdown("### 💰 Salary Distribution by Industry")
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(data=filtered_df, x='industry', y='salary')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
st.pyplot(fig)

# Salary vs Experience
st.markdown("### 📈 Salary vs Total Years of Experience")
fig, ax = plt.subplots(figsize=(8, 5))
sns.regplot(data=filtered_df, x='total_yoe', y='salary', scatter_kws={'alpha':0.3})
ax.set_xlim(0, filtered_df['total_yoe'].max())
st.pyplot(fig)

# Education Impact
st.markdown("### 🎓 Median Salary by Education Level")
edu_salary = filtered_df.groupby('highest_education_completed')['salary'].median().sort_values()
st.bar_chart(edu_salary)

# Demographic Breakdown
st.markdown("### 🧠 Salary by Gender and Race")
pivot = filtered_df.pivot_table(index='gender', columns='race', values='salary', aggfunc='median')
fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(pivot, annot=True, fmt=".0f", cmap='coolwarm', cbar_kws={'label': 'Median Salary'})
st.pyplot(fig)

# City-Level Insights
st.markdown("### 🗺️ Top-Paying Cities")
city_salary = filtered_df.groupby('city')['salary'].median().sort_values(ascending=False).head(10)
st.dataframe(city_salary)

# Interactive Altair Plot (Bonus)
st.markdown("### 🔍 Salary vs Experience by Industry")
alt_chart = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.4).encode(
    x='total_yoe:Q',
    y='salary:Q',
    color='industry:N',
    tooltip=['title', 'industry', 'salary', 'total_yoe']
).properties(width=800, height=400)
st.altair_chart(alt_chart, use_container_width=True)

# Export filtered data
with st.expander("📤 Export Filtered Data"):
    st.download_button("Download CSV", filtered_df.to_csv(index=False), "filtered_salary_data.csv", "text/csv")
    