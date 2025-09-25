"""
Main analysis orchestration for GBBO analysis.
"""

import pandas as pd
from pathlib import Path
from typing import Optional

from .config import Config
from .validation import GBBODataValidator
from .models import GBBOModelTrainer
from .calculator import StrengthScoreCalculator

# Theme analysis is now integrated into ANALYSIS_RESULTS.md


class GBBOAnalyzer:
    """Main analyzer class that orchestrates the complete analysis"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.df: Optional[pd.DataFrame] = None
        self.validator: Optional[GBBODataValidator] = None
        self.trainer: Optional[GBBOModelTrainer] = None
        self.calculator: Optional[StrengthScoreCalculator] = None
    
    def load_and_prepare_data(self) -> None:
        """Load and prepare the data for analysis"""
        if not Path(self.config.INPUT_FILE).exists():
            raise FileNotFoundError(f"Input file {self.config.INPUT_FILE} not found")
        
        self.df = pd.read_csv(self.config.INPUT_FILE)
        
        # Fill missing values with 0 as specified
        columns_to_fill = (self.config.SIGNATURE_COLS + self.config.SHOWSTOPPER_COLS + 
                          ['Second Half Review', 'Winner', 'Eliminated'])
        
        for col in columns_to_fill:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(0)
        
        # Create normalized tech scores
        self._normalize_tech_scores()
    
    def _normalize_tech_scores(self) -> None:
        """Normalize tech scores by round within each series"""
        self.df['Tech_Normalized'] = 0.0
        
        for series in self.df['Series'].unique():
            for round_num in self.df['Round'].unique():
                mask = (self.df['Series'] == series) & (self.df['Round'] == round_num)
                round_data = self.df[mask]
                
                if len(round_data) > 0:
                    min_tech = round_data['Tech'].min()
                    max_tech = round_data['Tech'].max()
                    
                    for idx in round_data.index:
                        raw_tech = self.df.loc[idx, 'Tech']
                        if max_tech > min_tech:
                            normalized = 1 - (raw_tech - min_tech) / (max_tech - min_tech)
                        else:
                            normalized = 1.0  # All contestants tied
                        self.df.loc[idx, 'Tech_Normalized'] = normalized
    
    def validate_data(self) -> bool:
        """Validate the loaded data"""
        if self.df is None:
            raise ValueError("Data must be loaded before validation")
        
        self.validator = GBBODataValidator(self.df)
        validation_passed = self.validator.validate_all()
        self.validator.print_results()
        return validation_passed
    
    def train_and_analyze_models(self) -> None:
        """Train models and analyze correlations"""
        if self.df is None:
            raise ValueError("Data must be loaded before training models")
        
        self.trainer = GBBOModelTrainer(self.df, self.config)
        second_accuracy = self.trainer.train_models()
        
        # Calculate correlations (needed for model weights) but don't print
        self.trainer.analyze_correlations()
        
        # Analyze component weights (this prints output)
        self.trainer.analyze_component_weights()
        
        # Analyze component variance (this prints output)
        self.trainer.analyze_component_variance()
        
        # Store accuracy for later printing
        self._second_accuracy = second_accuracy
        self._second_count = len(self.df[self.df['Second Half Review'] != 0])
    
    def calculate_strength_scores(self) -> pd.DataFrame:
        """Calculate strength scores for all contestants"""
        if self.df is None:
            raise ValueError("Data must be loaded before calculating strength scores")
        
        # Get model weights and pass to calculator
        model_weights = self.trainer.get_model_weights()
        self.calculator = StrengthScoreCalculator(self.config, model_weights)
        output_data = []
        
        for _, row in self.df.iterrows():
            # Handle missing handshake data
            sig_handshake = row['Signature Handshake'] if not pd.isna(row['Signature Handshake']) else 0
            show_handshake = row['Showstopper Handshake'] if not pd.isna(row['Showstopper Handshake']) else 0
            
            # Check if showstopper data exists
            has_showstopper = not pd.isna(row['Showstopper Bake'])
            
            # Calculate strength score
            if has_showstopper:
                score_result = self.calculator.calculate_strength_score(
                    row['Signature Bake'], row['Signature Flavor'], row['Signature Looks'],
                    sig_handshake, row['Tech_Normalized'],
                    row['Showstopper Bake'], row['Showstopper Flavor'], row['Showstopper Looks'],
                    show_handshake
                )
            else:
                score_result = self.calculator.calculate_strength_score(
                    row['Signature Bake'], row['Signature Flavor'], row['Signature Looks'],
                    sig_handshake, row['Tech_Normalized']
                )
            
            # Handle missing review/outcome data
            second_half_review = row['Second Half Review'] if not pd.isna(row['Second Half Review']) else 0
            winner = row['Winner'] if not pd.isna(row['Winner']) else 0
            eliminated = row['Eliminated'] if not pd.isna(row['Eliminated']) else 0
            
            # Determine result status
            if winner == 1:
                result = "Winner"
            elif eliminated == 1:
                result = "Eliminated"
            else:
                # Check second half review sentiment
                if second_half_review > 0:
                    result = "Positive Review"
                elif second_half_review < 0:
                    result = "Negative Review"
                else:
                    result = "Neutral Review"
            
            # Create output record
            output_record = {
                'Contestant': row['Contestant'],
                'Series': row['Series'],
                'Round': row['Round'],
                'Strength_Score': round(score_result['strength_score'], 2),
                'Result': result
            }
            
            output_data.append(output_record)
        
        return pd.DataFrame(output_data)
    
    def print_accuracy_metrics(self, output_df: pd.DataFrame) -> None:
        """Print all accuracy metrics together in organized sections"""
        print("\nACCURACY METRICS")
        print("-" * 40)
        
        # Subsection 1: Model Prediction Accuracy
        print(f"Model Prediction Accuracy:")
        print(f"  Second Half Review Prediction: {self._second_accuracy:.1%} accuracy ({self._second_count} rounds)")
        
        # Subsection 2: Prediction Accuracy (Weekly Outcomes)
        self._print_prediction_accuracy_subsection(output_df)
        
        # Subsection 3: Probability-Weighted Accuracy
        self._print_probability_weighted_accuracy_subsection(output_df)
        
        # Print strength score analysis after accuracy metrics
        self._print_strength_performance_analysis(output_df)
        self._print_season_winner_prediction_accuracy(output_df)

    def _print_strength_performance_analysis(self, output_df: pd.DataFrame) -> None:
        """Print combined strength score analysis and performance insights"""
        print(f"\nSTRENGTH SCORE & PERFORMANCE ANALYSIS")
        print("-" * 45)
        
        print(f"Strength Score Summary:")
        print(f"  Average: {output_df['Strength_Score'].mean():.2f}/10  |  Range: {output_df['Strength_Score'].min():.2f} - {output_df['Strength_Score'].max():.2f}")
        
        # Outcome correlations
        print(f"\nOutcome Correlations:")
        print(f"  Star Bakers: {output_df[output_df['Result']=='Winner']['Strength_Score'].mean():.2f}/10 average")
        print(f"  Eliminations: {output_df[output_df['Result']=='Eliminated']['Strength_Score'].mean():.2f}/10 average")
        print(f"  Safe contestants: {output_df[output_df['Result']!='Eliminated']['Strength_Score'].mean():.2f}/10 average")

        # Performance ranges analysis
        high_performers = output_df[output_df['Strength_Score'] >= self.config.HIGH_PERFORMANCE_THRESHOLD]
        mid_performers = output_df[(output_df['Strength_Score'] >= self.config.MID_PERFORMANCE_THRESHOLD) & 
                                 (output_df['Strength_Score'] < self.config.HIGH_PERFORMANCE_THRESHOLD)]
        low_performers = output_df[output_df['Strength_Score'] < self.config.MID_PERFORMANCE_THRESHOLD]
        
        # Win rates
        high_win_rate = (high_performers['Result'] == 'Winner').mean() * 100
        mid_win_rate = (mid_performers['Result'] == 'Winner').mean() * 100
        low_win_rate = (low_performers['Result'] == 'Winner').mean() * 100
        
        high_winner_count = (high_performers['Result'] == 'Winner').sum()
        mid_winner_count = (mid_performers['Result'] == 'Winner').sum()
        low_winner_count = (low_performers['Result'] == 'Winner').sum()
        
        print(f"\nStar Baker Win Rates by Performance Level:")
        print(f"  High performers ({self.config.HIGH_PERFORMANCE_THRESHOLD}+): {high_win_rate:.1f}% ({high_winner_count}/{len(high_performers)})")
        print(f"  Mid performers ({self.config.MID_PERFORMANCE_THRESHOLD}-{self.config.HIGH_PERFORMANCE_THRESHOLD-0.1:.1f}): {mid_win_rate:.1f}% ({mid_winner_count}/{len(mid_performers)})")
        print(f"  Low performers (<{self.config.MID_PERFORMANCE_THRESHOLD}): {low_win_rate:.1f}% ({low_winner_count}/{len(low_performers)})")
        
        # Elimination rates
        high_elim_rate = (high_performers['Result'] == 'Eliminated').mean() * 100
        mid_elim_rate = (mid_performers['Result'] == 'Eliminated').mean() * 100
        low_elim_rate = (low_performers['Result'] == 'Eliminated').mean() * 100
        
        high_elim_count = (high_performers['Result'] == 'Eliminated').sum()
        mid_elim_count = (mid_performers['Result'] == 'Eliminated').sum()
        low_elim_count = (low_performers['Result'] == 'Eliminated').sum()
        
        print(f"\nElimination Rates by Performance Level:")
        print(f"  High performers ({self.config.HIGH_PERFORMANCE_THRESHOLD}+): {high_elim_rate:.1f}% ({high_elim_count}/{len(high_performers)})")
        print(f"  Mid performers ({self.config.MID_PERFORMANCE_THRESHOLD}-{self.config.HIGH_PERFORMANCE_THRESHOLD-0.1:.1f}): {mid_elim_rate:.1f}% ({mid_elim_count}/{len(mid_performers)})")
        print(f"  Low performers (<{self.config.MID_PERFORMANCE_THRESHOLD}): {low_elim_rate:.1f}% ({low_elim_count}/{len(low_performers)})")

    def generate_performance_analysis(self, output_df: pd.DataFrame) -> None:
        """Generate comprehensive performance analysis - DEPRECATED, moved to new location"""
        # This function is now empty - the analysis was moved to _print_strength_performance_analysis
        pass

    def _get_contestant_stats(self, contestant_name: str, series: int, group: pd.DataFrame) -> dict:
        """Calculate contestant statistics including corrected star baker wins and handshakes"""
        # Get max round for this series to identify final round
        max_round = self.df[self.df['Series'] == series]['Round'].max()
        
        # Count star baker wins excluding final round
        star_baker_wins = len(group[(group['Result'] == 'Winner') & (group['Round'] != max_round)])
        
        # Get original data for this contestant to count handshakes
        contestant_original_data = self.df[(self.df['Contestant'] == contestant_name) & (self.df['Series'] == series)]
        
        # Count handshakes
        sig_handshakes = len(contestant_original_data[contestant_original_data['Signature Handshake'] == 1])
        show_handshakes = len(contestant_original_data[contestant_original_data['Showstopper Handshake'] == 1])
        
        return {
            'star_baker_wins': star_baker_wins,
            'sig_handshakes': sig_handshakes,
            'show_handshakes': show_handshakes
        }

    def _get_elimination_status(self, series: int, group: pd.DataFrame) -> str:
        """Determine detailed elimination status for a contestant"""
        # Get max round for this series
        max_round = self.df[self.df['Series'] == series]['Round'].max()
        
        # Check if contestant was eliminated
        elimination_round = group[group['Result'] == 'Eliminated']
        if len(elimination_round) == 0:
            # Not eliminated - they're a finalist
            return "finalist"
        
        # Get the round they were eliminated in
        elim_round = elimination_round.iloc[0]['Round']
        
        # Determine status based on elimination round relative to final
        if elim_round == max_round:
            # This shouldn't happen (eliminated in final), but handle it
            return "finalist"
        elif elim_round == max_round - 1:
            # Eliminated in penultimate round
            return "semifinalist"
        elif elim_round == max_round - 2:
            # Eliminated in round before semifinal
            return "quarterfinalist"
        else:
            # Eliminated earlier - show specific round
            return f"R{elim_round} elimination"

    def print_baker_performance(self, output_df: pd.DataFrame) -> None:
        """Print baker performance metrics"""
        print("\nBAKER PERFORMANCE")
        print("-" * 40)
        
        # Top and bottom performers
        self._print_top_bottom_performers(output_df)
        self._print_performance_outliers(output_df)
        self._print_series_winners_analysis(output_df)
        self._print_elimination_analysis_by_round(output_df)
    
    def _print_top_bottom_performers(self, output_df: pd.DataFrame) -> None:
        """Print top and bottom 5 performers"""
        print(f"\nTop 5 Performances:")
        top_5 = output_df.nlargest(5, 'Strength_Score')
        for _, row in top_5.iterrows():
            winner_str = " *" if row['Result'] == 'Winner' else ""
            print(f"  {row['Contestant']:12} S{row['Series']}R{row['Round']:2}: {row['Strength_Score']:.2f}/10{winner_str}")
        
        print(f"\nBottom 5 Performances:")
        bottom_5 = output_df.nsmallest(5, 'Strength_Score')
        for _, row in bottom_5.iterrows():
            elim_str = " X" if row['Result'] == 'Eliminated' else ""
            print(f"  {row['Contestant']:12} S{row['Series']}R{row['Round']:2}: {row['Strength_Score']:.2f}/10{elim_str}")
    
    def _print_prediction_accuracy_subsection(self, output_df: pd.DataFrame) -> None:
        """Print how accurately strength scores predict winners, eliminations, and reviews"""
        print("\nPrediction Accuracy (Weekly Outcomes):")
        print("-" * 40)
        
        # Group by series and round to analyze weekly predictions
        weekly_groups = output_df.groupby(['Series', 'Round'])
        
        winner_predictions_correct = 0
        elimination_predictions_correct = 0
        good_review_predictions_correct = 0
        bad_review_predictions_correct = 0
        total_weeks_with_winners = 0
        total_weeks_with_eliminations = 0
        total_weeks_with_good_reviews = 0
        total_weeks_with_bad_reviews = 0
        total_good_reviews_predicted = 0
        total_bad_reviews_predicted = 0
        
        
        for (series, round_num), week_data in weekly_groups:
            # Sort contestants by strength score for ranking analysis
            week_sorted = week_data.sort_values('Strength_Score', ascending=False).reset_index(drop=True)
            
            # Check winner prediction (highest strength score vs actual winner)
            if (week_data['Result'] == 'Winner').sum() > 0:  # Week has a winner
                total_weeks_with_winners += 1
                highest_score_contestant = week_data.loc[week_data['Strength_Score'].idxmax()]
                
                if highest_score_contestant['Result'] == 'Winner':
                    winner_predictions_correct += 1
            
            # Check elimination prediction (lowest strength score vs actual elimination)
            if (week_data['Result'] == 'Eliminated').sum() > 0:  # Week has an elimination
                total_weeks_with_eliminations += 1
                lowest_score_contestant = week_data.loc[week_data['Strength_Score'].idxmin()]
                
                if lowest_score_contestant['Result'] == 'Eliminated':
                    elimination_predictions_correct += 1
            
            # Check good review predictions (top N performers vs actual positive reviews)
            actual_good_reviews = week_data[week_data['Result'] == 'Positive Review']
            if len(actual_good_reviews) > 0:
                total_weeks_with_good_reviews += 1
                num_good_reviews = len(actual_good_reviews)
                
                # Get top N performers (where N = number of good reviews)
                predicted_good_performers = week_sorted.head(num_good_reviews)
                
                # Count how many of our top N predictions actually got good reviews
                correct_good_predictions = 0
                for _, predicted in predicted_good_performers.iterrows():
                    if predicted['Result'] == 'Positive Review':
                        correct_good_predictions += 1
                
                good_review_predictions_correct += correct_good_predictions
                total_good_reviews_predicted += num_good_reviews
            
            # Check bad review predictions (bottom N performers vs actual negative reviews)
            actual_bad_reviews = week_data[week_data['Result'] == 'Negative Review']
            if len(actual_bad_reviews) > 0:
                total_weeks_with_bad_reviews += 1
                num_bad_reviews = len(actual_bad_reviews)
                
                # Get bottom N performers (where N = number of bad reviews)
                predicted_bad_performers = week_sorted.tail(num_bad_reviews)
                
                # Count how many of our bottom N predictions actually got bad reviews
                correct_bad_predictions = 0
                for _, predicted in predicted_bad_performers.iterrows():
                    if predicted['Result'] == 'Negative Review':
                        correct_bad_predictions += 1
                
                bad_review_predictions_correct += correct_bad_predictions
                total_bad_reviews_predicted += num_bad_reviews
        
        # Calculate accuracies
        winner_accuracy = (winner_predictions_correct / total_weeks_with_winners * 100) if total_weeks_with_winners > 0 else 0
        elimination_accuracy = (elimination_predictions_correct / total_weeks_with_eliminations * 100) if total_weeks_with_eliminations > 0 else 0
        good_review_accuracy = (good_review_predictions_correct / total_good_reviews_predicted * 100) if total_good_reviews_predicted > 0 else 0
        bad_review_accuracy = (bad_review_predictions_correct / total_bad_reviews_predicted * 100) if total_bad_reviews_predicted > 0 else 0
        
        print(f"Winner Prediction Accuracy:")
        print(f"  Highest strength score = Star Baker: {winner_predictions_correct}/{total_weeks_with_winners} ({winner_accuracy:.1f}%)")
        
        print(f"\nElimination Prediction Accuracy:")
        print(f"  Lowest strength score = Eliminated: {elimination_predictions_correct}/{total_weeks_with_eliminations} ({elimination_accuracy:.1f}%)")
        
        print(f"\nReview Prediction Accuracy:")
        print(f"  Top N performers = Positive reviews: {good_review_predictions_correct}/{total_good_reviews_predicted} ({good_review_accuracy:.1f}%) across {total_weeks_with_good_reviews} weeks")
        print(f"  Bottom N performers = Negative reviews: {bad_review_predictions_correct}/{total_bad_reviews_predicted} ({bad_review_accuracy:.1f}%) across {total_weeks_with_bad_reviews} weeks")
    
    def _print_probability_weighted_accuracy_subsection(self, output_df: pd.DataFrame) -> None:
        """Calculate probability-weighted accuracy metrics (Brier Score, Log Loss, Calibration)"""
        import math
        
        print(f"\nProbability-Weighted Accuracy:")
        print("-" * 35)
        
        weekly_groups = output_df.groupby(['Series', 'Round'])
        
        # Collect predictions and outcomes for different metrics
        winner_predictions = []  # (predicted_probability, actual_outcome_0_or_1)
        elimination_predictions = []
        
        for (series, round_num), week_data in weekly_groups:
            
            # Winner predictions - calculate probability each contestant wins
            if (week_data['Result'] == 'Winner').sum() > 0:
                contestant_strengths = [(row['Contestant'], row['Strength_Score']) for _, row in week_data.iterrows()]
                win_probabilities = self.calculate_finalist_win_probabilities(contestant_strengths, method='softmax')
                
                for _, contestant in week_data.iterrows():
                    predicted_prob = win_probabilities[contestant['Contestant']]
                    actual_outcome = 1 if contestant['Result'] == 'Winner' else 0
                    winner_predictions.append((predicted_prob, actual_outcome))
            
            # Elimination predictions - calculate probability each contestant is eliminated
            if (week_data['Result'] == 'Eliminated').sum() > 0:
                # For elimination, we reverse the strength scores (lower strength = higher elimination probability)
                contestant_strengths_reversed = [(row['Contestant'], -row['Strength_Score']) for _, row in week_data.iterrows()]
                elim_probabilities = self.calculate_finalist_win_probabilities(contestant_strengths_reversed, method='softmax')
                
                for _, contestant in week_data.iterrows():
                    predicted_prob = elim_probabilities[contestant['Contestant']]
                    actual_outcome = 1 if contestant['Result'] == 'Eliminated' else 0
                    elimination_predictions.append((predicted_prob, actual_outcome))
        
        # Calculate Brier Score (lower is better, 0 = perfect, 1 = worst possible)
        def calculate_brier_score(predictions):
            if not predictions:
                return None
            total_score = sum((pred_prob - actual) ** 2 for pred_prob, actual in predictions)
            return total_score / len(predictions)
        
        # Calculate Log Loss (lower is better, 0 = perfect, higher = worse)
        def calculate_log_loss(predictions):
            if not predictions:
                return None
            # Add small epsilon to prevent log(0)
            epsilon = 1e-15
            total_loss = 0
            for pred_prob, actual in predictions:
                pred_prob = max(epsilon, min(1-epsilon, pred_prob))  # Clamp to [epsilon, 1-epsilon]
                if actual == 1:
                    total_loss -= math.log(pred_prob)
                else:
                    total_loss -= math.log(1 - pred_prob)
            return total_loss / len(predictions)
        
        # Calculate Calibration Error (how well probabilities match actual frequencies)
        def calculate_calibration_error(predictions, num_bins=10):
            if not predictions:
                return None
            
            # Sort predictions by probability
            sorted_predictions = sorted(predictions, key=lambda x: x[0])
            bin_size = len(sorted_predictions) // num_bins
            
            total_calibration_error = 0
            bins_used = 0
            
            for i in range(num_bins):
                start_idx = i * bin_size
                end_idx = (i + 1) * bin_size if i < num_bins - 1 else len(sorted_predictions)
                
                if start_idx >= len(sorted_predictions):
                    break
                    
                bin_predictions = sorted_predictions[start_idx:end_idx]
                if not bin_predictions:
                    continue
                
                avg_predicted_prob = sum(pred for pred, _ in bin_predictions) / len(bin_predictions)
                actual_frequency = sum(actual for _, actual in bin_predictions) / len(bin_predictions)
                bin_weight = len(bin_predictions) / len(sorted_predictions)
                
                total_calibration_error += bin_weight * abs(avg_predicted_prob - actual_frequency)
            
            return total_calibration_error
        
        # Calculate and display metrics
        winner_brier = calculate_brier_score(winner_predictions)
        winner_log_loss = calculate_log_loss(winner_predictions)
        winner_calibration = calculate_calibration_error(winner_predictions)
        
        elimination_brier = calculate_brier_score(elimination_predictions)
        elimination_log_loss = calculate_log_loss(elimination_predictions)
        elimination_calibration = calculate_calibration_error(elimination_predictions)
        
        print(f"Winner Predictions (based on strength score probabilities):")
        print(f"  Brier Score: {winner_brier:.3f} (lower = better, 0 = perfect)")
        print(f"  Log Loss: {winner_log_loss:.3f} (lower = better, 0 = perfect)")
        print(f"  Calibration Error: {winner_calibration:.3f} (lower = better, 0 = perfect)")
        print(f"  Total predictions: {len(winner_predictions)}")
        
        print(f"\nElimination Predictions (based on inverted strength scores):")
        print(f"  Brier Score: {elimination_brier:.3f} (lower = better, 0 = perfect)")
        print(f"  Log Loss: {elimination_log_loss:.3f} (lower = better, 0 = perfect)")
        print(f"  Calibration Error: {elimination_calibration:.3f} (lower = better, 0 = perfect)")
        print(f"  Total predictions: {len(elimination_predictions)}")
        
        # Calculate baseline accuracy for comparison
        if winner_predictions:
            baseline_winner_rate = sum(actual for _, actual in winner_predictions) / len(winner_predictions)
            baseline_brier = baseline_winner_rate * (1 - baseline_winner_rate) + (1 - baseline_winner_rate) * baseline_winner_rate
            winner_skill_score = 1 - (winner_brier / baseline_brier) if baseline_brier > 0 else 0
            winner_improvement = winner_skill_score * 100
        
        if elimination_predictions:
            baseline_elim_rate = sum(actual for _, actual in elimination_predictions) / len(elimination_predictions)
            baseline_brier_elim = baseline_elim_rate * (1 - baseline_elim_rate) + (1 - baseline_elim_rate) * baseline_elim_rate
            elim_skill_score = 1 - (elimination_brier / baseline_brier_elim) if baseline_brier_elim > 0 else 0
            elim_improvement = elim_skill_score * 100
        
        print(f"\nPERFORMANCE VS RANDOM GUESSING:")
        if winner_predictions:
            print(f"Winner Predictions:")
            print(f"  Brier Score: {winner_brier:.3f} (range 0-1, lower better) - {winner_improvement:.0f}% better than random")
            print(f"  Calibration: {winner_calibration:.3f} (range 0-1, lower better)")
        
        if elimination_predictions:
            print(f"Elimination Predictions:")
            print(f"  Brier Score: {elimination_brier:.3f} (range 0-1, lower better) - {elim_improvement:.0f}% better than random")
            print(f"  Calibration: {elimination_calibration:.3f} (range 0-1, lower better)")
    
    def _print_season_winner_prediction_accuracy(self, output_df: pd.DataFrame) -> None:
        """Analyze how accurately we predict final round winners from average strength scores among finalists"""
        print("\nFINAL ROUND WINNER PREDICTION ACCURACY")
        print("-" * 40)
        
        # Find finalists for each series (contestants who made it to the final round)
        finalist_data = []
        for series in output_df['Series'].unique():
            series_data = output_df[output_df['Series'] == series]
            final_round = series_data['Round'].max()
            finalists = series_data[series_data['Round'] == final_round]
            
            for _, finalist in finalists.iterrows():
                # Calculate average strength for this contestant across all their rounds
                contestant_rounds = series_data[series_data['Contestant'] == finalist['Contestant']]
                avg_strength = contestant_rounds['Strength_Score'].mean()
                is_winner = finalist['Result'] == 'Winner'
                
                finalist_data.append({
                    'Contestant': finalist['Contestant'],
                    'Series': series,
                    'Average_Strength': avg_strength,
                    'Total_Rounds': len(contestant_rounds),
                    'Is_Winner': is_winner,
                    'Final_Round_Score': finalist['Strength_Score']
                })
        
        finalist_df = pd.DataFrame(finalist_data)
        
        # Analyze prediction accuracy by series among finalists only
        correct_predictions = 0
        total_series = 0
        prediction_details = []
        
        for series in finalist_df['Series'].unique():
            total_series += 1
            series_finalists = finalist_df[finalist_df['Series'] == series].copy()
            
            # Find actual winner and predicted winner (highest average strength among finalists)
            actual_winner = series_finalists[series_finalists['Is_Winner'] == True]
            predicted_winner = series_finalists.loc[series_finalists['Average_Strength'].idxmax()]
            
            if len(actual_winner) > 0:
                actual_winner = actual_winner.iloc[0]
                
                # Check if prediction is correct
                is_correct = predicted_winner['Contestant'] == actual_winner['Contestant']
                if is_correct:
                    correct_predictions += 1
                
                # Calculate ranking error among finalists
                series_sorted = series_finalists.sort_values('Average_Strength', ascending=False).reset_index(drop=True)
                predicted_rank = series_sorted[series_sorted['Contestant'] == predicted_winner['Contestant']].index[0] + 1
                actual_rank = series_sorted[series_sorted['Contestant'] == actual_winner['Contestant']].index[0] + 1
                ranking_error = abs(predicted_rank - actual_rank)
                
                # Calculate strength score difference
                strength_diff = predicted_winner['Average_Strength'] - actual_winner['Average_Strength']
                
                # Count number of finalists
                num_finalists = len(series_finalists)
                
                prediction_details.append({
                    'series': series,
                    'predicted': predicted_winner['Contestant'],
                    'actual': actual_winner['Contestant'],
                    'correct': is_correct,
                    'predicted_strength': predicted_winner['Average_Strength'],
                    'actual_strength': actual_winner['Average_Strength'],
                    'strength_diff': strength_diff,
                    'ranking_error': ranking_error,
                    'predicted_rank': predicted_rank,
                    'actual_rank': actual_rank,
                    'num_finalists': num_finalists
                })
        
        # Calculate overall accuracy
        accuracy = (correct_predictions / total_series * 100) if total_series > 0 else 0
        
        print(f"Final Round Winner Prediction Accuracy (among finalists only):")
        print(f"  Highest average strength = Final winner: {correct_predictions}/{total_series} ({accuracy:.1f}%)")
        
        # Calculate error statistics for incorrect predictions
        incorrect_predictions = [p for p in prediction_details if not p['correct']]
        if incorrect_predictions:
            avg_strength_diff = sum(abs(p['strength_diff']) for p in incorrect_predictions) / len(incorrect_predictions)
            print(f"  Average strength difference when wrong: {avg_strength_diff:.2f} points")
        
        # Show all finalists and their rankings by series
        print(f"\nFinalist Rankings by Average Strength:")
        for series in sorted(finalist_df['Series'].unique()):
            series_finalists = finalist_df[finalist_df['Series'] == series].copy()
            series_sorted = series_finalists.sort_values('Average_Strength', ascending=False)
            winner = series_finalists[series_finalists['Is_Winner'] == True].iloc[0]['Contestant'] if len(series_finalists[series_finalists['Is_Winner'] == True]) > 0 else "Unknown"
            
            # Calculate win probabilities for this series' finalists
            finalist_strengths = [(row['Contestant'], row['Average_Strength']) for _, row in series_sorted.iterrows()]
            probabilities = self.calculate_finalist_win_probabilities(finalist_strengths, method='softmax')
            
            print(f"  Series {series} (Winner: {winner}):")
            for i, (_, finalist) in enumerate(series_sorted.iterrows(), 1):
                winner_mark = " *" if finalist['Is_Winner'] else ""
                win_prob = probabilities[finalist['Contestant']] * 100
                print(f"    {i}. {finalist['Contestant']:12}: {finalist['Average_Strength']:.2f}/10 avg ({win_prob:.1f}% win chance){winner_mark}")
            print()
        
        # Calculate and display series rankings by overall average strength - moved to bottom
        self._print_series_by_overall_strength(output_df)
    
    def calculate_finalist_win_probabilities(self, finalist_strengths: list, method: str = 'softmax') -> dict:
        """
        Calculate win probabilities for finalists based on their strength scores.
        
        Args:
            finalist_strengths: List of (contestant_name, avg_strength_score) tuples
            method: Calculation method - 'softmax', 'normalized', or 'exponential'
        
        Returns:
            Dictionary with contestant names as keys and win probabilities as values
        """
        import math
        
        if not finalist_strengths or len(finalist_strengths) < 2:
            raise ValueError("Need at least 2 finalists to calculate probabilities")
        
        names = [f[0] for f in finalist_strengths]
        scores = [f[1] for f in finalist_strengths]
        
        if method == 'softmax':
            # Softmax function - exponentially weights higher scores
            # Temperature parameter controls how sharp the distribution is
            temperature = 2.0  # Lower = more confident, higher = more spread out
            exp_scores = [math.exp(score / temperature) for score in scores]
            sum_exp = sum(exp_scores)
            probabilities = [exp_score / sum_exp for exp_score in exp_scores]
            
        elif method == 'normalized':
            # Simple normalized probabilities - linear relationship
            min_score = min(scores)
            # Add small offset to prevent zero probabilities
            adjusted_scores = [score - min_score + 0.1 for score in scores]
            sum_adjusted = sum(adjusted_scores)
            probabilities = [adj_score / sum_adjusted for adj_score in adjusted_scores]
            
        elif method == 'exponential':
            # Exponential weighting with moderate steepness
            exp_scores = [math.exp(score * 0.5) for score in scores]
            sum_exp = sum(exp_scores)
            probabilities = [exp_score / sum_exp for exp_score in exp_scores]
            
        else:
            raise ValueError(f"Unknown method: {method}. Use 'softmax', 'normalized', or 'exponential'")
        
        return dict(zip(names, probabilities))
    
    def predict_finalist_winner_probabilities(self, output_df: pd.DataFrame, series: int = None, 
                                            contestant_names: list = None, method: str = 'softmax') -> None:
        """
        Calculate and display win probabilities for finalists in a specific series or for given contestants.
        
        Args:
            output_df: Analysis output dataframe
            series: Series number to analyze (if None, analyzes most recent series)
            contestant_names: List of contestant names (if provided, calculates their probabilities)
            method: Probability calculation method
        """
        print(f"\nFINALIST WIN PROBABILITY ANALYSIS")
        print("-" * 40)
        
        if contestant_names:
            # Use provided contestant names - find their average strengths
            finalist_strengths = []
            for name in contestant_names:
                contestant_data = output_df[output_df['Contestant'] == name]
                if len(contestant_data) == 0:
                    print(f"Warning: Contestant '{name}' not found in data")
                    continue
                avg_strength = contestant_data['Strength_Score'].mean()
                finalist_strengths.append((name, avg_strength))
            
            print(f"Calculating probabilities for specified contestants using {method} method:")
            
        else:
            # Find finalists from specified or most recent series
            if series is None:
                series = output_df['Series'].max()
            
            series_data = output_df[output_df['Series'] == series]
            if len(series_data) == 0:
                print(f"No data found for Series {series}")
                return
                
            final_round = series_data['Round'].max()
            finalists = series_data[series_data['Round'] == final_round]
            
            if len(finalists) < 2:
                print(f"Series {series} has fewer than 2 finalists in the data")
                return
            
            finalist_strengths = []
            for _, finalist in finalists.iterrows():
                contestant_rounds = series_data[series_data['Contestant'] == finalist['Contestant']]
                avg_strength = contestant_rounds['Strength_Score'].mean()
                finalist_strengths.append((finalist['Contestant'], avg_strength))
            
            print(f"Series {series} Finalist Win Probabilities (using {method} method):")
        
        # Calculate probabilities
        probabilities = self.calculate_finalist_win_probabilities(finalist_strengths, method)
        
        # Sort by probability (highest first)
        sorted_finalists = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nRanked by Win Probability:")
        print(f"{'Rank':<5} {'Contestant':<15} {'Avg Strength':<12} {'Win Probability':<15} {'Odds':<10}")
        print("-" * 65)
        
        for i, (contestant, probability) in enumerate(sorted_finalists, 1):
            # Find the contestant's average strength
            avg_strength = next(strength for name, strength in finalist_strengths if name == contestant)
            
            # Calculate odds (e.g., 2.5:1 against)
            if probability > 0:
                odds_against = (1 - probability) / probability
                odds_str = f"{odds_against:.1f}:1" if odds_against >= 1 else f"1:{1/odds_against:.1f}"
            else:
                odds_str = "∞:1"
            
            print(f"{i:<5} {contestant:<15} {avg_strength:<12.2f} {probability*100:<14.1f}% {odds_str:<10}")
        
        # Display method explanation
        print(f"\nMethod Explanation ({method}):")
        if method == 'softmax':
            print("  Uses exponential weighting with temperature scaling - emphasizes score differences")
        elif method == 'normalized':
            print("  Simple linear normalization - proportional to adjusted score differences")
        elif method == 'exponential':
            print("  Moderate exponential weighting - balance between linear and softmax approaches")
        
        # Historical context
        total_finalists = len(finalist_strengths)
        equal_probability = 100 / total_finalists
        print(f"\nHistorical Context:")
        print(f"  Equal probability baseline: {equal_probability:.1f}% each ({total_finalists} finalists)")
        
        # Show strength score gaps
        strengths_only = [strength for _, strength in finalist_strengths]
        max_strength = max(strengths_only)
        min_strength = min(strengths_only)
        print(f"  Strength score range: {min_strength:.2f} - {max_strength:.2f} ({max_strength - min_strength:.2f} point gap)")
    
    def demonstrate_probability_methods(self, output_df: pd.DataFrame) -> None:
        """Demonstrate different probability calculation methods using sample finalist data"""
        print(f"\nPROBABILITY CALCULATION METHOD COMPARISON")
        print("-" * 50)
        
        # Use a recent series with clear strength differences as example
        series_to_demo = output_df['Series'].max()
        series_data = output_df[output_df['Series'] == series_to_demo]
        final_round = series_data['Round'].max()
        finalists = series_data[series_data['Round'] == final_round]
        
        if len(finalists) < 2:
            print("Not enough finalist data for demonstration")
            return
        
        finalist_strengths = []
        for _, finalist in finalists.iterrows():
            contestant_rounds = series_data[series_data['Contestant'] == finalist['Contestant']]
            avg_strength = contestant_rounds['Strength_Score'].mean()
            finalist_strengths.append((finalist['Contestant'], avg_strength))
        
        print(f"Example: Series {series_to_demo} Finalists")
        methods = ['softmax', 'normalized', 'exponential']
        
        # Calculate probabilities for each method
        all_results = {}
        for method in methods:
            probabilities = self.calculate_finalist_win_probabilities(finalist_strengths, method)
            all_results[method] = probabilities
        
        # Display comparison table
        print(f"\n{'Contestant':<15} {'Strength':<10} {'Softmax':<10} {'Normalized':<12} {'Exponential':<12}")
        print("-" * 70)
        
        for contestant, strength in sorted(finalist_strengths, key=lambda x: x[1], reverse=True):
            softmax_prob = all_results['softmax'][contestant] * 100
            normalized_prob = all_results['normalized'][contestant] * 100
            exponential_prob = all_results['exponential'][contestant] * 100
            
            print(f"{contestant:<15} {strength:<10.2f} {softmax_prob:<9.1f}% {normalized_prob:<11.1f}% {exponential_prob:<11.1f}%")
    
    def _print_series_by_overall_strength(self, output_df: pd.DataFrame) -> None:
        """Print series ranked by average strength of all performances in that series"""
        print(f"\nSeries Ranked by Overall Average Strength:")
        
        series_strength_data = []
        
        for series in sorted(output_df['Series'].unique()):
            series_data = output_df[output_df['Series'] == series]
            avg_series_strength = series_data['Strength_Score'].mean()
            total_performances = len(series_data)
            
            # Find series winner (winner in the final round)
            final_round = series_data['Round'].max()
            final_winner = series_data[(series_data['Round'] == final_round) & (series_data['Result'] == 'Winner')]
            winner = final_winner.iloc[0]['Contestant'] if len(final_winner) > 0 else "Unknown"
            
            series_strength_data.append({
                'Series': series,
                'Average_Series_Strength': avg_series_strength,
                'Total_Performances': total_performances,
                'Winner': winner
            })
        
        # Sort by average series strength
        series_strength_df = pd.DataFrame(series_strength_data).sort_values('Average_Series_Strength', ascending=False)
        
        for i, (_, series_data) in enumerate(series_strength_df.iterrows(), 1):
            print(f"  {i}. Series {series_data['Series']} (Winner: {series_data['Winner']}): {series_data['Average_Series_Strength']:.2f}/10 avg ({series_data['Total_Performances']} performances)")
    
    def _print_performance_outliers(self, output_df: pd.DataFrame) -> None:
        """Print performance outliers and rankings"""
        print("\nPERFORMANCE OUTLIERS & RANKINGS")
        print("-" * 40)
        
        # Strongest contestant to not win that week
        non_winners = output_df[output_df['Result'] != 'Winner']
        strongest_non_winner = non_winners.loc[non_winners['Strength_Score'].idxmax()]
        print(f"Strongest non-winner: {strongest_non_winner['Contestant']} S{strongest_non_winner['Series']}R{strongest_non_winner['Round']} ({strongest_non_winner['Strength_Score']:.2f}/10)")
        
        # Weakest contestant to win in a week
        winners = output_df[output_df['Result'] == 'Winner']
        weakest_winner = winners.loc[winners['Strength_Score'].idxmin()]
        print(f"Weakest star baker: {weakest_winner['Contestant']} S{weakest_winner['Series']}R{weakest_winner['Round']} ({weakest_winner['Strength_Score']:.2f}/10)")
        
        # Strongest contestant to be eliminated
        eliminated = output_df[output_df['Result'] == 'Eliminated']
        strongest_eliminated = eliminated.loc[eliminated['Strength_Score'].idxmax()]
        print(f"Strongest elimination: {strongest_eliminated['Contestant']} S{strongest_eliminated['Series']}R{strongest_eliminated['Round']} ({strongest_eliminated['Strength_Score']:.2f}/10)")
        
        # Weakest contestant to not be eliminated
        safe_contestants = output_df[output_df['Result'] != 'Eliminated']
        weakest_safe = safe_contestants.loc[safe_contestants['Strength_Score'].idxmin()]
        print(f"Weakest safe contestant: {weakest_safe['Contestant']} S{weakest_safe['Series']}R{weakest_safe['Round']} ({weakest_safe['Strength_Score']:.2f}/10)")
    
    def _print_series_winners_analysis(self, output_df: pd.DataFrame) -> None:
        """Print series winners analysis"""
        print(f"\nSeries Winners (by average strength):")
        
        # Find series winners and calculate their average strengths
        final_rounds = output_df.groupby('Series')['Round'].max().reset_index()
        series_winners = []
        
        for _, row in final_rounds.iterrows():
            series = row['Series']
            final_round = row['Round']
            final_winner = output_df[(output_df['Series'] == series) & 
                                   (output_df['Round'] == final_round) & 
                                   (output_df['Result'] == 'Winner')]
            if len(final_winner) > 0:
                winner_name = final_winner.iloc[0]['Contestant']
                winner_rounds = output_df[(output_df['Contestant'] == winner_name) & 
                                        (output_df['Series'] == series)]
                avg_strength = winner_rounds['Strength_Score'].mean()
                
                # Get corrected stats using helper method
                stats = self._get_contestant_stats(winner_name, series, winner_rounds)
                
                series_winners.append({
                    'Contestant': winner_name,
                    'Series': series,
                    'Average_Strength': avg_strength,
                    'Star_Baker_Wins': stats['star_baker_wins'],
                    'Sig_Handshakes': stats['sig_handshakes'],
                    'Show_Handshakes': stats['show_handshakes']
                })
        
        series_winners_df = pd.DataFrame(series_winners).sort_values('Average_Strength', ascending=False)
        
        for i, (_, winner) in enumerate(series_winners_df.iterrows(), 1):
            # Build handshake info string (only show if they have handshakes)
            handshake_info = ""
            if winner['Sig_Handshakes'] > 0 or winner['Show_Handshakes'] > 0:
                handshake_parts = []
                if winner['Sig_Handshakes'] > 0:
                    handshake_parts.append(f"{winner['Sig_Handshakes']} sig")
                if winner['Show_Handshakes'] > 0:
                    handshake_parts.append(f"{winner['Show_Handshakes']} show")
                handshake_info = f", {' + '.join(handshake_parts)} handshakes"
            
            print(f"  {i}. {winner['Contestant']:12} (S{winner['Series']}): {winner['Average_Strength']:.2f}/10 avg "
                  f"({winner['Star_Baker_Wins']} star baker wins{handshake_info})")
        
        # Top non-series-winners
        self._print_top_non_winners(output_df, set((w['Contestant'], w['Series']) for w in series_winners))
    
    def _print_top_non_winners(self, output_df: pd.DataFrame, series_winner_names: set) -> None:
        """Print top 10 non-series-winners"""
        print(f"\nTop Non-Series-Winners (by average strength):")
        
        # Calculate contestant averages with corrected star baker wins and handshakes
        contestant_data = []
        for (contestant, series), group in output_df.groupby(['Contestant', 'Series']):
            avg_strength = group['Strength_Score'].mean()
            total_rounds = len(group)
            was_eliminated = 1 if (group['Result'] == 'Eliminated').any() else 0
            
            # Get corrected stats using helper method
            stats = self._get_contestant_stats(contestant, series, group)
            
            contestant_data.append({
                'Contestant': contestant,
                'Series': series,
                'Average_Strength': avg_strength,
                'Total_Rounds': total_rounds,
                'Star_Baker_Wins': stats['star_baker_wins'],
                'Sig_Handshakes': stats['sig_handshakes'],
                'Show_Handshakes': stats['show_handshakes'],
                'Was_Eliminated': was_eliminated
            })
        
        contestant_averages = pd.DataFrame(contestant_data)
        
        # Filter out series winners
        non_series_winners = contestant_averages[
            ~contestant_averages.apply(lambda x: (x['Contestant'], x['Series']) in series_winner_names, axis=1)
        ]
        
        top_non_winners = non_series_winners.sort_values('Average_Strength', ascending=False).head(10)
        
        for i, (_, contestant) in enumerate(top_non_winners.iterrows(), 1):
            # Get detailed elimination status
            contestant_group = output_df[(output_df['Contestant'] == contestant['Contestant']) & 
                                       (output_df['Series'] == contestant['Series'])]
            elim_status = self._get_elimination_status(contestant['Series'], contestant_group)
            
            # Build handshake info string (only show if they have handshakes)
            handshake_info = ""
            if contestant['Sig_Handshakes'] > 0 or contestant['Show_Handshakes'] > 0:
                handshake_parts = []
                if contestant['Sig_Handshakes'] > 0:
                    handshake_parts.append(f"{contestant['Sig_Handshakes']} sig")
                if contestant['Show_Handshakes'] > 0:
                    handshake_parts.append(f"{contestant['Show_Handshakes']} show")
                handshake_info = f", {' + '.join(handshake_parts)} handshakes"
            
            print(f"  {i:2}. {contestant['Contestant']:12} (S{contestant['Series']}): {contestant['Average_Strength']:.2f}/10 avg "
                  f"({contestant['Star_Baker_Wins']} wins{handshake_info}, {elim_status})")
    
    def _print_performance_insights(self, output_df: pd.DataFrame) -> None:
        """Print performance insights by strength ranges"""
        print(f"\nPerformance Insights:")
        
        # Performance ranges
        high_performers = output_df[output_df['Strength_Score'] >= self.config.HIGH_PERFORMANCE_THRESHOLD]
        mid_performers = output_df[(output_df['Strength_Score'] >= self.config.MID_PERFORMANCE_THRESHOLD) & 
                                 (output_df['Strength_Score'] < self.config.HIGH_PERFORMANCE_THRESHOLD)]
        low_performers = output_df[output_df['Strength_Score'] < self.config.MID_PERFORMANCE_THRESHOLD]
        
        # Win rates
        high_win_rate = (high_performers['Result'] == 'Winner').mean() * 100
        mid_win_rate = (mid_performers['Result'] == 'Winner').mean() * 100
        low_win_rate = (low_performers['Result'] == 'Winner').mean() * 100
        
        high_winner_count = (high_performers['Result'] == 'Winner').sum()
        mid_winner_count = (mid_performers['Result'] == 'Winner').sum()
        low_winner_count = (low_performers['Result'] == 'Winner').sum()
        
        print(f"Star Baker Win Rates:")
        print(f"  High performers ({self.config.HIGH_PERFORMANCE_THRESHOLD}+): {high_win_rate:.1f}% ({high_winner_count}/{len(high_performers)})")
        print(f"  Mid performers ({self.config.MID_PERFORMANCE_THRESHOLD}-{self.config.HIGH_PERFORMANCE_THRESHOLD-0.1:.1f}): {mid_win_rate:.1f}% ({mid_winner_count}/{len(mid_performers)})")
        print(f"  Low performers (<{self.config.MID_PERFORMANCE_THRESHOLD}): {low_win_rate:.1f}% ({low_winner_count}/{len(low_performers)})")
        
        # Elimination rates
        high_elim_rate = (high_performers['Result'] == 'Eliminated').mean() * 100
        mid_elim_rate = (mid_performers['Result'] == 'Eliminated').mean() * 100
        low_elim_rate = (low_performers['Result'] == 'Eliminated').mean() * 100
        
        high_elim_count = (high_performers['Result'] == 'Eliminated').sum()
        mid_elim_count = (mid_performers['Result'] == 'Eliminated').sum()
        low_elim_count = (low_performers['Result'] == 'Eliminated').sum()
        
        print(f"Elimination Rates:")
        print(f"  High performers ({self.config.HIGH_PERFORMANCE_THRESHOLD}+): {high_elim_rate:.1f}% ({high_elim_count}/{len(high_performers)})")
        print(f"  Mid performers ({self.config.MID_PERFORMANCE_THRESHOLD}-{self.config.HIGH_PERFORMANCE_THRESHOLD-0.1:.1f}): {mid_elim_rate:.1f}% ({mid_elim_count}/{len(mid_performers)})")
        print(f"  Low performers (<{self.config.MID_PERFORMANCE_THRESHOLD}): {low_elim_rate:.1f}% ({low_elim_count}/{len(low_performers)})")
    
    def _print_elimination_analysis_by_round(self, output_df: pd.DataFrame) -> None:
        """Print elimination analysis by round showing average contestant strength and elimination performance"""
        print(f"\nELIMINATION ANALYSIS BY ROUND")
        print("-" * 40)
        
        # Group data by round to analyze eliminations
        elimination_data = []
        
        # Find all rounds except the final round for each series
        for series in sorted(output_df['Series'].unique()):
            series_data = output_df[output_df['Series'] == series]
            max_round = series_data['Round'].max()
            
            # Analyze each round except the final
            for round_num in sorted(series_data['Round'].unique()):
                if round_num < max_round:  # Skip final round
                    round_data = series_data[series_data['Round'] == round_num]
                    eliminated_contestants = round_data[round_data['Result'] == 'Eliminated']
                    
                    if len(eliminated_contestants) > 0:
                        # Get the eliminated contestant for this round
                        eliminated = eliminated_contestants.iloc[0]
                        
                        # Calculate contestant's average strength across ALL their performances
                        contestant_all_performances = series_data[series_data['Contestant'] == eliminated['Contestant']]
                        avg_contestant_strength = contestant_all_performances['Strength_Score'].mean()
                        
                        # Get their performance in the elimination round
                        elimination_round_performance = eliminated['Strength_Score']
                        
                        elimination_data.append({
                            'Round': round_num,
                            'Series': series,
                            'Contestant': eliminated['Contestant'],
                            'Average_Strength': avg_contestant_strength,
                            'Elimination_Performance': elimination_round_performance
                        })
        
        # Group by round number and calculate averages
        round_summary = {}
        for entry in elimination_data:
            round_num = entry['Round']
            if round_num not in round_summary:
                round_summary[round_num] = {
                    'avg_strengths': [],
                    'elimination_performances': [],
                    'count': 0
                }
            
            round_summary[round_num]['avg_strengths'].append(entry['Average_Strength'])
            round_summary[round_num]['elimination_performances'].append(entry['Elimination_Performance'])
            round_summary[round_num]['count'] += 1
        
        # Print round-by-round analysis
        print(f"Round-by-Round Elimination Patterns:")
        print(f"{'Round':<6} {'Eliminations':<12} {'Avg Contestant':<15} {'Avg Elimination':<15} {'Performance':<15}")
        print(f"{'':6} {'':12} {'Strength':<15} {'Performance':<15} {'Drop':<15}")
        print("-" * 75)
        
        for round_num in sorted(round_summary.keys()):
            data = round_summary[round_num]
            avg_strength = sum(data['avg_strengths']) / len(data['avg_strengths'])
            avg_elimination_perf = sum(data['elimination_performances']) / len(data['elimination_performances'])
            performance_drop = avg_strength - avg_elimination_perf
            count = data['count']
            
            print(f"R{round_num:<5} {count:<12} {avg_strength:<15.2f} {avg_elimination_perf:<15.2f} {performance_drop:<15.2f}")
        
        # Overall elimination statistics
        all_avg_strengths = []
        all_elimination_perfs = []
        for data in round_summary.values():
            all_avg_strengths.extend(data['avg_strengths'])
            all_elimination_perfs.extend(data['elimination_performances'])
        
        if all_avg_strengths:
            overall_avg_strength = sum(all_avg_strengths) / len(all_avg_strengths)
            overall_avg_elimination = sum(all_elimination_perfs) / len(all_elimination_perfs)
            
            print("-" * 75)
            print(f"Overall elimination averages:")
            print(f"  Average contestant strength (eliminated): {overall_avg_strength:.2f}/10")
            print(f"  Average elimination round performance: {overall_avg_elimination:.2f}/10")
            print(f"  Performance drop on elimination: {overall_avg_strength - overall_avg_elimination:.2f} points")
    
    def create_contestant_summary(self, output_df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive contestant summary statistics"""
        contestant_summary_data = []
        
        # Group by contestant and series to get comprehensive stats
        for (contestant, series), group in output_df.groupby(['Contestant', 'Series']):
            # Basic performance metrics
            avg_strength = group['Strength_Score'].mean()
            strength_variance = group['Strength_Score'].var()
            
            # Find strongest and weakest performances
            strongest_idx = group['Strength_Score'].idxmax()
            weakest_idx = group['Strength_Score'].idxmin()
            strongest_score = group.loc[strongest_idx, 'Strength_Score']
            strongest_round = group.loc[strongest_idx, 'Round']
            weakest_score = group.loc[weakest_idx, 'Strength_Score']
            weakest_round = group.loc[weakest_idx, 'Round']
            
            # Get original data for this contestant to count handshakes and reviews
            contestant_original_data = self.df[(self.df['Contestant'] == contestant) & (self.df['Series'] == series)]
            
            # Count handshakes
            sig_handshakes = len(contestant_original_data[contestant_original_data['Signature Handshake'] == 1])
            show_handshakes = len(contestant_original_data[contestant_original_data['Showstopper Handshake'] == 1])
            
            # Count reviews (using Second Half Review from original data)
            positive_reviews = len(contestant_original_data[contestant_original_data['Second Half Review'] > 0])
            negative_reviews = len(contestant_original_data[contestant_original_data['Second Half Review'] < 0])
            
            # Count star baker wins (excluding final round)
            max_round = group['Round'].max()
            star_baker_wins = len(group[(group['Result'] == 'Winner') & (group['Round'] != max_round)])
            
            # Determine result status using existing helper method
            elimination_status = self._get_elimination_status(series, group)
            
            # Determine if they're the series champion
            final_round_winner = group[(group['Round'] == max_round) & (group['Result'] == 'Winner')]
            if len(final_round_winner) > 0:
                result_status = "Champion"
            else:
                result_status = elimination_status
            
            contestant_summary_data.append({
                'Series': series,
                'Contestant': contestant,
                'Strength': round(avg_strength, 2),
                'Signature_Handshakes': sig_handshakes,
                'Showstopper_Handshakes': show_handshakes,
                'Positive_Reviews': positive_reviews,
                'Negative_Reviews': negative_reviews,
                'Star_Baker_Wins': star_baker_wins,
                'Result': result_status,
                'Strongest_Performance': round(strongest_score, 2),
                'Strongest_Round': strongest_round,
                'Weakest_Performance': round(weakest_score, 2),
                'Weakest_Round': weakest_round,
                'Strength_Variance': round(strength_variance, 2)
            })
        
        return pd.DataFrame(contestant_summary_data)
    
    def print_quarterfinalists_rankings(self, output_df: pd.DataFrame) -> None:
        """Print top 5 rankings for quarterfinalists+ across different categories"""
        print("\nTOP 5 QUARTERFINALIST+ RANKINGS")
        print("-" * 40)
        
        # Identify quarterfinalists+ (contestants who reached at least Round 7/8)
        # Assuming 10-round series, quarterfinalists typically reach R8+
        quarterfinalists_data = []
        
        for (contestant, series), group in output_df.groupby(['Contestant', 'Series']):
            max_round = group['Round'].max()
            # Consider quarterfinalists+ as those reaching Round 7 or later (covers different series lengths)
            if max_round >= 7:
                # Get original data for this contestant to calculate averages from signature/showstopper components
                contestant_original_data = self.df[(self.df['Contestant'] == contestant) & (self.df['Series'] == series)]
                
                # Calculate averages for different categories
                
                # For now, use the normalized technical scores from the processed data
                # Calculate technical average using the original normalized data
                tech_avg = contestant_original_data['Tech_Normalized'].mean()
                
                # Calculate signature and showstopper averages
                sig_bake_avg = contestant_original_data[['Signature Bake', 'Signature Flavor', 'Signature Looks']].mean().mean()
                show_bake_avg = contestant_original_data[['Showstopper Bake', 'Showstopper Flavor', 'Showstopper Looks']].mean().mean()
                
                # Calculate combined averages
                sig_flavor_avg = contestant_original_data['Signature Flavor'].mean()
                show_flavor_avg = contestant_original_data['Showstopper Flavor'].mean()
                flavor_avg = (sig_flavor_avg + show_flavor_avg) / 2
                
                sig_looks_avg = contestant_original_data['Signature Looks'].mean()
                show_looks_avg = contestant_original_data['Showstopper Looks'].mean()
                looks_avg = (sig_looks_avg + show_looks_avg) / 2
                
                bake_avg = (sig_bake_avg + show_bake_avg) / 2
                
                quarterfinalists_data.append({
                    'contestant': contestant,
                    'series': series,
                    'tech_avg': tech_avg,
                    'sig_avg': contestant_original_data[['Signature Bake', 'Signature Flavor', 'Signature Looks']].mean().mean(),
                    'show_avg': contestant_original_data[['Showstopper Bake', 'Showstopper Flavor', 'Showstopper Looks']].mean().mean(),
                    'flavor_avg': flavor_avg,
                    'bake_avg': bake_avg,
                    'looks_avg': looks_avg
                })
        
        if not quarterfinalists_data:
            print("No quarterfinalist data available")
            return
        
        qf_df = pd.DataFrame(quarterfinalists_data)
        
        # Print top 5 for each category
        categories = [
            ('tech_avg', 'Highest Average Technical', 'Technical Score'),
            ('sig_avg', 'Highest Average Signature', 'Signature Score'),
            ('show_avg', 'Highest Average Showstopper', 'Showstopper Score'),
            ('flavor_avg', 'Highest Average Flavor', 'Flavor Score'),
            ('bake_avg', 'Highest Average Bake', 'Bake Score'),
            ('looks_avg', 'Highest Average Looks', 'Looks Score')
        ]
        
        for col, title, score_name in categories:
            print(f"\n{title}:")
            top_5 = qf_df.nlargest(5, col)
            for i, (_, row) in enumerate(top_5.iterrows(), 1):
                print(f"  {i}. {row['contestant']:12} (S{int(row['series'])}): {row[col]:.2f} avg {score_name.lower()}")

    def print_variance_analysis(self, output_df: pd.DataFrame) -> None:
        """Print performance variance analysis for contestants."""
        print("\nPERFORMACE VARIANCE ANALYSIS")
        print("----------------------------------------")
        
        # Calculate variance for each contestant
        contestant_variance_data = []
        for (contestant, series), group in output_df.groupby(['Contestant', 'Series']):
            if len(group) >= 2:  # Need at least 2 performances to calculate variance
                variance = group['Strength_Score'].var()
                mean_performance = group['Strength_Score'].mean()
                num_rounds = len(group)
                
                # Determine how far they got
                max_round = group['Round'].max()
                if max_round >= 8:  # Quarterfinals or beyond (assuming 10 episodes)
                    reached_quarters = True
                elif max_round >= 7:
                    reached_quarters = True  # Close enough for series with different structures
                else:
                    reached_quarters = False
                
                contestant_variance_data.append({
                    'contestant': contestant,
                    'series': series,
                    'variance': variance,
                    'mean_performance': mean_performance,
                    'num_rounds': num_rounds,
                    'max_round': max_round,
                    'reached_quarters': reached_quarters
                })
        
        variance_df = pd.DataFrame(contestant_variance_data)
        
        if len(variance_df) == 0:
            print("No variance data available.")
            return
        
        # Top 5 highest variance (most inconsistent)
        highest_variance = variance_df.nlargest(5, 'variance')
        print("Top 5 Most Inconsistent Contestants (Highest Variance):")
        for _, row in highest_variance.iterrows():
            print(f"  {row['contestant']:12} (S{int(row['series'])}): {row['variance']:.2f} variance "
                  f"(avg: {row['mean_performance']:.2f}, {int(row['num_rounds'])} rounds)")
        
        # Top 5 lowest variance among quarterfinalists+ only
        quarterfinalists_df = variance_df[variance_df['reached_quarters'] == True]
        
        if len(quarterfinalists_df) >= 5:
            lowest_variance_quarters = quarterfinalists_df.nsmallest(5, 'variance')
            print(f"\nTop 5 Most Consistent Contestants (Lowest Variance, Quarterfinalists+):")
            for _, row in lowest_variance_quarters.iterrows():
                print(f"  {row['contestant']:12} (S{int(row['series'])}): {row['variance']:.2f} variance "
                      f"(avg: {row['mean_performance']:.2f}, {int(row['num_rounds'])} rounds)")
        else:
            print(f"\nTop {len(quarterfinalists_df)} Most Consistent Contestants (Lowest Variance, Quarterfinalists+):")
            for _, row in quarterfinalists_df.nsmallest(len(quarterfinalists_df), 'variance').iterrows():
                print(f"  {row['contestant']:12} (S{int(row['series'])}): {row['variance']:.2f} variance "
                      f"(avg: {row['mean_performance']:.2f}, {int(row['num_rounds'])} rounds)")
        
        # Summary statistics
        print(f"\nVariance Analysis Summary:")
        print(f"  Average variance across all contestants: {variance_df['variance'].mean():.2f}")
        print(f"  Highest variance: {variance_df['variance'].max():.2f}")
        if len(quarterfinalists_df) > 0:
            print(f"  Average variance (quarterfinalists+): {quarterfinalists_df['variance'].mean():.2f}")
    
    def generate_theme_analysis(self, output_df: pd.DataFrame) -> None:
        """Theme performance analysis is now integrated into ANALYSIS_RESULTS.md"""
        # Theme analysis has been moved to ANALYSIS_RESULTS.md - no processing needed
        pass
    
    def save_results(self, output_df: pd.DataFrame) -> None:
        """Save results to CSV files"""
        # Save original performance data
        output_df.to_csv(self.config.OUTPUT_FILE, index=False)
        
        # Create and save contestant summary
        contestant_summary = self.create_contestant_summary(output_df)
        summary_filename = self.config.OUTPUT_FILE.replace('.csv', '_contestant_summary.csv')
        contestant_summary.to_csv(summary_filename, index=False)
        
        print(f"\n" + "=" * 60)
        print(f"ANALYSIS COMPLETE - Files saved:")
        print(f"  Performance Data: {self.config.OUTPUT_FILE}")
        print(f"  Contestant Summary: {summary_filename}")
        print(f"Dataset: {len(output_df)} records, {output_df['Contestant'].nunique()} contestants, Series {min(output_df['Series'])}-{max(output_df['Series'])}")
        print("=" * 60)
    
    def run_complete_analysis(self) -> None:
        """Run the complete analysis pipeline"""
        print("=" * 60)
        print("GREAT BRITISH BAKE OFF - COMPLETE ANALYSIS")
        print("=" * 60)
        
        try:
            # Load and prepare data
            self.load_and_prepare_data()
            
            # Validate data
            self.validate_data()
            
            # Train models and analyze correlations
            self.train_and_analyze_models()
            
            # Calculate strength scores
            output_df = self.calculate_strength_scores()
            
            # Generate analysis in organized sections
            self.generate_performance_analysis(output_df)
            self.print_accuracy_metrics(output_df)
            self.print_baker_performance(output_df)
            
            # Generate variance analysis
            self.print_variance_analysis(output_df)
            
            # Generate quarterfinalist rankings analysis
            self.print_quarterfinalists_rankings(output_df)
            
            # Save results (needed for theme analysis)
            self.save_results(output_df)
            
            # Generate theme performance analysis
            self.generate_theme_analysis(output_df)
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            raise