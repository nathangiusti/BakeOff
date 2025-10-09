Parse the given transcripts from The Great British Baking Show.

  ## Judges
  - Paul Hollywood and Prue Leith are the judges
  - Only analyze dialogue from [Paul] and [Prue] speaker tags
  - This is a British show - be aware of British slang and terminology
  - Sometimes speaker tags will be missing, and must be inferred based on language that sounds like judging.
  - Alert if contestant names do not match previous episodes in the season.

  ## Episode Structure
  Each episode contains judging for TWO bakes:
  1. **Signature Bake**: Bakers are not often not explicitly introduced; When missing, the bakers name will be placed at the top of the section. 
  2. **Showstopper Bake**: Each baker is usually introduced by name (e.g., "Sophie, please bring up your cake"). It will be marked if not. 

  Assume all judge dialogue between a baker's introduction and the next baker's introduction pertains to that contestant.

  **End of Episode Summary**: After all judging is complete, the judges discuss the bakers and their performance. Use this discussion to adjust scores if necessary - it provides overall context on how the judges truly felt about each baker's bakes.

  ## Scoring Categories
  The judges comment on three aspects. Score each independently:

  ### 1. Looks/Appearance
  - Positive indicators: "stunning", "beautiful", "neat", "professional", "striking", "uniform"
  - Negative indicators: "rustic", "rough and ready", "messy", "basic", "simplistic"

  ### 2. Flavor/Taste
  - Comments on taste, flavor balance, sweetness, spice levels
  - Positive: "delicious", "perfect", "lovely flavour", "well-balanced", "I'll have another piece"
  - Negative: "bland", "overpowering", "tastes like toothpaste", "too sweet"

  ### 3. Bake/Execution
  - Texture, cooking doneness, structural integrity
  - Positive: "perfectly baked", "lovely texture", "moist", "light", "well done"
  - Negative: "stodgy", "claggy", "soggy bottom", "underbaked", "overbaked", "dry", "dense", "collapsed", "underproved", "overproved"

  ### Additional British Phrases to Watch For:
  **Positive (often understated):**
  - "That's not bad at all", "You've got away with it", "I think it's lovely"
  - Paul Hollywood handshake = exceptional, consider as strong positive signal

  **Negative (often polite):**
  - "It's a shame about...", "Unfortunately...", "I'm not convinced"
  - "It could have been better", "Not quite there"

  ## Scoring Scale
  For each category, assign:
  - **1.0**: Strongly positive (enthusiastic praise, no negatives mentioned)
  - **0.5**: Generally positive with minor critiques
  - **0.0**: Mixed feedback, neutral, or not mentioned
  - **-0.5**: Generally negative with minor positives
  - **-1.0**: Strongly negative (harsh criticism, no positives mentioned)

  ### Scoring Guidelines:
  - When judges disagree, average their sentiments
  - If only one judge comments on a category, assume the other agrees
  - Summative statements (e.g., "Well done", "Overall, I'm disappointed") should be used to:
    - Resolve scores that fall between two scale values
    - Infer missing categories if the statement seems sincere (e.g., "This is stunning" without specific flavor mention can imply positive flavor)
  - Ignore host commentary and baker interviews
  - If a baker doesn't present a bake, use empty/null values
  - Contestants often say thank you to the judges. Judges will often say this out of politeness to the contestant. 

  ## Output Format
  Add each row of data to claude_judging.csv

  