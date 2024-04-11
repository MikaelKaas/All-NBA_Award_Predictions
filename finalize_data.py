# combine and filter down data to only columns we want
# create seperate 2022-2023 file
# remove invalid players from data (not enough GP...)
# deal with potential NaN values?
import pandas as pd
import unicodedata

IN_DIRECTORY = 'data/clean/'
OUT_DIRECTORY = 'data/final/'

def main():
    playerStats = pd.read_csv(IN_DIRECTORY + 'player_stats_clean.csv')
    additionalStats = pd.read_csv(IN_DIRECTORY + 'additional_player_stats.csv')


    # merge...

    # clean...


    # finalize All-NBA team award winner data
    # this data was pulled from: https://www.basketball-reference.com/awards/all_league.html
    allNBAteams = pd.read_csv('data/all-nba_teams.csv')
    
    # remove irrelevant seasons
    allNBAteams = allNBAteams.drop(allNBAteams[allNBAteams['Season'] < '1996-97'].index)
    
    # right now there are five players in every row
    # we want to reorganize the data so that every row contains one player like our other data
    p1Data = allNBAteams[['Season', 'Team', 'P1']] # C
    p2Data = allNBAteams[['Season', 'Team', 'P2']] # F
    p3Data = allNBAteams[['Season', 'Team', 'P3']] # F
    p4Data = allNBAteams[['Season', 'Team', 'P4']] # G
    p5Data = allNBAteams[['Season', 'Team', 'P5']] # G
    p1Data = p1Data.rename(columns={'P1' : 'PLAYER_NAME'})
    p2Data = p2Data.rename(columns={'P2' : 'PLAYER_NAME'})
    p3Data = p3Data.rename(columns={'P3' : 'PLAYER_NAME'})
    p4Data = p4Data.rename(columns={'P4' : 'PLAYER_NAME'})
    p5Data = p5Data.rename(columns={'P5' : 'PLAYER_NAME'})

    # this data contains the players position at the end of the PLAYER_NAME string
    # we want to remove this to match are other data
    # additionally, players like Nikola Jokic and Luka Doncic have accents in their names in this data
    # but not in out other data, so we need to normalize the names
    p1Data = normalize_player_names(p1Data, 'C')
    p2Data = normalize_player_names(p2Data, 'F')
    p3Data = normalize_player_names(p3Data, 'F')
    p4Data = normalize_player_names(p4Data, 'G')
    p5Data = normalize_player_names(p5Data, 'G')

    # combine p1 through p5 data back into one dataframe
    allNBAteamsFinal = pd.DataFrame()
    allNBAteamsFinal = pd.concat([allNBAteamsFinal, p1Data])
    allNBAteamsFinal = pd.concat([allNBAteamsFinal, p2Data])
    allNBAteamsFinal = pd.concat([allNBAteamsFinal, p3Data])
    allNBAteamsFinal = pd.concat([allNBAteamsFinal, p4Data])
    allNBAteamsFinal = pd.concat([allNBAteamsFinal, p5Data])

    # rename columns, sort values
    allNBAteamsFinal = allNBAteamsFinal.rename(columns={'Season' : 'SEASON', 'Team' : 'ALL_NBA_TM'})
    allNBAteamsFinal = allNBAteamsFinal.sort_values(by=['SEASON', 'ALL_NBA_TM', 'PLAYER_NAME']).set_index('SEASON')

    allNBAteamsFinal.to_csv(OUT_DIRECTORY + 'all-nba_teams_final.csv')


# remove position suffix from PLAYER_NAME column and normalize accented letters
def normalize_player_names(data, position):
    # remove position suffix
    data['PLAYER_NAME'] = data['PLAYER_NAME'].str.removesuffix(' ' + position)

    # normalize accented letters
    data['PLAYER_NAME'] = data['PLAYER_NAME'].apply(remove_accents)

    return data

# source: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


if __name__ == '__main__':
    main()