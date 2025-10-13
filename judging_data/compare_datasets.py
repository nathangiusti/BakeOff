"""
Compare performance predictions between Claude's detailed transcript analysis and original data.

This script uses hardcoded weights from a previous model run to calculate strength scores
for each contestant in each episode, then identifies the largest differences between
the two datasets.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

# Actual weights from main.py model output (from component analysis)
WEIGHTS = {
    'signature_bake': 0.691,
    'signature_flavor': 0.240,
    'signature_looks': 0.816,
    'signature_handshake': 0.614,
    'tech': -3.176,  # Negative because lower tech rank is better  
    'showstopper_bake': 1.050,
    'showstopper_flavor': 1.362,
    'showstopper_looks': 1.411,
    'showstopper_handshake': 0.188
}

def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load both datasets"""
    claude_data = pd.read_csv('claude/claude_data.csv')
    original_data = pd.read_csv('data.csv')
    return claude_data, original_data

def calculate_strength_score(row: pd.Series) -> float:
    """Calculate strength score for a single row using hardcoded weights"""
    score = 0.0
    
    # Signature bake features
    if pd.notna(row.get('Signature Bake')):
        score += WEIGHTS['signature_bake'] * row['Signature Bake']
    if pd.notna(row.get('Signature Flavor')):
        score += WEIGHTS['signature_flavor'] * row['Signature Flavor']
    if pd.notna(row.get('Signature Looks')):
        score += WEIGHTS['signature_looks'] * row['Signature Looks']
    if pd.notna(row.get('Signature Handshake')) and row['Signature Handshake'] == 1:
        score += WEIGHTS['signature_handshake']
    
    # Technical (lower rank is better, so negative weight)
    if pd.notna(row.get('Tech')):
        # Normalize tech rank (assuming 12 contestants max)
        normalized_tech = (row['Tech'] - 1) / 11  # 0 = best, 1 = worst
        score += WEIGHTS['tech'] * normalized_tech
    
    # Showstopper features
    if pd.notna(row.get('Showstopper Bake')):
        score += WEIGHTS['showstopper_bake'] * row['Showstopper Bake']
    if pd.notna(row.get('Showstopper Flavor')):
        score += WEIGHTS['showstopper_flavor'] * row['Showstopper Flavor']
    if pd.notna(row.get('Showstopper Looks')):
        score += WEIGHTS['showstopper_looks'] * row['Showstopper Looks']
    if pd.notna(row.get('Showstopper Handshake')) and row['Showstopper Handshake'] == 1:
        score += WEIGHTS['showstopper_handshake']
    
    return score

def add_strength_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add strength scores to dataframe"""
    df = df.copy()
    df['Strength_Score'] = df.apply(calculate_strength_score, axis=1)
    return df

def find_overlapping_episodes(claude_data: pd.DataFrame, original_data: pd.DataFrame) -> List[Tuple[int, int]]:
    """Find episodes that appear in both datasets"""
    claude_episodes = set(zip(claude_data['Series'], claude_data['Round']))
    original_episodes = set(zip(original_data['Series'], original_data['Round']))
    return sorted(list(claude_episodes.intersection(original_episodes)))

def compare_datasets(claude_data: pd.DataFrame, original_data: pd.DataFrame) -> pd.DataFrame:
    """Compare strength scores between datasets for overlapping episodes"""
    overlapping_episodes = find_overlapping_episodes(claude_data, original_data)
    
    comparisons = []
    
    for series, episode in overlapping_episodes:
        # Get data for this episode from both datasets
        claude_episode = claude_data[(claude_data['Series'] == series) & 
                                   (claude_data['Round'] == episode)].copy()
        original_episode = original_data[(original_data['Series'] == series) & 
                                       (original_data['Round'] == episode)].copy()
        
        # Merge on contestant name
        merged = claude_episode.merge(
            original_episode, 
            on=['Contestant', 'Series', 'Round'], 
            suffixes=('_claude', '_original')
        )
        
        if len(merged) > 0:
            # Calculate strength scores
            merged['Claude_Score'] = merged.apply(
                lambda row: calculate_strength_score(
                    pd.Series({
                        'Signature Bake': row.get('Signature Bake_claude'),
                        'Signature Flavor': row.get('Signature Flavor_claude'),
                        'Signature Looks': row.get('Signature Looks_claude'),
                        'Signature Handshake': row.get('Signature Handshake_claude'),
                        'Tech': row.get('Tech_claude'),
                        'Showstopper Bake': row.get('Showstopper Bake_claude'),
                        'Showstopper Flavor': row.get('Showstopper Flavor_claude'),
                        'Showstopper Looks': row.get('Showstopper Looks_claude'),
                        'Showstopper Handshake': row.get('Showstopper Handshake_claude')
                    })
                ), axis=1
            )
            
            merged['Original_Score'] = merged.apply(
                lambda row: calculate_strength_score(
                    pd.Series({
                        'Signature Bake': row.get('Signature Bake_original'),
                        'Signature Flavor': row.get('Signature Flavor_original'),
                        'Signature Looks': row.get('Signature Looks_original'),
                        'Signature Handshake': row.get('Signature Handshake_original'),
                        'Tech': row.get('Tech_original'),
                        'Showstopper Bake': row.get('Showstopper Bake_original'),
                        'Showstopper Flavor': row.get('Showstopper Flavor_original'),
                        'Showstopper Looks': row.get('Showstopper Looks_original'),
                        'Showstopper Handshake': row.get('Showstopper Handshake_original')
                    })
                ), axis=1
            )
            
            # Calculate difference
            merged['Score_Difference'] = merged['Claude_Score'] - merged['Original_Score']
            merged['Abs_Difference'] = abs(merged['Score_Difference'])
            
            # Add episode info
            merged['Episode'] = f"S{series}E{episode}"
            
            comparisons.append(merged)
    
    if comparisons:
        return pd.concat(comparisons, ignore_index=True)
    else:
        return pd.DataFrame()

def print_largest_differences(comparison_df: pd.DataFrame, top_n: int = 20):
    """Print the performances with the largest differences"""
    if comparison_df.empty:
        print("No overlapping data found between datasets.")
        return
    
    # Sort by absolute difference
    sorted_df = comparison_df.sort_values('Abs_Difference', ascending=False)
    
    print(f"\nTop {top_n} Largest Differences in Strength Scores:")
    print("=" * 100)
    print(f"{'Contestant':<15} {'Episode':<8} {'Claude Score':<12} {'Original Score':<14} {'Difference':<12} {'Abs Diff':<10}")
    print("-" * 100)
    
    for _, row in sorted_df.head(top_n).iterrows():
        contestant = row['Contestant']
        episode = row['Episode']
        claude_score = row['Claude_Score']
        original_score = row['Original_Score']
        difference = row['Score_Difference']
        abs_diff = row['Abs_Difference']
        
        print(f"{contestant:<15} {episode:<8} {claude_score:>11.3f} {original_score:>13.3f} {difference:>11.3f} {abs_diff:>9.3f}")

def analyze_feature_differences(comparison_df: pd.DataFrame, top_n: int = 10):
    """Analyze which specific features contribute most to the differences"""
    if comparison_df.empty:
        return
    
    print(f"\n\nDetailed Analysis of Top {top_n} Differences:")
    print("=" * 120)
    
    sorted_df = comparison_df.sort_values('Abs_Difference', ascending=False)
    
    feature_pairs = [
        ('Signature Bake', 'signature_bake'),
        ('Signature Flavor', 'signature_flavor'), 
        ('Signature Looks', 'signature_looks'),
        ('Showstopper Bake', 'showstopper_bake'),
        ('Showstopper Flavor', 'showstopper_flavor'),
        ('Showstopper Looks', 'showstopper_looks'),
        ('Tech', 'tech')
    ]
    
    for _, row in sorted_df.head(top_n).iterrows():
        contestant = row['Contestant']
        episode = row['Episode']
        total_diff = row['Score_Difference']
        
        print(f"\n{contestant} - {episode} (Total Difference: {total_diff:.3f})")
        print("-" * 80)
        
        feature_contributions = []
        
        for feature_name, weight_key in feature_pairs:
            claude_val = row.get(f'{feature_name}_claude')
            original_val = row.get(f'{feature_name}_original')
            
            if pd.notna(claude_val) and pd.notna(original_val):
                if feature_name == 'Tech':
                    # Special handling for tech (lower is better)
                    claude_norm = (claude_val - 1) / 11
                    original_norm = (original_val - 1) / 11
                    diff = claude_norm - original_norm
                    contribution = WEIGHTS[weight_key] * diff
                else:
                    diff = claude_val - original_val
                    contribution = WEIGHTS[weight_key] * diff
                
                if abs(contribution) > 0.01:  # Only show significant contributions
                    feature_contributions.append((feature_name, claude_val, original_val, contribution))
        
        # Sort by absolute contribution
        feature_contributions.sort(key=lambda x: abs(x[3]), reverse=True)
        
        for feature_name, claude_val, original_val, contribution in feature_contributions:
            print(f"  {feature_name:<18}: Claude={claude_val:>5.1f}, Original={original_val:>5.1f}, "
                  f"Contribution={contribution:>7.3f}")

def main():
    """Main function"""
    print("Loading datasets...")
    claude_data, original_data = load_data()
    
    print(f"Claude data: {len(claude_data)} rows")
    print(f"Original data: {len(original_data)} rows")
    
    # Find overlapping episodes
    overlapping_episodes = find_overlapping_episodes(claude_data, original_data)
    print(f"Found {len(overlapping_episodes)} overlapping episodes")
    
    # Compare datasets
    print("Calculating strength scores and comparing...")
    comparison_df = compare_datasets(claude_data, original_data)
    
    if not comparison_df.empty:
        print(f"Successfully compared {len(comparison_df)} contestant performances")
        
        # Print statistics
        print(f"\nComparison Statistics:")
        print(f"Mean absolute difference: {comparison_df['Abs_Difference'].mean():.3f}")
        print(f"Median absolute difference: {comparison_df['Abs_Difference'].median():.3f}")
        print(f"Max absolute difference: {comparison_df['Abs_Difference'].max():.3f}")
        print(f"Min absolute difference: {comparison_df['Abs_Difference'].min():.3f}")
        
        # Show largest differences
        print_largest_differences(comparison_df, top_n=20)
        
        # Detailed analysis
        analyze_feature_differences(comparison_df, top_n=10)
        
        # Save results with truncated floats
        output_df = comparison_df.copy()
        
        # Round float columns to 2 decimal places
        float_columns = output_df.select_dtypes(include=['float64', 'float32']).columns
        for col in float_columns:
            output_df[col] = output_df[col].round(2)
        
        output_df.to_csv('dataset_comparison.csv', index=False)
        print(f"\nFull comparison saved to 'dataset_comparison.csv'")
        
    else:
        print("No matching data found for comparison.")

if __name__ == "__main__":
    main()