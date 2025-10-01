# A Great British Bake Off Data-Based Analysis

## Executive Summary

This analysis examines The Great British Bake Off data to understand the relative importance of different bakes and components, and to create a comprehensive ranking system for bakers across seasons. Using logistic regression modeling, we achieved 93% accuracy in predicting judge reviews and developed strength scores that effectively differentiate baker performance levels.

## Methodology

### Data Collection
- **Scope**: Netflix seasons only (Seasons 5 onward) both to maintain consistent judging standards and because this all I have access to. I apologize to the British, but thanks for the great content. 
- **Sources**: Wikipedia was pulled for technicals and final reviews, all other data was collected by manually watching all episodes

### Scoring System
- The Signature and Showstopper Bakes are graded on three categories:
  - Bake/Text/Execution - How will was the baked component made? How well did the structure hold up? Did the bake meet the specifications?
  - Flavor/Taste - Did it taste good? Were the flavors-well balanced?
  - Looks/Presentation - Did it look neat? Did it look appetizing?

- Each component was scored as:
  - **+1**: Generally positive feedback
  - **0**: Mixed feedback or not mentioned
  - **-1**: Generally negative feedback. 

**Note**: This crude scoring system treats generally positive reviews the same as rave reviews. For multi-component bakes, scores were averaged across elements combined with judges' closing remarks. 

### Statistical Model
A logistic regression model was used to determine the relative importance of each bake component. The model analyzes the relationship between bake scores and final judge reviews specifically the post-showstopper discussion/who the camera pans to when announcing the Star Baker/Eliminated Baker.

### Notes about failed models:

#### First-half reviews

I collected the data where available for the reviews that happen after the technical, but it was not useful. We tried:
    
- Using the first half review to provide a balance to the first two bakes that could then be compared to the second half review. 
- Using the first half review as a feature in and of itself. 

Ultimately none of these provided improved accuracy. 

#### Overweighting Winners/Losers
Right now we don't really differentiate between winning and just being one of the judges favorites. I tried weighting the winner/loser more strongly that others who just had final reviews, but this did not increase accuracy. 

This indicates that as far as your strength as a baker, there isn't much difference between being Star Baker and being highly rated. And similar would be true for Eliminated/low rated bakers. 

## Model Accuracy

### Overall Performance
- **Judge Review Prediction**: 93% accuracy
- **Star Baker Prediction**: 63% accuracy
- **Elimination Prediction**: 57% accuracy
- **Season Winner Prediction**: 63% accuracy (from finalists)

## Results

### Bake Importance Rankings

| Challenge | Total Weight | Percentage |
|-----------|--------------|------------|
| Showstopper | 4.012 | 42.0% |
| Technical | 3.176 | 33.3% |
| Signature | 2.361 | 24.7% |

**Key Finding**: The showstopper is the most important single bake, though combined technical and signature still outweigh it. Technical challenges significantly outweigh signature bakes.

### Component Analysis

#### Signature Bake Components

| Component | Weight | Mean Score | Variance | % Negative | % Neutral | % Positive | % of Signature |
|-----------|---------|------------|----------|------------|-----------|------------|----------------|
| Looks | 0.816 | 0.24 | 0.729 | 27.2% | 21.4% | 51.4% | 34.6% |
| Bake/Execution | 0.691 | 0.17 | 0.775 | 31.7% | 19.7% | 48.6% | 29.3% |
| Handshake | 0.614 | - | - | 0% | 93.0% | 7.0% | 26.0% |
| Flavor | 0.240 | 0.53 | 0.602 | 17.6% | 11.9% | 70.5% | 10.2% |

#### Showstopper Components

| Component | Weight | Mean Score | Variance | % Negative | % Neutral | % Positive | % of Showstopper |
|-----------|---------|------------|----------|------------|-----------|------------|------------------|
| Looks | 1.411 | 0.39 | 0.686 | 22.4% | 16.4% | 61.2% | 35.2% |
| Flavor | 1.362 | 0.51 | 0.639 | 19.4% | 10.1% | 70.5% | 33.9% |
| Bake/Execution | 1.050 | 0.23 | 0.798 | 31.0% | 15.1% | 53.9% | 26.2% |
| Handshake | 0.188 | - | - | 0% | 98.5% | 1.3% | 4.7% |

**Key Insights**:
- **Presentation matters most**: "Looks" is the highest-weighted component in both signature and showstopper bakes
- **Flavor paradox**: Despite 70% of bakes receiving positive flavor feedback, it has lower predictive weight due to its commonality. The average flavor score is around .5 while the average for the others is closer to .25.
- **Handshake rarity**: Showstopper handshakes are extremely rare (1.1%) which causes our model to not rate them highly. Signature handshakes happen often enough (7.2%) to carry weight.
- **Style over Substance?**: Assuming your flavors are correct, it's generally better to ensure your bake looks good then it is to ensure the bake itself is good. 

## Baker Performance Analysis

### Overall Performance Distribution
- **Average Score**: 6.24/10
- **Range**: 0.75 - 9.88 (A perfect 10 would require two handshakes and a top placing in technical. It has never been done.)
- **Star Baker Average**: 8.34/10
- **Elimination Average**: 3.89/10
- **Safe Contestant Average**: 6.56/10

### Performance Thresholds

#### Star Baker Win Rates by Performance Level
- **High Performers** (8.0+): 43.0% win rate (49/114)
- **Mid Performers** (6.0-7.9): 12.7% win rate (29/229)
- **Low Performers** (<6.0): 0.8% win rate (2/260)

#### Elimination Rates by Performance Level
- **High Performers** (8.0+): 0.9% elimination rate (1/114)
- **Mid Performers** (6.0-7.9): 1.7% elimination rate (4/229)
- **Low Performers** (<6.0): 25.8% elimination rate (67/260)

The one baker to be eliminated with a Star Baker level performance was Jurgen in Season 9.

### Elimination Patterns by Round

| Round | Eliminations | Avg Contestant Strength | Avg Elimination Performance | Performance Drop |
|-------|--------------|------------------------|----------------------------|------------------|
| 1 | 7 | 3.23 | 3.23 | 0.00 |
| 2 | 8 | 4.60 | 4.31 | 0.29 |
| 3 | 7 | 5.46 | 3.69 | 1.77 |
| 4 | 6 | 4.95 | 2.79 | 2.16 |
| 5 | 8 | 5.40 | 3.83 | 1.56 |
| 6 | 8 | 5.59 | 3.39 | 2.20 |
| 7 | 8 | 5.82 | 4.09 | 1.74 |
| 8 | 8 | 6.21 | 4.13 | 2.09 |
| 9 | 8 | 6.72 | 5.61 | 1.11 |

**Pattern Analysis**:
- **Early rounds** (1-2): Eliminate consistently weak bakers
- **Middle rounds** (3-7): Eliminate average-to-good bakers having poor performances  
- **Late rounds** (8-9): Strong bakers eliminated due to single bad performances

## Season Analysis

### Finale Predictions vs. Actual Results

#### Season 5
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Sophie*** | 7.58/10 | 49.0% | **Winner** |
| 2 | Steven | 6.72/10 | 32.0% | Finalist |
| 3 | Kate | 5.69/10 | 19.1% | Finalist |

#### Season 6
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Rahul*** | 7.17/10 | 40.7% | **Winner** |
| 2 | Kim-Joy | 6.81/10 | 33.9% | Finalist |
| 3 | Ruby | 6.22/10 | 25.4% | Finalist |

#### Season 7
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | Steph | 7.38/10 | 37.7% | Finalist |
| 2 | Alice | 7.02/10 | 31.5% | Finalist |
| 3 | **David*** | 6.97/10 | 30.8% | **Winner** |

#### Season 8
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Peter*** | 7.56/10 | 47.5% | **Winner** |
| 2 | Dave | 6.89/10 | 33.9% | Finalist |
| 3 | Laura | 5.69/10 | 18.6% | Finalist |

#### Season 9
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Giuseppe*** | 7.90/10 | 37.5% | **Winner** |
| 2 | Crystelle | 7.56/10 | 31.6% | Finalist |
| 3 | Chigs | 7.52/10 | 31.0% | Finalist |

#### Season 10
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | **Syabira*** | 7.36/10 | 43.5% | **Winner** |
| 2 | Sandro | 6.57/10 | 29.2% | Finalist |
| 3 | Abdul | 6.43/10 | 27.3% | Finalist |

#### Season 11
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | Josh | 7.19/10 | 46.7% | Finalist |
| 2 | Dan | 6.35/10 | 30.6% | Finalist |
| 3 | **Matty*** | 5.74/10 | 22.7% | **Winner** |

#### Season 12
| Rank | Contestant | Avg Strength | Win Probability | Result |
|------|------------|--------------|-----------------|---------|
| 1 | Dylan | 7.14/10 | 34.9% | Finalist |
| 2 | **Georgie*** | 7.07/10 | 33.6% | **Winner** |
| 3 | Christiaan | 6.94/10 | 31.5% | Finalist |

**Prediction Accuracy**: The model correctly predicted 5 out of 8 winners. Notable misses were David (Season 7, very close finale), Matty (Season 11, significant underperformance relative to model expectations), and Georgie (Season 12, extremely close finale).

### Winners Ranked by Strength

| Rank | Winner | Season | Avg Strength | Star Baker Wins | Handshakes |
|------|--------|--------|--------------|-----------------|------------|
| 1 | Giuseppe | 9 | 7.90/10 | 2 | 2 sig |
| 2 | Sophie | 5 | 7.58/10 | 2 | 1 sig |
| 3 | Peter | 8 | 7.56/10 | 2 | 1 sig + 1 show |
| 4 | Syabira | 10 | 7.36/10 | 3 | 1 sig |
| 5 | Rahul | 6 | 7.17/10 | 2 | 2 sig + 1 show |
| 6 | Georgie | 12 | 7.07/10 | 2 | 0 |
| 7 | David | 7 | 6.97/10 | 0 | 1 sig |
| 8 | Matty | 11 | 5.74/10 | 2 | 1 sig |

**Notable Findings**: 
- Matty ranks as the weakest winner by a significant margin
- Giuseppe shows the highest overall strength with a notable gap over second place
- David uniquely won without any Star Baker awards
- Star Bakers don't show the same strength trends as overall season strength. 

### Season Strength Rankings

| Rank | Season | Winner | Average Strength |
|------|--------|--------|------------------|
| 1 | Season 12 | Georgie | 6.73/10 |
| 2 | Season 9 | Giuseppe | 6.49/10 |
| 3 | Season 8 | Peter | 6.31/10 |
| 4 | Season 10 | Syabira | 6.20/10 |
| 5 | Season 7 | David | 6.12/10 |
| 6 | Season 6 | Rahul | 6.10/10 |
| 7 | Season 11 | Matty | 6.07/10 |
| 8 | Season 5 | Sophie | 5.90/10 |

Seasons 9 and 12 had a lot of strong Bakers. Many of those eliminated in the last few episodes (Jurgen, Gill) would have been likely finalists in weaker season,  
In general the seasons have gotten strong over the time, with the exception of Season 11. 

## Individual Excellence Rankings

### Top Non-Winners

| Rank | Contestant | Season | Avg Strength | Star Baker Wins | Handshakes | Result |
|------|------------|--------|--------------|-----------------|------------|---------|
| 1 | Jurgen | 9 | 7.85/10 | 3 | 1 sig | Semi-finalist |
| 2 | Crystelle | 9 | 7.56/10 | 2 | 1 sig + 1 show | Finalist |
| 3 | Chigs | 9 | 7.52/10 | 2 | 2 sig | Finalist |
| 4 | Gill | 12 | 7.48/10 | 1 | 0 | Semi-finalist |
| 5 | Steph | 7 | 7.38/10 | 4 | 1 sig | Finalist |
| 6 | John | 12 | 7.37/10 | 1 | 0 | R3 elimination |
| 7 | Josh | 11 | 7.19/10 | 2 | 1 show | Finalist |
| 8 | Dylan | 12 | 7.14/10 | 2 | 3 sig | Finalist |
| 9 | Dan | 6 | 7.09/10 | 1 | 3 sig | R6 elimination |
| 10 | Tasha | 11 | 7.06/10 | 2 | 1 sig | Semi-finalist |

**Key Insights**: 
- Seasons 9 and 12 dominate the top non-winner positions, with Jurgen's semi-final elimination representing a significant statistical anomaly. 
- The early eliminations of Dan and John despite strong previous performances shows that one weak performance can send you home.

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

*Overall average: 0.23*

#### Showstopper Masters
1. **Gill** (S12): 0.89 average
2. **Crystelle** (S9): 0.87 average
3. **Jurgen** (S9): 0.81 average
4. **Sophie** (S5): 0.73 average
5. **Chigs** (S9): 0.70 average

*Overall average: 0.25*

#### Flavor Excellence
1. **Crystelle** (S9): 1.00 average (perfect flavor record)
2. **Sophie** (S5): 0.95 average
3. **Gill** (S12): 0.89 average
4. **Georgie** (S12): 0.85 average
5. **Illiyin** (S12): 0.81 average

*Overall average: 0.42*

Notice that Flavor has the highest overall score, thus it's low importance. 

#### Bake Execution Excellence
1. **Crystelle** (S9): 0.77 average
2. **Gill** (S12): 0.76 average
3. **Giuseppe** (S9): 0.72 average
4. **Syabira** (S10): 0.67 average
5. **Chigs** (S9): 0.65 average

*Overall average: 0.24*

#### Visual Presentation Excellence
1. **Giuseppe** (S9): 0.90 average
2. **Christiaan** (S12): 0.80 average
3. **Syabira** (S10): 0.80 average
4. **Sumayah** (S12): 0.79 average
5. **Gill** (S12): 0.78 average

*Overall average: 0.20*

## Notable Individual Performances

### Top 5 Individual Weekly Performances
1. **Peter** S8R9: 9.88/10 (Star Baker)
2. **Giuseppe** S9R3: 9.88/10 (Star Baker)
3. **Dylan** S12R7: 9.88/10 (Star Baker)
4. **Steven** S5R7: 9.50/10 (Star Baker)
5. **Alice** S7R2: 9.50/10 (Star Baker)

*The 9.88 scores indicate perfect performance across all signature and showstopper components, first place in technical, and signature handshake receipt.*

### Bottom 5 Weekly Performances
1. **Terry** S6R5: 0.75/10 (Eliminated)
2. **Julia** S5R6: 1.02/10 (Eliminated)
3. **Sura** S8R4: 1.15/10 (Eliminated)
4. **Manon** S6R6: 1.50/10 (Safe)
5. **Dawn** S10R6: 1.60/10 (Eliminated)

### Performance Extremes
- **Strongest Non-Winner Performance**: Sura S8R1 (9.50/10)
- **Weakest Star Baker Performance**: Matty S11R10 (5.44/10)
- **Strongest Elimination Performance**: Jurgen S9R9 (8.46/10)
- **Weakest Safe Performance**: Manon S6R6 (1.50/10)

## Theme Week Analysis

Analysis of recurring theme weeks (3+ appearances) shows relative difficulty based on average performance deviation:

| Rank | Theme | Avg Difference | % Underperform | Difficulty |
|------|-------|----------------|----------------|------------|
| 1 | Chocolate | -0.84 | 58.8% | Most Difficult |
| 2 | Pastry | -0.41 | 53.6% | Difficult |
| 3 | Bread | -0.17 | 48.1% | Average |
| 4 | Celebration | -0.10 | 44.4% | Average |
| 5 | Desserts | -0.07 | 46.9% | Average |
| 6 | Final | -0.02 | 37.5% | Average |
| 7 | Temporal | +0.03 | 46.9% | Average |
| 8 | Cake | +0.04 | 46.3% | Average |
| 9 | Ethnic | +0.04 | 47.2% | Average |
| 10 | Caramel | +0.09 | 45.8% | Average |
| 11 | Ingredient | +0.16 | 46.2% | Average |
| 12 | Biscuits | +0.29 | 44.4% | Easiest |
| 13 | Patisserie | +0.33 | 43.8% | Easiest |

**Analysis**: 
 - Biscuit and Patisserie weeks show above-average performance. 
   - Biscuits are usually something made at home by the bakers. 
   - Patisserie is always the semi-final, so it seems bakers who make it that far over perform
 - Chocolate week proves most challenging with contestants averaging nearly a full point below their typical strength. 
 - Bread, despite its reputation, seems to be on the easy side of average. 

## Future Improvements

### Data Enhancement Opportunities

#### Expanded Dataset
- **Historical Seasons**: Include pre-Netflix seasons, though this may require addressing judging consistency differences

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

## Conclusions

This analysis successfully quantifies the relative importance of different baking challenges and provides a robust framework for comparing baker performance across seasons. The model's strong predictive accuracy for general performance levels validates its utility, though individual prediction challenges remain.

**Key Takeaways**:
1. Visual presentation significantly outweighs flavor in judge decision-making
2. Technical challenges carry more weight than signature bakes
3. Performance thresholds clearly differentiate star baker, safe, and elimination zones
4. Theme weeks show measurable difficulty variations aligned with technical complexity

The analysis provides a data-driven foundation for understanding judge preferences and baker evaluation, offering insights that extend beyond subjective viewing impressions.

---

*All code, input data, and output data available on GitHub. This analysis uses Netflix season numbering conventions.*