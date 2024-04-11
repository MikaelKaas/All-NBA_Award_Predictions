# here I will calculate additional advanced stats with out data
# these will be popular stats that aren't given by the nba api but can be calculated with what we do have
# these will be important stats for comparing players which will be valuable for our predictions
# stats that I want to calculate:
# - player efficiency rating PER
# - win shares
import pandas as pd

IN_DIRECTORY = 'data/clean/'
OUT_DIRECTORY = 'data/clean/'

def main():
    playerStats = pd.read_csv(IN_DIRECTORY + 'player_stats_clean.csv')
    teamStats = pd.read_csv(IN_DIRECTORY + 'team_stats_clean.csv')

    leagueStats = get_league_stats(teamStats)

    winShareStats = get_win_shares(playerStats, teamStats, leagueStats)
    playerEfficiencyRatingStats = get_player_efficiency_rating(playerStats, teamStats, leagueStats)

    playerStats = pd.merge(playerStats, winShareStats, on=['PLAYER_ID', 'SEASON'])
    playerStats = pd.merge(playerStats, playerEfficiencyRatingStats, on=['PLAYER_ID', 'SEASON'])

    playerStats = playerStats[['SEASON', 'PLAYER_ID', 'PLAYER_NAME', 'WS', 'PER']]

    playerStats.to_csv(OUT_DIRECTORY + 'additional_player_stats.csv', index=False)


# source: https://www.basketball-reference.com/about/per.html
def get_league_stats(teamStats):
    lgStats = pd.DataFrame()

    lgStats = teamStats.groupby('SEASON').agg({col: 'mean' if col == 'PACE' else 'sum' for col in teamStats.columns})
    lgStats = lgStats[['GP', 'FGM', 'FGA', 'FTM', 'FTA', 'PF', 'PTS', 'AST', 'OREB', 'REB', 'TOV', 'PACE']]

    # calculate stats needed for getting win shares
    lgStats['PPG_LG'] = lgStats['PTS'] / lgStats['GP']
    lgStats['PPP_LG'] = lgStats['PTS'] / (lgStats['FGA'] + lgStats['FTA'] * 0.44 + lgStats['TOV'])

    # calculate stats needed for getting player efficiency rating
    # factor = (2 / 3) - (0.5 * (lg_AST / lg_FG)) / (2 * (lg_FG / lg_FT))
    lgStats['factor'] = (2/3) - (0.5 * (lgStats['AST'] / lgStats['FGM'])) / (2 * (lgStats['FGM'] / lgStats['FTM']))
    
    # VOP = lg_PTS / (lg_FGA - lg_ORB + lg_TOV + 0.44 * lg_FTA)
    lgStats['VOP'] = lgStats['PTS'] / (lgStats['FGA'] - lgStats['OREB'] + lgStats['TOV'] + lgStats['FTA'] * 0.44)
    
    # DRB%   = (lg_TRB - lg_ORB) / lg_TRB
    lgStats['DREB_PCT'] = (lgStats['REB'] - lgStats['OREB']) / lgStats['REB']

    return lgStats

# source: https://www.basketball-reference.com/about/ws.html
def get_win_shares(plStats, tmStats, lgStats):
    # get points produced and total possessions for each player
    PProdStats = get_points_produced(plStats, tmStats)

    # merge all the stats we need into one dataframe
    plStats = pd.merge(plStats, lgStats, on=['SEASON'], suffixes=['', '_LG'])
    plStats = pd.merge(plStats, tmStats, on=['TEAM_ID', 'SEASON'], suffixes=['', '_TM'])
    plStats = pd.merge(plStats, PProdStats, on=['PLAYER_ID', 'SEASON'])
    
    # calculate offensive win shares
    # source: https://www.nbastuffer.com/analytics101/possession/
    # Basic Possession Formula=0.96*[(Field Goal Attempts)+(Turnovers)+0.44*(Free Throw Attempts)-(Offensive Rebounds)]
    plStats['POSSESSIONS'] = 0.96 * (plStats['FGA'] + plStats['TOV'] + 0.44 * plStats['FTA'] - plStats['OREB'])

    # Marginal offense = (points produced) - 0.92 * (league points per possession) * (offensive possessions)
    plStats['MARG_OFF'] = plStats['PPROD'] - 0.92 * plStats['PPP_LG'] * plStats['POSSESSIONS']

    # Marginal points per win = 0.32 * (league points per game) * ((team pace) / (league pace))
    plStats['MARG_PPW'] = 0.32 * plStats['PPG_LG'] * (plStats['PACE_TM'] / plStats['PACE_LG'])

    # Offensive Win Shares = (marginal offense) / (marginal points per win)
    plStats['OFF_WS'] = plStats['MARG_OFF'] / plStats['MARG_PPW']


    # calculate defensive win shares
    plStats['POSSESSIONS_TM'] = (0.96 * (plStats['FGA_TM'] + plStats['TOV_TM'] + 0.44 * plStats['FTA_TM'] - plStats['OREB_TM']))
    # Marginal defense = (player minutes played / team minutes played) * (team defensive possessions) 
    # * (1.08 * (league points per possession) - ((Defensive Rating) / 100))
    plStats['MARG_DEF'] = ((plStats['MIN'] / plStats['MIN_TM']) * (plStats['POSSESSIONS_TM']) 
                           * (1.08 * (plStats['PPP_LG']) - ((plStats['DEF_RATING']) / 100)))

    # Defensive Win Shares = (marginal defense) / (marginal points per win)
    plStats['DEF_WS'] = plStats['MARG_DEF'] / plStats['MARG_PPW']

    # Win Share = (Offensive Win Shares) + (Deffensive Win Shares)
    plStats['WS'] = plStats['OFF_WS'] + plStats['DEF_WS']

    return plStats [['SEASON', 'PLAYER_ID', 'WS']]

# source: https://www.basketball-reference.com/about/per.html
def get_player_efficiency_rating(plStats, tmStats, lgStats):
    # merge all the stats we need into one dataframe
    plStats = pd.merge(plStats, lgStats, on=['SEASON'], suffixes=['', '_LG'])
    plStats = pd.merge(plStats, tmStats, on=['TEAM_ID', 'SEASON'], suffixes=['', '_TM'])
    
    # calculate unadjusted PER
    # uPER = (1 / MP) *
    #     [ 3P
    #     + (2/3) * AST
    #     + (2 - factor * (team_AST / team_FG)) * FG
    #     + (FT *0.5 * (1 + (1 - (team_AST / team_FG)) + (2/3) * (team_AST / team_FG)))
    #     - VOP * TOV
    #     - VOP * DRB% * (FGA - FG)
    #     - VOP * 0.44 * (0.44 + (0.56 * DRB%)) * (FTA - FT)
    #     + VOP * (1 - DRB%) * (TRB - ORB)
    #     + VOP * DRB% * ORB
    #     + VOP * STL
    #     + VOP * DRB% * BLK
    #     - PF * ((lg_FT / lg_PF) - 0.44 * (lg_FTA / lg_PF) * VOP) ]
    plStats['uPER'] = ((1 / plStats['MIN']) * (plStats['FG3M'] + (2/3) * plStats['AST'] + (2 - plStats['factor'] 
                        * (plStats['AST_TM'] / plStats['FGM_TM'])) * plStats['FGM']
                        + (plStats['FTM'] * 0.5 * (1 + (1 - (plStats['AST_TM'] / plStats['FGM_TM'])) + (2/3) * (plStats['AST_TM'] / plStats['FGM_TM'])))
                        - plStats['VOP'] * plStats['TOV'] - plStats['VOP'] * plStats['DREB_PCT'] * (plStats['FGA'] - plStats['FGM'])
                        - plStats['VOP'] * 0.44 * (0.44 + (0.56 * plStats['DREB_PCT'])) * (plStats['FTA'] - plStats['FTM'])
                        + plStats['VOP'] * (1 - plStats['DREB_PCT']) * (plStats['REB'] - plStats['OREB'])
                        + plStats['VOP'] * plStats['DREB_PCT'] * plStats['OREB'] 
                        + plStats['VOP'] * plStats['STL'] + plStats['VOP'] * plStats['DREB_PCT'] * plStats['BLK']
                        - plStats['PF'] * ((plStats['FTM_LG'] / plStats['PF_LG']) - 0.44 * (plStats['FTA_LG'] / plStats['PF_LG']) * plStats['VOP'])))
    
    # pace adjustment = lg_Pace / team_Pace
    # aPER = (pace adjustment) * uPER
    plStats['aPER'] = (plStats['PACE_LG'] / plStats['PACE_TM']) * plStats['uPER']
    
    # finally, calculte player efficiency rating
    # PER = aPER * (15 / lg_aPER)
    lg_aPER = plStats.groupby('SEASON').agg({'aPER' : 'mean'})
    plStats = pd.merge(plStats, lg_aPER, on=['SEASON'], suffixes=['', '_LG'])
    plStats['PER'] = plStats['aPER'] * (15 / plStats['aPER_LG'])

    return plStats[['SEASON', 'PLAYER_ID', 'PER']]

# source: https://www.basketball-reference.com/about/ratings.html
def get_points_produced(plStats, tmStats):
    plStats = get_metrics(plStats, tmStats)

    # PProd_FG_Part = 2 * (FGM + 0.5 * 3PM) * (1 - 0.5 * ((PTS - FTM) / (2 * FGA)) * qAST)
    plStats['PPROD_FG_PART'] = (2 * (plStats['FGM'] + 0.5 * plStats['FG3M']) 
                                * (1 - 0.5 * ((plStats['PTS'] - plStats['FTM']) / (2 * plStats['FGA'])) * plStats['qAST']))

    # PProd_AST_Part = 2 * ((Team_FGM - FGM + 0.5 * (Team_3PM - 3PM)) / (Team_FGM - FGM)) 
    # * 0.5 * (((Team_PTS - Team_FTM) - (PTS - FTM)) / (2 * (Team_FGA - FGA))) * AST
    plStats['PPROD_AST_PART'] = (2 * ((plStats['FGM_TM'] - plStats['FGM'] + 0.5 * (plStats['FG3M_TM'] - plStats['FG3M'])) 
                                / (plStats['FGM_TM'] - plStats['FGM'])) * 0.5 * (((plStats['PTS_TM'] - plStats['FTM_TM']) 
                                - (plStats['PTS'] - plStats['FTM'])) / (2 * (plStats['FGA_TM'] - plStats['FGA']))) * plStats['AST'])

    # PProd_ORB_Part = ORB * Team_ORB_Weight * Team_Play% * (Team_PTS / (Team_FGM + (1 - (1 - (Team_FTM / Team_FTA))^2) * 0.4 * Team_FTA))
    plStats['PPROD_ORB_PART'] = (plStats['OREB'] * plStats['TEAM_ORB_WEIGHT'] * plStats['TEAM_PLAY_PCT'] * (plStats['PTS_TM'] / (plStats['FGM_TM'] 
                                + (1 - (1 - (plStats['FTM_TM'] / plStats['FTA_TM']))**2) * 0.4 * plStats['FTA_TM'])))

    # PProd = (PProd_FG_Part + PProd_AST_Part + FTM) * (1 - (Team_ORB / Team_Scoring_Poss) * Team_ORB_Weight * Team_Play%) + PProd_ORB_Part
    plStats['PPROD'] = ((plStats['PPROD_FG_PART'] + plStats['PPROD_AST_PART'] + plStats['FTM']) * (1 - (plStats['OREB_TM'] 
                        / plStats['TEAM_SCORING_POSS']) * plStats['TEAM_ORB_WEIGHT'] * plStats['TEAM_PLAY_PCT']) + plStats['PPROD_ORB_PART'])

    return plStats[['SEASON', 'PLAYER_ID', 'PPROD']]

# calculate additional stats needed for calculations
# source: https://www.basketball-reference.com/about/ratings.html
def get_metrics(plStats, tmStats):
    # add team stats to player for every player's team
    plStats = pd.merge(plStats, tmStats, on=['TEAM_ID', 'SEASON'], suffixes=['', '_TM'])
    
    # Team_Scoring_Poss = Team_FGM + (1 - (1 - (Team_FTM / Team_FTA))^2) * Team_FTA * 0.4
    plStats['TEAM_SCORING_POSS'] = plStats['FGM_TM'] + (1 - (1 - (plStats['FTM_TM'] / plStats['FTA_TM']))**2) * plStats['FTA_TM'] * 0.4

    # Team_Play% = Team_Scoring_Poss / (Team_FGA + Team_FTA * 0.4 + Team_TOV)
    plStats['TEAM_PLAY_PCT'] = plStats['TEAM_SCORING_POSS'] / (plStats['FGA_TM'] + plStats['FTA_TM'] * 0.4 + plStats['TOV_TM'])

    # Team_ORB_Weight = ((1 - Team_ORB%) * Team_Play%) / ((1 - Team_ORB%) * Team_Play% + Team_ORB% * (1 - Team_Play%))
    plStats['TEAM_ORB_WEIGHT'] = (((1 - plStats['OREB_PCT_TM']) * plStats['TEAM_PLAY_PCT'])
                                / ((1 - plStats['OREB_PCT_TM']) * plStats['TEAM_PLAY_PCT']
                                + plStats['OREB_PCT_TM'] * (1 - plStats['TEAM_PLAY_PCT'])))
    
    # qAST = ((MP / (Team_MP / 5)) * (1.14 * ((Team_AST - AST) / Team_FGM)))
    # + ((((Team_AST / Team_MP) * MP * 5 - AST) / ((Team_FGM / Team_MP) * MP * 5 - FGM)) * (1 - (MP / (Team_MP / 5))))
    plStats['qAST'] = (((plStats['MIN'] / (plStats['MIN_TM'] / 5)) 
                        * (1.14 * ((plStats['AST_TM'] - plStats['AST']) / plStats['FGM_TM'])))
                        + ((((plStats['AST_TM'] / plStats['MIN_TM']) * plStats['MIN'] * 5 - plStats['AST'])
                        / ((plStats['FGM_TM'] / plStats['MIN_TM']) * plStats['MIN'] * 5 - plStats['FGM']))
                        * (1 - (plStats['MIN'] / (plStats['MIN_TM'] / 5)))))

    return plStats


if __name__ == '__main__':
    main()