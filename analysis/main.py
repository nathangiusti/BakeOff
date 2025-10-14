"""
Main entry point for GBBO analysis.

Run this script to perform the complete Great British Bake Off analysis using pre-calculated weights.

Usage:
  python main.py [--weights WEIGHTS_FILE] [--input INPUT_FILE]

Examples:
  python main.py --weights ../correlation_analysis/model_weights.json
  python main.py --weights ../correlation_analysis/model_weights_claude.json --input ../data_collection/judging/claude/claude_data.csv
  python main.py  # Uses default weights file if available, otherwise trains new model

IMPLEMENTATION NOTES:
- First half reviews were tested for integration but showed no accuracy improvement
- Two approaches were tested: adding reviews as features and two-model ensemble
- Both approaches performed worse than the integrated single-model approach
- The current system uses only second half review predictions which capture
  all necessary information from signature, technical, and showstopper challenges
- Theme performance analysis identifies which episode themes cause bakers to excel or struggle
"""

import argparse
import sys
from pathlib import Path

# Add shared directory to path
sys.path.append(str(Path(__file__).parent.parent / "shared"))

from gbbo_analysis import GBBOAnalyzer, Config


def main():
    """Main function that runs the complete analysis"""
    parser = argparse.ArgumentParser(
        description="Run complete GBBO analysis with pre-calculated or newly trained weights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --weights ../correlation_analysis/model_weights.json
  python main.py --weights ../correlation_analysis/model_weights_claude.json --input ../data_collection/judging/claude/claude_data.csv
  python main.py  # Uses model_weights.json if available, otherwise trains new model
        """
    )
    
    parser.add_argument(
        '--weights',
        help='Path to pre-calculated weights JSON file (default: model_weights.json if exists)'
    )
    
    parser.add_argument(
        '--input',
        help='Input CSV file with judging data (default: data_collection/judging/human/data.csv)'
    )
    
    args = parser.parse_args()
    
    # Set up configuration
    config = Config()
    if args.input:
        config.INPUT_FILE = args.input
    
    # Determine weights file
    weights_file = args.weights
    if not weights_file:
        # Check for default weights file
        default_weights = '../correlation_analysis/model_weights.json'
        if Path(default_weights).exists():
            weights_file = default_weights
            print(f"Using default weights file: {default_weights}")
        else:
            print("No weights file specified and ../correlation_analysis/model_weights.json not found.")
            print("Will train new model from scratch.")
            weights_file = None
    elif not Path(weights_file).exists():
        print(f"Warning: Weights file {weights_file} not found.")
        print("Will train new model from scratch.")
        weights_file = None
    
    # Create analyzer with weights file if available
    analyzer = GBBOAnalyzer(config=config, weights_file=weights_file)
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()