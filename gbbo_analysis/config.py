"""
Configuration and constants for GBBO analysis.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Config:
    """Configuration constants for the analysis
    
    NOTE: Always use ASCII characters in console output to avoid Unicode encoding errors.
    Use * instead of ✓, X instead of ✗, > instead of →, etc.
    """
    INPUT_FILE: str = 'data.csv'
    OUTPUT_FILE: str = 'gbbo_complete_analysis.csv'
    
    # Column names
    SIGNATURE_COLS: List[str] = None
    SHOWSTOPPER_COLS: List[str] = None
    TECH_COL: str = 'Tech'
    
    
    # Performance thresholds
    HIGH_PERFORMANCE_THRESHOLD: float = 8.0
    MID_PERFORMANCE_THRESHOLD: float = 6.0
    
    def __post_init__(self):
        if self.SIGNATURE_COLS is None:
            self.SIGNATURE_COLS = ['Signature Bake', 'Signature Flavor', 'Signature Looks', 'Signature Handshake']
        
        if self.SHOWSTOPPER_COLS is None:
            self.SHOWSTOPPER_COLS = ['Showstopper Bake', 'Showstopper Flavor', 'Showstopper Looks', 'Showstopper Handshake']
        
