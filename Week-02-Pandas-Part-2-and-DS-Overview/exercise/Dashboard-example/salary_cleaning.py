import pandas as pd

#filepath ='/workspaces/ds-fall-2025-fri-0630/Week-02-Pandas-Part-2-and-DS-Overview/exercise/Dashboard-example/salary_cleaned.csv'
def clean_salary(filepath):
    df = pd.read_csv(filepath)
    
    df = df.dropna(subset=['salary', 'industry', 'title'])
    df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
    df['additional_compensation'] = pd.to_numeric(df['additional_compensation'], errors='coerce')
    df['total_yoe'] = pd.to_numeric(df['total_yoe'], errors='coerce')
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    return df
