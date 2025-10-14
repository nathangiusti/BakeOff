"""
Data validation logic for GBBO analysis.
"""

import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ValidationError:
    """Structure for validation errors"""
    error_type: str
    series: int
    round_num: int
    message: str
    details: Optional[Dict] = None


class GBBODataValidator:
    """Handles all data validation logic"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.errors: List[ValidationError] = []
    
    def validate_all(self) -> bool:
        """Run all validation checks and return True if all pass"""
        self._validate_tech_scores()
        self._validate_second_half_reviews()
        self._validate_unique_records()
        self._validate_contestant_counts()
        self._validate_winner_counts()
        return len(self.errors) == 0
    
    def _validate_tech_scores(self) -> None:
        """Validate tech scores follow 1-N pattern within each round"""
        for series in sorted(self.df['Series'].unique()):
            for round_num in sorted(self.df['Round'].unique()):
                round_data = self.df[(self.df['Series'] == series) & (self.df['Round'] == round_num)]
                
                if len(round_data) > 0:
                    tech_scores = sorted(round_data['Tech'].tolist())
                    expected_scores = list(range(1, len(round_data) + 1))
                    
                    if tech_scores != expected_scores:
                        self.errors.append(ValidationError(
                            error_type="tech_scores",
                            series=series,
                            round_num=round_num,
                            message=f"Expected {expected_scores}, Got {tech_scores}",
                            details={'actual': tech_scores, 'expected': expected_scores}
                        ))
    
    def _validate_second_half_reviews(self) -> None:
        """Validate second half reviews for non-final rounds"""
        for series in sorted(self.df['Series'].unique()):
            max_round = self.df[self.df['Series'] == series]['Round'].max()
            
            for round_num in sorted(self.df[self.df['Series'] == series]['Round'].unique()):
                if round_num < max_round:  # Not final round
                    round_data = self.df[(self.df['Series'] == series) & (self.df['Round'] == round_num)]
                    second_half_reviews = round_data['Second Half Review']
                    
                    if second_half_reviews.isna().all():
                        self.errors.append(ValidationError(
                            error_type="second_half_reviews",
                            series=series,
                            round_num=round_num,
                            message=f"All {len(round_data)} contestants missing second half reviews"
                        ))
    
    def _validate_unique_records(self) -> None:
        """Validate unique contestant-series-round combinations"""
        duplicates = self.df[['Contestant', 'Series', 'Round']].duplicated(keep=False)
        
        if duplicates.any():
            duplicate_groups = (self.df[duplicates]
                              .groupby(['Contestant', 'Series', 'Round'])
                              .size()
                              .reset_index(name='count'))
            
            for _, group in duplicate_groups.iterrows():
                self.errors.append(ValidationError(
                    error_type="duplicate_records",
                    series=group['Series'],
                    round_num=group['Round'],
                    message=f"{group['Contestant']} S{group['Series']}R{group['Round']}: {group['count']} duplicate records"
                ))
    
    def print_results(self) -> None:
        """Print validation results only if there are failures"""
        if self.errors:
            print("DATA VALIDATION")
            print("-" * 40)
            
            for error in self.errors:
                if error.error_type == "tech_scores":
                    print(f"X TECH SCORE VALIDATION FAILED:")
                    print(f"  Series {error.series}, Round {error.round_num}: {error.message}")
                elif error.error_type == "second_half_reviews":
                    print(f"X SECOND HALF REVIEW VALIDATION FAILED:")
                    print(f"  Series {error.series}, Round {error.round_num}: {error.message}")
                elif error.error_type == "duplicate_records":
                    print(f"X UNIQUE RECORD VALIDATION FAILED:")
                    print(f"  {error.message}")
                elif error.error_type == "contestant_count":
                    print(f"X CONTESTANT COUNT VALIDATION FAILED:")
                    print(f"  Series {error.series}: {error.message}")
                elif error.error_type == "winner_count":
                    print(f"X WINNER COUNT VALIDATION FAILED:")
                    print(f"  Series {error.series}, Round {error.round_num}: {error.message}")
            
            print("X DATA VALIDATION FAILED - Issues detected above")
            print("  Analysis will continue but results may be affected")
            print()
    
    def _validate_contestant_counts(self) -> None:
        """Validate that each series has the expected number of contestants"""
        expected_counts = {7: 13, 12: 11}  # Series 7 has 13, Series 12 has 11, all others have 12
        default_count = 12
        
        for series in sorted(self.df['Series'].unique()):
            series_data = self.df[self.df['Series'] == series]
            actual_count = series_data['Contestant'].nunique()
            expected_count = expected_counts.get(series, default_count)
            
            if actual_count != expected_count:
                total_records = len(series_data)
                self.errors.append(ValidationError(
                    error_type="contestant_count",
                    series=series,
                    round_num=0,  # Not applicable for this validation
                    message=f"Expected {expected_count} contestants, found {actual_count} ({total_records} total records)"
                ))
    
    def _validate_winner_counts(self) -> None:
        """Validate that every round has exactly one winner/star baker"""
        for series in sorted(self.df['Series'].unique()):
            for round_num in sorted(self.df['Round'].unique()):
                round_data = self.df[(self.df['Series'] == series) & (self.df['Round'] == round_num)]
                
                if len(round_data) > 0:
                    winner_count = (round_data['Winner'] == 1).sum()
                    
                    if winner_count == 0:
                        self.errors.append(ValidationError(
                            error_type="winner_count",
                            series=series,
                            round_num=round_num,
                            message=f"No winner found (expected exactly 1)"
                        ))
                    elif winner_count > 1:
                        self.errors.append(ValidationError(
                            error_type="winner_count",
                            series=series,
                            round_num=round_num,
                            message=f"Found {winner_count} winners (expected exactly 1)"
                        ))