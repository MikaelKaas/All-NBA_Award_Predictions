import pandas as pd

IN_DIRECTORY = 'data/raw/'
OUT_DIRECTORY = 'data/clean/'

# update depending on what columns end up being required

# player_stats columns to keep
PLAYER_STATS_COLS = [
    'SEASON',
    'PLAYER_ID',
    'PLAYER_NAME',
    # NICKNAME
    'TEAM_ID',
    'TEAM_ABBREVIATION',
    # AGE
    'GP',
    'W',
    'L',
    'W_PCT',
    'MIN',
    'FGM',
    'FGA',
    'FG_PCT',
    'FG3M',
    'FG3A',
    'FG3_PCT',
    'FTM',
    'FTA',
    'FT_PCT',
    'OREB',
    'DREB',
    'REB',
    'AST',
    'TOV',
    'STL',
    'BLK',
    'BLKA',
    'PF',
    'PFD',
    'PTS',
    'PLUS_MINUS',
    'OFF_RATING',
    'DEF_RATING',
    'NET_RATING',
    'AST_PCT',
    'AST_TO',
    'AST_RATIO',
    'OREB_PCT',
    'DREB_PCT',
    'REB_PCT',
    'TM_TOV_PCT',
    'EFG_PCT',
    'TS_PCT',
    'USG_PCT',
    'PACE',
    'PACE_PER40',
    'PIE',
    'POSS',
    'FGM_PG',
    'FGA_PG'
]

# team_stats columns to keep
TEAM_STATS_COLS = [
    'SEASON',
    'TEAM_ID',
    'TEAM_NAME',
    'GP',
    'W',
    'L',
    'W_PCT',
    'MIN',
    'FGM',
    'FGA',
    'FG_PCT',
    'FG3M',
    'FG3A',
    'FG3_PCT',
    'FTM',
    'FTA',
    'FT_PCT',
    'OREB',
    'DREB',
    'REB',
    'AST',
    'TOV',
    'STL',
    'BLK',
    'BLKA',
    'PF',
    'PFD',
    'PTS',
    'PLUS_MINUS',
    'OFF_RATING',
    'DEF_RATING',
    'NET_RATING',
    'AST_PCT',
    'AST_TO',
    'AST_RATIO',
    'OREB_PCT',
    'DREB_PCT',
    'REB_PCT',
    'TM_TOV_PCT',
    'EFG_PCT',
    'TS_PCT',
    'PACE',
    'PACE_PER40',
    'POSS',
    'PIE'
]

def main():
    playerStats = pd.read_csv(IN_DIRECTORY + 'player_stats.csv')
    teamStats = pd.read_csv(IN_DIRECTORY + 'team_stats.csv')
    
    # for col in playerStats.columns:
    #     print(col)

    playerStats = playerStats[PLAYER_STATS_COLS]
    playerStats.to_csv(OUT_DIRECTORY + 'player_stats_clean.csv', index=False)

    teamStats = teamStats[TEAM_STATS_COLS]
    teamStats.to_csv(OUT_DIRECTORY + 'team_stats_clean.csv', index=False)


if __name__ == '__main__':
    main()