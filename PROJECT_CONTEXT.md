# Great British Bake Off Data Analysis Project

## Project Overview
This project provides a comprehensive analysis system for The Great British Bake Off performance data, organized into four distinct phases:

1. **Data Collection** - Scraping, transcript processing, and judging data compilation
2. **Correlation Analysis** - ML model training to determine component importance weights  
3. **Monte Carlo Simulations** - Generating predictions based on strength scores and variances
4. **Analysis & Reporting** - Comprehensive performance analytics and insights

## Project Structure

```
BakeOff/
├── data_collection/             # Part 1: Data Collection
│   ├── scraping/
│   │   ├── wikiscraper.py
│   │   ├── wiki_v_google_validation.py
│   │   └── gbbo_episodes.csv
│   ├── judging/
│   │   ├── human/
│   │   │   └── data.csv                    # Human-interpreted judging
│   │   ├── claude/
│   │   │   ├── claude_judging.csv          # Claude AI analysis
│   │   │   ├── claude_data.csv             # Combined data
│   │   │   ├── claude_judging_prompt.md
│   │   │   └── combine_claude_data.py
│   │   ├── compare_datasets.py
│   │   └── current.csv                     # Current season data
│   ├── transcripts/
│   │   ├── netflix_transcripts/            # Raw Netflix subtitle files
│   │   ├── parsed_transcripts/             # Processed transcript text
│   │   ├── audited_transcripts/            # Judge-scored transcripts
│   │   ├── claude_todo/                    # Transcripts pending scoring
│   │   └── parse_transcripts.py            # Transcript processing tool
│   └── validation/
│
├── correlation_analysis/        # Part 2: Correlation Analysis
│   ├── train_weights.py                    # Main weight training program
│   ├── model_weights.json                  # Generated weights
│   └── weights/                            # Different weight configurations
│
├── monte_carlo/                 # Part 3: Monte Carlo Simulations
│   ├── historical_monte_carlo.py
│   ├── weekly_predictions.py
│   └── predictions_output/
│       ├── weekly_predictions.md
│       └── season_markdown/
│           ├── weekly_predictions_s5.md
│           └── ...
│
├── analysis/                    # Part 4: Analysis & Reporting
│   ├── main.py                             # Main analysis program
│   ├── reports/
│   │   ├── gbbo_complete_analysis.csv
│   │   └── gbbo_complete_analysis_contestant_summary.csv
│   └── visualization/
│
├── shared/                      # Shared utilities across all parts
│   ├── gbbo_analysis/           # Core analysis package
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── calculator.py
│   │   ├── analyzer.py
│   │   └── validation.py
│   └── utils/
│
└── README.md
```

## Four-Part Analysis Workflow

### **Part 1: Data Collection**
**Purpose**: Gather and process all source data for analysis
**Location**: `data_collection/`

- **Scraping**: Wikipedia episode data and metadata
- **Judging**: Human interpretation and Claude AI analysis of judge comments
- **Transcripts**: Processing Netflix subtitles into analyzable text
- **Validation**: Data quality checks and consistency verification

**Key Outputs**: 
- `data_collection/judging/human/data.csv` - Human-interpreted judging data
- `data_collection/judging/claude/claude_data.csv` - Claude AI judging data
- `data_collection/scraping/gbbo_episodes.csv` - Episode metadata

### **Part 2: Correlation Analysis** 
**Purpose**: Train ML models to determine component importance weights
**Location**: `correlation_analysis/`

- **Model Training**: Logistic Regression and Random Forest models
- **Weight Calculation**: Component importance weights for strength score calculation
- **Correlation Analysis**: Statistical relationships between judging components
- **Performance Validation**: Model accuracy and predictive power assessment

**Usage**:
```bash
cd correlation_analysis
python train_weights.py  # Human data
python train_weights.py --input ../data_collection/judging/claude/claude_data.csv --output model_weights_claude.json  # Claude data
```

**Key Outputs**:
- `model_weights.json` - Pre-calculated ML model weights
- Component weight analysis and performance metrics

### **Part 3: Monte Carlo Simulations**
**Purpose**: Generate predictions using strength scores and performance variances
**Location**: `monte_carlo/`

- **Historical Analysis**: Simulate past seasons with known outcomes
- **Prediction Generation**: Finalist and winner probability calculations
- **Weekly Forecasts**: Episode-by-episode prediction updates
- **Variance Modeling**: Account for contestant performance consistency

**Usage**:
```bash
cd monte_carlo
python historical_monte_carlo.py 8 4  # Season 8, Episode 4
```

**Key Outputs**:
- Weekly prediction tables and probability rankings
- Historical prediction accuracy validation
- Season markdown files with analysis commentary

### **Part 4: Analysis & Reporting**
**Purpose**: Comprehensive performance analytics and insights generation
**Location**: `analysis/`

- **Strength Score Calculation**: Weighted performance metrics using ML-derived weights
- **Performance Analytics**: Rankings, variance analysis, and outcome predictions
- **Statistical Reporting**: Accuracy metrics and behavioral pattern analysis
- **Comprehensive Reports**: CSV outputs and detailed performance insights

**Usage**:
```bash
cd analysis
python main.py --weights ../correlation_analysis/model_weights.json
```

**Key Outputs**:
- `reports/gbbo_complete_analysis.csv` - Complete performance data
- `reports/gbbo_complete_analysis_contestant_summary.csv` - Aggregated statistics
- Comprehensive console analysis with rankings and insights

## Data Sources and Structure

### Judging Data Sources

The project uses two primary judging datasets:

1. **Human-Interpreted Judging (`judging_data/data.csv`)**
   - Manually scored judge comments based on human interpretation of episode transcripts
   - Covers Series 5-12 with comprehensive scoring across all baking challenges
   - Uses integer scoring: -1 (negative), 0 (neutral), 1 (positive)
   - Includes handshakes, technical rankings, and judge review classifications

2. **Claude AI Transcript Analysis (`judging_data/claude/claude_judging.csv`)**
   - Automated scoring of judge comments using Claude AI analysis of episode transcripts
   - Generated using structured prompt analysis of judge feedback patterns
   - Uses decimal scoring: -1.0 to 1.0 scale with more granular distinctions
   - Focuses on signature and showstopper bakes (6 scores per contestant per episode)

### Data Structure (judging_data/data.csv - Human Interpreted)

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
- **Series 5-12 included**
- **603 total contestant-round records across 90 contestants**
- Series 5: 13 contestants, 10 rounds
- Series 6: 12 contestants, 10 rounds  
- Series 7: 13 contestants, 10 rounds
- Series 8: 12 contestants, 10 rounds
- Series 9: 12 contestants, 10 rounds
- Series 10: 12 contestants, 10 rounds
- Series 11: 12 contestants, 9 rounds
- Series 12: 12 contestants, 10 rounds

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

### Commentary Generation Guidelines
**IMPORTANT**: When asked to generate commentary for analysis files, do NOT create code-generated commentary. Instead:
1. Parse and analyze the generated results manually
2. Identify key patterns, trends, and insights from the data
3. Write thoughtful commentary based on your analysis
4. Include observations about contestant performance, predictions accuracy, and strategic patterns
5. Commentary should be written in markdown format as part of the output file
6. The word "technical" in the context of bakeoff refers to a technical challenge. So referring to technical skill should only be used in reference to someone's skills in the technical challenge.
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

**Data File**: `judging_data/data.csv` contains all raw data with descriptive column headers

### Model Results
**Analysis results and conclusions have been moved to ANALYSIS_RESULTS.md**

The project has successfully developed prediction models:
1. **Second Half Review Prediction**: 92.8% accuracy on 362 rounds
2. **Winner Prediction**: 62.5% accuracy (50/80 correct)
3. **Elimination Prediction**: 57.4% accuracy (39/68 correct)
4. **Final Winner Prediction**: 62.5% accuracy among finalists (5/8 series correct)

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

### Historical Monte Carlo Analysis (prediction_analysis/historical_monte_carlo.py)
- **Purpose**: Generates Monte Carlo simulation predictions for historical seasons (5-12) using existing strength scores
- **Usage**: `cd prediction_analysis && python historical_monte_carlo.py <season> <episode>` (e.g., `cd prediction_analysis && python historical_monte_carlo.py 8 4`)
- **Command Line Arguments**:
  - `season`: Season number (5-12)
  - `episode`: Episode/week number within the season
  - `--data-path`: Optional path to data file (defaults to '../analysis_output/gbbo_complete_analysis.csv')
- **Output**: Console-only data tables showing:
  - Contestant rankings by finals probability and winner probability
  - Average strength scores, variance, week performance, and achievement counts
  - Top 3 predictions and predicted winner with percentages
- **Method**: Monte Carlo simulation (10,000 iterations) using contestant performance history through specified week
- **Usage Context**: Output from this script is used to update markdown files in `prediction_analysis/season_markdown/` folder
  - Raw data/tables are generated by the script
  - Commentary and insights are added manually by parsing the results with Claude
  - Final markdown files combine both data tables and human-generated analysis

### Output Reports
- **Performance Data**: Complete round-by-round strength scores and outcomes (analysis_output/gbbo_complete_analysis.csv)
- **Contestant Summary**: Aggregated statistics including handshakes, reviews, and final placements (analysis_output/gbbo_complete_analysis_contestant_summary.csv) 
- **Analysis Insights**: Performance correlations, prediction accuracies, and behavioral patterns
- **Theme Analysis**: Episode theme difficulty analysis with performance vs expectation metrics
- **Historical Predictions**: Season-by-season weekly prediction markdown files in `prediction_analysis/season_markdown/` folder

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
11. **Four-Part Modular Architecture**: Organized into data collection, correlation analysis, Monte Carlo simulations, and analysis/reporting ✓

## Technical Approach

### **Four-Part Modular Architecture**
- **Data Collection**: Automated scraping, transcript processing, and judging compilation
- **Correlation Analysis**: ML model training to determine component importance weights
- **Monte Carlo Simulations**: Probabilistic prediction generation using strength scores
- **Analysis & Reporting**: Comprehensive performance analytics and insights

### **Key Technical Features**
- **Python-based Analysis**: Uses pandas for data manipulation and scikit-learn for machine learning
- **Modular Package Structure**: Clean separation of concerns across the shared analysis package
- **Data Validation**: Automated checks for tech score patterns, review completeness, and data uniqueness
- **Flexible Path Handling**: Supports running from different working directories with intelligent path resolution
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
The analysis is implemented as a four-part modular system with shared utilities:

**Shared Analysis Package (`shared/gbbo_analysis/`)**:
```
shared/gbbo_analysis/
├── __init__.py           # Package initialization and exports
├── config.py             # Configuration constants and settings
├── validation.py         # Data validation and quality checks
├── models.py            # ML model training and correlation analysis
├── calculator.py        # Strength score calculation logic
└── analyzer.py          # Main analysis orchestration
```

**Four Main Parts**:
- `data_collection/` - Scraping, judging, and transcript processing
- `correlation_analysis/` - Weight training and model development
- `monte_carlo/` - Prediction generation and simulation
- `analysis/` - Reporting and comprehensive analytics

#### Module Responsibilities:

**Shared Package (`shared/gbbo_analysis/`)**:
- **config.py**: Centralized configuration, column definitions, and file paths
- **validation.py**: Data quality validation including tech score patterns and review completeness
- **models.py**: Machine learning model training, component weight calculation, and variance analysis
- **calculator.py**: Strength score computation with normalized scaling using ML-derived weights
- **analyzer.py**: Main orchestration class that coordinates all analysis phases

**Part-Specific Scripts**:
- **correlation_analysis/train_weights.py**: Weight training program with ML model development
- **monte_carlo/historical_monte_carlo.py**: Historical prediction analysis and simulation
- **analysis/main.py**: Main analysis program with comprehensive reporting

This four-part modular structure provides:
- **Clear Workflow**: Each directory represents a logical step in the analysis process
- **Better Maintainability**: Each part has focused responsibility and can be developed independently
- **Easier Testing**: Individual parts can be tested in isolation
- **Flexible Deployment**: Parts can be run on different systems or schedules as needed
- **Enhanced Collaboration**: Teams can work on different analysis phases simultaneously
- **Reproducible Research**: Each part has clearly defined inputs and outputs

### Code Quality Improvements

**Recent Refactoring (analyzer.py)**:
The main analyzer module has undergone significant refactoring to improve code quality and maintainability:

1. **Extracted Constants** - Replaced magic numbers with named class constants:
   - `SOFTMAX_TEMPERATURE = 2.0` for probability calculations
   - `MIN_QUARTERFINALIST_ROUND = 7` for quarterfinalist qualification
   - `THEME_MIN_APPEARANCES = 3` for theme analysis threshold
   - Difficulty threshold constants for theme classification

2. **Helper Methods** - Extracted reusable helper functions:
   - `_format_handshake_info()` - Centralized handshake string formatting (eliminated ~20 lines of duplication)
   - `_calculate_performance_ranges()` - Performance range statistics calculation (eliminated 60+ lines of duplication)
   - `_calculate_brier_score()`, `_calculate_log_loss()`, `_calculate_calibration_error()` - Promoted nested functions to reusable static methods

3. **Comprehensive Documentation** - Added detailed docstrings to all helper methods:
   - Parameter documentation with types
   - Return value descriptions
   - Usage context and examples

4. **DRY Principle** - Eliminated major code duplication:
   - ~140 lines of duplicate code removed
   - Single source of truth for calculations
   - Consistent formatting across all outputs

**Impact**:
- Better maintainability through centralized logic
- Improved readability with self-documenting code
- Easier testing with extracted, reusable methods
- 100% output validation ensures no behavioral changes

### Development Guidelines:
- **Code Quality**: Follow DRY (Don't Repeat Yourself) principles - extract duplicate code into reusable helpers
- **Documentation**: Provide comprehensive docstrings with parameter types and return values
- **Constants**: Use named constants instead of magic numbers for better maintainability
- **Unicode Characters**: Always use ASCII characters in console output (*, X, >) to avoid encoding errors
- **Error Handling**: All modules include proper exception handling and validation
- **Type Safety**: Comprehensive type hints throughout for IDE support and documentation
- **Configuration**: Centralized settings in config.py for easy maintenance
- **Output Validation**: Validate that refactoring maintains identical output to baseline

## Key Questions Addressed
- **Which scoring components best predict weekly winners/eliminations?** ✓ Technical challenge performance is most critical for first half reviews; showstopper bakes are most important overall
- **How do technical challenge rankings correlate with overall performance?** ✓ Strongest predictor (0.739 correlation) for first half reviews; normalized scoring accounts for varying contestant numbers
- **What role do handshakes play in final outcomes?** ✓ Variable predictive value - signature handshakes more predictive (0.304) than showstopper handshakes (0.088)
- **How does performance vary across different series?** ✓ Series ranked by overall average strength with comprehensive finalist analysis
- **How much do contestants underperform in elimination rounds?** ✓ Performance drop analysis shows quantified underperformance patterns by round
- **What are the elimination patterns across different rounds?** ✓ Round-by-round analysis reveals elimination dynamics and contestant strength patterns