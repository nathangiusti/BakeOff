# A Data-Based Analysis of Great British Bake Off

**Note:** This data will use Netflix series numbers. I apologize in advance for those upset by this. It will also only use the Netflix seasons as the judges are consistent and I don't know what "the Roku Channel" is.

## Table of Contents
- [1. Methodology](#1-methodology)
  - [1.1 Data Gathering](#11-data-gathering)
  - [1.2 Model Weighting](#12-model-weighting)
- [2. Model Results](#2-model-results)
  - [2.1 Component Importance Weights](#21-component-importance-weights)
  - [2.2 Strength Score Definition](#22-strength-score-definition)
  - [2.3 Model Accuracy](#23-model-accuracy)
- [3. Historical Series Analysis](#3-historical-series-analysis)
  - [3.1 Series Finalists](#31-series-finalists)
  - [3.2 Series Rankings & Trends](#32-series-rankings--trends)
- [4. Individual Performance Analysis](#4-individual-performance-analysis)
  - [4.1 Series Winners](#41-series-winners)
  - [4.2 Top Non-Winners](#42-top-non-winners)
  - [4.3 Performance Outliers](#43-performance-outliers)
  - [4.4 Specialty Rankings](#44-specialty-rankings)
- [5. Theme Difficulty Analysis](#5-theme-difficulty-analysis)
- [6. Data & Resources](#6-data--resources)

---

## 1. Methodology

### 1.1 Data Gathering

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

### 1.2 Model Weighting

Using the data gathered, I use a logistic regression model to determine the relative importance of each component. The model analyzes the relationship between bake scores and final judge reviews, specifically the post-showstopper discussion and camera focus during the Star Baker and elimination announcements.

More information on the math can be found on [Wikipedia](https://en.wikipedia.org/wiki/Logistic_regression).

**Note:** I tried incorporating reviews done after the first half, as well as weighting star bakers/eliminated contestants more heavily, but none of these provided meaningful gains in accuracy for the complexity it added to the model.

---

## 2. Model Results

### 2.1 Component Importance Weights

#### Bake Importance (Total Weight)

| Rank | Bake Group | Weight | Percentage |
|------|------------|--------|------------|
| 1 | Showstopper Bake | 4.396 | 43.5% |
| 2 | Technical Challenge | 3.264 | 32.3% |
| 3 | Signature Bake | 2.446 | 24.2% |


Signature is about 1/4 of your score, tech is 1/3 of your score, and the rest is showstopper.

#### Signature Bake Components

| Component | Weight | Mean | Variance | %-1 | %0 | %+1 |
|-----------|--------|------|----------|-----|----|----|
| Signature Looks | 0.801 | 0.26 | 0.724 | 26.5% | 20.9% | 52.5% |
| Signature Bake | 0.743 | 0.14 | 0.783 | 33.2% | 19.9% | 46.9% |
| Signature Handshake | 0.579 | N/A | N/A | N/A | 93.5% | 6.5% |
| Signature Flavor | 0.323 | 0.53 | 0.604 | 17.7% | 11.4% | 70.9% |

Looks matter more than bake or flavor, although not as much as both combined. Flavor comes in as the least important aspect. Flavor is generally the area people score best in with 70% of signature bakes receiving generally positive flavor comments. This may account for its low importance.

It is assumed if you got a handshake, all other components received positive scores, so the handshake component is measuring the difference between an excellent bake without a handshake and an excellent bake with a handshake.

#### Showstopper Bake Components

| Component | Weight | Mean | Variance | %-1 | %0 | %+1 |
|-----------|--------|------|----------|-----|----|----|
| Showstopper Flavor | 1.555 | 0.52 | 0.622 | 18.6% | 10.6% | 70.8% |
| Showstopper Looks | 1.502 | 0.40 | 0.685 | 22.3% | 15.9% | 61.8% |
| Showstopper Bake | 1.080 | 0.24 | 0.784 | 30.1% | 16.1% | 53.8% |
| Showstopper Handshake | 0.259 | N/A | N/A | N/A | 98.4% | 1.5% |

The showstopper shows the same patterns with looks mattering more than either flavor or bake but not both together. Handshakes are much lower here because of how rare they are. Handshakes are received by 7% of signature bakes, but only 1.5% of showstopper bakes. Flavor is also drastically more important in the showstopper despite similar patterns in scores to the signature.

### 2.2 Strength Score Definition

From these components and strengths I have put together a 0-10 scale for how each baker did in a given week. -1's in all components and last in technical would grant a score of 0, while two handshakes, plus first in technical would be a 10. I call this a strength score.

The average strength score is 6.29. The lowest strength score ever received was Terry in S6E5 with a 0.73. The highest score ever achieved was 9.85, which is a handshake signature, first in technical, and a strong showstopper. This has been achieved three times: Peter S8R9, Giuseppe S9R3, and Dylan S12R7.

### 2.3 Model Accuracy

Given a baker's strength score we predict whether they were a favorite or up for elimination with 93% accuracy.

The highest strength score of the week wins star baker about 66% of the time. The lowest score is eliminated 55% of the time.

---

## 3. Historical Series Analysis

Everything that comes after this is based on the above assumptions about relative bake importance. All data is complete through Series 13.

### 3.1 Series Finalists

#### Series 5 (Winner: Sophie)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Sophie | 7.64/10 | 7.67/10 | ✓ |
| 2 | Steven | 6.76/10 | 4.64/10 | |
| 3 | Kate | 5.75/10 | 7.58/10 | |

#### Series 6 (Winner: Rahul)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Rahul | 7.22/10 | 7.55/10 | ✓ |
| 2 | Kim-Joy | 6.87/10 | 6.27/10 | |
| 3 | Ruby | 6.23/10 | 4.95/10 | |

#### Series 7 (Winner: David)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Steph | 7.42/10 | 3.81/10 | |
| 2 | Alice | 7.03/10 | 7.41/10 | |
| 3 | David | 6.99/10 | 9.12/10 | ✓ |

Poor Steph. The clear favorite and then imploding in the finale while David shocked turning in an amazing performance to seal it.

#### Series 8 (Winner: Peter)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Peter | 7.59/10 | 8.70/10 | ✓ |
| 2 | Dave | 6.94/10 | 7.91/10 | |
| 3 | Laura | 5.76/10 | 3.83/10 | |

#### Series 9 (Winner: Giuseppe)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Giuseppe | 7.92/10 | 6.70/10 | ✓ |
| 2 | Crystelle | 7.65/10 | 6.85/10 | |
| 3 | Chigs | 7.56/10 | 7.67/10 | |

The model suggests Chigs delivered the best finale performance, but in a close episode, Giuseppe's season-long dominance may have put him ahead.

#### Series 10 (Winner: Syabira)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Syabira | 7.36/10 | 7.66/10 | ✓ |
| 2 | Sandro | 6.57/10 | 3.66/10 | |
| 3 | Abdul | 6.49/10 | 4.60/10 | |

#### Series 11 (Winner: Matty)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Josh | 7.22/10 | 7.06/10 | |
| 2 | Dan | 6.38/10 | 4.31/10 | |
| 3 | Matty | 5.81/10 | 5.56/10 | ✓ |

The model rates Matty as a below-average baker with a below-average finale performance who won against statistically stronger contestants.

#### Series 12 (Winner: Georgie)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Dylan | 7.17/10 | 3.22/10 | |
| 2 | Georgie | 7.13/10 | 7.16/10 | ✓ |
| 3 | Christiaan | 6.96/10 | 6.88/10 | |

#### Series 13 (Winner: Jasmine)

| Rank | Baker | Avg Score | Final Score | Winner |
|------|-------|-----------|-------------|--------|
| 1 | Jasmine | 8.11/10 | 6.63/10 | ✓ |
| 2 | Tom | 7.26/10 | 8.63/10 | |
| 3 | Aaron | 6.09/10 | 4.12/10 | |

Jasmine was the dominant favorite, winning five star baker titles, the most of any baker in the dataset. Tom turned in the best finale of the three, but Jasmine's season-long strength carried her.

### 3.2 Series Rankings & Trends

#### Series Ranked by Overall Average Strength

1. Series 12 (Winner: Georgie): 6.78/10 avg (74 performances)
2. Series 9 (Winner: Giuseppe): 6.53/10 avg (75 performances)
3. Series 13 (Winner: Jasmine): 6.42/10 avg (75 performances)
4. Series 8 (Winner: Peter): 6.35/10 avg (75 performances)
5. Series 10 (Winner: Syabira): 6.23/10 avg (74 performances)
6. Series 7 (Winner: David): 6.15/10 avg (80 performances)
7. Series 6 (Winner: Rahul): 6.12/10 avg (75 performances)
8. Series 11 (Winner: Matty): 6.11/10 avg (75 performances)
9. Series 5 (Winner: Sophie): 5.93/10 avg (75 performances)

Series 11 seems to be the odd one out in a general pattern of stronger bakers over time.

---

## 4. Individual Performance Analysis

### 4.1 Series Winners

#### Series Winners (by average strength)

1. Jasmine (S13): 8.11/10 avg (5 star baker wins, 1 show handshakes)
2. Giuseppe (S9): 7.92/10 avg (2 star baker wins, 2 sig handshakes)
3. Sophie (S5): 7.64/10 avg (2 star baker wins, 1 sig handshakes)
4. Peter (S8): 7.59/10 avg (2 star baker wins, 1 sig + 1 show handshakes)
5. Syabira (S10): 7.36/10 avg (3 star baker wins, 1 sig handshakes)
6. Rahul (S6): 7.22/10 avg (2 star baker wins, 2 sig + 1 show handshakes)
7. Georgie (S12): 7.13/10 avg (2 star baker wins)
8. David (S7): 6.99/10 avg (0 star baker wins, 1 sig handshakes)
9. Matty (S11): 5.81/10 avg (2 star baker wins, 1 sig handshakes)

The gap between Matty and the next best series winner (David) is larger than the gap between David and the strongest baker in Bake Off history (Jasmine).

### 4.2 Top Non-Winners

#### Top Non-Series-Winners (by average strength)

1. Jurgen (S9): 7.89/10 avg (3 wins, 1 sig handshakes, semifinalist)
2. Crystelle (S9): 7.65/10 avg (2 wins, 1 sig + 1 show handshakes, finalist)
3. Chigs (S9): 7.56/10 avg (2 wins, 2 sig handshakes, finalist)
4. Gill (S12): 7.55/10 avg (1 win, semifinalist)
5. John (S12): 7.43/10 avg (1 win, R3 elimination)
6. Steph (S7): 7.42/10 avg (4 wins, 1 sig handshakes, finalist)
7. Tom (S13): 7.26/10 avg (1 win, 1 sig + 1 show handshakes, finalist)
8. Josh (S11): 7.22/10 avg (2 wins, 1 show handshakes, finalist)
9. Dylan (S12): 7.17/10 avg (2 wins, 3 sig handshakes, finalist)
10. Tasha (S11): 7.12/10 avg (2 wins, 1 sig handshakes, semifinalist)

Season 9 with Jurgen, Crystelle, Chigs, and Giuseppe was ridiculously stacked. Any of them would have finished as a very strong series champion, with Giuseppe as the second strongest baker of all time behind only Jasmine.

Season 11 looks pretty weak in comparison with Matty being the weakest series winner. But even the strongest Season 11 competitor, Josh, would have been a middling champion.

### 4.3 Performance Outliers

- **Strongest non-winner:** Sura S8R1 (9.51/10)
- **Weakest star baker:** Matty S11R10 (5.56/10)
- **Strongest elimination:** Jurgen S9R9 (8.43/10)
- **Weakest safe contestant:** Manon S6R6 (1.46/10)

Matty's finale performance was the worst performance by any episode winner. Jurgen's semifinal elimination was the best performance to have resulted in elimination from the competition.

Manon survived a disastrous week 6 performance somehow resulting in the elimination of Dan instead who seemed to have outperformed her that week and over the course of the competition to that point.

### 4.4 Specialty Rankings

#### Who is the flavor/bake/technical/signature/showstopper king/queen?

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
2. Jasmine (S13): 0.70 avg signature score
3. Kim-Joy (S6): 0.70 avg signature score
4. Syabira (S10): 0.70 avg signature score
5. Crystelle (S9): 0.67 avg signature score

*Overall average (all bakers): 0.23*

#### Highest Average Showstopper

1. Gill (S12): 0.89 avg showstopper score
2. Crystelle (S9): 0.87 avg showstopper score
3. Jasmine (S13): 0.87 avg showstopper score
4. Jurgen (S9): 0.81 avg showstopper score
5. Lesley (S13): 0.81 avg showstopper score

*Overall average (all bakers): 0.27*

#### Highest Average Flavor

1. Crystelle (S9): 1.00 avg flavor score
2. Sophie (S5): 0.95 avg flavor score
3. Jasmine (S13): 0.90 avg flavor score
4. Gill (S12): 0.89 avg flavor score
5. Georgie (S12): 0.85 avg flavor score

*Overall average (all bakers): 0.43*

Crystelle got positive reviews on flavor in every one of her bakes. FLAVOR QUEEN!
Sophie, the only contestant from S5 to appear in any of these rankings at 2.
Jasmine takes the bronze, followed by two bakers from S12.

#### Highest Average Bake

1. Jasmine (S13): 0.78 avg bake score
2. Crystelle (S9): 0.77 avg bake score
3. Gill (S12): 0.76 avg bake score
4. Giuseppe (S9): 0.72 avg bake score
5. Syabira (S10): 0.67 avg bake score

*Overall average (all bakers): 0.25*

#### Highest Average Looks

1. Giuseppe (S9): 0.90 avg looks score
2. Jasmine (S13): 0.85 avg looks score
3. Christiaan (S12): 0.80 avg looks score
4. Syabira (S10): 0.80 avg looks score
5. Tom (S13): 0.80 avg looks score

*Overall average (all bakers): 0.20*

Giuseppe wasn't quite perfect in looks, but darn close enough, especially for being in the category with the lowest average score.

---

## 5. Theme Difficulty Analysis

I also pulled all the episode titles from Wikipedia and looked for patterns where bakers under- or over-performed compared to their average.

| Rank | Theme | Avg Diff | % Under | Count | Difficulty |
|------|-------|----------|---------|-------|------------|
| 1 | Chocolate | -0.36 | 48.0% | 25 | Hard |
| 2 | Pastry | -0.35 | 50.8% | 63 | Hard |
| 3 | Bread | -0.16 | 46.1% | 89 | Average |
| 4 | Celebration | -0.13 | 44.4% | 18 | Average |
| 5 | Desserts | -0.09 | 46.3% | 54 | Average |
| 6 | Temporal | -0.03 | 46.3% | 41 | Average |
| 7 | Cake | -0.00 | 47.7% | 107 | Average |
| 8 | Final | +0.01 | 40.7% | 27 | Average |
| 9 | Ethnic | +0.04 | 47.2% | 36 | Average |
| 10 | Caramel | +0.07 | 45.8% | 24 | Average |
| 11 | Ingredient | +0.11 | 46.2% | 39 | Average |
| 12 | Biscuits | +0.26 | 44.6% | 101 | Easy |
| 13 | Patisserie | +0.27 | 47.2% | 36 | Easy |

I grouped several one-off weeks into groups like ingredients (Pudding, Spice, Vegan, etc.), temporal (The 20's, The 80's, etc.), or ethnic (Japanese, German, etc.). You can see the mappings [here](data_collection/scraping/gbbo_episodes.csv)

In chocolate, the most difficult theme, about half of contestants perform below their average. Pastry is a close second, and Bread comes in on the slightly harder part of average. Patisserie, the semi-final, actually comes up as the easiest. Remember this is the difference of a baker from their average, so already strong bakers who make it to the semi-final, still tend to exceed expectations.

---

## 6. Data & Resources

### Source Data
The human-graded data used to train the model is available in [data.csv](data_collection/judging/human/data.csv).

### Analysis Outputs
- **[GBBO Complete Analysis](analysis/reports/gbbo_complete_analysis.csv)** - Weekly strength scores and results for each contestant in every episode
- **[GBBO Contestant Summary](analysis/reports/gbbo_complete_analysis_contestant_summary.csv)** - Aggregated statistics per contestant (the Complete Analysis file rolled up to the contestant level)
- **[GBBO Results](analysis/reports/gbbo_results.csv)** - Contestant performance data scraped from Wikipedia

### Predictions & Historical Analysis
Week-by-week analysis for past seasons is available in the [season markdown directory](output/season_markdown).
