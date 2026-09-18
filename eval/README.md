# What are in this folder?

This folder contains the data and analysis for the system ablation test.

## Folder Guide
1. logs/ - raw data folder, contains logged run1 interactions (.jsonl) in multi/multi_verifier/single conditions.
2. plots/ - plots folder, contains plots from the ablation test [analysis](https://github.com/11awrence/socratic-tutoring-system/blob/main/eval/analysis.ipynb).
3. Trajectory_Design.pdf - PDF file, contains strong/average/struggling student trajectories.
4. analysis.ipynb - script for the analysis of scored student trajectories.
5. disagreement.csv - scored two run2 trajectories that observed strong disagreement with the corresponding run1 trajectories.
6. extract_turns.py - helper to convert raw data (.jsonl) to CSV for scoring and analysis.
7. multi_scored.csv - scored trajectories for multi-agent condition based on the scoring rubric.
8. multi_verifier_scored.csv - scored trajectories for multi-agent + verifier condition based on the scoring rubric.
9. single_scored.csv - scored trajectories for single-agent condition based on the scoring rubric.

## Additional Notes
- Primary results use run1 only (30 trajectories × 3 conditions).
- Run2 is a stability check; only two strong disagreements are scored in `disagreement.csv`. Raw run2 jsonl were not in this folder.
- Re-extract run1: `python extract_turns.py` 
- Scored CSVs use `;` as the separator.