import pandas as pd
from nba_api.stats.endpoints import leaguegamelog, leaguedashplayerstats, leaguedashteamstats
from nba_api.stats.library.parameters import SeasonType

# year interval we want to collect data from (2023 means the 2023-24 season)
FIRST_YEAR = 1996 # nba_api game logs only go back to 1996 (this is completely fine, will explain in report)
LAST_YEAR = 2023
# directory name (directory must already exist)
OUT_DIRECTORY = 'data/raw'
# string for logging purposes
SEPERATOR = '-------------------------------------'


def main():
    # create list of seaons from FIRST_YEAR to LAST_YEAR
    seasons = []
    for year in range(FIRST_YEAR, LAST_YEAR):
        # example: int 2023 -> string 2023-24
        seasons.append(str(year) + '-' + (str((year + 1) % 100)).zfill(2))
    
    # get player stats
    print(SEPERATOR + '\nGetting regular season player data\n' + SEPERATOR)
    regularSeasonPlayerData = get_data(leaguedashplayerstats.LeagueDashPlayerStats, seasons)
    print('exporting player data')
    regularSeasonPlayerData.to_csv(OUT_DIRECTORY + '/player_stats_.csv')
    
    # get team stats
    print(SEPERATOR + '\nGetting regular season team data\n' + SEPERATOR)
    regularSeasonTeamData = get_data(leaguedashteamstats.LeagueDashTeamStats, seasons)
    print('exporting team data')
    regularSeasonTeamData.to_csv(OUT_DIRECTORY + '/team_stats.csv')

    # get game logs
    print(SEPERATOR + '\nGetting regular season game logs\n' + SEPERATOR)
    regularSeasonGameLogs = get_data(leaguegamelog.LeagueGameLog, seasons)
    print('exporting game logs')
    regularSeasonGameLogs.to_csv(OUT_DIRECTORY + '/game_logs.csv')


# get a dataframe of data from an endpoint for every season in seasons[]
def get_data(endpoint, seasons):
    data = pd.DataFrame()
    # get data for every season in the list of seasons
    for season in seasons:
        print("Getting data for " + season)
        result = call_nba_api(endpoint, season)
        # add season column to api result
        result['SEASON'] = season
        data = pd.concat([data, result])
    
    data.set_index('SEASON', inplace=True)
    return data

# use nba_api to get data from a specific endpoint for a specific season
def call_nba_api(endpoint, seasonStr):
    result = endpoint(season=seasonStr, season_type_all_star=SeasonType.regular)
    return result.get_data_frames()[0]


if __name__ == '__main__':
    main()