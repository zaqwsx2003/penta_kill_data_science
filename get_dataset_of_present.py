import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
from tqdm import tqdm
import pickle
from calculateColumnsForModel import calculateColumnsForModel, getMedianOfCollectedData, numberToRoleName
from common_constants import PARTICIPANTS_NUMBER_OF_A_TEAM, RANGE_OF_RECENT_GAME, YEAR_DAYS, HALF_OF_YEAR_DAYS, STAT_MEDIAN_MULTIPLIER, SHRINKAGE_RATE

participant_ids_by_role = []
team_Ids_list = []
DETAIL_PATH = "../data/collected_data/"

strcolumn_dict = {"tournamentId":"str", "matchId":"str", "gameId":"str", "patch":"str", "esportsTeamId_Blue":"str", "esportsTeamId_Red":"str"}
esportsPlayerIds_columns = [f"esportsPlayerId_{i}" for i in range(10)]
temp2 = ["str" for i in range(10)]
esportsPlayerId_type_dict = dict(zip(esportsPlayerIds_columns, temp2))
strcolumn_dict.update(esportsPlayerId_type_dict)
game_ids_df = pd.read_excel("../data/game_ids.xlsx", dtype=strcolumn_dict, index_col = 0)
#game_ids_df = pd.read_excel("../data/game_ids_for_test.xlsx", dtype=strcolumn_dict, index_col = 0)
strcolumn_dict = {"gameId":"str", "esportsTeamId_Blue":"str", "esportsTeamId_Red":"str"}
esportsPlayerId_type_dict = dict(zip(esportsPlayerIds_columns, temp2))
strcolumn_dict.update(esportsPlayerId_type_dict)
last_row_of_collected_datas_df = pd.read_excel("../data/last_row_of_collected_datas.xlsx", dtype = strcolumn_dict)
#last_row_of_collected_datas_df = pd.read_excel("../data/last_row_of_collected_datas_of_test.xlsx", dtype = strcolumn_dict)

#이거 넣어야 됨. id에 널값이 있는 게임은 누군지도 모르니까 걍 제외.
included_all_ids_df = game_ids_df[game_ids_df["esportsPlayerId_0"].notna() & game_ids_df["esportsPlayerId_1"].notna() & game_ids_df["esportsPlayerId_2"].notna() &\
                                  game_ids_df["esportsPlayerId_3"].notna() & game_ids_df["esportsPlayerId_4"].notna() & game_ids_df["esportsPlayerId_5"].notna() &\
                                    game_ids_df["esportsPlayerId_6"].notna() & game_ids_df["esportsPlayerId_7"].notna() & game_ids_df["esportsPlayerId_8"].notna() &\
                                        game_ids_df["esportsPlayerId_9"].notna()]

included_all_ids_df_sorted = included_all_ids_df.sort_values(by=["startTime(match)", "gameNumberInAMatch"], ascending=[False, False]).reset_index() # 최근 경기가 위로 오도록 내림차순 정렬

median_playerstat = getMedianOfCollectedData()
last_game_time = included_all_ids_df_sorted.iloc[0, :]["startTime(match)"]  # 가장 최근 경기한 시간. 여기서는 모델에 들어갈 기준 시간이 된다.



teamId_blue_ser = game_ids_df[pd.isna(game_ids_df["esportsTeamId_Blue"]) == False]["esportsTeamId_Blue"]
teamId_red_ser = game_ids_df[pd.isna(game_ids_df["esportsTeamId_Red"]) == False]["esportsTeamId_Red"]
team_Ids_list = list(set(pd.concat([teamId_blue_ser, teamId_red_ser], ignore_index=True)))          # 게임데이터에 나온 모든 팀들 리스트
#print(len(team_Ids_list))

for i in range(PARTICIPANTS_NUMBER_OF_A_TEAM):       # 탑 정글 미드 원딜 서폿 이렇게.. 포지션별
    playerId_blue_ser = game_ids_df[pd.isna(game_ids_df[f"esportsPlayerId_{i}"]) == False][f"esportsPlayerId_{i}"]  # 블루팀 플레이어id 시리즈
    playerId_red_ser = game_ids_df[pd.isna(game_ids_df[f"esportsPlayerId_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]) == False][f"esportsPlayerId_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]    # 레드팀 플레이어id 시리즈
    participant_ids_by_role.append(list(set(pd.concat([playerId_blue_ser,playerId_red_ser], ignore_index=True))))   # 블루팀 레드팀 상관없이 역할군에 참여한 플레이어들이 리스트에 append.
    
past_games_df = included_all_ids_df_sorted
team_history_dict = {}
player_form_dict = {}
for team_id in tqdm(team_Ids_list):
    team_wincount = 1       # 데이터가 적을 때 극단적인 승률이 나오는 걸 방지하기 위해 가상의 1승 1패를 더하는데 그 중 1승 부분
    subrow_count = 0
    team_golddiff_sum = 0
    team_killdiff_sum = 0
    weight = 1
    target_games = past_games_df[(past_games_df["esportsTeamId_Blue"] == team_id) | (past_games_df["esportsTeamId_Red"] == team_id)]    # 블루팀에 있든 레드팀에 있든 상관없이
    for idx, row in target_games.iterrows():
        target_game_detail = last_row_of_collected_datas_df[last_row_of_collected_datas_df["gameId"] == row["gameId"]].T.squeeze()
        if (last_game_time - row["startTime(match)"]) > timedelta(days=YEAR_DAYS):      # 최근 1년 경기가 아니면
            break
        else:                   # 팀 승리 여부와, 해당 경기에서 골드격차와 킬격차를 얼마나 냈는지 계산하는 부분이다.
            subrow_count += weight
            if row["esportsTeamId_Blue"] == team_id:
                team_golddiff_sum += ((target_game_detail["blue_totalGold"] - target_game_detail["red_totalGold"]) / target_game_detail["duration"]) * weight
                team_killdiff_sum += ((target_game_detail["blue_totalKills"] - target_game_detail["red_totalKills"]) / target_game_detail["duration"]) * weight
                if row["winner_side"] == "Blue":
                    team_wincount += weight
            elif row["esportsTeamId_Red"] == team_id:
                team_golddiff_sum += ((target_game_detail["red_totalGold"] - target_game_detail["blue_totalGold"]) / target_game_detail["duration"]) * weight
                team_killdiff_sum += ((target_game_detail["red_totalKills"] - target_game_detail["blue_totalKills"]) / target_game_detail["duration"]) * weight
                if row["winner_side"] == "Red":
                    team_wincount += weight
            weight = weight * SHRINKAGE_RATE
                
    team_winrate = team_wincount / (subrow_count + 2)   # 데이터가 적을 때 극단적인 승률이 나오는 걸 방지하기 위해 가상의 1승 1패를 더하는데 그 중 1패(정확히는 가상의 2전을 더하는) 부분
    if subrow_count == 0:                   # 0으로 나누는 걸 피하기 위한 코드
        team_golddiff = team_golddiff_sum
        team_killdiff = team_killdiff_sum
    else:
        team_golddiff = team_golddiff_sum / subrow_count
        team_killdiff = team_killdiff_sum / subrow_count
    if team_id not in team_history_dict:
        team_history_dict[team_id] = {}
    
    if "self" not in team_history_dict[team_id]:
        team_history_dict[team_id]["self"] = {}
    team_history_dict[team_id]["self"].update({"winrate": team_winrate})        # 다중 딕셔너리는 한번에 업데이트가 안 되는 걸까..?
    team_history_dict[team_id]["self"].update({"golddiff": team_golddiff})
    team_history_dict[team_id]["self"].update({"killdiff": team_killdiff})
    for opposite_team_id in team_Ids_list:
        particular_winrate_dict = {}
        if opposite_team_id == team_id:
            continue
        else:
            target_games = past_games_df[((past_games_df["esportsTeamId_Blue"] == team_id) & (past_games_df["esportsTeamId_Red"] == opposite_team_id)) |
                                        ((past_games_df["esportsTeamId_Red"] == team_id) & (past_games_df["esportsTeamId_Blue"] == opposite_team_id))
                                        ]
            particular_wincount = 1         # 데이터가 적을 때 극단적인 승률이 나오는 걸 방지하기 위해 가상의 1승 1패를 더하는데 그 중 1승 부분
            particular_subrow_count = 0
            particular_golddiff_sum = 0
            particular_killdiff_sum = 0
            particular_weight = 1
            for idx, row in target_games.iterrows():
                target_game_detail = last_row_of_collected_datas_df[last_row_of_collected_datas_df["gameId"] == row["gameId"]].T.squeeze()
                if (particular_subrow_count > RANGE_OF_RECENT_GAME) and (last_game_time - row["startTime(match)"] > timedelta(days=YEAR_DAYS)): # 여기서는 최소 count 조건을 하나 더 추가했는데, 특정한 어떤 두 팀이 만나는 경우가 1년에 얼마 없을 수도 있기 때문이다.
                                                                                                                                                # (e.g. 다른 리그에 속한 팀끼리 국제전을 하는 경우 등등)
                    break
                else:
                    particular_subrow_count += particular_weight
                    if ((row["esportsTeamId_Blue"] == team_id) & (row["esportsTeamId_Red"] == opposite_team_id)):
                        particular_golddiff_sum += ((target_game_detail["blue_totalGold"] - target_game_detail["red_totalGold"]) / target_game_detail["duration"]) * particular_weight
                        particular_killdiff_sum += ((target_game_detail["blue_totalKills"] - target_game_detail["red_totalKills"]) / target_game_detail["duration"]) * particular_weight
                        if (row["winner_side"] == "Blue"):
                            particular_wincount += particular_weight
                    elif ((row["esportsTeamId_Red"] == team_id) & (row["esportsTeamId_Blue"] == opposite_team_id)):
                        particular_golddiff_sum += ((target_game_detail["red_totalGold"] - target_game_detail["blue_totalGold"]) / target_game_detail["duration"]) * particular_weight
                        particular_killdiff_sum += ((target_game_detail["red_totalKills"] - target_game_detail["blue_totalKills"]) / target_game_detail["duration"]) * particular_weight
                        if (row["winner_side"] == "Red"):
                            particular_wincount += particular_weight
                    particular_weight = particular_weight * SHRINKAGE_RATE
            particular_winrate = particular_wincount / (particular_subrow_count + 2)    # 데이터가 적을 때 극단적인 승률이 나오는 걸 방지하기 위해 가상의 1승 1패를 더하는데 그 중 1패(정확히는 가상의 2전을 더하는) 부분
            if particular_subrow_count == 0:                                # 0으로 나누는걸 피하기 위한 코드.
                particular_golddiff = particular_golddiff_sum
                particular_killdiff = particular_killdiff_sum
            else:
                particular_golddiff = particular_golddiff_sum / particular_subrow_count
                particular_killdiff = particular_killdiff_sum / particular_subrow_count
            if team_id not in team_history_dict:
                team_history_dict[team_id] = {}
            
            if opposite_team_id not in team_history_dict[team_id]:
                team_history_dict[team_id][opposite_team_id] = {}
            team_history_dict[team_id][opposite_team_id].update({"winrate": particular_winrate})
            team_history_dict[team_id][opposite_team_id].update({"golddiff": particular_golddiff})
            team_history_dict[team_id][opposite_team_id].update({"killdiff": particular_killdiff})
        
##### 아래는 선수별 최근 n경기 스탯을 통해 폼을 뽑아내는 코드 #####
desired_labels = [f'esportsPlayerId_{j}' for j in range(PARTICIPANTS_NUMBER_OF_A_TEAM * 2)]
for role in tqdm(range(PARTICIPANTS_NUMBER_OF_A_TEAM)):
    for player_id in tqdm(participant_ids_by_role[role], leave=False):
        playerstat_list = []    # 선수별 최근 n경기의 기록을 저장할 곳
        subdata_playerstat = past_games_df[(past_games_df[f"esportsPlayerId_{role}"] == player_id) |
                                           (past_games_df[f"esportsPlayerId_{role + PARTICIPANTS_NUMBER_OF_A_TEAM}"] == player_id)].head(RANGE_OF_RECENT_GAME)
        number_of_past_games_of_player = subdata_playerstat.shape[0]
        for sub_idx, sub_row in subdata_playerstat.iterrows():
            #딕셔너리로 만들어서 playerstat_list에 append하자. 그 다음에 형태를 보자.
            playerstat_dict_of_the_game = {}    # 한 경기에 대한 플레이어 활약상을 넣을 딕셔너리
            game_ids_of_sub_row = sub_row[desired_labels]
            matched_column = game_ids_of_sub_row[game_ids_of_sub_row.values == player_id].index[0]      # ID가 서로 맞는 컬럼이 어디인지(블루팀인지레드팀인지 모르니까)
            matched_column_number = matched_column[matched_column.find("_")+1:]     # 번호 추출
            target_game = calculateColumnsForModel(last_row_of_collected_datas_df[last_row_of_collected_datas_df["gameId"] == sub_row["gameId"]].T.squeeze())

            playerstat_dict_of_the_game["kda"] = target_game[f"kda_{matched_column_number}"]
            playerstat_dict_of_the_game["killsPerTime"] = target_game[f"killsPerTime_{matched_column_number}"]
            playerstat_dict_of_the_game["deathsPerTime"] = target_game[f"deathsPerTime_{matched_column_number}"]
            playerstat_dict_of_the_game["assistsPerTime"] = target_game[f"assistsPerTime_{matched_column_number}"]
            playerstat_dict_of_the_game["championDamageShare"] = target_game[f"championDamageShare_{matched_column_number}"]
            playerstat_dict_of_the_game["creepScorePerTime"] = target_game[f"creepScorePerTime_{matched_column_number}"]
            playerstat_dict_of_the_game["wardsScorePerTime"] = target_game[f"wardsScorePerTime_{matched_column_number}"]
            playerstat_dict_of_the_game["goldEarnedPerTime"] = target_game[f"goldEarnedPerTime_{matched_column_number}"]
            playerstat_list.append(playerstat_dict_of_the_game)
            # 넣을거 : kda, kills, deaths, assists, championDamageShare, creepScore, wardsScore, goldEarned
        if number_of_past_games_of_player <= 1:     # 선수의 최근 경기 기록이 1경기 이하일때는 신인선수 또는 기록이 없는 선수로 간주.
            playerstat_dict_of_the_game = {         # 중간값의 70%값을 채워 넣고
                "kda" : median_playerstat[f"kdaof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                "killsPerTime" : median_playerstat[f"killsPerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                "deathsPerTime" : median_playerstat[f"deathsPerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                "assistsPerTime" : median_playerstat[f"assistsPerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                "championDamageShare" : median_playerstat[f"championDamageShareof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                "creepScorePerTime" : median_playerstat[f"creepScorePerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                "wardsScorePerTime" : median_playerstat[f"wardsScorePerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                "goldEarnedPerTime" : median_playerstat[f"goldEarnedPerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER
            }
        else:                       # 선수의 최근 기록이 2경기 이상 있을때는
            playerstat_keys = playerstat_list[0].keys()
            playerstat_values = {key: [] for key in playerstat_keys}
            for entry in playerstat_list:
                for key in playerstat_keys:
                    playerstat_values[key].append(entry[key])       # 이건 선수의 경기별로 리스트에 들어갔던 딕셔너리를 키별로 쭈루룩 바꾸는 작업.
            playerstat_dict_of_the_game = {key : np.mean(playerstat_values[key]) for key in playerstat_keys}        # 그 다음 키별 평균을 구한다.
            
        player_form = pd.DataFrame(playerstat_dict_of_the_game, index=[0]).T
        player_form.reset_index(inplace = True)
        player_form.columns = ["elements", "formvalue"]
        if numberToRoleName(role) not in player_form_dict:
            player_form_dict[numberToRoleName(role)] = {}    
        player_form_dict[numberToRoleName(role)].update({player_id: player_form})
data_dict = {
    "team_history" : team_history_dict,
    "player_form" : player_form_dict
}

with open('../data/present_data.pkl', 'wb') as f:
#with open('../data/present_data_for_test.pkl', 'wb') as f:
    pickle.dump(data_dict, f)