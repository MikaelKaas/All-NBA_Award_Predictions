# combine and filter down data to only columns we want
# create seperate 2022-2023 file
# remove invalid players from data (not enough GP...)
# deal with potential NaN values?
import pandas as pd

IN_DIRECTORY = 'data/'
OUT_DIRECTORY = 'data/final/'

FINAL_COLUMNS = [
    'SEASON',
    'PLAYER_NAME'
    'PLAYER_ID',
    # ...
]

def main():
    playerStats = pd.read_csv(IN_DIRECTORY + 'clean/player_stats_clean.csv')
    additionalStats = pd.read_csv(IN_DIRECTORY + 'clean/additional_player_stats.csv')
    allNBAteams = pd.read_csv(IN_DIRECTORY + 'allNBA_teams.csv')

    # merge...

    # clean...


    playerStats.to_csv(OUT_DIRECTORY + 'player_stats_final.csv')

if __name__ == '__main__':
    main()