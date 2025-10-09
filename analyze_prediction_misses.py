#!/usr/bin/env python3
"""
Analyze the largest combined misses in star baker and elimination predictions by round.

Total Miss = Star Baker Miss + Elimination Miss
Where:
- Star Baker Miss = |Predicted Winner Strength - Actual Winner Strength|
- Elimination Miss = |Predicted Eliminated Strength - Actual Eliminated Strength|
"""

import pandas as pd


def analyze_prediction_misses():
    """Analyze largest combined misses by round."""

    # Load the complete analysis data
    df = pd.read_csv('gbbo_complete_analysis.csv')

    # Get all unique series/round combinations
    rounds = df[['Series', 'Round']].drop_duplicates().sort_values(['Series', 'Round'])

    round_misses = []

    for _, round_info in rounds.iterrows():
        series = round_info['Series']
        round_num = round_info['Round']

        # Get all contestants in that series/round
        round_df = df[(df['Series'] == series) & (df['Round'] == round_num)]

        # Find predicted and actual winners
        best_strength = round_df['Strength_Score'].max()
        predicted_winner_row = round_df[round_df['Strength_Score'] == best_strength].iloc[0]
        predicted_winner = predicted_winner_row['Contestant']

        actual_winner_row = round_df[round_df['Result'] == 'Winner']
        if len(actual_winner_row) > 0:
            actual_winner = actual_winner_row.iloc[0]['Contestant']
            actual_winner_strength = actual_winner_row.iloc[0]['Strength_Score']
            winner_miss = abs(best_strength - actual_winner_strength)
        else:
            actual_winner = None
            actual_winner_strength = None
            winner_miss = 0.0

        # Find predicted and actual eliminated
        worst_strength = round_df['Strength_Score'].min()
        predicted_eliminated_row = round_df[round_df['Strength_Score'] == worst_strength].iloc[0]
        predicted_eliminated = predicted_eliminated_row['Contestant']

        actual_eliminated_row = round_df[round_df['Result'] == 'Eliminated']
        if len(actual_eliminated_row) > 0:
            actual_eliminated = actual_eliminated_row.iloc[0]['Contestant']
            actual_eliminated_strength = actual_eliminated_row.iloc[0]['Strength_Score']
            elimination_miss = abs(actual_eliminated_strength - worst_strength)
        else:
            actual_eliminated = None
            actual_eliminated_strength = None
            elimination_miss = 0.0

        # Calculate total miss
        total_miss = winner_miss + elimination_miss

        round_misses.append({
            'Series': int(series),
            'Round': int(round_num),
            'Predicted_Winner': predicted_winner,
            'Predicted_Winner_Strength': best_strength,
            'Actual_Winner': actual_winner,
            'Actual_Winner_Strength': actual_winner_strength,
            'Winner_Miss': winner_miss,
            'Predicted_Eliminated': predicted_eliminated,
            'Predicted_Eliminated_Strength': worst_strength,
            'Actual_Eliminated': actual_eliminated,
            'Actual_Eliminated_Strength': actual_eliminated_strength,
            'Elimination_Miss': elimination_miss,
            'Total_Miss': total_miss
        })

    # Create dataframe and sort by total miss
    misses_df = pd.DataFrame(round_misses).sort_values('Total_Miss', ascending=False)

    print("=" * 90)
    print("COMBINED PREDICTION MISS ANALYSIS BY ROUND")
    print("=" * 90)
    print("\nTotal Miss = Star Baker Miss + Elimination Miss")
    print("\nTop 20 Rounds with Largest Combined Misses:\n")

    for idx, row in misses_df.head(20).iterrows():
        print(f"Total Miss: {row['Total_Miss']:.2f} | Series {row['Series']} Round {row['Round']}")
        print(f"  Star Baker Miss: {row['Winner_Miss']:.2f}")
        if row['Actual_Winner']:
            print(f"    Predicted: {row['Predicted_Winner']:20s} (Strength: {row['Predicted_Winner_Strength']:.2f})")
            print(f"    Actual:    {row['Actual_Winner']:20s} (Strength: {row['Actual_Winner_Strength']:.2f})")
        else:
            print(f"    Predicted: {row['Predicted_Winner']:20s} (Strength: {row['Predicted_Winner_Strength']:.2f})")
            print(f"    Actual:    No winner this round")

        print(f"  Elimination Miss: {row['Elimination_Miss']:.2f}")
        if row['Actual_Eliminated']:
            print(f"    Predicted: {row['Predicted_Eliminated']:20s} (Strength: {row['Predicted_Eliminated_Strength']:.2f})")
            print(f"    Actual:    {row['Actual_Eliminated']:20s} (Strength: {row['Actual_Eliminated_Strength']:.2f})")
        else:
            print(f"    Predicted: {row['Predicted_Eliminated']:20s} (Strength: {row['Predicted_Eliminated_Strength']:.2f})")
            print(f"    Actual:    No elimination this round")
        print()

    # Summary statistics
    print("=" * 90)
    print("SUMMARY STATISTICS")
    print("=" * 90)

    rounds_with_both = misses_df[(misses_df['Actual_Winner'].notna()) & (misses_df['Actual_Eliminated'].notna())]

    print(f"\nTotal Rounds Analyzed: {len(misses_df)}")
    print(f"Rounds with Both Winner and Elimination: {len(rounds_with_both)}")
    print(f"\nAverage Total Miss: {misses_df['Total_Miss'].mean():.2f}")
    print(f"Average Winner Miss: {misses_df['Winner_Miss'].mean():.2f}")
    print(f"Average Elimination Miss: {misses_df['Elimination_Miss'].mean():.2f}")

    perfect_predictions = len(misses_df[misses_df['Total_Miss'] < 0.01])
    print(f"\nPerfect Rounds (both predictions correct): {perfect_predictions}")

    print("\n" + "=" * 90)


if __name__ == '__main__':
    analyze_prediction_misses()