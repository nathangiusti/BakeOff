import pandas as pd
import numpy as np
from gbbo_analysis import GBBOAnalyzer

def normalize_tech_score(tech_score, num_contestants):
    """Normalize technical score to 0-1 scale."""
    if pd.isna(tech_score) or num_contestants <= 1:
        return 0
    return 1 - (tech_score - 1) / (num_contestants - 1)

def calculate_strength_score(row, num_contestants, calculator):
    """Calculate strength score using the calculator with model weights."""
    # Get normalized tech score
    tech_norm = normalize_tech_score(row['Tech'], num_contestants)

    # Calculate strength score
    result = calculator.calculate_strength_score(
        signature_bake=row['S - Bake'] if not pd.isna(row['S - Bake']) else 0,
        signature_flavor=row['S - Flavor'] if not pd.isna(row['S - Flavor']) else 0,
        signature_looks=row['S - Looks'] if not pd.isna(row['S - Looks']) else 0,
        signature_handshake=row['Handshake 1'] if not pd.isna(row['Handshake 1']) else 0,
        tech_normalized=tech_norm,
        showstopper_bake=row['F - Bake'] if not pd.isna(row['F - Bake']) else 0,
        showstopper_flavor=row['F - Flavor'] if not pd.isna(row['F - Flavor']) else 0,
        showstopper_looks=row['F - Looks'] if not pd.isna(row['F - Looks']) else 0,
        showstopper_handshake=row['Handshake 2'] if not pd.isna(row['Handshake 2']) else 0
    )
    return result['strength_score']

def monte_carlo_simulation(contestants_df, n_simulations=10000, n_finalists=3):
    """Run Monte Carlo simulation."""
    np.random.seed(42)

    finalist_counts = {name: 0 for name in contestants_df['Contestant']}
    winner_counts = {name: 0 for name in contestants_df['Contestant']}

    for sim in range(n_simulations):
        remaining = contestants_df[~contestants_df['Eliminated']].copy()

        while len(remaining) > n_finalists:
            performances = {}
            for _, contestant in remaining.iterrows():
                std_dev = np.sqrt(contestant['Variance']) if contestant['Variance'] > 0 else 0.1
                performance = np.random.normal(contestant['Avg_Strength'], std_dev)
                performances[contestant['Contestant']] = performance

            weakest = min(performances, key=performances.get)
            remaining = remaining[remaining['Contestant'] != weakest]

        for _, finalist in remaining.iterrows():
            finalist_counts[finalist['Contestant']] += 1

        if len(remaining) > 0:
            final_performances = {}
            for _, contestant in remaining.iterrows():
                std_dev = np.sqrt(contestant['Variance']) if contestant['Variance'] > 0 else 0.1
                final_performance = np.random.normal(contestant['Avg_Strength'], std_dev)
                final_performances[contestant['Contestant']] = final_performance

            winner = max(final_performances, key=final_performances.get)
            winner_counts[winner] += 1

    results = []
    for contestant in contestants_df['Contestant']:
        finalist_prob = (finalist_counts[contestant] / n_simulations) * 100
        winner_prob = (winner_counts[contestant] / n_simulations) * 100

        results.append({
            'Contestant': contestant,
            'Finalist_Probability': finalist_prob,
            'Winner_Probability': winner_prob
        })

    return pd.DataFrame(results)

def analyze_week(current_df, week_num, calculator, fixed_variance=None):
    """Analyze a specific week with progressive variance calculation."""
    # Get all contestants up to this week
    week_data = current_df[current_df['Round'] <= week_num].copy()

    contestant_stats = []

    for contestant in week_data['Contestant'].unique():
        contestant_rounds = week_data[week_data['Contestant'] == contestant]

        # Calculate strength scores
        strength_scores = []
        for _, row in contestant_rounds.iterrows():
            num_contestants = len(week_data[week_data['Round'] == row['Round']])
            strength = calculate_strength_score(row, num_contestants, calculator)
            strength_scores.append(strength)

        avg_strength = np.mean(strength_scores)
        rounds_competed = len(strength_scores)

        # Use fixed variance for week 1, otherwise calculate from data
        if fixed_variance is not None:
            variance = fixed_variance
        else:
            variance = np.var(strength_scores, ddof=1) if rounds_competed > 1 else 0

        # Check if eliminated and when
        eliminated = contestant_rounds['Eliminated'].max() == 1
        elimination_round = contestant_rounds[contestant_rounds['Eliminated'] == 1]['Round'].max() if eliminated else 999

        # Count stats
        star_bakers = int(contestant_rounds['Winner'].sum())
        pos_reviews = int((contestant_rounds['Second Half Review'] == 1).sum())
        neg_reviews = int((contestant_rounds['Second Half Review'] == -1).sum())
        
        # High reviews include positive reviews AND star baker wins
        high_reviews = pos_reviews + star_bakers

        contestant_stats.append({
            'Contestant': contestant,
            'Avg_Strength': avg_strength,
            'Variance': variance,
            'Star_Bakers': star_bakers,
            'High_Reviews': high_reviews,
            'Low_Reviews': neg_reviews,
            'Eliminated': eliminated,
            'Elimination_Round': elimination_round
        })

    stats_df = pd.DataFrame(contestant_stats)

    # Run Monte Carlo
    predictions_df = monte_carlo_simulation(stats_df, n_simulations=10000, n_finalists=3)

    # Merge and sort
    results_df = stats_df.merge(predictions_df, on='Contestant')
    
    # Sort active contestants by Winner_Probability (descending), eliminated by Elimination_Round (ascending)
    results_df = results_df.sort_values(
        by=['Eliminated', 'Winner_Probability', 'Elimination_Round'],
        ascending=[True, False, True]
    )

    return results_df

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python weekly_predictions.py <week_number>")
        sys.exit(1)
    
    week_num = int(sys.argv[1])
    
    # Initialize analyzer to get calculator with model weights
    print("Initializing analyzer and loading model weights...")
    analyzer = GBBOAnalyzer()
    analyzer.load_and_prepare_data()
    analyzer.validate_data()
    analyzer.train_and_analyze_models()

    # Initialize calculator by calling calculate_strength_scores
    _ = analyzer.calculate_strength_scores()

    # Load current season data
    current_df = pd.read_csv('current.csv')
    
    # For week 1, use fixed variance of 3.0
    fixed_variance = 3.0 if week_num == 1 else None
    
    print(f"\nAnalyzing Week {week_num}...")
    results_df = analyze_week(current_df, week_num, analyzer.calculator, fixed_variance)
    
    # Print table
    print(f"\n=== WEEK {week_num} PREDICTIONS ===")
    print(f"{'Rank':<4} {'Contestant':<12} {'Finals':<8} {'Winner':<8} {'Avg Str':<8} {'Variance':<8} {'Star':<4} {'High':<4} {'Low':<4} {'Status':<8}")
    print("=" * 80)
    
    for idx, (_, row) in enumerate(results_df.iterrows(), 1):
        status = "ELIM" if row['Eliminated'] else "Active"
        print(f"{idx:<4} {row['Contestant']:<12} {row['Finalist_Probability']:<7.1f}% "
              f"{row['Winner_Probability']:<7.1f}% {row['Avg_Strength']:<8.2f} "
              f"{row['Variance']:<8.2f} {int(row['Star_Bakers']):<4} "
              f"{int(row['High_Reviews']):<4} {int(row['Low_Reviews']):<4} {status:<8}")
    
    return results_df

if __name__ == "__main__":
    main()
