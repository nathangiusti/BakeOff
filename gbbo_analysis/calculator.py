"""
Strength score calculation logic for GBBO analysis.
"""

from typing import Dict, Optional

from .config import Config


class StrengthScoreCalculator:
    """Handles strength score calculations"""
    
    def __init__(self, config: Config, model_weights: Dict[str, float]):
        self.config = config
        self.weights = model_weights
    
    def calculate_strength_score(self, signature_bake: float, signature_flavor: float, 
                               signature_looks: float, signature_handshake: float, 
                               tech_normalized: float, showstopper_bake: Optional[float] = None,
                               showstopper_flavor: Optional[float] = None, 
                               showstopper_looks: Optional[float] = None,
                               showstopper_handshake: Optional[float] = None) -> Dict[str, float]:
        """Calculate strength score (0-10 scale)"""
        
        weights = self.weights
        
        # Calculate weighted score
        score = 0.0
        total_weight = 0.0
        
        # First half components (always present)
        score += signature_bake * weights['signature_bake']
        score += signature_flavor * weights['signature_flavor']
        score += signature_looks * weights['signature_looks']
        score += signature_handshake * weights['signature_handshake']
        score += tech_normalized * weights['tech_normalized']
        
        total_weight += (weights['signature_bake'] + weights['signature_flavor'] + 
                        weights['signature_looks'] + weights['signature_handshake'] + 
                        weights['tech_normalized'])
        
        # Add showstopper components if available
        has_showstopper = all(x is not None for x in [showstopper_bake, showstopper_flavor, 
                                                    showstopper_looks, showstopper_handshake])
        if has_showstopper:
            score += showstopper_bake * weights['showstopper_bake']
            score += showstopper_flavor * weights['showstopper_flavor']
            score += showstopper_looks * weights['showstopper_looks']
            score += showstopper_handshake * weights['showstopper_handshake']
            
            total_weight += (weights['showstopper_bake'] + weights['showstopper_flavor'] + 
                           weights['showstopper_looks'] + weights['showstopper_handshake'])
        
        # Normalize to 0-10 scale based on theoretical bounds
        tech_weight = weights['tech_normalized']
        
        if has_showstopper:
            other_weights = total_weight - tech_weight
            min_raw_score = -1 * other_weights + 0 * tech_weight
            max_raw_score = 1 * other_weights + 1 * tech_weight
        else:
            sig_weights = (weights['signature_bake'] + weights['signature_flavor'] + 
                          weights['signature_looks'] + weights['signature_handshake'])
            other_weights = sig_weights
            min_raw_score = -1 * other_weights + 0 * tech_weight
            max_raw_score = 1 * other_weights + 1 * tech_weight
        
        # Convert to weighted averages
        min_weighted_avg = min_raw_score / total_weight
        max_weighted_avg = max_raw_score / total_weight
        weighted_average = score / total_weight
        
        # Scale to 0-10
        normalized_score = 10 * (weighted_average - min_weighted_avg) / (max_weighted_avg - min_weighted_avg)
        normalized_score = max(0.0, min(10.0, normalized_score))
        
        return {
            'strength_score': normalized_score,
            'components_used': 'full' if has_showstopper else 'first_half'
        }