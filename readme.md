# A Data-Based Analysis of Great British Bake Off

**Note:** This data will use Netflix series numbers. I apologize in advance for those upset by this. It will also only use the Netflix seasons as the judges are consistent and I don't know what "the Roku Channel" is.

## Data Gathering

Each episode is composed of the signature, technical, and showstopper bakes.

I have broken the signature and showstopper bakes into three components:

1. Bake - Includes texture and execution
2. Flavor - Does it taste good?
3. Looks

I rewatched each episode and for the signature and showstopper bakes assigned the following scores for each component:

1. 1 - Generally positive reviews
2. 0 - Mixed reviews/not mentioned
3. -1 - Generally negative reviews

I have also tracked handshakes received in the signature and showstopper bakes.

I pulled technical scores and high/low reviews and star bakers/eliminations from Wikipedia.

To create a more uniform grading experience, I ran various show transcripts through an LLM to do grading, but the LLM's grading proved to have lower accuracy than human grading.

## Model Weighting

Using the data gathered, I use a logistic regression model to determine the relative importance of each component. The model analyzes the relationship between bake scores and final judge reviews, specifically the post-showstopper discussion and camera focus during the Star Baker and elimination announcements.

More information on the math can be found on [Wikipedia](https://en.wikipedia.org/wiki/Logistic_regression).

**Note:** I tried incorporating reviews done after the first half, as well as weighting star bakers/eliminated contestants more heavily, but none of these provided meaningful gains in accuracy for the complexity it added to the model.

## Results - Component baking scores

### Bake Importance (Total Weight)

1. Showstopper Bake: 4.012 (42.0%)
2. Technical Challenge: 3.176 (33.3%)
3. Signature Bake: 2.361 (24.7%)

Signature is about 1/4 of your score, tech is 1/3 of your score, and the rest is showstopper.

### Signature Bake Components

| Component | Weight | Mean | Variance | %-1 | %0 | %+1 |
|-----------|--------|------|----------|-----|-------|-----|
| Signature Looks | 0.816 | 0.24 | 0.729 | 27.2 | 21.4 | 51.4 |
| Signature Bake | 0.691 | 0.17 | 0.775 | 31.7 | 19.7 | 48.6 |
| Signature Handshake | 0.614 | N/A | N/A | N/A | 93.0 | 7.0 |
| Signature Flavor | 0.240 | 0.53 | 0.602 | 17.6 | 11.9 | 70.5 |

Looks matter more than bake or flavor, although not as much as both combined. Flavor comes in as the least important aspect. Flavor is generally the area people score best in with 70% of signature bakes receiving generally positive flavor comments. This may account for its low importance. 

It is assumed if you got a handshake, all other components received positive scores, so the handshake component is measuring the difference between an excellent bake without a handshake and an excellent bake with a handshake.

### Showstopper Bake Components

| Component | Weight | Mean | Variance | %-1 | %0 | %+1 |
|-----------|--------|------|----------|-----|-------|-----|
| Showstopper Looks | 1.411 | 0.39 | 0.686 | 22.4 | 16.4 | 61.2 |
| Showstopper Flavor | 1.362 | 0.51 | 0.639 | 19.4 | 10.1 | 70.5 |
| Showstopper Bake | 1.050 | 0.23 | 0.798 | 31.0 | 15.1 | 53.9 |
| Showstopper Handshake | 0.188 | N/A | N/A | N/A | 98.5 | 1.3 |

The showstopper shows the same patterns with looks mattering more than either flavor or bake but not both together. Handshakes are much lower here because of how rare they are. Handshakes are received by 7% of signature bakes, but only 1% of showstopper bakes. Flavor is also drastically more important in the showstopper despite similar patterns in scores to the signature.

## Strength Score

From these components and strengths I have put together a 0-10 scale for how each baker did in a given week. -1's in all components and last in technical would grant a score of 0, while two handshakes, plus first in technical would be a 10. I call this a strength score.

The average strength score is 6.24. The lowest strength score ever received was Terry in S6E5 with a 0.75. The highest score ever achieved was 9.88, which is a handshake signature, first in technical, and a strong showstopper. This has been achieved three times: Peter S8R9, Giuseppe S9R3, and Dylan S12R8.

## Accuracy

Given a baker's strength score we predict whether they were a favorite or up for elimination with 92% accuracy.

The highest strength score of the week wins star baker about 62% of the time. The lowest score is eliminated 57% of the time.

## Analysis

Everything that comes after this is based on the above assumptions about relative bake importance. Series 13 data will be added after the conclusion of that season.

### Series Finalists Analysis

#### Series 5 (Winner: Sophie)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Sophie | 7.58/10 | 7.63/10 | ✓ |
| 2 | Steven | 6.72/10 | 4.51/10 | |
| 3 | Kate | 5.69/10 | 7.50/10 | |

#### Series 6 (Winner: Rahul)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Rahul | 7.17/10 | 7.59/10 | ✓ |
| 2 | Kim-Joy | 6.81/10 | 6.24/10 | |
| 3 | Ruby | 6.22/10 | 4.92/10 | |

#### Series 7 (Winner: David)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Steph | 7.38/10 | 3.78/10 | |
| 2 | Alice | 7.02/10 | 7.32/10 | |
| 3 | David | 6.97/10 | 9.19/10 | ✓ |

Poor Steph. The clear favorite and then imploding in the finale while David shocked turning in an amazing performance to seal it. 

#### Series 8 (Winner: Peter)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Peter | 7.56/10 | 8.62/10 | ✓ |
| 2 | Dave | 6.89/10 | 7.78/10 | |
| 3 | Laura | 5.69/10 | 3.72/10 | |

#### Series 9 (Winner: Giuseppe)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Giuseppe | 7.90/10 | 6.63/10 | ✓ |
| 2 | Crystelle | 7.56/10 | 6.72/10 | |
| 3 | Chigs | 7.52/10 | 7.63/10 | |

The model suggests Chigs delivered the best finale performance, but in a close episode, Giuseppe's season-long dominance may have put him ahead.  

#### Series 10 (Winner: Syabira)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Syabira | 7.36/10 | 7.61/10 | ✓ |
| 2 | Sandro | 6.57/10 | 3.54/10 | |
| 3 | Abdul | 6.43/10 | 4.52/10 | |

#### Series 11 (Winner: Matty)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Josh | 7.19/10 | 7.09/10 | |
| 2 | Dan | 6.35/10 | 4.17/10 | |
| 3 | Matty | 5.74/10 | 5.44/10 | ✓ |

The model rates Matty as a below-average baker with a below-average finale performance who won against statistically stronger contestants. 

#### Series 12 (Winner: Georgie)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Dylan | 7.14/10 | 3.10/10 | |
| 2 | Georgie | 7.07/10 | 7.04/10 | ✓ |
| 3 | Christiaan | 6.94/10 | 6.89/10 | |

### Series Ranked by Overall Average Strength

1. Series 12 (Winner: Georgie): 6.73/10 avg (74 performances)
2. Series 9 (Winner: Giuseppe): 6.49/10 avg (75 performances)
3. Series 8 (Winner: Peter): 6.31/10 avg (75 performances)
4. Series 10 (Winner: Syabira): 6.20/10 avg (74 performances)
5. Series 7 (Winner: David): 6.12/10 avg (80 performances)
6. Series 6 (Winner: Rahul): 6.10/10 avg (75 performances)
7. Series 11 (Winner: Matty): 6.07/10 avg (75 performances)
8. Series 5 (Winner: Sophie): 5.90/10 avg (75 performances)

Series 11 seems to be the odd one out in a general pattern of stronger bakers over time.

### Series Winners (by average strength)

1. Giuseppe (S9): 7.90/10 avg (2 star baker wins, 2 sig handshakes)
2. Sophie (S5): 7.58/10 avg (2 star baker wins, 1 sig handshakes)
3. Peter (S8): 7.56/10 avg (2 star baker wins, 1 sig + 1 show handshakes)
4. Syabira (S10): 7.36/10 avg (3 star baker wins, 1 sig handshakes)
5. Rahul (S6): 7.17/10 avg (2 star baker wins, 2 sig + 1 show handshakes)
6. Georgie (S12): 7.07/10 avg (2 star baker wins)
7. David (S7): 6.97/10 avg (0 star baker wins, 1 sig handshakes)
8. Matty (S11): 5.74/10 avg (2 star baker wins, 1 sig handshakes)

The gap between Matty and the next best series winner (David) is larger than the gap between David and the strongest baker in Bake Off history (Giuseppe).

### Top Non-Series-Winners (by average strength)

1. Jurgen (S9): 7.85/10 avg (3 wins, 1 sig handshakes, semifinalist)
2. Crystelle (S9): 7.56/10 avg (2 wins, 1 sig + 1 show handshakes, finalist)
3. Chigs (S9): 7.52/10 avg (2 wins, 2 sig handshakes, finalist)
4. Gill (S12): 7.48/10 avg (1 win, semifinalist)
5. Steph (S7): 7.38/10 avg (4 wins, 1 sig handshakes, finalist)
6. John (S12): 7.37/10 avg (1 win, R3 elimination)
7. Josh (S11): 7.19/10 avg (2 wins, 1 show handshakes, finalist)
8. Dylan (S12): 7.14/10 avg (2 wins, 3 sig handshakes, finalist)
9. Dan (S6): 7.09/10 avg (1 win, 3 sig handshakes, R6 elimination)
10. Tasha (S11): 7.06/10 avg (2 wins, 1 sig handshakes, semifinalist)

Season 9 with Jurgen, Crystelle, Chigs, and Giuseppe was ridiculously stacked. Any of them would have finished as a very strong series champion, with Giuseppe as the strongest baker of all time.

Season 11 looks pretty weak in comparison with Matty being the weakest series winner. But even the strongest Season 11 competitor, Josh, would have been a middling champion.

## Performance Outliers

- **Strongest non-winner:** Sura S8R1 (9.50/10)
- **Weakest star baker:** Matty S11R10 (5.44/10)
- **Strongest elimination:** Jurgen S9R9 (8.46/10)
- **Weakest safe contestant:** Manon S6R6 (1.50/10)

Matty's finale performance was the worst performance by any episode winner. Jurgen's semifinal elimination was the best performance to have resulted in elimination from the competition.

Manon survived a disastrous week 6 performance somehow resulting in the elimination of Dan instead who seemed to have outperformed her that week and over the course of the competition to that point. 

### Who is the flavor/bake/technical/signature/showstopper king/queen?

**Note:** Only quarterfinalists and above are included. Scores go from -1 to 1.

#### Highest Average Technical

1. Jurgen (S9): 0.75 avg technical score
2. David (S7): 0.72 avg technical score
3. Peter (S8): 0.69 avg technical score
4. Sophie (S5): 0.68 avg technical score
5. Jon (S6): 0.67 avg technical score

Since technicals are ranked, the average score for technical scores is always 0. 

#### Highest Average Signature

1. Giuseppe (S9): 0.77 avg signature score
2. Kim-Joy (S6): 0.70 avg signature score
3. Syabira (S10): 0.70 avg signature score
4. Crystelle (S9): 0.67 avg signature score
5. Steph (S7): 0.63 avg signature score

*Overall average (all bakers): 0.23*

#### Highest Average Showstopper

1. Gill (S12): 0.89 avg showstopper score
2. Crystelle (S9): 0.87 avg showstopper score
3. Jurgen (S9): 0.81 avg showstopper score
4. Sophie (S5): 0.73 avg showstopper score
5. Chigs (S9): 0.70 avg showstopper score

*Overall average (all bakers): 0.25*

#### Highest Average Flavor

1. Crystelle (S9): 1.00 avg flavor score
2. Sophie (S5): 0.95 avg flavor score
3. Gill (S12): 0.89 avg flavor score
4. Georgie (S12): 0.85 avg flavor score
5. Illiyin (S12): 0.81 avg flavor score

*Overall average (all bakers): 0.42*

Crystelle got positive reviews on flavor in every one of her bakes. FLAVOR QUEEN!
Sophie, the only contestant from S5 to appear in any of these rankings at 2. 
And then 3-5 filled by the women from S12. 

#### Highest Average Bake

1. Crystelle (S9): 0.77 avg bake score
2. Gill (S12): 0.76 avg bake score
3. Giuseppe (S9): 0.72 avg bake score
4. Syabira (S10): 0.67 avg bake score
5. Chigs (S9): 0.65 avg bake score

*Overall average (all bakers): 0.24*

#### Highest Average Looks

1. Giuseppe (S9): 0.90 avg looks score
2. Christiaan (S12): 0.80 avg looks score
3. Syabira (S10): 0.80 avg looks score
4. Sumayah (S12): 0.79 avg looks score
5. Gill (S12): 0.78 avg looks score

*Overall average (all bakers): 0.20*

Giuseppe wasn't quite perfect in looks, but darn close enough, especially for being in the category with the lowest average score.

## Theme Analysis

I also pulled all the episode titles from Wikipedia and looked for patterns where bakers under- or over-performed compared to their average.

| Rank | Theme | Avg Diff | % Under | Count | Difficulty |
|------|-------|----------|---------|-------|------------|
| 1 | Chocolate | -0.84 | 58.8% | 17 | Very Hard |
| 2 | Pastry | -0.41 | 53.6% | 56 | Hard |
| 3 | Bread | -0.17 | 48.1% | 79 | Average |
| 4 | Celebration | -0.10 | 44.4% | 18 | Average |
| 5 | Desserts | -0.07 | 46.9% | 49 | Average |
| 6 | Final | -0.02 | 37.5% | 24 | Average |
| 7 | Temporal | +0.03 | 46.9% | 32 | Average |
| 8 | Cake | +0.04 | 46.3% | 95 | Average |
| 9 | Ethnic | +0.04 | 47.2% | 36 | Average |
| 10 | Caramel | +0.09 | 45.8% | 24 | Average |
| 11 | Ingredient | +0.16 | 46.2% | 39 | Average |
| 12 | Biscuits | +0.29 | 44.4% | 90 | Easy |
| 13 | Patisserie | +0.33 | 43.8% | 32 | Easy |

I grouped several one-off weeks into groups like ingredients (Pudding, Spice, Vegan, etc.), temporal (The 20's, The 80's, etc.), or ethnic (Japanese, German, etc.). You can see the mappings [here](data_collection/scraping/gbbo_episodes.csv)

In chocolate, the most difficult theme, almost 60% of contestants perform below their average. Bread comes in on the slightly harder part of average. Patisserie, the semi-final, actually comes up as the easiest. Remember this is the difference of a baker from their average, so already strong bakers who make it to the semi-final, still tend to exceed expectations. 

## Data in GitHub

The human graded data used to train the model is in [data.csv](data_collection/judging/human/data.csv).

[GBBO Complete Analysis](analysis/reports/gbbo_complete_analysis.csv) contains the weekly strength score and result for each contestant each episode. 

[GBBO Contestant Summary](analysis/reports/gbbo_complete_analysis_contestant_summary.csv) contains summary data for each contestant. It's like the GBBO Complete Analysis file rolled up to the contestant level. 

[GBBO Results](analysis/reports/gbbo_results.csv) contains contestant performance data pulled from Wikipedia. 

Week by week analysis for past seasons is [also available](monte_carlo/predictions_output/season_markdown). 
