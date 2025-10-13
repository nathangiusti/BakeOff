#!/usr/bin/env python3
"""
Historical Monte Carlo Analysis for GBBO Previous Seasons
Generates weekly predictions for specific season/episode using existing strength scores
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import random
import sys
import argparse

class HistoricalMonteCarloAnalyzer:
    def __init__(self, data_path: str):
        """Initialize with historical data"""
        self.data = pd.read_csv(data_path)
        self.series_data = {}
        self._prepare_data()
    
    def _prepare_data(self):
        """Organize data by series"""
        for series in range(5, 13):
            series_df = self.data[self.data['Series'] == series].copy()
            self.series_data[series] = series_df
    
    def calculate_variance(self, contestant_scores: List[float]) -> float:
        """Calculate variance for a contestant's scores"""
        if len(contestant_scores) < 2:
            return 3.0  # Default variance for single data point
        return np.var(contestant_scores, ddof=1)
    
    def get_contestants_for_week(self, series: int, week: int) -> List[str]:
        """Get all contestants who appear in a specific week (including those eliminated that week)"""
        series_df = self.series_data[series]
        
        # Get all contestants who appeared in this week
        current_week_contestants = series_df[series_df['Round'] == week]['Contestant'].unique().tolist()
        
        return current_week_contestants
    
    def get_contestant_stats(self, series: int, contestant: str, through_week: int) -> Dict:
        """Get contestant statistics through a specific week"""
        series_df = self.series_data[series]
        contestant_data = series_df[
            (series_df['Contestant'] == contestant) & 
            (series_df['Round'] <= through_week)
        ]
        
        if contestant_data.empty:
            return {'avg_strength': 0, 'variance': 3.0, 'scores': [], 'results': []}
        
        scores = contestant_data['Strength_Score'].tolist()
        results = contestant_data['Result'].tolist()
        
        # Count achievements
        star_baker_count = sum(1 for r in results if r == 'Winner')
        high_count = sum(1 for score in scores if score >= 8.0)
        low_count = sum(1 for score in scores if score <= 4.0)
        
        return {
            'avg_strength': np.mean(scores),
            'variance': self.calculate_variance(scores),
            'scores': scores,
            'results': results,
            'star_baker_count': star_baker_count,
            'high_count': high_count,
            'low_count': low_count,
            'current_week_score': scores[-1] if scores else 0
        }
    
    def monte_carlo_simulation(self, contestants_stats: Dict, num_simulations: int = 10000) -> Dict:
        """Run Monte Carlo simulation for a given week"""
        results = {contestant: {'finals': 0, 'winner': 0} for contestant in contestants_stats.keys()}
        
        for _ in range(num_simulations):
            # Simulate remaining competition
            remaining_contestants = list(contestants_stats.keys())
            
            # Simulate until we have 3 finalists
            while len(remaining_contestants) > 3:
                # Generate performance scores for each contestant
                week_performances = {}
                for contestant in remaining_contestants:
                    stats = contestants_stats[contestant]
                    # Sample from normal distribution based on avg and variance
                    std_dev = np.sqrt(stats['variance'])
                    performance = np.random.normal(stats['avg_strength'], std_dev)
                    week_performances[contestant] = max(0, min(10, performance))  # Clamp to 0-10
                
                # Eliminate lowest performer (with some randomness)
                sorted_contestants = sorted(remaining_contestants, 
                                          key=lambda x: week_performances[x] + np.random.normal(0, 0.5))
                eliminated = sorted_contestants[0]
                remaining_contestants.remove(eliminated)
            
            # Count finalists
            for finalist in remaining_contestants:
                results[finalist]['finals'] += 1
            
            # Determine winner from finalists
            finalist_performances = {}
            for contestant in remaining_contestants:
                stats = contestants_stats[contestant]
                std_dev = np.sqrt(stats['variance'])
                performance = np.random.normal(stats['avg_strength'], std_dev)
                finalist_performances[contestant] = max(0, min(10, performance))
            
            winner = max(remaining_contestants, key=lambda x: finalist_performances[x])
            results[winner]['winner'] += 1
        
        # Convert to percentages
        for contestant in results:
            results[contestant]['finals'] = (results[contestant]['finals'] / num_simulations) * 100
            results[contestant]['winner'] = (results[contestant]['winner'] / num_simulations) * 100
        
        return results
    
    def analyze_series_week(self, series: int, week: int) -> Dict:
        """Analyze a specific week of a series"""
        contestants = self.get_contestants_for_week(series, week)
        
        # Get stats for each contestant through this week
        contestants_stats = {}
        for contestant in contestants:
            stats = self.get_contestant_stats(series, contestant, week)
            contestants_stats[contestant] = stats
        
        # Run Monte Carlo simulation
        mc_results = self.monte_carlo_simulation(contestants_stats)
        
        # Combine stats with MC results
        weekly_analysis = {}
        for contestant in contestants:
            stats = contestants_stats[contestant]
            mc_result = mc_results[contestant]
            
            # Determine status
            series_df = self.series_data[series]
            week_data = series_df[(series_df['Contestant'] == contestant) & (series_df['Round'] == week)]
            status = "ELIM" if not week_data.empty and week_data.iloc[0]['Result'] == 'Eliminated' else "Active"
            
            weekly_analysis[contestant] = {
                'finals_prob': mc_result['finals'],
                'winner_prob': mc_result['winner'],
                'avg_strength': stats['avg_strength'],
                'variance': stats['variance'],
                'week_score': stats['current_week_score'],
                'star_baker_count': stats['star_baker_count'],
                'high_count': stats['high_count'],
                'low_count': stats['low_count'],
                'status': status
            }
        
        return weekly_analysis
    
    def get_series_max_weeks(self, series: int) -> int:
        """Get maximum number of weeks for a series"""
        return self.series_data[series]['Round'].max()

def print_week_analysis_table(analyzer: HistoricalMonteCarloAnalyzer, series: int, week: int):
    """Print analysis table for a specific week to console"""
    weekly_analysis = analyzer.analyze_series_week(series, week)
    
    # Sort contestants by finals probability, then winner probability
    sorted_contestants = sorted(weekly_analysis.items(), 
                              key=lambda x: (x[1]['finals_prob'], x[1]['winner_prob']), 
                              reverse=True)
    
    print(f"## Week {week}")
    print()
    
    # Create table
    print("| Rank | Contestant | Finals | Winner | Avg Str | Variance | Week Score | Star | High | Low | Status |")
    print("|------|------------|--------|--------|---------|----------|------------|------|------|-----|--------|")
    
    series_df = analyzer.series_data[series]
    max_weeks = analyzer.get_series_max_weeks(series)
    
    for rank, (contestant, stats) in enumerate(sorted_contestants, 1):
        week_score = f"{stats['week_score']:.2f}" if stats['status'] == 'Active' or week == max_weeks else "-"
        if stats['status'] == 'ELIM' and week > 1:
            # Check if this is their elimination week
            elimination_week = None
            for w in range(1, week + 1):
                week_contestants = analyzer.get_contestants_for_week(series, w)
                if contestant in week_contestants:
                    week_data_check = series_df[(series_df['Contestant'] == contestant) & (series_df['Round'] == w)]
                    if not week_data_check.empty and week_data_check.iloc[0]['Result'] == 'Eliminated':
                        elimination_week = w
                        break
            
            if elimination_week and elimination_week < week:
                week_score = "-"
        
        print(f"| {rank} | {contestant} | {stats['finals_prob']:.1f}% | {stats['winner_prob']:.1f}% | "
              f"{stats['avg_strength']:.2f} | {stats['variance']:.2f} | {week_score} | "
              f"{stats['star_baker_count']} | {stats['high_count']} | {stats['low_count']} | {stats['status']} |")
    
    # Add predicted top 3 and winner
    top_3 = sorted_contestants[:3]
    predicted_winner = max(sorted_contestants, key=lambda x: x[1]['winner_prob'])
    
    print()
    print("**Predicted Top 3:**")
    for i, (contestant, stats) in enumerate(top_3, 1):
        print(f"{i}. **{contestant}** - Finalist: {stats['finals_prob']:.1f}%, Winner: {stats['winner_prob']:.1f}%")
    
    print(f"\n**Predicted Winner:** {predicted_winner[0]} ({predicted_winner[1]['winner_prob']:.1f}%)")
    print()

def main():
    """Main function to handle command line arguments and run analysis"""
    parser = argparse.ArgumentParser(description='Generate Monte Carlo analysis for specific GBBO season/episode')
    parser.add_argument('season', type=int, help='Season number (5-12)')
    parser.add_argument('episode', type=int, help='Episode number')
    parser.add_argument('--data-path', default='../analysis_output/gbbo_complete_analysis.csv', help='Path to data file')
    
    args = parser.parse_args()
    
    # Validate season
    if args.season < 5 or args.season > 12:
        print("Error: Season must be between 5 and 12")
        sys.exit(1)
    
    # Initialize analyzer
    try:
        analyzer = HistoricalMonteCarloAnalyzer(args.data_path)
    except FileNotFoundError:
        print(f"Error: Data file '{args.data_path}' not found")
        sys.exit(1)
    
    # Validate episode
    max_episodes = analyzer.get_series_max_weeks(args.season)
    if args.episode < 1 or args.episode > max_episodes:
        print(f"Error: Episode must be between 1 and {max_episodes} for Season {args.season}")
        sys.exit(1)
    
    # Generate and print analysis
    print_week_analysis_table(analyzer, args.season, args.episode)

if __name__ == "__main__":
    main()