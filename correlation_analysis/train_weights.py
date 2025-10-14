"""
Weight Training Program for GBBO Analysis

This program trains ML models on judging data to calculate optimal component weights
and saves the results to a weights file for use by the main analysis program.

Usage:
  python train_weights.py [--input INPUT_FILE] [--output WEIGHTS_FILE] [--random-forest]

Examples:
  python train_weights.py
  python train_weights.py --input ../data_collection/judging/claude/claude_data.csv --output model_weights_claude.json
  python train_weights.py --random-forest
"""

import argparse
import json
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add shared directory to path
sys.path.append(str(Path(__file__).parent.parent / "shared"))

from gbbo_analysis import Config, GBBODataValidator, GBBOModelTrainer


def train_weights(input_file: str, output_file: str, use_random_forest: bool = False) -> Dict[str, Any]:
    """
    Train models and extract component weights.
    
    Args:
        input_file: Path to judging data CSV
        output_file: Path to save weights JSON
        use_random_forest: Whether to use Random Forest instead of Logistic Regression
        
    Returns:
        Dictionary containing all weights and metadata
    """
    print("=" * 60)
    print("GBBO WEIGHT TRAINING")
    print("=" * 60)
    
    # Initialize configuration
    config = Config()
    
    # Override input file if provided
    if input_file != config.INPUT_FILE:
        config.INPUT_FILE = input_file
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Model type: {'Random Forest' if use_random_forest else 'Logistic Regression'}")
    
    # Load and prepare data
    print("\n1. Loading and preparing data...")
    if not Path(input_file).exists():
        raise FileNotFoundError(f"Input file {input_file} not found")
    
    df = pd.read_csv(input_file)
    
    # Fill missing values with 0 as specified
    columns_to_fill = (config.SIGNATURE_COLS + config.SHOWSTOPPER_COLS + 
                      ['Second Half Review', 'Winner', 'Eliminated'])
    
    for col in columns_to_fill:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # Create normalized tech scores
    print("2. Normalizing technical scores...")
    df['Tech_Normalized'] = 0.0
    
    for series in df['Series'].unique():
        for round_num in df['Round'].unique():
            mask = (df['Series'] == series) & (df['Round'] == round_num)
            round_data = df[mask]
            
            if len(round_data) > 0:
                min_tech = round_data['Tech'].min()
                max_tech = round_data['Tech'].max()
                
                for idx in round_data.index:
                    raw_tech = df.loc[idx, 'Tech']
                    if max_tech > min_tech:
                        normalized = 1 - (raw_tech - min_tech) / (max_tech - min_tech)
                    else:
                        normalized = 1.0  # All contestants tied
                    df.loc[idx, 'Tech_Normalized'] = normalized
    
    # Validate data
    print("3. Validating data...")
    validator = GBBODataValidator(df)
    validation_passed = validator.validate_all()
    validator.print_results()
    
    if not validation_passed:
        print("WARNING: Data validation failed, but continuing with analysis")
    
    # Train models
    print("4. Training models and analyzing correlations...")
    trainer = GBBOModelTrainer(df, config, use_random_forest=use_random_forest)
    second_accuracy = trainer.train_models()
    
    # Get correlations and weights
    correlations = trainer.analyze_correlations()
    individual_weights = trainer.get_model_weights()
    
    # Print component analysis
    trainer.analyze_component_weights()
    
    # Create weights data structure
    weights_data = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "input_file": input_file,
            "model_type": "random_forest" if use_random_forest else "logistic_regression",
            "total_records": len(df),
            "series_range": f"{df['Series'].min()}-{df['Series'].max()}",
            "contestants": df['Contestant'].nunique()
        },
        "model_performance": {
            "second_half_review_accuracy": second_accuracy,
            "second_half_review_count": len(df[df['Second Half Review'] != 0])
        },
        "correlations": correlations,
        "individual_weights": individual_weights,
        "component_groups": {
            "signature_total": sum(individual_weights[k] for k in ['signature_bake', 'signature_flavor', 'signature_looks', 'signature_handshake']),
            "tech_weight": individual_weights['tech_normalized'],
            "showstopper_total": sum(individual_weights[k] for k in ['showstopper_bake', 'showstopper_flavor', 'showstopper_looks', 'showstopper_handshake'])
        }
    }
    
    # Calculate traditional ratios
    first_two_weight = weights_data["component_groups"]["signature_total"] + weights_data["component_groups"]["tech_weight"]
    showstopper_weight = weights_data["component_groups"]["showstopper_total"]
    
    weights_data["traditional_ratios"] = {
        "first_two_bakes": first_two_weight,
        "showstopper": showstopper_weight,
        "showstopper_vs_first_two": showstopper_weight / first_two_weight if first_two_weight > 0 else 0
    }
    
    # Save weights file
    print(f"\n5. Saving weights to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(weights_data, f, indent=2)
    
    print(f"\nWeight training complete!")
    print(f"Model accuracy: {second_accuracy:.1%}")
    print(f"Weights saved to: {output_file}")
    
    return weights_data


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description="Train ML models to calculate GBBO component weights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train_weights.py
  python train_weights.py --input ../data_collection/judging/claude/claude_data.csv --output model_weights_claude.json  
  python train_weights.py --random-forest --output model_weights_rf.json
        """
    )
    
    parser.add_argument(
        '--input', 
        default='../data_collection/judging/human/data.csv',
        help='Input CSV file with judging data (default: ../data_collection/judging/human/data.csv)'
    )
    
    parser.add_argument(
        '--output',
        default='model_weights.json', 
        help='Output JSON file for weights (default: model_weights.json)'
    )
    
    parser.add_argument(
        '--random-forest',
        action='store_true',
        help='Use Random Forest instead of Logistic Regression'
    )
    
    args = parser.parse_args()
    
    try:
        weights_data = train_weights(
            input_file=args.input,
            output_file=args.output,
            use_random_forest=args.random_forest
        )
        
        print("\n" + "=" * 60)
        print("SUCCESS: Weight training completed")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Weight training failed")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())