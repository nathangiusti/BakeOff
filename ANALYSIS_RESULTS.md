# A Great British Bake Off Data-Based Analysis

## Executive Summary

This analysis examines The Great British Bake Off data to understand the relative importance of different bakes and components, and to create a comprehensive ranking system for bakers across seasons. Using logistic regression modeling, we achieved 93% accuracy in predicting judge reviews and developed strength scores that effectively differentiate baker performance levels.

## Methodology

### Data Collection
- **Scope**: Netflix seasons only (Seasons 5-11) to maintain consistent judging standards
- **Sources**: Episode reviews, Wikipedia technical rankings, and comprehensive episode analysis
- **Scoring System**: Each baker received scores for seven components per episode:
  - Technical Challenge: Single numerical ranking
  - Signature Bake: Three categories (Bake/Texture/Execution, Flavor/Taste, Presentation)
  - Showstopper Bake: Three categories (same as signature)

### Scoring Methodology
Each component was scored as:
- **+1**: Positive judge feedback
- **0**: Mixed feedback or not mentioned
- **-1**: Negative judge feedback

**Note**: This crude scoring system treats generally positive reviews the same as rave reviews. For multi-component bakes, scores were averaged across elements combined with judges' closing remarks.

### Statistical Model
A logistic regression model was used to determine the relative importance of each bake component. The model analyzes the relationship between bake scores and final judge reviews (specifically the post-showstopper discussion).

**Important Limitations**: 
- First-half reviews (between technical and showstopper) were excluded from the final model due to poor accuracy
- Alternative weighting methods for winners/eliminations proved less accurate
- Testing was performed on training data due to limited sample size

## Model Accuracy

### Overall Performance
- **Judge Review Prediction**: 93% accuracy
- **Star Baker Prediction**: 61% accuracy  
- **Elimination Prediction**: 57% accuracy
- **Season Winner Prediction**: 71% accuracy (from finalists)

### Probability Accuracy (Brier Scores)
- **Winner Prediction**: 0.079 (excellent - close to perfect 0.0)
- **Elimination Prediction**: 0.082 (excellent)
- **Baseline**: 0.25 (random 50% assignment)

The model performs best with broader performance gaps and more data points per baker.

## Results

### Bake Importance Rankings

| Challenge | Total Weight | Percentage |
|-----------|--------------|------------|
| Showstopper | 4.011 | 44.2% |
| Technical | 2.936 | 32.3% |
| Signature | 2.131 | 23.5% |

**Key Finding**: The showstopper is the most important single bake, though combined technical and signature still outweigh it. Technical challenges significantly outweigh signature bakes.

### Component Analysis

#### Signature Bake Components

| Component | Weight | Mean Score | Variance | % Negative | % Neutral | % Positive | % of Signature |
|-----------|---------|------------|----------|------------|-----------|------------|----------------|
| Looks | 0.898 | 0.21 | 0.752 | 29.1% | 20.4% | 50.5% | 42.2% |
| Bake/Execution | 0.554 | 0.17 | 0.783 | 32.1% | 19.1% | 48.8% | 26.0% |
| Handshake | 0.470 | - | - | 0% | 92.8% | 7.2% | 22.1% |
| Flavor | 0.209 | 0.51 | 0.618 | 18.3% | 12.7% | 69.0% | 9.8% |

#### Showstopper Components

| Component | Weight | Mean Score | Variance | % Negative | % Neutral | % Positive | % of Showstopper |
|-----------|---------|------------|----------|------------|-----------|------------|------------------|
| Looks | 1.457 | 0.36 | 0.715 | 24.2% | 15.7% | 60.1% | 36.3% |
| Flavor | 1.315 | 0.48 | 0.663 | 20.6% | 10.4% | 69.0% | 32.8% |
| Bake/Execution | 1.139 | 0.22 | 0.815 | 32.1% | 13.8% | 54.1% | 28.4% |
| Handshake | 0.099 | - | - | 0% | 98.7% | 1.1% | 2.5% |

**Key Insights**:
- **Presentation matters most**: "Looks" is the highest-weighted component in both signature and showstopper bakes
- **Flavor paradox**: Despite 70% of bakes receiving positive flavor feedback, it has lower predictive weight due to its commonality
- **Handshake rarity**: Showstopper handshakes are extremely rare (1.1%) but signature handshakes are more impactful when given

## Baker Performance Analysis

### Overall Performance Distribution
- **Average Score**: 6.21/10 
- **Range**: 0.62 - 9.93
- **Star Baker Average**: 8.44/10
- **Elimination Average**: 3.76/10
- **Safe Contestant Average**: 6.54/10

### Performance Thresholds

#### Star Baker Win Rates by Performance Level
- **High Performers** (8.0+): 41.1% win rate (46/112)
- **Mid Performers** (6.0-7.9): 12.0% win rate (22/183)  
- **Low Performers** (<6.0): 0.9% win rate (2/234)

#### Elimination Rates by Performance Level
- **High Performers** (8.0+): 0.9% elimination rate (1/112)
- **Mid Performers** (6.0-7.9): 1.1% elimination rate (2/183)
- **Low Performers** (<6.0): 26.1% elimination rate (61/234)

### Elimination Patterns by Round

| Round | Eliminations | Avg Contestant Strength | Avg Elimination Performance | Performance Drop |
|-------|--------------|------------------------|----------------------------|------------------|
| 1 | 7 | 3.14 | 3.14 | 0.00 |
| 2 | 7 | 4.72 | 4.36 | 0.36 |
| 3 | 6 | 5.20 | 3.27 | 1.93 |
| 4 | 5 | 4.75 | 2.32 | 2.44 |
| 5 | 7 | 5.47 | 3.99 | 1.48 |
| 6 | 7 | 5.41 | 3.18 | 2.23 |
| 7 | 7 | 5.71 | 4.14 | 1.58 |
| 8 | 7 | 6.21 | 4.11 | 2.11 |
| 9 | 7 | 6.67 | 5.33 | 1.34 |

**Pattern Analysis**:
- **Early rounds** (1-2): Eliminate consistently weak bakers
- **Middle rounds** (3-7): Eliminate average-to-good bakers having poor performances  
- **Late rounds** (8-9): Strong bakers eliminated due to single bad performances

## Season Analysis

### Finale Predictions vs. Actual Results

#### Season 5
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Sophie*** | 7.66/10 | 50.4% | **Winner** |
| 2 | Steven | 6.70/10 | 31.2% | Finalist |
| 3 | Kate | 5.64/10 | 18.4% | Finalist |

#### Season 6
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Rahul*** | 7.15/10 | 40.0% | **Winner** |
| 2 | Kim-Joy | 6.85/10 | 34.4% | Finalist |
| 3 | Ruby | 6.26/10 | 25.6% | Finalist |

#### Season 7
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | Steph | 7.49/10 | 38.3% | Finalist |
| 2 | Alice | 7.14/10 | 32.1% | Finalist |
| 3 | **David*** | 6.98/10 | 29.7% | **Winner** |

#### Season 8
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Peter*** | 7.68/10 | 48.0% | **Winner** |
| 2 | Dave | 6.98/10 | 33.9% | Finalist |
| 3 | Laura | 5.72/10 | 18.1% | Finalist |

#### Season 9
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Giuseppe*** | 8.00/10 | 37.5% | **Winner** |
| 2 | Crystelle | 7.67/10 | 31.7% | Finalist |
| 3 | Chigs | 7.61/10 | 30.8% | Finalist |

#### Season 10
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Syabira*** | 7.49/10 | 44.5% | **Winner** |
| 2 | Sandro | 6.63/10 | 29.0% | Finalist |
| 3 | Abdul | 6.44/10 | 26.4% | Finalist |

#### Season 11
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | Josh | 7.33/10 | 48.8% | Finalist |
| 2 | Dan | 6.36/10 | 30.0% | Finalist |
| 3 | **Matty*** | 5.67/10 | 21.2% | **Winner** |

**Prediction Accuracy**: The model correctly predicted 5 out of 7 winners. Notable misses were David (Season 7, very close finale) and Matty (Season 11, significant underperformance relative to model expectations).

### Winners Ranked by Strength

| Rank | Winner | Season | Avg Strength | Star Baker Wins | Handshakes |
|------|--------|--------|--------------|-----------------|------------|
| 1 | Giuseppe | 9 | 8.00/10 | 2 | 2 sig |
| 2 | Peter | 8 | 7.68/10 | 2 | 1 sig + 1 show |
| 3 | Sophie | 5 | 7.66/10 | 2 | 1 sig |
| 4 | Syabira | 10 | 7.49/10 | 3 | 1 sig |
| 5 | Rahul | 6 | 7.15/10 | 2 | 2 sig + 1 show |
| 6 | David | 7 | 6.98/10 | 0 | 1 sig |
| 7 | Matty | 11 | 5.67/10 | 2 | 1 sig |

**Notable Findings**: 
- Matty ranks as the weakest winner by a significant margin
- Giuseppe shows the highest overall strength with a notable gap over second place
- David uniquely won without any Star Baker awards

### Season Strength Rankings

| Rank | Season | Winner | Average Strength |
|------|--------|--------|------------------|
| 1 | Season 9 | Giuseppe | 6.53/10 |
| 2 | Season 8 | Peter | 6.36/10 |
| 3 | Season 10 | Syabira | 6.24/10 |
| 4 | Season 7 | David | 6.16/10 |
| 5 | Season 6 | Rahul | 6.13/10 |
| 6 | Season 11 | Matty | 6.10/10 |
| 7 | Season 5 | Sophie | 5.92/10 |

Season 9 emerges as exceptionally strong, with multiple high-performing contestants.

## Individual Excellence Rankings

### Top Non-Winners

| Rank | Contestant | Season | Avg Strength | Star Baker Wins | Handshakes | Result |
|------|------------|--------|--------------|-----------------|------------|---------|
| 1 | Jurgen | 9 | 7.91/10 | 3 | 1 sig | Semi-finalist |
| 2 | Crystelle | 9 | 7.67/10 | 2 | 1 sig + 1 show | Finalist |
| 3 | Chigs | 9 | 7.61/10 | 2 | 2 sig | Finalist |
| 4 | Steph | 7 | 7.49/10 | 4 | 1 sig | Finalist |
| 5 | Josh | 11 | 7.33/10 | 2 | 1 show | Finalist |

**Key Insight**: Season 9 dominates the top non-winner positions, with Jurgen's semi-final elimination representing a significant statistical anomaly.

### Specialty Excellence Leaders

#### Technical Challenge Masters
1. **Jurgen** (S9): 0.75 average
2. **David** (S7): 0.72 average  
3. **Peter** (S8): 0.69 average
4. **Sophie** (S5): 0.68 average
5. **Jon** (S6): 0.67 average

#### Signature Bake Masters
1. **Giuseppe** (S9): 0.77 average
2. **Kim-Joy** (S6): 0.70 average
3. **Syabira** (S10): 0.70 average
4. **Crystelle** (S9): 0.67 average
5. **Steph** (S7): 0.63 average

*Overall average: 0.21*

#### Showstopper Masters
1. **Crystelle** (S9): 0.87 average
2. **Jurgen** (S9): 0.81 average
3. **Sophie** (S5): 0.73 average
4. **Chigs** (S9): 0.70 average
5. **Alice** (S7): 0.70 average

*Overall average: 0.23*

#### Flavor Excellence
1. **Crystelle** (S9): 1.00 average (perfect flavor record)
2. **Sophie** (S5): 0.95 average
3. **Tasha** (S11): 0.81 average
4. **Chigs** (S9): 0.80 average
5. **Kim-Joy** (S6): 0.80 average

*Overall average: 0.39*

#### Bake Execution Excellence
1. **Crystelle** (S9): 0.77 average
2. **Giuseppe** (S9): 0.72 average
3. **Syabira** (S10): 0.67 average
4. **Chigs** (S9): 0.65 average
5. **Steph** (S7): 0.65 average

*Overall average: 0.22*

#### Visual Presentation Excellence
1. **Giuseppe** (S9): 0.90 average
2. **Syabira** (S10): 0.80 average
3. **Janusz** (S10): 0.72 average
4. **Crystelle** (S9): 0.70 average
5. **Dave** (S8): 0.70 average

*Overall average: 0.16*

## Notable Individual Performances

### Top 5 Individual Weekly Performances
1. **Peter** S8R9: 9.93/10 (Star Baker)
2. **Giuseppe** S9R3: 9.93/10 (Star Baker)
3. **Steven** S5R7: 9.63/10 (Star Baker)
4. **Alice** S7R2: 9.63/10 (Star Baker)
5. **Steph** S7R4: 9.63/10 (Star Baker)

*The 9.93 scores indicate perfect performance across all signature and showstopper components, first place in technical, and signature handshake receipt.*

### Bottom 5 Weekly Performances
1. **Terry** S6R5: 0.62/10 (Eliminated)
2. **Julia** S5R6: 0.96/10 (Eliminated)
3. **Sura** S8R4: 0.99/10 (Eliminated)
4. **Kate** S5R2: 1.23/10 (Safe)
5. **Manon** S6R6: 1.34/10 (Safe)

### Performance Extremes
- **Strongest Non-Winner Performance**: Sura S8R1 (9.63/10)
- **Weakest Star Baker Performance**: Matty S11R10 (5.42/10)
- **Strongest Elimination Performance**: Jurgen S9R9 (8.53/10)
- **Weakest Safe Performance**: Kate S5R2 (1.23/10)

## Theme Week Analysis

Analysis of recurring theme weeks (3+ appearances) shows relative difficulty based on average performance deviation:

| Rank | Theme | Avg Difference | % Underperform | Difficulty |
|------|-------|----------------|----------------|------------|
| 1 | Pastry | -0.97 | 68.8% | Most Difficult |
| 2 | Bread | -0.76 | 62.3% | Most Difficult |
| 3 | Desserts | -0.67 | 65.1% | Moderate |
| 4 | Final | -0.66 | 57.1% | Moderate |
| 5 | Pâtisserie | -0.45 | 53.6% | Moderate |
| 6 | Caramel | -0.35 | 66.7% | Moderate |
| 7 | Cake | +0.07 | 46.4% | Easiest |
| 8 | Biscuits | +0.13 | 48.1% | Easiest |

**Analysis**: Cake and biscuit weeks show above-average performance, likely reflecting contestants' greater familiarity with home baking. Pastry and bread weeks prove most challenging, aligning with Paul Hollywood's well-known high standards for these technical specialties.

## Future Improvements

### Data Enhancement Opportunities

#### Expanded Dataset
- **Historical Seasons**: Include pre-Netflix seasons, though this may require addressing judging consistency differences
- **International Versions**: Potential cross-cultural analysis

#### Refined Scoring System
Proposed 5-point scale:
- **+1.0**: Judges love it, no criticism
- **+0.5**: Judges like it, minor nitpicks
- **0.0**: Not mentioned or extremely mixed feedback
- **-0.5**: Judges dislike it, some positives but mostly negative
- **-1.0**: Complete disaster

#### Methodology Improvements
- **Multi-Rater Reliability**: Group rewatching with multiple scorers to reduce individual bias
- **Inter-Rater Agreement**: Standardized scoring protocols
- **Proper Train/Test Split**: Larger dataset would allow for proper model validation

#### Additional Variables
- **Judge-Specific Patterns**: Individual judge preferences and consistency
- **Seasonal Effects**: Performance changes throughout filming
- **Background Factors**: Contestant demographics and experience levels

## Conclusions

This analysis successfully quantifies the relative importance of different baking challenges and provides a robust framework for comparing baker performance across seasons. The model's strong predictive accuracy for general performance levels validates its utility, though individual prediction challenges remain.

**Key Takeaways**:
1. Visual presentation significantly outweighs flavor in judge decision-making
2. Technical challenges carry more weight than signature bakes
3. Season 9 represents an exceptionally strong cohort of bakers
4. Performance thresholds clearly differentiate star baker, safe, and elimination zones
5. Theme weeks show measurable difficulty variations aligned with technical complexity

The analysis provides a data-driven foundation for understanding judge preferences and baker evaluation, offering insights that extend beyond subjective viewing impressions.

---

*All code, input data, and output data available on GitHub. This analysis uses Netflix season numbering conventions.*