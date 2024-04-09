import pandas as pd
from nba_api.stats.endpoints import leaguegamelog, leaguedashplayerstats, leaguedashteamstats

# year interval we want to collect data from (2023 means the 2023-24 season)
FIRST_YEAR = 1996 # nba_api game logs only go back to 1996 (this is completely fine, will explain in report)
LAST_YEAR = 2023
# output directory name (directory must already exist)
OUT_DIRECTORY = 'data/raw/'
# string for logging purposes
SEPERATOR = '-------------------------------------'

def main():
    # create list of seaons from FIRST_YEAR to LAST_YEAR
    seasons = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        # example: int 2023 -> string 2023-24
        seasons.append(str(year) + '-' + (str((year + 1) % 100)).zfill(2))
    
    # get player stats
    print(SEPERATOR + '\nGetting regular season player data\n' + SEPERATOR)
    regularSeasonPlayerData = get_data(leaguedashplayerstats.LeagueDashPlayerStats, seasons, getAdvancedStats=True, key='PLAYER_ID')
    print('exporting player data')
    regularSeasonPlayerData.to_csv(OUT_DIRECTORY + 'player_stats.csv')
    
    # get team stats
    print(SEPERATOR + '\nGetting regular season team data\n' + SEPERATOR)
    regularSeasonTeamData = get_data(leaguedashteamstats.LeagueDashTeamStats, seasons, getAdvancedStats=True, key='TEAM_ID')
    print('exporting team data')
    regularSeasonTeamData.to_csv(OUT_DIRECTORY + 'team_stats.csv')

    # get game logs
    print(SEPERATOR + '\nGetting regular season game logs\n' + SEPERATOR)
    regularSeasonGameLogs = get_data(leaguegamelog.LeagueGameLog, seasons)
    print('exporting game logs')
    regularSeasonGameLogs.to_csv(OUT_DIRECTORY + 'game_logs.csv')


# get a dataframe of data from an endpoint for every season in seasons[]
def get_data(endpoint, seasons, getAdvancedStats=False, key='PLAYER_ID'):
    data = pd.DataFrame()
    # get data for every season in the list of seasons
    for season in seasons:
        print("Getting data for " + season)
        result = call_nba_api(endpoint, season)

        # get advanced stats if available
        if getAdvancedStats:
            advancedResult = call_nba_api(endpoint, season, 'Advanced')
            # adpated from https://stackoverflow.com/questions/19125091/pandas-merge-how-to-avoid-duplicating-columns 
            result = pd.merge(result, advancedResult, on=key, suffixes=('','_y'))
            result.drop(result.filter(regex='_y$').columns, axis=1, inplace=True)
        
        # add season column to api result
        result['SEASON'] = season
        data = pd.concat([data, result])
    
    data.set_index('SEASON', inplace=True)
    return data

# use nba_api to get data from a specific endpoint for a specific season
def call_nba_api(endpoint, seasonStr, measureType='null'):
    if measureType == 'null':
        result = endpoint(season=seasonStr, season_type_all_star='Regular Season')
    else:
       result = endpoint(season=seasonStr, season_type_all_star='Regular Season', measure_type_detailed_defense=measureType)
    return result.get_data_frames()[0]


if __name__ == '__main__':
    main()