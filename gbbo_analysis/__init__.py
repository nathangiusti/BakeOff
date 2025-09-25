"""
Great British Bake Off Analysis Package

A comprehensive analysis system for GBBO contestant performance data.
"""

from .analyzer import GBBOAnalyzer
from .config import Config

__version__ = "1.0.0"
__all__ = ["GBBOAnalyzer", "Config"]