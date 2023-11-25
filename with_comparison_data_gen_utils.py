"""After finding the best matches from aaron with jared and vice-versa, here I can build intersection
and set difference dataframes respectively"""


# ============================================================================================
# Imports
# ============================================================================================


import pandas as pd


# ============================================================================================
# Imports
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

threshold = 75

jared_aaron_best_match = read_csv_and_drop_index('ComparionData/jared_aaron_data/best_matches_jared_aaron_df.csv', 'utf-8')

intersection_df = jared_aaron_best_match[jared_aaron_best_match['Match Score'] >= threshold]

set_difference_aaron_jared_df = jared_aaron_best_match[jared_aaron_best_match['Match Score'] < threshold]

intersection_df.to_csv('intersection_threshold_75_df_nov_2.csv')

set_difference_aaron_jared_df.to_csv('set_diff_hathi_less_web_df.csv')

print(intersection_df.shape[0])
print(set_difference_aaron_jared_df.shape[0])
