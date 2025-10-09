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

def analyze_week(current_df, week_num, calculator, avg_variance):
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

        # For week 1, use average variance; otherwise calculate from data
        if week_num == 1:
            variance = avg_variance
        else:
            variance = np.var(strength_scores, ddof=1) if rounds_competed > 1 else 0

        # Check if eliminated and when
        eliminated = contestant_rounds['Eliminated'].max() == 1
        elimination_round = contestant_rounds[contestant_rounds['Eliminated'] == 1]['Round'].max() if eliminated else 999

        # Count stats
        star_bakers = int(contestant_rounds['Winner'].sum())
        pos_reviews = int((contestant_rounds['Second Half Review'] == 1).sum())
        neg_reviews = int((contestant_rounds['Second Half Review'] == -1).sum())

        contestant_stats.append({
            'Contestant': contestant,
            'Avg_Strength': avg_strength,
            'Variance': variance,
            'Star_Bakers': star_bakers,
            'Positive_Reviews': pos_reviews,
            'Negative_Reviews': neg_reviews,
            'Eliminated': eliminated,
            'Elimination_Round': elimination_round
        })

    stats_df = pd.DataFrame(contestant_stats)

    # Run Monte Carlo
    predictions_df = monte_carlo_simulation(stats_df, n_simulations=10000, n_finalists=3)

    # Merge and sort - active contestants by Finalist_Probability, then eliminated contestants by elimination round (descending)
    results_df = stats_df.merge(predictions_df, on='Contestant')
    results_df = results_df.sort_values(
        by=['Eliminated', 'Finalist_Probability', 'Elimination_Round'],
        ascending=[True, False, False]
    )

    return results_df

def main():
    # Placeholder string for end of output
    placeholder_string = """## Competition Evolution Commentary

### Week 1: Early Frontrunners Emerge
The season opened with **Nataliia** establishing herself as the clear favorite (73.2% finalist probability, 32.4% winner), earning Star Baker with a strong 8.27 average strength score. **Jessika** and **Lesley** rounded out the predicted top 3, with the field showing a wide spread of talent from 8.27 down to 3.78 (Hassan, who was eliminated).

### Week 2: The Great Shake-Up
Week 2 brought dramatic shifts in the predictions. **Tom** surged to dominance (98.8% finalist, 54.2% winner) with remarkably consistent performance (variance of just 0.03), claiming Star Baker. Meanwhile, **Nataliia** suffered a catastrophic collapse, plummeting from 1st to 7th place with a massive variance spike to 9.45—indicating highly inconsistent performance. **Jessika** maintained her position in the top tier despite dropping slightly, while **Iain** emerged as a dark horse with impressive consistency.

### Week 3: Volatility and New Contenders
**Tom** maintained his stranglehold on the competition with continued consistency (variance 0.12). **Jasmine** made a spectacular leap, climbing from 5th to 3rd place after earning Star Baker, though her high variance (3.10) suggests feast-or-famine performances. **Lesley** moved into the silver position with steady, reliable baking. The week saw further deterioration for previous favorites **Nataliia** (variance spiking to 5.50) and **Iain** (variance 4.65), with both now struggling in the bottom tier. **Jessika** fell out of the top 3 entirely due to increasing inconsistency.

### Week 4: The Jasmine Surge
By Week 4, a two-horse race emerged between **Tom** and **Jasmine**. While Tom maintained his near-lock on a finals spot (98.9%), **Jasmine's** winner probability exploded to 36.6% after claiming her second Star Baker award. Her average strength (8.05) now slightly exceeds Tom's (7.92), though her higher variance (2.99 vs 0.13) creates uncertainty. **Lesley** remained a steady third-place finisher, while former star **Jessika** was eliminated after her variance ballooned to 5.84—a cautionary tale of inconsistency in the tent.

### Key Patterns Observed
- **Consistency is King**: Tom's near-zero variance (.13) has made him the prohibitive favorite despite not having the highest raw strength score
- **High Variance Eliminates Contenders**: Nataliia, Iain, and Jessika all saw their chances evaporate when variance exceeded 4-5, regardless of their Star Baker wins
- **Late Surges Matter**: Jasmine's back-to-back strong performances transformed her from a long shot (17.8% in Week 2) to a genuine title contender
- **The Middle Ground Persists**: Lesley's steady, unspectacular consistency (variance 0.66) has kept her firmly in the finals conversation without ever threatening to win

As the competition enters its final stages, Tom appears virtually assured of a finals spot, while Jasmine and Lesley battle for the remaining positions. The question remains: can Jasmine's high-ceiling performances overcome Tom's machine-like consistency, or will variance prove her undoing?
"""

    # Initialize analyzer to get calculator with model weights
    print("Initializing analyzer and loading model weights...")
    analyzer = GBBOAnalyzer()
    analyzer.load_and_prepare_data()
    analyzer.validate_data()
    analyzer.train_and_analyze_models()

    # Initialize calculator by calling calculate_strength_scores
    _ = analyzer.calculate_strength_scores()

    # Calculate average historical variance
    summary_df = pd.read_csv('gbbo_complete_analysis_contestant_summary.csv')
    avg_variance = summary_df['Strength_Variance'].mean()
    print(f"Historical average variance: {avg_variance:.2f}")

    # Load current season data
    current_df = pd.read_csv('current.csv')
    max_week = int(current_df['Round'].max())

    # Open markdown file for writing
    with open('WEEKLY_PREDICTIONS.md', 'w') as f:
        f.write("# Season 13 Weekly Predictions\n\n")
        f.write("Progressive Monte Carlo simulation predictions for each week of Season 13.\n\n")
        f.write(f"**Method:** Monte Carlo simulation (10,000 iterations per week)\n\n")
        f.write("**Variance Calculation:**\n")
        f.write(f"- Week 1: All contestants use historical average variance ({avg_variance:.2f})\n")
        f.write("- Week 2+: Variance calculated from contestant's performance up to that week\n\n")
        f.write("---\n\n")

        # Analyze each week
        for week in range(1, max_week + 1):
            print(f"\nAnalyzing Week {week}...")
            results_df = analyze_week(current_df, week, analyzer.calculator, avg_variance)

            active_count = (~results_df['Eliminated']).sum()
            season_avg = results_df['Avg_Strength'].mean()

            # Write to markdown
            f.write(f"## Week {week}\n\n")
            f.write(f"**Active Contestants:** {active_count} | **Season Avg Strength:** {season_avg:.2f}\n\n")

            # Table header
            f.write("| Rank | Contestant | Finals | Winner | Avg Str | Variance | Star | Pos | Neg | Status |\n")
            f.write("|------|------------|--------|--------|---------|----------|------|-----|-----|--------|\n")

            # Table rows
            for idx, (_, row) in enumerate(results_df.iterrows(), 1):
                status = "ELIM" if row['Eliminated'] else "Active"
                f.write(f"| {idx} | {row['Contestant']} | {row['Finalist_Probability']:.1f}% | "
                       f"{row['Winner_Probability']:.1f}% | {row['Avg_Strength']:.2f} | "
                       f"{row['Variance']:.2f} | {int(row['Star_Bakers'])} | "
                       f"{int(row['Positive_Reviews'])} | {int(row['Negative_Reviews'])} | {status} |\n")

            # Top 3 prediction
            active_top3 = results_df[~results_df['Eliminated']].head(3)
            f.write(f"\n**Predicted Top 3:**\n")
            for idx, (_, row) in enumerate(active_top3.iterrows(), 1):
                f.write(f"{idx}. **{row['Contestant']}** - Finalist: {row['Finalist_Probability']:.1f}%, "
                       f"Winner: {row['Winner_Probability']:.1f}%\n")

            # Predicted winner
            winner = results_df.loc[results_df['Winner_Probability'].idxmax()]
            f.write(f"\n**Predicted Winner:** {winner['Contestant']} ({winner['Winner_Probability']:.1f}%)\n\n")
            f.write("---\n\n")

        # Write placeholder string at the end
        f.write(placeholder_string)

    print(f"\nWeekly predictions saved to WEEKLY_PREDICTIONS.md")

if __name__ == "__main__":
    main()
