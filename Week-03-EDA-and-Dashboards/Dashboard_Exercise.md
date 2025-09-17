# Week 3 Dashboard Exercise: MovieLens Data Analysis

## Overview
In this exercise, you will create visualizations or a small dashboard to analyze movie ratings from the MovieLens 200k dataset. Your goal is to answer analytical questions with clear, well-designed charts.

## Dataset
**File**: `data/movie_ratings.csv`

### Columns
- **user_id**: Unique user identifier
- **movie_id**: Unique movie identifier
- **rating**: Rating (1–5 scale)
- **timestamp**: When the rating was given
- **age**: User age
- **gender**: User gender (M/F)
- **occupation**: User occupation
- **zip_code**: User ZIP code
- **title**: Movie title with year
- **year**: Movie release year
- **decade**: Movie release decade
- **genres**: Pipe-separated genres for each movie
- **rating_year**: Year the rating was given

## Questions to Answer
1. What's the breakdown of genres for the movies that were rated?
2. Which genres have the highest viewer satisfaction (highest ratings)? 
3. How does mean rating change across movie release years?
4. What are the 5 best-rated movies that have at least 50 ratings? At least 150 ratings?

## Extra Credit
5. Pick 4 genres. For each genre, how does the rating change as viewer age increases?
   - Suggestion: try to do this for more than 4 genres and see which have the most interesting visualization.
6. Plot number of ratings vs mean rating per genre. Is there a correlation between the volume of ratings and mean rating?
7. We gave you a pre-cleaned `genres` column, the original dataset is `movie_ratings_EC.csv`, can you clean it yourself?
   - Hint: Use `.explode()` 

## Notes and Caveats
- Movies can belong to multiple genres. Exploding genres is acceptable for preference profiling but not for market share.
- Use minimum sample thresholds (e.g., n ≥ 50 or 100) to avoid small-sample noise.
- Decade and age-group distributions are uneven; include counts or context where relevant.

## Deliverables

### Option A: Streamlit Dashboard (Recommended)
Create an interactive Streamlit app that:
- Loads and displays the dataset
- Contains visualizations answering each question
- Includes interactive filters (age ranges, occupations, genres, etc.)
- Has clear titles, labels, and explanations for each chart
- Provides insights and conclusions based on the visualizations

### Option B: Jupyter Notebook
Create a comprehensive notebook that:
- Explores the dataset with summary statistics
- Creates static visualizations answering each question
- Includes markdown explanations of findings
- Uses professional-quality plots with proper styling

As long as you can demonstrate your visualizations effectively and answer the analytical questions.

## Getting Started

1. **Load the data**:
```python
import pandas as pd
df = pd.read_csv('data/movie_ratings.csv')
```

2. **Explore the dataset**:
```python
print(df.info())
print(df.describe())
print(df.head())
```

3. **Start with basic visualizations** for each question
4. **Iterate and improve** based on insights
5. **Add interactivity** if using Streamlit or similar tools

## Resources

### Visualization Libraries & Tools
- [Streamlit Documentation](https://docs.streamlit.io/) - Build interactive web apps
- [Plotly Python Documentation](https://plotly.com/python/) - Interactive plots
- [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html) - Static plotting
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html) - Statistical visualization

### Design & Best Practices
- [Data Visualization Catalogue](https://datavizcatalogue.com/) - Chart type selection guide
- [Storytelling with Data](https://www.storytellingwithdata.com/) - Visualization best practices

## Submission Instructions
- Submit your code files (`.py` for Streamlit apps, `.ipynb` for notebooks)
- Include a brief README with instructions to run your code
- If using Streamlit, include a `requirements.txt` file
- Basically, if using Streamlit, follow the example in `georgios_dashboard/`.

Good luck, and have fun exploring the data!
