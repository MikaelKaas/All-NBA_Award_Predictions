# combine and filter down data to only columns we want
# create seperate 2022-2023 file
# remove invalid players from data (not enough GP...)
# deal with potential NaN values?
import pandas as pd

IN_DIRECTORY = 'data/final/'
OUT_DIRECTORY = 'data/final/'

def main():
    playerStats = pd.read_csv(IN_DIRECTORY + 'player_stats_clean.csv')
    additionalStats = pd.read_csv(IN_DIRECTORY + 'additional_player_stats.csv')

    # merge...

    # clean...



if __name__ == '__main__':
    main()