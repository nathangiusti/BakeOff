"""
Main entry point for GBBO analysis.

Run this script to perform the complete Great British Bake Off analysis.

IMPLEMENTATION NOTES:
- First half reviews were tested for integration but showed no accuracy improvement
- Two approaches were tested: adding reviews as features and two-model ensemble
- Both approaches performed worse than the integrated single-model approach
- The current system uses only second half review predictions which capture
  all necessary information from signature, technical, and showstopper challenges
- Theme performance analysis identifies which episode themes cause bakers to excel or struggle
"""

from gbbo_analysis import GBBOAnalyzer


def main():
    """Main function that runs the complete analysis"""
    analyzer = GBBOAnalyzer()
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()