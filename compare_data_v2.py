"""Kicked off of lambda machine. Will simplify the process so I only have to run it once. Then I can build the
set difference and intersection dfs in a later step"""

# ============================================================================================
# Imports
# ============================================================================================


import pandas as pd
from rapidfuzz import process, fuzz
from tqdm import tqdm
import re


# ============================================================================================
# Data Reading
# ============================================================================================


def read_csv_and_drop_index(filename: str, enc: str):
  # Reading the CSV file normally
  df = pd.read_csv(filename, encoding=enc)

  # Dropping the first column
  df = df.drop(df.columns[0], axis=1)
  return df


# ============================================================================================
# Our Data
# ============================================================================================


jared_df = read_csv_and_drop_index('DocData/jared_metadata.csv', 'latin1')
aaron_df = read_csv_and_drop_index('DocData/aaron_scrape_data.csv', 'utf-8')

jared_df = jared_df.rename(columns={'245a': 'Title', '245b': 'Title_alt'})


# ============================================================================================
# Best Match
# ============================================================================================


def preprocess_title(title):
    if pd.isna(title):
        return ''
    title = str(title).strip(" '\".;:,/?\\")  # Strip leading and trailing whitespaces, single quotes, double quotes, and specific punctuation characters
    title = re.sub(r"^[\"'\[\(].+?[\"'\]\)]$", lambda x: x.group(0)[1:-1], title)
    title = title.strip(" '\".;:,/?\\")  # Strip again to handle cases like "'Title;'"
    return title


jared_df['Title'] = jared_df['Title'].apply(preprocess_title)
aaron_df['Title'] = aaron_df['Title'].apply(preprocess_title)

print(jared_df['Title'])
print(aaron_df['Title'])

def find_best_matches(df1, df2, title_col_df1, id_col_df1, title_col_df2, id_col_df2):
    result_rows = []
    titles_series_df2 = df2[title_col_df2].astype(str)  # Convert to string to handle NaN values

    for idx, row in tqdm(df1.iterrows(), total=len(df1), desc="Finding Best Matches"):
        title_df1 = str(row[title_col_df1])  # Convert to string to handle NaN values

        match = process.extractOne(title_df1, titles_series_df2, scorer=fuzz.token_sort_ratio)

        if match:
            best_match, score, idx_df2 = match
            row_df2 = df2.iloc[idx_df2]
            id_df1 = row[id_col_df1]
            id_df2 = row_df2[id_col_df2]
            result_rows.append(pd.Series([title_df1, best_match, id_df1, id_df2, score], index=[title_col_df1, title_col_df2, id_col_df1, id_col_df2, 'Match Score']))
        else:
            print(f"No match found for: {title_df1}")

    result_df = pd.concat(result_rows, axis=1).T
    return result_df


# Assuming 'Title' is the column for titles in both DataFrames,
# 'ESTC System No.' is the identifier in aaron_df,
# and 'HTID' is the identifier in jared_df.
#best_matches_df = find_best_matches(aaron_df, jared_df, 'Title', 'ESTC System No.', 'Title', 'HTID')
#print(best_matches_df)
#best_matches_df.to_csv('best_matches_aaron_jared_df_v2.csv')



#best_matches_df_jared_aaron = find_best_matches(jared_df, aaron_df, 'Title', 'HTID', 'Title', 'ESTC System No.')
#print(best_matches_df_jared_aaron)
#best_matches_df_jared_aaron.to_csv('best_matches_jared_aaron_df.csv')
