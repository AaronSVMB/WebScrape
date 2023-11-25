"""From aaron_df and jared_df find the intersection and set difference of both of these groups
 off of the 'Title' Column. These titles do not need to be exactly the same. To achieve this
 end, I utilize the fuzzywuzzy package which has a parameter for string leniency in regard
 to how similar the spelling has to be marked as the same string. """


# ============================================================================================
# Imports
# ============================================================================================


import pandas as pd
from rapidfuzz import process, fuzz


# ============================================================================================
# Data Reading
# ============================================================================================

def read_csv_and_drop_index(filename: str, enc: str):
  # Reading the CSV file normally
  df = pd.read_csv(filename, encoding = enc)

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


# Function to get best match, its score, and associated column (HTID or 'ESTC System No.')
def best_match(title, titles_list, df_reference, col_reference):
    result = process.extractOne(title, titles_list, scorer=fuzz.token_sort_ratio)
    if result:
        best_match, score, idx = result
        reference_value = df_reference.iloc[idx][col_reference]
        return pd.Series([best_match, score, reference_value])
    else:
        return pd.Series([None, 0, None])

# For df1 compared to df2
aaron_df[['Best Match', 'Score', 'HTID']] = aaron_df['Title'].apply(best_match, args=(jared_df['Title'].tolist(), jared_df, 'HTID'))

# For df2 compared to df1
jared_df[['Best Match', 'Score', 'ESTC System No.']] = jared_df['Title'].apply(best_match, args=(aaron_df['Title'].tolist(), aaron_df, 'ESTC System No.'))

# Define a threshold for match score
threshold = 90

# Create Intersection and Set Difference DataFrames for df1 compared to df2
intersection_aaron_jared_df = aaron_df[aaron_df['Score'] > threshold][['Title', 'ESTC System No.', 'HTID', 'Score']]
set_difference_aaron_jared_df = aaron_df[aaron_df['Score'] <= threshold][['Title', 'ESTC System No.', 'Score']]

# Create Intersection and Set Difference DataFrames for df2 compared to df1
intersection_jared_aaron_df = jared_df[jared_df['Score'] > threshold][['Title', 'HTID', 'ESTC System No.', 'Score']]
set_difference_jared_aaron_df = jared_df[jared_df['Score'] <= threshold][['Title', 'HTID', 'Score']]

print("Intersection DF1:\n", intersection_aaron_jared_df)
print("\nSet Difference DF1:\n", set_difference_aaron_jared_df)
print("\nIntersection DF2:\n", intersection_jared_aaron_df)
print("\nSet Difference DF2:\n", set_difference_jared_aaron_df)

print("Num Rows: \n aaron_df:", len(aaron_df),
      "\n jared_df", len(jared_df),
      "\n intersection_aaron_jared_df", len(intersection_aaron_jared_df),
      "\n set_difference_aaron_jared_df", len(set_difference_aaron_jared_df),
      "\n intersection_jared_aaron_df", len(intersection_jared_aaron_df),
      "\n set_difference_jared_aaron_df", len(set_difference_jared_aaron_df))

intersection_aaron_jared_df.to_csv('intersection_aaron_jared_df.csv')
set_difference_aaron_jared_df.to_csv('set_difference_aaron_jared_df.csv')
intersection_jared_aaron_df.to_csv('intersection_jared_aaron_df.csv')
set_difference_jared_aaron_df.to_csv('set_difference_jared_aaron_df.csv')
