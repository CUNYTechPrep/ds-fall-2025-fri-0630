import pandas as pd

#filepath ='/workspaces/ds-fall-2025-fri-0630/Week-02-Pandas-Part-2-and-DS-Overview/exercise/Dashboard-example/salary_cleaned.csv'
def clean_salary(filepath):
    df = pd.read_csv(filepath)
    
    df = df.dropna(subset=['salary', 'industry', 'title'])
    df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
    df['additional_compensation'] = pd.to_numeric(df['additional_compensation'], errors='coerce')
    df['age'] = pd.to_numeric(df['age'], errors='coerce')

    def clean_yoe(value):
        if pd.isna(value):
            return None
        value = str(value).lower().replace("years", "").strip()
        if "-" in value:
            parts = value.split("-")
            try:
                return (float(parts[0].strip()) + float(parts[1].strip())) / 2
            except ValueError:
                return None
        else:
            try:
                return float(value.strip())
            except ValueError:
                return None
    df['total_yoe'] = df['total_yoe'].apply(clean_yoe)
    return df
