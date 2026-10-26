"""
Weekly Monte Carlo predictions for the season in progress.

Reads data_collection/judging/human/current.csv and writes (or updates) the
week's section of output/season_markdown/weekly_predictions_s<series>.md.
Re-running a week replaces its table but keeps any commentary already written.

Usage:
  python monte_carlo/weekly_predictions.py <week> [--series N] [--simulations N]

Examples:
  python monte_carlo/weekly_predictions.py 3
  python monte_carlo/weekly_predictions.py 3 --series 14
"""

import argparse
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "shared"))

from gbbo_analysis.analyzer import GBBOAnalyzer

CURRENT_FILE = PROJECT_ROOT / 'data_collection/judging/human/current.csv'
MARKDOWN_DIR = PROJECT_ROOT / 'output/season_markdown'
FIXED_WEEK_1_VARIANCE = 3.0
COMMENTARY_PLACEHOLDER = "_TODO: add commentary_"
LF, CRLF = chr(10), chr(13) + chr(10)


def normalize_tech_score(tech_score, num_contestants):
    """Normalize technical rank to 0-1 scale."""
    if pd.isna(tech_score) or num_contestants <= 1:
        return 0
    return 1 - (tech_score - 1) / (num_contestants - 1)


def calculate_strength_score(row, num_contestants, calculator):
    """Calculate strength score using the calculator with model weights."""
    def val(col):
        return 0 if pd.isna(row[col]) else row[col]

    result = calculator.calculate_strength_score(
        signature_bake=val('Signature Bake'),
        signature_flavor=val('Signature Flavor'),
        signature_looks=val('Signature Looks'),
        signature_handshake=val('Signature Handshake'),
        tech_normalized=normalize_tech_score(row['Tech'], num_contestants),
        showstopper_bake=val('Showstopper Bake'),
        showstopper_flavor=val('Showstopper Flavor'),
        showstopper_looks=val('Showstopper Looks'),
        showstopper_handshake=val('Showstopper Handshake')
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
        results.append({
            'Contestant': contestant,
            'Finalist_Probability': (finalist_counts[contestant] / n_simulations) * 100,
            'Winner_Probability': (winner_counts[contestant] / n_simulations) * 100
        })

    return pd.DataFrame(results)


def analyze_week(current_df, week_num, calculator, fixed_variance=None, n_simulations=10000):
    """Analyze a specific week with progressive variance calculation."""
    week_data = current_df[current_df['Round'] <= week_num].copy()

    contestant_stats = []
    all_scores = []

    for contestant in week_data['Contestant'].unique():
        contestant_rounds = week_data[week_data['Contestant'] == contestant]

        strength_scores = []
        week_score = None
        for _, row in contestant_rounds.iterrows():
            num_contestants = len(week_data[week_data['Round'] == row['Round']])
            strength = calculate_strength_score(row, num_contestants, calculator)
            strength_scores.append(strength)
            if row['Round'] == week_num:
                week_score = strength

        all_scores.extend(strength_scores)
        avg_strength = np.mean(strength_scores)
        rounds_competed = len(strength_scores)

        # Use fixed variance for week 1, otherwise calculate from data
        if fixed_variance is not None:
            variance = fixed_variance
        else:
            variance = np.var(strength_scores, ddof=1) if rounds_competed > 1 else 0

        eliminated = contestant_rounds['Eliminated'].max() == 1
        # A baker who stops appearing without being eliminated withdrew (not a performance exit)
        withdrawn = not eliminated and contestant_rounds['Round'].max() < week_num
        elimination_round = contestant_rounds[contestant_rounds['Eliminated'] == 1]['Round'].max() if eliminated else 999
        if withdrawn:
            elimination_round = contestant_rounds['Round'].max()

        contestant_stats.append({
            'Contestant': contestant,
            'Avg_Strength': avg_strength,
            'Variance': variance,
            'Week_Score': week_score,
            'Star_Bakers': int(contestant_rounds['Winner'].sum()),
            'High_Reviews': int((contestant_rounds['Second Half Review'] == 1).sum()),
            'Low_Reviews': int((contestant_rounds['Second Half Review'] == -1).sum()),
            'Eliminated': eliminated or withdrawn,
            'Withdrawn': withdrawn,
            'Elimination_Round': elimination_round
        })

    stats_df = pd.DataFrame(contestant_stats)
    predictions_df = monte_carlo_simulation(stats_df, n_simulations=n_simulations, n_finalists=3)
    results_df = stats_df.merge(predictions_df, on='Contestant')

    # Active contestants by finalist probability, then eliminated ones (latest exit first)
    results_df = results_df.sort_values(
        by=['Eliminated', 'Finalist_Probability', 'Winner_Probability', 'Elimination_Round'],
        ascending=[True, False, False, False]
    )

    return results_df, float(np.mean(all_scores))


def build_week_section(week_num, results_df, season_avg, commentary, heading=None):
    """Build the markdown section for one week."""
    active = int((~results_df['Eliminated']).sum())
    lines = [
        heading or f"## Week {week_num}",
        "",
        f"**Active Contestants:** {active} | **Season Avg Strength:** {season_avg:.2f}",
        "",
        "| Rank | Contestant | Finals | Winner | Avg Str | Variance | Week Score | Star | High | Low | Status |",
        "|------|------------|--------|--------|---------|----------|------------|------|------|-----|--------|",
    ]

    for idx, (_, row) in enumerate(results_df.iterrows(), 1):
        week_score = "-" if pd.isna(row['Week_Score']) else f"{row['Week_Score']:.2f}"
        status = "WITHDREW" if row['Withdrawn'] else "ELIM" if row['Eliminated'] else "Active"
        lines.append(
            f"| {idx} | {row['Contestant']} | {row['Finalist_Probability']:.1f}% | "
            f"{row['Winner_Probability']:.1f}% | {row['Avg_Strength']:.2f} | {row['Variance']:.2f} | "
            f"{week_score} | {row['Star_Bakers']} | {row['High_Reviews']} | {row['Low_Reviews']} | {status} |"
        )

    lines += ["", "**Predicted Top 3:**"]
    for i, (_, row) in enumerate(results_df.head(3).iterrows(), 1):
        lines.append(f"{i}. **{row['Contestant']}** - Finalist: {row['Finalist_Probability']:.1f}%, "
                     f"Winner: {row['Winner_Probability']:.1f}%")

    winner = results_df.loc[results_df['Winner_Probability'].idxmax()]
    lines += ["", f"**Predicted Winner:** {winner['Contestant']} ({winner['Winner_Probability']:.1f}%)", ""]
    lines.append(commentary.strip() if commentary else f"### Week {week_num} Commentary\n\n{COMMENTARY_PLACEHOLDER}")
    return "\n".join(lines) + "\n\n---\n\n"


def split_blocks(text):
    """Split a season markdown file into blocks that each start with '## '."""
    return [b for b in re.split(r'(?m)^(?=## )', text) if b]


def existing_commentary(block):
    """Pull the hand-written commentary (from '### Week N Commentary' on) out of a week block."""
    match = re.search(r'(?ms)^### Week \d+ Commentary.*', block)
    if not match:
        return None
    commentary = re.sub(r'\s*\n---\s*$', '', match.group(0)).strip()
    return None if commentary.endswith(COMMENTARY_PLACEHOLDER) else commentary


def existing_heading(block):
    """Keep a hand-edited heading such as '## Week 9 (Semifinals)'."""
    return block.splitlines()[0].strip()


def season_header(series):
    return (f"# Season {series} Weekly Predictions\n\n"
            f"Progressive Monte Carlo simulation predictions for each week of Season {series}.\n\n"
            "**Method:** Monte Carlo simulation (10,000 iterations per week)\n\n"
            "**Variance Calculation:**\n"
            f"- Week 1: All contestants use fixed variance ({FIXED_WEEK_1_VARIANCE})\n"
            "- Week 2+: Variance calculated from contestant's performance up to that week\n\n"
            "---\n\n")


def write_week(series, week_num, section_builder, markdown_dir=MARKDOWN_DIR):
    """Insert or replace one week's section in the season markdown file."""
    markdown_dir.mkdir(parents=True, exist_ok=True)
    path = markdown_dir / f"weekly_predictions_s{series}.md"
    newline = os.linesep
    if path.exists():
        raw = path.read_bytes().decode('utf-8')
        newline = CRLF if CRLF in raw else LF  # keep the file's existing line endings
        text = raw.replace(CRLF, LF)
    else:
        text = season_header(series)

    blocks = split_blocks(text)
    header = blocks[0] if blocks and not blocks[0].startswith('## ') else season_header(series)
    rest = blocks[1:] if blocks and not blocks[0].startswith('## ') else blocks

    weeks, others = {}, []
    for block in rest:
        match = re.match(r'## Week (\d+)', block)
        if match:
            weeks[int(match.group(1))] = block
        else:
            others.append(block)

    old = weeks.get(week_num)
    weeks[week_num] = section_builder(existing_commentary(old) if old else None,
                                      existing_heading(old) if old else None)

    ordered = [weeks[w] for w in sorted(weeks)]
    path.write_text(header + "".join(ordered) + "".join(others), encoding='utf-8', newline='\n')
    return path


def main():
    parser = argparse.ArgumentParser(description="Weekly Monte Carlo predictions for the current season")
    parser.add_argument('week', type=int, help='Week (round) number to analyze')
    parser.add_argument('--series', type=int, help='Series number (default: taken from current.csv)')
    parser.add_argument('--input', type=Path, default=CURRENT_FILE, help='Season data CSV (default: current.csv)')
    parser.add_argument('--output-dir', type=Path, default=MARKDOWN_DIR, help='Markdown output folder')
    parser.add_argument('--simulations', type=int, default=10000, help='Monte Carlo iterations (default 10000)')
    args = parser.parse_args()

    current_df = pd.read_csv(args.input)
    if current_df.empty:
        print(f"No data in {args.input} yet.")
        sys.exit(1)

    series = args.series or int(current_df['Series'].iloc[0])
    current_df = current_df[current_df['Series'] == series]
    if args.week not in set(current_df['Round']):
        print(f"No Series {series} data for week {args.week} in current.csv "
              f"(weeks present: {sorted(current_df['Round'].unique())})")
        sys.exit(1)

    # Initialize analyzer to get calculator with model weights
    print("Initializing analyzer and loading model weights...")
    analyzer = GBBOAnalyzer()
    analyzer.load_and_prepare_data()
    analyzer.validate_data()
    analyzer.train_and_analyze_models()
    _ = analyzer.calculate_strength_scores()

    # Week 1 has no history, so use a fixed variance
    fixed_variance = FIXED_WEEK_1_VARIANCE if args.week == 1 else None

    print(f"\nAnalyzing Series {series}, Week {args.week}...")
    results_df, season_avg = analyze_week(current_df, args.week, analyzer.calculator,
                                          fixed_variance, args.simulations)

    path = write_week(series, args.week,
                      lambda commentary, heading: build_week_section(args.week, results_df, season_avg,
                                                                     commentary, heading),
                      args.output_dir)
    print(f"Week {args.week} written to {path}")


if __name__ == "__main__":
    main()
