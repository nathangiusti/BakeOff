# Great British Bake Off Data Analysis Project

## Project Overview
This project analyzes performance data from The Great British Bake Off to:
1. Determine the relative importance of different scoring metrics
2. Create a method to judge baker performance strength each week
3. Develop an overall performance assessment system

## Data Structure (data.csv)

### Column Definitions
- **Contestant**: Baker's name
- **Series**: Season number (contestants in same series compete against each other)
- **Round**: Week number within the series
- **Signature Bake**: Signature bake execution score (1=positive, 0=neutral, -1=negative)
- **Signature Flavor**: Signature bake flavor score (1=positive, 0=neutral, -1=negative)
- **Signature Looks**: Signature bake visual presentation score (1=positive, 0=neutral, -1=negative)
- **Signature Handshake**: Paul Hollywood handshake for signature bake (1 if given, blank if not)
- **Tech**: Technical challenge ranking (1=best, higher numbers=worse performance)
- **First Half Review**: Review after first two bakes (1=positive, -1=negative, blank=none)
- **Showstopper Bake**: Showstopper bake execution score (1=positive, 0=neutral, -1=negative)
- **Showstopper Flavor**: Showstopper bake flavor score (1=positive, 0=neutral, -1=negative)
- **Showstopper Looks**: Showstopper bake visual presentation score (1=positive, 0=neutral, -1=negative)
- **Showstopper Handshake**: Paul Hollywood handshake for showstopper (1 if given, blank if not)
- **Second Half Review**: Post-showstopper review identifying strongest/weakest bakers
- **Winner**: Star baker for the week (1 if winner, blank if not)
- **Eliminated**: Eliminated this round (1 if eliminated, blank if not)

### Data Coverage
- **Series 5-11 included**
- **529 total contestant-round records across 79 contestants**
- Series 5: 13 contestants, 10 rounds
- Series 6: 12 contestants, 10 rounds  
- Series 7: 13 contestants, 10 rounds
- Series 8: 12 contestants, 10 rounds
- Series 9: 12 contestants, 10 rounds
- Series 10: 12 contestants, 10 rounds
- Series 11: 12 contestants, 9 rounds

### Scoring System
- **Bake Quality Scores**: -1 (negative) to +1 (positive)
- **Technical Challenge**: Ranked 1 (best) to N (worst, where N = number of contestants)
- **Handshakes**: Binary indicator (1 = received, blank = not received)
- **Reviews**: -1 (negative feedback) to +1 (positive feedback)
- **Weekly Outcomes**: Binary (1 = winner/eliminated, blank = safe)

### Key Patterns Observed
- Final rounds (Round 10) only have winners, no eliminations (confirmed)
- Handshakes are rare and indicate exceptional performance
- Technical rankings vary by number of contestants remaining
- All contestants have complete tech scores (1-N ranking where N = contestants remaining)

### Data Processing Rules
- **Missing scores**: Treat blank cells as 0/neutral (confirmed by user)
- **Handshakes**: Treat blank cells as 0 (no handshake received)
- **Reviews**: Treat blank cells as 0 (no review/neutral feedback)
- **Winner/Eliminated**: Treat blank cells as 0 (safe/continuing)

### Tech Score Normalization
**Problem**: Raw tech scores range from 1 (best) to N (worst), where N = contestants in round. A score of 3 in a 12-contestant round (3rd place) is much better than a score of 3 in a 5-contestant round (3rd place).

**Data Status**: All tech scores follow the expected 1-to-N pattern. Data validation confirms all rounds are consistent.

**Solution**: Normalize tech scores to 0.0-1.0 scale within each round:
- Formula: `normalized = 1 - (raw_score - min_score) / (max_score - min_score)`
- 1st place (lowest score) → 1.0 (best performance)
- Last place (highest score) → 0.0 (worst performance)
- Uses actual min/max scores per round (handles inconsistencies)
- Accounts for varying contestant numbers per round

**Data File**: `data.csv` contains all raw data with descriptive column headers

### Model Results
**Analysis results and conclusions have been moved to ANALYSIS_RESULTS.md**

The project has successfully developed prediction models:
1. **Second Half Review Prediction**: 93.1% accuracy on 321 rounds
2. **Winner Prediction**: 61.4% accuracy (43/70 correct)
3. **Elimination Prediction**: 56.7% accuracy (34/60 correct)
4. **Final Winner Prediction**: 71.4% accuracy among finalists

See ANALYSIS_RESULTS.md for complete findings, model performance details, and practical applications.

## Current Analysis Features

### Comprehensive Performance Analytics
- **Strength Score System**: 0-10 scale performance metric using weighted bake components
- **Component Weight Analysis**: ML-derived importance weights for each baking component
- **Component Variance Analysis**: Statistical validation of component weights through variance analysis
- **Prediction Accuracy Analysis**: Multiple accuracy metrics including winner, elimination, and review predictions
- **Performance Insights**: Analysis by strength ranges (high/mid/low performers)
- **Series Winner Analysis**: Ranking series winners by average strength scores
- **Top Performer Rankings**: Identification of strongest non-series-winners
- **Top 5 Quarterfinalist+ Rankings**: Category-specific excellence rankings with overall field averages

### Advanced Elimination Analysis
- **Round-by-Round Patterns**: Analysis of elimination patterns across different rounds
- **Performance Drop Tracking**: Quantifies how much contestants underperform in elimination rounds
- **Contestant Strength Metrics**: Average strength vs. elimination round performance comparison
- **Performance Variance Analysis**: Top 5 most/least consistent contestants with detailed statistics including star bakers, positive/negative reviews, and handshakes
- **Elimination Statistics**: Comprehensive statistics on elimination patterns and performance drops

### Category-Specific Excellence Analysis
- **Technical Challenge Excellence**: Rankings of quarterfinalists+ by technical performance
- **Signature Bake Excellence**: Rankings by signature bake performance with field averages
- **Showstopper Excellence**: Rankings by showstopper performance with field averages
- **Flavor Excellence**: Rankings by combined flavor performance with field averages
- **Bake Execution Excellence**: Rankings by overall bake execution with field averages
- **Visual Presentation Excellence**: Rankings by visual presentation with field averages

### Enhanced Statistical Reporting
- **Comprehensive Contestant Statistics**: Pre-calculated dataframes with all contestant metrics to eliminate duplicate calculations
- **Centralized Data Processing**: Single calculation pass for all contestant statistics including:
  - Average strength scores, total rounds, maximum round reached
  - Star baker wins, handshakes (signature + showstopper), positive/negative reviews
  - Elimination status and quarterfinalist qualification
  - Performance variance statistics
  - Category-specific averages (technical, signature, showstopper, flavor, bake, looks)

### Output Reports
- **Performance Data**: Complete round-by-round strength scores and outcomes (gbbo_complete_analysis.csv)
- **Contestant Summary**: Aggregated statistics including handshakes, reviews, and final placements (gbbo_complete_analysis_contestant_summary.csv) 
- **Analysis Insights**: Performance correlations, prediction accuracies, and behavioral patterns
- **Theme Analysis**: Episode theme difficulty analysis with performance vs expectation metrics

## Analysis Goals
1. **Weight Calculation**: Determine relative importance of each scoring component ✓
2. **Weekly Performance Model**: Create scoring system for weekly baker strength ✓
3. **Data Validation**: Ensure data quality and consistency ✓
4. **Predictive Modeling**: Use historical data to predict judge reviews and outcomes ✓
5. **Performance Analytics**: Comprehensive contestant ranking and outcome analysis ✓
6. **Elimination Pattern Analysis**: Understanding performance drops and elimination dynamics ✓
7. **Component Variance Validation**: Statistical validation that model weights reflect genuine predictive power ✓
8. **Theme Difficulty Analysis**: Understanding which episode themes create performance challenges ✓
9. **Category Excellence Rankings**: Top 5 quarterfinalist+ rankings across baking categories with field comparisons ✓
10. **Code Optimization**: Eliminate duplicate calculations through centralized statistical computation ✓

## Technical Approach
- **Modular Architecture**: Clean package structure with separation of concerns
- **Data Validation**: Automated checks for tech score patterns, review completeness, and data uniqueness
- **Python-based Analysis**: Uses pandas for data manipulation and scikit-learn for machine learning
- **Centralized Calculation Architecture**: Single-pass computation of all contestant statistics to eliminate duplication
- **Pre-calculated Dataframes**: Three core dataframes store all computed statistics:
  - `contestant_stats_df`: Basic contestant statistics and outcomes
  - `variance_stats_df`: Performance variance analysis data
  - `quarterfinalist_stats_df`: Category-specific performance averages
- **Strength Score Calculation**: Weighted performance metric on 0-10 scale using ML-derived weights
- **Statistical Analysis**: Logistic regression models to determine component importance weights
- **Component Variance Analysis**: Statistical validation of weights through variance and distribution analysis
- **Performance Prediction**: Machine learning models for judge reviews, winner/elimination outcomes
- **Theme Analysis**: Statistical difficulty assessment across different episode themes
- **Optimized Performance**: Eliminates duplicate calculations by computing statistics once and referencing throughout analysis

### Code Architecture
The analysis is implemented as a modular Python package:

```
gbbo_analysis/
├── __init__.py           # Package initialization and exports
├── config.py             # Configuration constants and settings
├── validation.py         # Data validation and quality checks
├── models.py            # ML model training and correlation analysis
├── calculator.py        # Strength score calculation logic
└── analyzer.py          # Main analysis orchestration
main.py                  # Entry point script
```

#### Module Responsibilities:
- **config.py**: Centralized configuration, column definitions, model weights, and thresholds
- **validation.py**: Data quality validation including tech score patterns, review completeness, and uniqueness checks
- **models.py**: Machine learning model training, component weight calculation, and variance analysis
- **calculator.py**: Strength score computation with normalized scaling using ML-derived weights
- **analyzer.py**: Main orchestration class that coordinates all analysis phases including variance and theme analysis
- **theme_analysis.py**: Episode theme difficulty analysis and performance vs expectation metrics
- **main.py**: Simple entry point for running complete analysis

This modular structure provides:
- **Better maintainability**: Each module has single responsibility
- **Easier testing**: Individual components can be tested independently
- **Improved reusability**: Components can be imported and used separately
- **Clearer dependencies**: Module imports show component relationships
- **Enhanced collaboration**: Multiple developers can work on different modules

### Development Guidelines:
- **Unicode Characters**: Always use ASCII characters in console output (*, X, >) to avoid encoding errors
- **Error Handling**: All modules include proper exception handling and validation
- **Type Safety**: Comprehensive type hints throughout for IDE support and documentation
- **Configuration**: Centralized settings in config.py for easy maintenance

## Key Questions Addressed
- **Which scoring components best predict weekly winners/eliminations?** ✓ Technical challenge performance is most critical for first half reviews; showstopper bakes are most important overall
- **How do technical challenge rankings correlate with overall performance?** ✓ Strongest predictor (0.739 correlation) for first half reviews; normalized scoring accounts for varying contestant numbers
- **What role do handshakes play in final outcomes?** ✓ Variable predictive value - signature handshakes more predictive (0.304) than showstopper handshakes (0.088)
- **How does performance vary across different series?** ✓ Series ranked by overall average strength with comprehensive finalist analysis
- **How much do contestants underperform in elimination rounds?** ✓ Performance drop analysis shows quantified underperformance patterns by round
- **What are the elimination patterns across different rounds?** ✓ Round-by-round analysis reveals elimination dynamics and contestant strength patterns