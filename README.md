# Machine Learning All-NBA Awards Predictions
Computational Data Science final project

## Requirements
- nba_api (https://github.com/swar/nba_api)
- pandas
- unicodedata
- numpy
- Scikit-learn
- matplotlib
- seaborn

### Notes
The following directories must exist before running the programs
- data
  - data/raw
  - data/clean
  - data/final
  - data/predictions

### Running the programs
All directory/file names are hard-coded so there are no command-line arguments required.\
The programs can be run in the following order (or in any order as long as the listed files below exist before running a given program).
- **1-get_data.py**
  - data/raw
  - No files required

- **2-remove_irrelevant_columns.py**
  - data/raw/
    - player_stats.csv
    - team_stats.csv
  - data/clean

- **3-calculate_additional_stats.py**
  - data/clean/
    - player_stats_clean.csv
    - team_stats_clean.csv
 
- **4-clean_allNBA_teams_data.py**
  - data/raw/
    - allNBA_teams.csv
  - data/clean
 
- **5-finalize_training_data.py**
  - data/clean/
    - player_stats_clean.csv
    - additional_player_stats.csv
    - allNBA_teams_clean.csv
  - data/final
 
- **6-make_predictions.py**
  - data/final/
    - player_stats_training.csv
    - player_stats_2022-23.csv
    - player_stats_2023-24.csv
  - data/predictions
