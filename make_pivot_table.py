import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from tqdm import tqdm
from calculateColumnsForModel import calculateColumnsForModel, getMedianOfCollectedData, numberToRoleName
from common_constants import PARTICIPANTS_NUMBER_OF_A_TEAM, PITCHERS_NUMBER_OF_A_PLAYER, RANGE_OF_RECENT_GAME, YEAR_DAYS, HALF_OF_YEAR_DAYS, STAT_MEDIAN_MULTIPLIER, SHRINKAGE_RATE

participant_ids_by_role = []
DETAIL_PATH = "../data/collected_data/"

strcolumn_dict = {"tournamentId":"str", "matchId":"str", "gameId":"str", "patch":"str", "esportsTeamId_Blue":"str", "esportsTeamId_Red":"str"}
temp1 = [f"esportsPlayerId_{i}" for i in range(10)]
temp2 = ["str" for i in range(10)]
esportsPlayerId_type_dict = dict(zip(temp1, temp2))
strcolumn_dict.update(esportsPlayerId_type_dict)        # id가 잘리는 문제가 있어 반드시 str타입으로 들어가야 할 컬럼들
game_ids_df = pd.read_excel("../data/game_ids.xlsx", dtype=strcolumn_dict, index_col = 0)

# esportsPlayerId가 전부 들어간 row들만 남김.
included_all_ids_df = game_ids_df[game_ids_df["esportsPlayerId_0"].notna() & game_ids_df["esportsPlayerId_1"].notna() & game_ids_df["esportsPlayerId_2"].notna() &\
                                game_ids_df["esportsPlayerId_3"].notna() & game_ids_df["esportsPlayerId_4"].notna() & game_ids_df["esportsPlayerId_5"].notna() &\
                                    game_ids_df["esportsPlayerId_6"].notna() & game_ids_df["esportsPlayerId_7"].notna() & game_ids_df["esportsPlayerId_8"].notna() &\
                                        game_ids_df["esportsPlayerId_9"].notna()]

included_all_ids_df_sorted = included_all_ids_df.sort_values(by=["startTime(match)", "gameNumberInAMatch"], ascending=[False, False]).reset_index() # 최근 경기가 위로 오도록 내림차순 정렬

median_playerstat = getMedianOfCollectedData() # 플레이어 스탯의 중간값 목록을 불러옴. 돌리는데 10분정도 걸림.

strcolumn_dict = {"gameId":"str", "esportsTeamId_Blue":"str", "esportsTeamId_Red":"str"}
strcolumn_dict.update(esportsPlayerId_type_dict)
last_row_of_collected_datas_df = pd.read_excel("../data/last_row_of_collected_datas.xlsx", dtype = strcolumn_dict)

most_early_game_time = included_all_ids_df_sorted.iloc[-1]["startTime(match)"]

pre_make_pivot_table_df = None
for idx, row in tqdm(included_all_ids_df_sorted.iterrows(), total = included_all_ids_df_sorted.shape[0]):
    if row["startTime(match)"] - most_early_game_time < timedelta(days=HALF_OF_YEAR_DAYS):  # 너무 오래전꺼는 과거의 데이터가 없어서 힘들다. 데이터시작부터 반년 이내 게임들은 아예 잘라버림
        break
    else:
        previous_subdata_df = included_all_ids_df_sorted[idx+1:] # 현재 행의 바로 다음 행부터

        blueteam_wincount = 1       # 블루팀의 승리 횟수, 100%가 나오는걸 피하기 위해 임의로 1승을 추가한 것임.
        subrow_count = 0
        blueteam_golddiff_sum = 0
        blueteam_killdiff_sum = 0
        weight = 1
        subdata_blueteam = previous_subdata_df[(previous_subdata_df["esportsTeamId_Blue"] == row["esportsTeamId_Blue"]) | 
                                               (previous_subdata_df["esportsTeamId_Red"] == row["esportsTeamId_Blue"])
                                               ]# 블루 레드팀 어디든 현재 블루팀과 팀이 같은 경기가 있을 떼
        for sub_idx, sub_row in subdata_blueteam.iterrows():
            if row["startTime(match)"] - sub_row["startTime(match)"] > timedelta(days=YEAR_DAYS): # 최근 1년 경기가 아니면(바꾸는중)
                break   
            else:
                subrow_count += weight
                target_game = last_row_of_collected_datas_df[last_row_of_collected_datas_df["gameId"] == sub_row["gameId"]].T.squeeze()
                if (sub_row["esportsTeamId_Blue"] == row["esportsTeamId_Blue"]):
                    blueteam_golddiff_sum += ((target_game["blue_totalGold"] - target_game["red_totalGold"]) / target_game["duration"]) * weight
                    blueteam_killdiff_sum += ((target_game["blue_totalKills"] - target_game["red_totalKills"]) / target_game["duration"]) * weight
                    if (sub_row["winner_side"] == "Blue"):
                        blueteam_wincount += weight
                elif (sub_row["esportsTeamId_Red"] == row["esportsTeamId_Blue"]):
                    blueteam_golddiff_sum += ((target_game["red_totalGold"] - target_game["blue_totalGold"]) / target_game["duration"]) * weight
                    blueteam_killdiff_sum += ((target_game["red_totalKills"] - target_game["blue_totalKills"]) / target_game["duration"]) * weight
                    if (sub_row["winner_side"] == "Red"):
                        blueteam_wincount += weight
                weight = weight * SHRINKAGE_RATE
         
        blueteam_winrate = blueteam_wincount / (subrow_count + 2)  # + 2의 의미는 임의로 2전을 추가해서 바로위에 wincount+1한거와 함께 1전 1패의 가상데이터를 넣어준거임.
        if subrow_count == 0:
            blueteam_golddiff = blueteam_golddiff_sum
            blueteam_killdiff = blueteam_killdiff_sum
        else:
            blueteam_golddiff = blueteam_golddiff_sum / subrow_count
            blueteam_killdiff = blueteam_killdiff_sum / subrow_count

        redteam_wincount = 1        # 레드팀의 승리 횟수, 100%가 나오는걸 피하기 위해 임의로 1승을 추가한 것임.
        subrow_count = 0
        redteam_golddiff_sum = 0
        redteam_killdiff_sum = 0
        weight = 1
        subdata_redteam = previous_subdata_df[(previous_subdata_df["esportsTeamId_Blue"] == row["esportsTeamId_Red"]) | 
                                              (previous_subdata_df["esportsTeamId_Red"] == row["esportsTeamId_Red"])
                                              ]# 블루 레드팀 어디든 현재 레드팀과 팀이 같은 경기가 있을 떼
        for sub_idx, sub_row in subdata_redteam.iterrows():
            if row["startTime(match)"] - sub_row["startTime(match)"] > timedelta(days=YEAR_DAYS): # 최근 1년 경기가 아니면(바꾸는중)
                break
            else:
                subrow_count += weight
                target_game = last_row_of_collected_datas_df[last_row_of_collected_datas_df["gameId"] == sub_row["gameId"]].T.squeeze()
                if (sub_row["esportsTeamId_Blue"] == row["esportsTeamId_Red"]):
                    redteam_golddiff_sum += ((target_game["blue_totalGold"] - target_game["red_totalGold"]) / target_game["duration"]) * weight
                    redteam_killdiff_sum += ((target_game["blue_totalKills"] - target_game["red_totalKills"]) / target_game["duration"]) * weight
                    if (sub_row["winner_side"] == "Blue"):
                        redteam_wincount += weight
                elif (sub_row["esportsTeamId_Red"] == row["esportsTeamId_Red"]):
                    redteam_golddiff_sum += ((target_game["red_totalGold"] - target_game["blue_totalGold"]) / target_game["duration"]) * weight
                    redteam_killdiff_sum += ((target_game["red_totalKills"] - target_game["blue_totalKills"]) / target_game["duration"]) * weight
                    if (sub_row["winner_side"] == "Red"):
                        redteam_wincount += weight
                weight = weight * SHRINKAGE_RATE

        redteam_winrate = redteam_wincount / (subrow_count + 2)  # + 2의 의미는 임의로 2전을 추가해서 바로위에 wincount+1한거와 함께 1전 1패의 가상데이터를 넣어준거임. 이렇게 100%와 0%의 극단적인 경우를 피해봄
        if subrow_count == 0:
            redteam_golddiff = redteam_golddiff_sum
            redteam_killdiff = redteam_killdiff_sum
        else:
            redteam_golddiff = redteam_golddiff_sum / subrow_count
            redteam_killdiff = redteam_killdiff_sum / subrow_count
        
        headtohead_wincount = 1     # 같은 팀이 만났을때 블루팀!!의 승리 횟수 (나중에 rate를 구할 때 0~1의 값으로 나올 것임)
        subrow_count = 0
        headtohead_golddiff_sum = 0
        headtohead_killdiff_sum = 0
        weight = 1
        subdata_headtohead = previous_subdata_df[
            ((previous_subdata_df["esportsTeamId_Blue"] == row["esportsTeamId_Blue"]) & 
            (previous_subdata_df["esportsTeamId_Red"] == row["esportsTeamId_Red"])) |
            ((previous_subdata_df["esportsTeamId_Blue"] == row["esportsTeamId_Red"]) & 
            (previous_subdata_df["esportsTeamId_Red"] == row["esportsTeamId_Blue"])) # 양쪽에 교차해서 들어가 있으면 전부
        ]
        for sub_idx, sub_row in subdata_headtohead.iterrows():
            if (subrow_count > RANGE_OF_RECENT_GAME) and (row["startTime(match)"] - sub_row["startTime(match)"] > timedelta(days=YEAR_DAYS)): # 10개 이상 상대전적 데이터가 모였고 최근 1년 경기가 아니면(바꿔보는중)
                break
            else:
                subrow_count += weight
                target_game = last_row_of_collected_datas_df[last_row_of_collected_datas_df["gameId"] == sub_row["gameId"]].T.squeeze()
                if (sub_row["esportsTeamId_Blue"] == row["esportsTeamId_Blue"]):
                    headtohead_golddiff_sum += ((target_game["blue_totalGold"] - target_game["red_totalGold"]) / target_game["duration"]) * weight
                    headtohead_killdiff_sum += ((target_game["blue_totalKills"] - target_game["red_totalKills"]) / target_game["duration"]) * weight
                    if (sub_row["winner_side"] == "Blue"): # 현재 블루팀과 비교할 블루팀이 같으면서 블루팀이 이겼을 경우
                        headtohead_wincount += weight
                elif (sub_row["esportsTeamId_Red"] == row["esportsTeamId_Blue"]):
                    headtohead_golddiff_sum += ((target_game["red_totalGold"] - target_game["blue_totalGold"]) / target_game["duration"]) * weight
                    headtohead_killdiff_sum += ((target_game["red_totalKills"] - target_game["blue_totalKills"]) / target_game["duration"]) * weight
                    if (sub_row["winner_side"] == "Red"): # 현재 블루팀과 레드팀이 비교할 게임에서 서로 진영을 바꾸었는데 레드팀이 이겼을 경우(결국 같은 팀이 이겼나를 보기 위한 조건이다)
                        headtohead_wincount += weight
                weight = weight * SHRINKAGE_RATE

        headtohead_winrate = headtohead_wincount / (subrow_count + 2)
        if subrow_count == 0:
            headtohead_golddiff = headtohead_golddiff_sum
            headtohead_killdiff = headtohead_killdiff_sum
        else:
            headtohead_golddiff = headtohead_golddiff_sum / subrow_count
            headtohead_killdiff = headtohead_killdiff_sum / subrow_count
        
        ##### 아래는 선수별 최근 n경기 스탯을 통해 폼을 뽑아내는 코드 #####
        desired_labels = [f'esportsPlayerId_{j}' for j in range(PARTICIPANTS_NUMBER_OF_A_TEAM * 2)]
        for i in range(PARTICIPANTS_NUMBER_OF_A_TEAM * 2):   # 선수 10명에 대해
            playerstat_list = []    # 선수별 최근 n경기의 기록을 저장할 곳
            role = i % 5
            subdata_playerstat = previous_subdata_df[(previous_subdata_df[f"esportsPlayerId_{role}"] == row[f"esportsPlayerId_{i}"]) |
                                                     (previous_subdata_df[f"esportsPlayerId_{role + PARTICIPANTS_NUMBER_OF_A_TEAM}"] == row[f"esportsPlayerId_{i}"])].head(RANGE_OF_RECENT_GAME)
            number_of_past_games_of_player = subdata_playerstat.shape[0]
            #print(row[f"esportsPlayerId_{i}"])

            for sub_idx, sub_row in subdata_playerstat.iterrows():
                #딕셔너리로 만들어서 playerstat_list에 append하자. 그 다음에 형태를 보자.
                playerstat_dict_of_the_game = {}    # 한 경기에 대한 플레이어 활약상을 넣을 딕셔너리
                game_ids_of_sub_row = sub_row[desired_labels]
                matched_column = game_ids_of_sub_row[game_ids_of_sub_row.values == row[f"esportsPlayerId_{i}"]].index[0]      # ID가 서로 맞는 컬럼이 어디인지(블루팀인지레드팀인지 모르니까)
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
                # 넣을거 : kda, championDamageShare, creepScore, wardsScore, goldEarned, 5안에서 추가 : killsPerTime, deathsPerTime, assistsPerTime
            if number_of_past_games_of_player <= 1:
                playerstat_dict_of_the_game = {         # 빈 자리에 일반적인 평균을 채워 넣고
                    "kda" : median_playerstat[f"kdaof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                    "killsPerTime" : median_playerstat[f"killsPerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                    "deathsPerTime" : median_playerstat[f"deathsPerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                    "assistsPerTime" : median_playerstat[f"assistsPerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                    "championDamageShare" : median_playerstat[f"championDamageShareof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                    "creepScorePerTime" : median_playerstat[f"creepScorePerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                    "wardsScorePerTime" : median_playerstat[f"wardsScorePerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER,
                    "goldEarnedPerTime" : median_playerstat[f"goldEarnedPerTimeof{numberToRoleName(i)}"] * STAT_MEDIAN_MULTIPLIER
                }
            else:
                playerstat_keys = playerstat_list[0].keys()
                playerstat_values = {key: [] for key in playerstat_keys}
                for entry in playerstat_list:
                    for key in playerstat_keys:
                        playerstat_values[key].append(entry[key])           # 데이터를 키별로 분류해 리스트에 넣고
                playerstat_dict_of_the_game = {key : np.mean(playerstat_values[key]) for key in playerstat_keys}    # 리스트로 넣은 키들에 대해 평균을 각각 구함. - 한 선수의 최근 N경기 스탯의 평균
            if i == 0:  # 첫번째선수니까 데이터프레임을 새로 만들고
                player_form = pd.DataFrame(playerstat_dict_of_the_game, index=[0]).T
                player_form.reset_index(inplace = True)
                player_form.columns = ["elements", "formvalue"]

            else:       # 아니면 위아래로 이어붙이는 작업
                temp_player_form = pd.DataFrame(playerstat_dict_of_the_game, index=[0]).T
                temp_player_form.reset_index(inplace=True)
                temp_player_form.columns = ["elements", "formvalue"]
                player_form = pd.concat([player_form, temp_player_form], ignore_index=True)
        # 나온 선수별 폼을 팀별 승률과 이어붙이는 곳
        columns_of_role = []
        for i in range(2):  # 블루팀과 레드팀 2개
            columns_of_role.extend(["Top" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
            columns_of_role.extend(["Jgl" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
            columns_of_role.extend(["Mid" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
            columns_of_role.extend(["Adc" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
            columns_of_role.extend(["Spt" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
        
        each_team_winrate_extended = [blueteam_winrate for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)] # 역할군 갯수가 5개, 총 25개만큼 복제 -> 5안에서 40개로 추가
        each_team_winrate_extended.extend([redteam_winrate for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)])
        each_team_golddiff_extended = [blueteam_golddiff for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)]
        each_team_golddiff_extended.extend([redteam_golddiff for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)])
        each_team_killdiff_extended = [blueteam_killdiff for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)]
        each_team_killdiff_extended.extend([redteam_killdiff for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)])
        columns_of_each_team_winrate_extended = ["Blue" for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)]
        columns_of_each_team_winrate_extended.extend(["Red" for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)])
        headtohead_winrate_extended = [headtohead_winrate for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5 * 2)]
        headtohead_golddiff_extend = [headtohead_golddiff for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5 * 2)]
        headtohead_killdiff_extend = [headtohead_killdiff for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5 * 2)]
        winnerside_extended = [row["winner_side"] for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5 * 2)]
        gameId_extended = [row["gameId"] for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5 * 2)]
        
        each_team_winrate_dict = {                                  # 50개 행으로 만들 예정 -> 5안에서 80개로 추가. 왜냐하면 킬 뎃 어시를 각자 입력해보려고. kda로는 부족한듯?
            "gameId" : gameId_extended,
            "headtoHeadWinrate" : headtohead_winrate_extended,
            "headtoHeadGoldDiff" : headtohead_golddiff_extend,
            "headtoHeadKillDiff" : headtohead_killdiff_extend,
            "winner" : winnerside_extended,                         # 라벨, !!!! 제 일 중 요 !!!!
            "side" : columns_of_each_team_winrate_extended,         # "Blue" 또는 "Red", 피벗테이블의 컬럼으로 만들 예정
            "teamWinrate" : each_team_winrate_extended,             # Side에 따라 다른 값
            "teamGoldDiff" : each_team_golddiff_extended,
            "teamKillDiff" : each_team_killdiff_extended,
            "role" : columns_of_role
        }
        dataset_of_a_game_df = pd.DataFrame(each_team_winrate_dict)
        dataset_of_a_game_df = pd.concat([dataset_of_a_game_df, player_form], axis=1, ignore_index=True)
        dataset_of_a_game_df.columns = (["gameId", "headtoHeadWinrate", "headtoHeadGoldDiff", "headtoHeadKillDiff", "winner", "side", "teamWinrate", "teamGoldDiff", "teamKillDiff", "role", "elements", "formvalue"])
        if pre_make_pivot_table_df is None:
            pre_make_pivot_table_df = dataset_of_a_game_df
        else:
            pre_make_pivot_table_df = pd.concat([pre_make_pivot_table_df, dataset_of_a_game_df], ignore_index=True)

pre_make_pivot_table_df.to_excel("../data/pre_make_pivot_table_draft7.xlsx")    