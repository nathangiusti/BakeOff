import pandas as pd
import numpy as np

def combine_claude_data():
    # Read the data files - handle potential parsing issues
    print("Reading input files...")
    claude_judging = pd.read_csv('claude_judging.csv', on_bad_lines='skip')
    gbbo_results = pd.read_csv('../../../analysis/reports/gbbo_results.csv')
    data_reference = pd.read_csv('../human/data.csv')
    
    print(f"Claude judging data: {len(claude_judging)} rows")
    print(f"GBBO results data: {len(gbbo_results)} rows")
    print(f"Data reference: {len(data_reference)} rows")
    
    # Check for rows in claude data that don't map to gbbo data
    print("\nChecking for unmapped claude data...")
    claude_keys = set(zip(claude_judging['Contestant'], claude_judging['Season'], claude_judging['Episode']))
    gbbo_keys = set(zip(gbbo_results['Contestant'], gbbo_results['Series'], gbbo_results['Episode']))
    
    unmapped_claude = claude_keys - gbbo_keys
    if unmapped_claude:
        print(f"ALERT: {len(unmapped_claude)} rows in claude data do not map to gbbo data:")
        for contestant, season, episode in sorted(unmapped_claude):
            print(f"  - {contestant}, Season {season}, Episode {episode}")
    else:
        print("All claude data rows map to gbbo data")
    
    # Merge the datasets on Contestant, Season, and Episode
    merged_data = claude_judging.merge(
        gbbo_results, 
        left_on=['Contestant', 'Season', 'Episode'],
        right_on=['Contestant', 'Series', 'Episode'],
        how='left',  # Changed to left join to preserve all claude data
        indicator=True
    )
    
    # Also merge with data_reference to get handshake and first review information
    merged_data = merged_data.merge(
        data_reference[['Contestant', 'Series', 'Round', 'Signature Handshake', 'First Half Review', 'Showstopper Handshake']],
        left_on=['Contestant', 'Season', 'Episode'],
        right_on=['Contestant', 'Series', 'Round'],
        how='left',
        suffixes=('', '_ref')
    )
    
    # Alert on merge issues
    merge_issues = merged_data[merged_data['_merge'] != 'both']
    if len(merge_issues) > 0:
        print(f"\n🚨 ALERT: {len(merge_issues)} rows in claude data could not be merged with gbbo data:")
        for _, row in merge_issues.iterrows():
            print(f"  - {row['Contestant']}, Season {row['Season']}, Episode {row['Episode']}")
    
    # Remove the merge indicator column
    merged_data = merged_data.drop('_merge', axis=1)
    
    # Apply handshake logic: Set scores to 1.0 for bakes that received handshakes
    print("\nApplying handshake score adjustments...")
    handshake_adjustments = 0
    
    for idx, row in merged_data.iterrows():
        # Check for Signature Handshake
        if pd.notna(row['Signature Handshake']) and row['Signature Handshake'] == 1:
            # Set all signature scores to 1.0
            merged_data.at[idx, 'Signature_Bake'] = 1.0
            merged_data.at[idx, 'Signature_Flavor'] = 1.0
            merged_data.at[idx, 'Signature_Looks'] = 1.0
            handshake_adjustments += 1
            print(f"  * {row['Contestant']} S{row['Season']}E{row['Episode']}: Signature handshake -> All signature scores set to 1.0")
        
        # Check for Showstopper Handshake
        if pd.notna(row['Showstopper Handshake']) and row['Showstopper Handshake'] == 1:
            # Set all showstopper scores to 1.0
            merged_data.at[idx, 'Showstopper_Bake'] = 1.0
            merged_data.at[idx, 'Showstopper_Flavor'] = 1.0
            merged_data.at[idx, 'Showstopper_Looks'] = 1.0
            handshake_adjustments += 1
            print(f"  * {row['Contestant']} S{row['Season']}E{row['Episode']}: Showstopper handshake -> All showstopper scores set to 1.0")
    
    if handshake_adjustments == 0:
        print("  No handshake adjustments needed")
    else:
        print(f"  Applied {handshake_adjustments} handshake score adjustments")
    
    # Create the output dataframe with the same structure as data.csv
    output_data = pd.DataFrame()
    
    # Map the columns to match data.csv structure in exact order
    output_data['Contestant'] = merged_data['Contestant']
    output_data['Series'] = merged_data['Season']  # Use Season from claude_judging
    output_data['Round'] = merged_data['Episode']
    
    # Signature bake columns
    output_data['Signature Bake'] = merged_data['Signature_Bake']
    output_data['Signature Flavor'] = merged_data['Signature_Flavor'] 
    output_data['Signature Looks'] = merged_data['Signature_Looks']
    output_data['Signature Handshake'] = merged_data['Signature Handshake'].fillna('')
    
    # Technical rank
    output_data['Tech'] = merged_data['Technical_Rank'].astype('Int64')
    
    # First Half Review (before showstopper)
    output_data['First Half Review'] = merged_data['First Half Review'].fillna('')
    
    # Showstopper columns
    output_data['Showstopper Bake'] = merged_data['Showstopper_Bake']
    output_data['Showstopper Flavor'] = merged_data['Showstopper_Flavor']
    output_data['Showstopper Looks'] = merged_data['Showstopper_Looks']
    output_data['Showstopper Handshake'] = merged_data['Showstopper Handshake'].fillna('')
    
    # Map Final Review to Second Half Review
    output_data['Second Half Review'] = merged_data['Final Review'].fillna('')
    
    # Winner and Eliminated columns
    output_data['Winner'] = merged_data['Winner'].fillna('')
    output_data['Eliminated'] = merged_data['Eliminated'].fillna('')
    
    # Validate bake scores completeness
    print("\nValidating bake scores completeness...")
    score_columns = ['Signature_Bake', 'Signature_Flavor', 'Signature_Looks', 
                    'Showstopper_Bake', 'Showstopper_Flavor', 'Showstopper_Looks']
    
    incomplete_scores = []
    for idx, row in merged_data.iterrows():
        missing_scores = []
        for col in score_columns:
            if pd.isna(row[col]) or row[col] == '':
                missing_scores.append(col)
        
        if missing_scores:
            incomplete_scores.append({
                'contestant': row['Contestant'],
                'season': row['Season'], 
                'episode': row['Episode'],
                'missing': missing_scores
            })
    
    if incomplete_scores:
        print(f"🚨 ALERT: {len(incomplete_scores)} bakers do not have scores for all three bakes:")
        for item in incomplete_scores:
            print(f"  - {item['contestant']}, Season {item['season']}, Episode {item['episode']}: Missing {', '.join(item['missing'])}")
    else:
        print("* All bakers have complete scores for all three bakes")
    
    # Sort by Series, Round, then Contestant for consistency
    output_data = output_data.sort_values(['Series', 'Round', 'Contestant'])
    
    # Check for any rows that cause errors
    print("\nChecking for problematic rows...")
    error_rows = []
    
    try:
        # Check for any NaN values in critical columns that shouldn't have them
        critical_cols = ['Contestant', 'Series', 'Round']
        for col in critical_cols:
            nan_count = output_data[col].isna().sum()
            if nan_count > 0:
                error_rows.append(f"Column '{col}' has {nan_count} NaN values")
        
        # Check for duplicate entries
        duplicates = output_data.duplicated(subset=['Contestant', 'Series', 'Round'])
        if duplicates.any():
            dup_count = duplicates.sum()
            error_rows.append(f"{dup_count} duplicate rows found")
            print(f"🚨 ALERT: {dup_count} duplicate contestant/series/round combinations:")
            dup_rows = output_data[duplicates]
            for _, row in dup_rows.iterrows():
                print(f"  - {row['Contestant']}, Season {row['Series']}, Episode {row['Round']}")
        
        # Check for invalid data types
        if not pd.api.types.is_numeric_dtype(output_data['Tech']):
            non_numeric_tech = output_data[~pd.to_numeric(output_data['Tech'], errors='coerce').notna() & output_data['Tech'].notna()]
            if len(non_numeric_tech) > 0:
                error_rows.append(f"{len(non_numeric_tech)} non-numeric Tech values")
        
        if error_rows:
            print("🚨 ALERT: Issues found in claude_data:")
            for error in error_rows:
                print(f"  - {error}")
        else:
            print("* No problematic rows detected")
            
    except Exception as e:
        print(f"🚨 ALERT: Error during validation: {str(e)}")
    
    # Save to claude_data.csv
    try:
        output_data.to_csv('claude_data.csv', index=False)
        print(f"\n* Successfully created claude_data.csv with {len(output_data)} rows")
    except Exception as e:
        print(f"🚨 ALERT: Error saving claude_data.csv: {str(e)}")
        return None
    
    return output_data

if __name__ == "__main__":
    try:
        result = combine_claude_data()
        if result is not None:
            print("\nProcess completed successfully!")
        else:
            print("\nProcess failed!")
    except Exception as e:
        print(f"\nCRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()