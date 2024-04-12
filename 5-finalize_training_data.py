import pandas as pd

IN_DIRECTORY = 'data/clean/'
OUT_DIRECTORY = 'data/final/'

TRAINING_DATA_COLUMNS = [
    'SEASON',
    'PLAYER_NAME',
    'TEAM_ABBREVIATION',
    'PLAYER_ID',
    'TEAM_ID',
    'GP',
    'MIN',
    'PTS',
    'REB',
    'AST',
    'STL',
    'BLK',
    'OFF_RATING',
    'DEF_RATING',
    'TS_PCT',
    'USG_PCT',
    'PIE',
    'WS',
    'PER',
    'ALL_NBA',
    'ALL_NBA_TM'
]

def main():
    playerStats = pd.read_csv(IN_DIRECTORY + 'player_stats_clean.csv')
    additionalStats = pd.read_csv(IN_DIRECTORY + 'additional_player_stats.csv')
    allNBAteams = pd.read_csv(IN_DIRECTORY + 'allNBA_teams_clean.csv')

    # merge additional stats
    # adpated from https://stackoverflow.com/questions/19125091/pandas-merge-how-to-avoid-duplicating-columns 
    playerStats = pd.merge(playerStats, additionalStats, on=['SEASON', 'PLAYER_ID'], suffixes=('','_y'))
    playerStats.drop(playerStats.filter(regex='_y$').columns, axis=1, inplace=True)
    
    # merge All-NBA award winners
    # add column to identify All-NBA players
    playerStats['ALL_NBA'] = 0
    
    # merge to get every All-NBA player, update identifier for every All-NBA player
    allNBAplayers = pd.merge(playerStats, allNBAteams, on=['SEASON', 'PLAYER_NAME'])
    allNBAplayers['ALL_NBA'] = 1

    # combine All-NBA players with the rest of the data, remove duplicates
    playerStatsFinal = pd.concat([playerStats, allNBAplayers], ignore_index=True)
    playerStatsFinal = playerStatsFinal.drop_duplicates(subset=['SEASON', 'PLAYER_ID'], keep='last')
    
    # some cleaning
    playerStatsFinal['ALL_NBA_TM'] = playerStatsFinal['ALL_NBA_TM'].fillna('0')
    playerStatsFinal = playerStatsFinal.fillna(0)
    playerStatsFinal = playerStatsFinal.sort_values(by=['SEASON', 'PLAYER_NAME'])

    # round long floats
    playerStatsFinal['MIN'] = playerStatsFinal['MIN'].apply(lambda x : round(x, 2))
    playerStatsFinal['WS'] = playerStatsFinal['WS'].apply(lambda x : round(x, 2))
    playerStatsFinal['PER'] = playerStatsFinal['PER'].apply(lambda x : round(x, 2))


    # save complete final data
    playerStatsFinal.to_csv(OUT_DIRECTORY + 'player_stats_final.csv', index=False)

    # create training data (does not include seasons 2022-23 and later)
    playerStatsTraining = playerStatsFinal[TRAINING_DATA_COLUMNS]
    playerStatsTraining = playerStatsTraining.drop(playerStatsTraining[playerStatsTraining['SEASON'] > '2021-22'].index)
    playerStatsTraining.to_csv(OUT_DIRECTORY + 'player_stats_training.csv', index=False)

    # save data for the 2022-23 season
    playerStats2022_23 = playerStatsFinal[TRAINING_DATA_COLUMNS]
    playerStats2022_23 = playerStats2022_23.drop(playerStats2022_23[playerStats2022_23['SEASON'] != '2022-23'].index)
    playerStats2022_23.to_csv(OUT_DIRECTORY + 'player_stats_2022-23.csv', index=False)

    # save data for the 2023-24 season
    # just for fun as we won't be able to check the accuracy of predictions on this data
    playerStats2023_24 = playerStatsFinal[TRAINING_DATA_COLUMNS]
    playerStats2023_24 = playerStats2023_24.drop(playerStats2023_24[playerStats2023_24['SEASON'] != '2023-24'].index)
    playerStats2023_24.to_csv(OUT_DIRECTORY + 'player_stats_2023-24.csv', index=False)



if __name__ == '__main__':
    main()