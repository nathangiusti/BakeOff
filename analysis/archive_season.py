"""
End-of-season archive step.

Moves a finished season from current.csv into data.csv, resets current.csv to an
empty file (header only), and optionally retrains the weights and re-runs the analysis.

Usage:
  python analysis/archive_season.py [--dry-run] [--run-pipeline] [--force]

Examples:
  python analysis/archive_season.py --dry-run         # check what would happen
  python analysis/archive_season.py --run-pipeline    # archive, retrain weights, re-run analysis
"""

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / 'data_collection/judging/human/data.csv'
CURRENT_FILE = PROJECT_ROOT / 'data_collection/judging/human/current.csv'
EXPECTED_ROUNDS = 10


def fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def check_season(current_df, data_df, force):
    """Return the series number if current.csv is ready to archive, otherwise exit."""
    if current_df.empty:
        fail("current.csv has no data to archive.")

    series_values = current_df['Series'].dropna().unique()
    if len(series_values) != 1:
        fail(f"current.csv should hold exactly one series, found {sorted(series_values)}.")
    series = int(series_values[0])

    if list(current_df.columns) != list(data_df.columns):
        fail("current.csv columns do not match data.csv columns.")

    if series in set(data_df['Series']):
        fail(f"Series {series} is already in data.csv.")

    rounds = int(current_df['Round'].max())
    problems = []
    if rounds != EXPECTED_ROUNDS:
        problems.append(f"only {rounds} of {EXPECTED_ROUNDS} rounds entered")
    if (current_df['Round'] < 1).any():
        problems.append("rounds below 1 present (stray rows?)")
    star_bakers = current_df.groupby('Round')['Winner'].sum()
    if (star_bakers.iloc[:-1] != 1).any():
        problems.append(f"rounds without exactly one star baker: {list(star_bakers.index[:-1][star_bakers.iloc[:-1] != 1])}")
    final = current_df[current_df['Round'] == rounds]
    if len(final) != 3:
        problems.append(f"final round has {len(final)} bakers, expected 3")

    if problems and not force:
        fail("Season does not look finished: " + "; ".join(problems) + ". Use --force to archive anyway.")
    elif problems:
        print("WARNING (ignored with --force): " + "; ".join(problems))

    return series


def load_files():
    data_df = pd.read_csv(DATA_FILE)
    current_df = pd.read_csv(CURRENT_FILE)
    return data_df, current_df


def append_rows(series_rows_text):
    """Append raw CSV lines to data.csv, keeping its line ending style."""
    raw = DATA_FILE.read_bytes().decode('utf-8')
    newline = '\r\n' if '\r\n' in raw else '\n'
    if not raw.endswith('\n'):
        raw += newline
    DATA_FILE.write_bytes((raw + newline.join(series_rows_text) + newline).encode('utf-8'))


def run_step(command, cwd):
    print(f"\n>>> {' '.join(command)}  (in {cwd.relative_to(PROJECT_ROOT)})")
    if subprocess.run(command, cwd=cwd).returncode != 0:
        fail(f"Step failed: {' '.join(command)}")


def main():
    parser = argparse.ArgumentParser(description="Archive a finished season from current.csv into data.csv")
    parser.add_argument('--dry-run', action='store_true', help='Run the checks only; change nothing')
    parser.add_argument('--run-pipeline', action='store_true', help='Retrain weights and re-run the analysis afterwards')
    parser.add_argument('--force', action='store_true', help='Archive even if the season looks incomplete')
    args = parser.parse_args()

    data_df, current_df = load_files()
    series = check_season(current_df, data_df, args.force)
    print(f"Series {series}: {len(current_df)} rows over {int(current_df['Round'].max())} rounds ready to archive.")

    if args.dry_run:
        print("Dry run: nothing changed.")
        return

    lines = CURRENT_FILE.read_text(encoding='utf-8').splitlines()
    header, rows = lines[0], [line for line in lines[1:] if line.strip()]
    append_rows(rows)
    CURRENT_FILE.write_text(header + '\n', encoding='utf-8', newline='')
    print(f"Appended {len(rows)} rows to {DATA_FILE.relative_to(PROJECT_ROOT)} and reset current.csv.")

    if args.run_pipeline:
        run_step([sys.executable, 'train_weights.py'], PROJECT_ROOT / 'correlation_analysis')
        run_step([sys.executable, 'main.py'], PROJECT_ROOT / 'analysis')
    else:
        print("\nNext steps:")
        print("  cd correlation_analysis && python train_weights.py")
        print("  cd analysis && python main.py")

    print("\nStill manual: update readme.md (finalist table, rankings, theme table) and the season markdown.")


if __name__ == "__main__":
    main()
