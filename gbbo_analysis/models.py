"""
Machine learning model training and analysis for GBBO.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from typing import Dict, List, Tuple, Optional

from .config import Config


class GBBOModelTrainer:
    """Handles model training and analysis"""
    
    def __init__(self, df: pd.DataFrame, config: Config):
        self.df = df
        self.config = config
        self.second_model: Optional[LogisticRegression] = None

        
    def train_models(self) -> float:
        """Train prediction model and return accuracy"""
        second_accuracy = self._train_second_half_model()
        return second_accuracy
    
    def _train_second_half_model(self) -> float:
        """Train second half review prediction model"""
        second_half_data = self.df[self.df['Second Half Review'] != 0].copy()
        second_features = self.config.SIGNATURE_COLS + ['Tech_Normalized'] + self.config.SHOWSTOPPER_COLS
        
        X_second = second_half_data[second_features]
        y_second = second_half_data['Second Half Review']
        
        self.second_model = LogisticRegression(random_state=42)
        self.second_model.fit(X_second, y_second)
        
        return accuracy_score(y_second, self.second_model.predict(X_second))
    
    def analyze_correlations(self) -> Dict[str, float]:
        """Analyze feature correlations for the model"""
        # Second half correlations
        second_half_data = self.df[self.df['Second Half Review'] != 0].copy()
        second_features = self.config.SIGNATURE_COLS + ['Tech_Normalized'] + self.config.SHOWSTOPPER_COLS
        
        second_correlations = {}
        for feature in second_features:
            second_correlations[feature] = second_half_data[feature].corr(second_half_data['Second Half Review'])
        
        # Add composite correlations
        second_half_data['First_Two_Total'] = (second_half_data[self.config.SIGNATURE_COLS].sum(axis=1) + 
                                             second_half_data['Tech_Normalized'])
        second_half_data['Showstopper_Total'] = second_half_data[self.config.SHOWSTOPPER_COLS].sum(axis=1)
        
        second_correlations['First Two Total'] = second_half_data['First_Two_Total'].corr(second_half_data['Second Half Review'])
        second_correlations['Showstopper Total'] = second_half_data['Showstopper_Total'].corr(second_half_data['Second Half Review'])
        
        return second_correlations
    
    def get_model_weights(self) -> Dict[str, float]:
        """Extract weights from the trained second model"""
        if self.second_model is None:
            raise ValueError("Second model must be trained before extracting weights")
        
        # Calculate individual component weights from model coefficients
        individual_weights = {
            'signature_bake': abs(self.second_model.coef_[0][0]),
            'signature_flavor': abs(self.second_model.coef_[0][1]),
            'signature_looks': abs(self.second_model.coef_[0][2]),
            'signature_handshake': abs(self.second_model.coef_[0][3]),
            'tech_normalized': abs(self.second_model.coef_[0][4]),
            'showstopper_bake': abs(self.second_model.coef_[0][5]),
            'showstopper_flavor': abs(self.second_model.coef_[0][6]),
            'showstopper_looks': abs(self.second_model.coef_[0][7]),
            'showstopper_handshake': abs(self.second_model.coef_[0][8])
        }
        return individual_weights

    def analyze_component_weights(self) -> None:
        """Analyze and print component weight breakdown"""
        if self.second_model is None:
            raise ValueError("Second model must be trained before analyzing weights")
        
        print(f"\nCOMPONENT WEIGHT ANALYSIS")
        print("-" * 40)
        
        # Get weights from the model
        individual_weights = self.get_model_weights()
        
        # Calculate bake group totals
        signature_total_weight = sum(individual_weights[k] for k in ['signature_bake', 'signature_flavor', 'signature_looks', 'signature_handshake'])
        tech_weight = individual_weights['tech_normalized']
        showstopper_total_weight = sum(individual_weights[k] for k in ['showstopper_bake', 'showstopper_flavor', 'showstopper_looks', 'showstopper_handshake'])
        
        overall_total = signature_total_weight + tech_weight + showstopper_total_weight
        
        # Create sorted list of bake groups by weight
        bake_groups = [
            ('Showstopper Bake', showstopper_total_weight),
            ('Technical Challenge', tech_weight),
            ('Signature Bake', signature_total_weight)
        ]
        bake_groups_sorted = sorted(bake_groups, key=lambda x: x[1], reverse=True)
        
        print("Bake Group Importance (Total Weight):")
        for i, (name, weight) in enumerate(bake_groups_sorted, 1):
            print(f"  {i}. {name:18}: {weight:.3f} ({weight/overall_total:.1%})")
        
        # Print component breakdowns
        self._print_component_breakdown("Signature Bake Components", individual_weights, 
                                      ['signature_looks', 'signature_handshake', 'signature_bake', 'signature_flavor'],
                                      signature_total_weight)
        
        self._print_component_breakdown("Showstopper Bake Components", individual_weights,
                                      ['showstopper_looks', 'showstopper_flavor', 'showstopper_bake', 'showstopper_handshake'],
                                      showstopper_total_weight)
        
        # Traditional comparison
        first_two_weight = signature_total_weight + tech_weight
        weight_ratio = showstopper_total_weight / first_two_weight if first_two_weight > 0 else 0
        
        print(f"\nTraditional Bake Comparison:")
        print(f"  First Two Bakes:  {first_two_weight:.3f} ({first_two_weight/overall_total:.1%})")
        print(f"  Showstopper:      {showstopper_total_weight:.3f} ({showstopper_total_weight/overall_total:.1%})")
        print(f"  Ratio: {weight_ratio:.2f} (showstopper vs first two bakes)")
    
    def _print_component_breakdown(self, title: str, weights: Dict[str, float], 
                                 component_keys: List[str], total_weight: float) -> None:
        """Helper method to print component breakdown"""
        print(f"\n{title}:")
        
        # Create readable names
        name_map = {
            'signature_looks': 'Signature Looks',
            'signature_handshake': 'Signature Handshake', 
            'signature_bake': 'Signature Bake',
            'signature_flavor': 'Signature Flavor',
            'showstopper_looks': 'Showstopper Looks',
            'showstopper_flavor': 'Showstopper Flavor',
            'showstopper_bake': 'Showstopper Bake',
            'showstopper_handshake': 'Showstopper Handshake'
        }
        
        components = [(name_map[key], weights[key]) for key in component_keys]
        components_sorted = sorted(components, key=lambda x: x[1], reverse=True)
        
        for name, weight in components_sorted:
            percentage = weight / total_weight * 100 if total_weight > 0 else 0
            category = "signature" if "Signature" in name else "showstopper"
            print(f"    {name:18}: {weight:.3f} ({percentage:.1f}% of {category})")
    
    def analyze_component_variance(self) -> None:
        """Analyze variance and distributions for signature and showstopper components"""
        if self.second_model is None:
            raise ValueError("Second model must be trained before analyzing variance")
        
        print(f"\nCOMPONENT VARIANCE ANALYSIS")
        print("-" * 40)
        print("Understanding component weights through variance analysis")
        
        # Get model weights
        weights = self.get_model_weights()
        
        # Define signature and showstopper components (exclude handshakes as requested)
        component_groups = {
            'Signature Components': ['Signature Bake', 'Signature Flavor', 'Signature Looks'],
            'Showstopper Components': ['Showstopper Bake', 'Showstopper Flavor', 'Showstopper Looks']
        }
        
        # Column name mapping for data access
        col_mapping = {
            'Signature Bake': 'Signature Bake',
            'Signature Flavor': 'Signature Flavor', 
            'Signature Looks': 'Signature Looks',
            'Showstopper Bake': 'Showstopper Bake',
            'Showstopper Flavor': 'Showstopper Flavor',
            'Showstopper Looks': 'Showstopper Looks'
        }
        
        # Weight key mapping
        weight_mapping = {
            'Signature Bake': 'signature_bake',
            'Signature Flavor': 'signature_flavor',
            'Signature Looks': 'signature_looks', 
            'Showstopper Bake': 'showstopper_bake',
            'Showstopper Flavor': 'showstopper_flavor',
            'Showstopper Looks': 'showstopper_looks'
        }
        
        for group_name, components in component_groups.items():
            print(f"\n{group_name}:")
            print(f"{'Component':<18} {'Weight':<8} {'Mean':<6} {'Variance':<9} {'%-1':<6} {'%0':<6} {'%+1':<6}")
            print("-" * 65)
            
            # Sort components by weight for display
            component_weights = [(comp, weights[weight_mapping[comp]]) for comp in components]
            component_weights.sort(key=lambda x: x[1], reverse=True)
            
            for component, weight in component_weights:
                col_name = col_mapping[component]
                
                if col_name in self.df.columns:
                    # Get non-null values for this component
                    values = self.df[col_name].dropna()
                    
                    if len(values) > 0:
                        # Calculate statistics
                        mean_val = values.mean()
                        variance = values.var()
                        
                        # Calculate distribution percentages
                        total_count = len(values)
                        pct_neg = (values == -1).sum() / total_count * 100
                        pct_zero = (values == 0).sum() / total_count * 100  
                        pct_pos = (values == 1).sum() / total_count * 100
                        
                        print(f"{component:<18} {weight:<8.3f} {mean_val:<6.2f} {variance:<9.3f} {pct_neg:<6.1f} {pct_zero:<6.1f} {pct_pos:<6.1f}")
                    else:
                        print(f"{component:<18} {weight:<8.3f} {'N/A':<6} {'N/A':<9} {'N/A':<6} {'N/A':<6} {'N/A':<6}")
                else:
                    print(f"{component:<18} {weight:<8.3f} {'N/A':<6} {'N/A':<9} {'N/A':<6} {'N/A':<6} {'N/A':<6}")
        
