
import pandas as pd
import unicodedata

def normalize_name(name):
    """Normalize names by removing diacritical marks (umlauts, accents, etc.)"""
    if pd.isna(name):
        return name
    # Remove diacritical marks (umlauts, accents, etc.) and convert to ASCII
    normalized = unicodedata.normalize('NFD', str(name))
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
    return ascii_name.strip()

wiki = pd.read_csv('gbbo_results.csv')
google = pd.read_csv('data.csv')

# Filter out rows where Technical_Rank is blank/null
wiki = wiki[~wiki['Technical_Rank'].isna()]

# Clean up and normalize contestant names 
wiki['Contestant'] = wiki['Contestant'].str.strip()
google['Contestant'] = google['Contestant'].str.strip()

# Normalize names to handle umlauts and other diacritical marks
wiki['Contestant_Normalized'] = wiki['Contestant'].apply(normalize_name)
google['Contestant_Normalized'] = google['Contestant'].apply(normalize_name)

merged_df = pd.merge(wiki, google, left_on=['Contestant_Normalized','Series','Episode'], right_on=['Contestant_Normalized','Series','Round'], how='outer')

# Check for rows with data discrepancies AND unmatched rows
discrepancies = []

# 1. Rows where both sources have data but values differ
both_sources = merged_df[~merged_df['Final Review'].isna() & ~merged_df['Second Half Review'].isna()]
value_discrepancies = both_sources[
    ((both_sources["Final Review"] != both_sources["Second Half Review"]) & 
     ~(both_sources["Final Review"].isna() | both_sources["Second Half Review"].isna())) |
    ((both_sources["Winner_x"] != both_sources["Winner_y"]) & 
     ~(both_sources["Winner_x"].isna() & both_sources["Winner_y"].isna())) |
    ((both_sources["Eliminated_x"] != both_sources["Eliminated_y"]) & 
     ~(both_sources["Eliminated_x"].isna() & both_sources["Eliminated_y"].isna())) |
    ((both_sources["Technical_Rank"] != both_sources["Tech"]) & 
     ~(both_sources["Technical_Rank"].isna() | both_sources["Tech"].isna()))
]

# 2. Rows where only Wiki has contestant data (Google missing this contestant entirely)
wiki_only = merged_df[~merged_df['Episode'].isna() & merged_df['Round'].isna()]

# 3. Rows where only Google has contestant data (Wiki missing this contestant entirely)  
google_only = merged_df[merged_df['Episode'].isna() & ~merged_df['Round'].isna()]

# Combine all issues
filtered_df = pd.concat([value_discrepancies, wiki_only, google_only], ignore_index=True)

print(f"Found {len(filtered_df)} total issues:")
print(f"  - {len(value_discrepancies)} value discrepancies (both sources have data)")
print(f"  - {len(wiki_only)} rows only in Wiki data")
print(f"  - {len(google_only)} rows only in Google data")

if len(filtered_df) > 0:
    filtered_df.to_csv('discrepancies.csv', index=False)
    print(f"All issues saved to discrepancies.csv")
    
    # Additional breakdown by issue type
    if len(value_discrepancies) > 0:
        print(f"\nValue discrepancies found:")
        for _, row in value_discrepancies.iterrows():
            contestant = row['Contestant_x'] if pd.notna(row['Contestant_x']) else row['Contestant_y']
            print(f"  Series {row['Series']}, Episode {row['Episode']}, {contestant}")
    
    if len(wiki_only) > 0:
        print(f"\nRows only in Wiki data (missing from Google):")
        for _, row in wiki_only.head(10).iterrows():  # Show first 10
            contestant = row['Contestant_x'] if pd.notna(row['Contestant_x']) else row['Contestant_y']
            print(f"  Series {row['Series']}, Episode {row['Episode']}, {contestant}")
        if len(wiki_only) > 10:
            print(f"  ... and {len(wiki_only) - 10} more")
    
    if len(google_only) > 0:
        print(f"\nRows only in Google data (missing from Wiki):")
        for _, row in google_only.head(10).iterrows():  # Show first 10
            contestant = row['Contestant_x'] if pd.notna(row['Contestant_x']) else row['Contestant_y']
            print(f"  Series {row['Series']}, Round {row['Round']}, {contestant}")
        if len(google_only) > 10:
            print(f"  ... and {len(google_only) - 10} more")
else:
    print("No issues found - data sources match perfectly!")