import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
from tqdm import tqdm
from calculateColumnsForModel import calculateColumnsForModel, getAvgOfCollectedData, numberToRoleName

# 나중에 현재기준 테이블 만들때는 row안에 데이터를 직접 넣고 가장 겉의 for문 하나 제거하고 뚝딱뚝딱 돌리면 되겠지 ㅎㅎ
# 대신 앞에 last_row_of 저건 읽어와야한다. 반복문에서 하나하나읽지않고 한번 읽고 끝내는 것이 스피드를 위해 핵심.

strcolumn_dict = {"gameId":"str", "esportsTeamId_Blue":"str", "esportsTeamId_Red":"str"}
temp1 = [f"esportsPlayerId_{i}" for i in range(10)]
temp2 = ["str" for i in range(10)]
esportsPlayerId_type_dict = dict(zip(temp1, temp2))
strcolumn_dict.update(esportsPlayerId_type_dict)
last_row_of_collected_datas_df = pd.read_excel("../data/last_row_of_collected_datas.xlsx", dtype = strcolumn_dict)
print("read done")
RANGE_OF_RECENT_GAME = 5   
# RANGE_OF_RECENT_GAME_OF_TEAM = RANGE_OF_RECENT_GAME * 3 # 5개로 하니까 좀 안좋다는 의견이 있어서 15개로 늘려봄 # 그냥 시간기준으로 할까?
#TOO_OLD = datetime(2021, 7, 3)
#average_playerstat = getAvgOfCollectedData()
final_time = included_all_ids_df_sorted.iloc[-1]["startTime(match)"]
pre_make_pivot_table_df = None
for idx, row in tqdm(included_all_ids_df_sorted.iterrows(), total = included_all_ids_df_sorted.shape[0]):
    #if idx + RANGE_OF_RECENT_GAME >= included_all_ids_df.shape[0]: # 거의 끝행에 도달하면 어차피 지난 데이터도 얼마 없기 때문에 스톱한다.
    if row["startTime(match)"] - final_time < timedelta(days=30):  # 너무 오래전꺼는 과거의 데이터가 없어서 힘들다. 2021년 6월 4일자부터만 게임데이터를 가지고 있기 때문에 가장 과거 데이터 1달정도를 자른다.
        break
    else:
        #print(f"현재 row : 블루팀 : {row["esportsTeamId_Blue"]}, 레드팀 : {row["esportsTeamId_Red"]}")
        previous_subdata_df = included_all_ids_df_sorted[idx+1:] # 현재 행의 바로 다음 행부터

        blueteam_wincount = 0       # 블루팀의 승리 횟수
        subdata_blueteam = previous_subdata_df[(previous_subdata_df["esportsTeamId_Blue"] == row["esportsTeamId_Blue"]) | 
                                               (previous_subdata_df["esportsTeamId_Red"] == row["esportsTeamId_Blue"])
                                               ]# 블루 레드팀 어디든 현재 블루팀과 팀이 같은 경기가 있을 떼
        for sub_idx, sub_row in subdata_blueteam.iterrows():
            if row["startTime(match)"] - sub_row["startTime(match)"] > timedelta(days=365): # 최근 1년 경기가 아니면
                break
            else:
                if sub_row["esportsTeamId_Blue"] == row["esportsTeamId_Blue"] and sub_row["winner_side"] == "Blue":
                    blueteam_wincount += 1
                elif sub_row["esportsTeamId_Red"] == row["esportsTeamId_Blue"] and sub_row["winner_side"] == "Red":
                    blueteam_wincount += 1
        blueteam_wincount += 1 # 이건 100%가 나오는걸 피하기 위해 임의로 1승을 추가한 것임.
        blueteam_winrate = blueteam_wincount / (subdata_blueteam.shape[0] + 2)  # + 2의 의미는 임의로 2전을 추가해서 바로위에 wincount+1한거와 함께 1전 1패의 가상데이터를 넣어준거임.

        redteam_wincount = 0        # 레드팀의 승리 횟수
        subdata_redteam = previous_subdata_df[(previous_subdata_df["esportsTeamId_Blue"] == row["esportsTeamId_Red"]) | 
                                              (previous_subdata_df["esportsTeamId_Red"] == row["esportsTeamId_Red"])
                                              ]# 블루 레드팀 어디든 현재 레드팀과 팀이 같은 경기가 있을 떼
        for sub_idx, sub_row in subdata_redteam.iterrows():
            if row["startTime(match)"] - sub_row["startTime(match)"] > timedelta(days=365): # 최근 1년 경기가 아니면
                break
            else:
                if sub_row["esportsTeamId_Blue"] == row["esportsTeamId_Red"] and sub_row["winner_side"] == "Blue":
                    redteam_wincount += 1
                elif sub_row["esportsTeamId_Red"] == row["esportsTeamId_Red"] and sub_row["winner_side"] == "Red":
                    redteam_wincount += 1
        redteam_wincount += 1 # 이건 100%가 나오는걸 피하기 위해 임의로 1승을 추가한 것임.
        redteam_winrate = redteam_wincount / (subdata_redteam.shape[0] + 2)  # + 2의 의미는 임의로 2전을 추가해서 바로위에 wincount+1한거와 함께 1전 1패의 가상데이터를 넣어준거임. 이렇게 100%와 0%의 극단적인 경우를 피해봄
        
        headtohead_wincount = 0     # 같은 팀이 만났을때 블루팀!!의 승리 횟수 (나중에 rate를 구할 때 0~1의 값으로 나올 것임)
        subdata_headtohead = previous_subdata_df[
            ((previous_subdata_df["esportsTeamId_Blue"] == row["esportsTeamId_Blue"]) & 
            (previous_subdata_df["esportsTeamId_Red"] == row["esportsTeamId_Red"])) |
            ((previous_subdata_df["esportsTeamId_Blue"] == row["esportsTeamId_Red"]) & 
            (previous_subdata_df["esportsTeamId_Red"] == row["esportsTeamId_Blue"]))
        ]
        for sub_idx, sub_row in subdata_headtohead.iterrows():
            if row["startTime(match)"] - sub_row["startTime(match)"] > timedelta(days=365): # 최근 1년 경기가 아니면
                break
            else:
                if sub_row["esportsTeamId_Blue"] == row["esportsTeamId_Blue"] and sub_row["winner_side"] == "Blue": # 현재 블루팀과 비교할 블루팀이 같으면서 블루팀이 이겼을 경우
                    headtohead_wincount += 1
                elif sub_row["esportsTeamId_Red"] == row["esportsTeamId_Blue"] and sub_row["winner_side"] == "Red": # 현재 블루팀과 레드팀이 비교할 게임에서 서로 진영을 바꾸었는데 레드팀이 이겼을 경우(결국 같은 팀이 이겼나를 보기 위한 조건이다)
                    headtohead_wincount += 1
        headtohead_wincount += 1
        headtohead_winrate = headtohead_wincount / (subdata_headtohead.shape[0] + 2)
        #print(f"팀 ID {row["esportsTeamId_Blue"]} 와 {row["esportsTeamId_Red"]} 이 붙었을 때 {row["esportsTeamId_Blue"]} 가 이긴 확률은 {headtohead_winrate * 100}% 입니다.")
        
        ##### 아래는 선수별 최근 n경기 스탯을 통해 폼을 뽑아내는 코드 #####
        desired_labels = [f'esportsPlayerId_{j}' for j in range(PARTICIPANT_NUMBER_OF_A_TEAM * 2)]
        for i in range(PARTICIPANT_NUMBER_OF_A_TEAM * 2):   # 선수 10명에 대해
            playerstat_list = []    # 선수별 최근 n경기의 기록을 저장할 곳
            role = i % 5
            subdata_playerstat = previous_subdata_df[(previous_subdata_df[f"esportsPlayerId_{role}"] == row[f"esportsPlayerId_{i}"]) |
                                                     (previous_subdata_df[f"esportsPlayerId_{role + PARTICIPANT_NUMBER_OF_A_TEAM}"] == row[f"esportsPlayerId_{i}"])].head(RANGE_OF_RECENT_GAME)
            number_of_past_games_of_player = subdata_playerstat.shape[0]
            #print(row[f"esportsPlayerId_{i}"])

            for sub_idx, sub_row in subdata_playerstat.iterrows():
                #딕셔너리로 만들어서 playerstat_list에 append하자. 그 다음에 형태를 보자.
                playerstat_dict_of_the_game = {}    # 한 경기에 대한 플레이어 활약상을 넣을 딕셔너리
                game_ids_of_sub_row = sub_row[desired_labels]
                matched_column = game_ids_of_sub_row[game_ids_of_sub_row.values == row[f"esportsPlayerId_{i}"]].index[0]      # ID가 서로 맞는 컬럼이 어디인지(블루팀인지레드팀인지 모르니까)
                matched_column_number = matched_column[matched_column.find("_")+1:]     # 번호 추출
                target_game = calculateColumnsForModel(last_row_of_collected_datas_df[last_row_of_collected_datas_df["gameId"] == sub_row["gameId"]].T.squeeze())
                #print(target_game["gameId"])
                playerstat_dict_of_the_game["kda"] = target_game[f"kda_{matched_column_number}"]
                playerstat_dict_of_the_game["championDamageShare"] = target_game[f"championDamageShare_{matched_column_number}"]
                playerstat_dict_of_the_game["creepScorePerTime"] = target_game[f"creepScorePerTime_{matched_column_number}"]
                playerstat_dict_of_the_game["wardsScorePerTime"] = target_game[f"wardsScorePerTime_{matched_column_number}"]
                playerstat_dict_of_the_game["goldEarnedPerTime"] = target_game[f"goldEarnedPerTime_{matched_column_number}"]
                #print(playerstat_dict_of_the_game)
                playerstat_list.append(playerstat_dict_of_the_game)
                # 넣을거 : kda, championDamageShare, creepScore, wardsScore, goldEarned
            
            #print(number_of_past_games_of_player)
            if number_of_past_games_of_player <= 1:         # 해당 선수의 지난 경기 데이터가 1개 이하이면
                #print("number_of_past_games_of_player <= 1")
                playerstat_dict_of_the_game = {         # 빈 자리에 일반적인 평균을 채워 넣고
                    "kda" : average_playerstat[f"kdaof{numberToRoleName(i)}"],
                    "championDamageShare" : average_playerstat[f"championDamageShareof{numberToRoleName(i)}"],
                    "creepScorePerTime" : average_playerstat[f"creepScorePerTimeof{numberToRoleName(i)}"],
                    "wardsScorePerTime" : average_playerstat[f"wardsScorePerTimeof{numberToRoleName(i)}"],
                    "goldEarnedPerTime" : average_playerstat[f"goldEarnedPerTimeof{numberToRoleName(i)}"]
                }
                for j in range(number_of_past_games_of_player, RANGE_OF_RECENT_GAME):   # 만약 1개면 첫번째만 채워졌을거니 range(1,5)를 해서 4번 반복하는 것이 맞다
                    playerstat_list.append(playerstat_dict_of_the_game)
            else:       # 선수의 지난 데이터가 2개 이상이면, 지난경기가 원한 만큼 다 차도 상관없다 왜냐하면 range에서 리스트를 안 주는 식으로 하면 되니까.
                sum_of_playerstat_dict_of_the_game = {
                    "kda" : 0,
                    "championDamageShare" : 0,
                    "creepScorePerTime" : 0,
                    "wardsScorePerTime" : 0,
                    "goldEarnedPerTime" : 0
                }
                average_of_playerstat_dict_of_the_game = {}
                for playerstat in playerstat_list: # 덧셈과 나눗셈 연산을 써서 시리즈의 평균을 구하자.
                    sum_of_playerstat_dict_of_the_game["kda"] = sum_of_playerstat_dict_of_the_game["kda"] + playerstat["kda"]
                    sum_of_playerstat_dict_of_the_game["championDamageShare"] = sum_of_playerstat_dict_of_the_game["championDamageShare"] + playerstat["championDamageShare"]
                    sum_of_playerstat_dict_of_the_game["creepScorePerTime"] = sum_of_playerstat_dict_of_the_game["creepScorePerTime"] + playerstat["creepScorePerTime"]
                    sum_of_playerstat_dict_of_the_game["wardsScorePerTime"] = sum_of_playerstat_dict_of_the_game["wardsScorePerTime"] + playerstat["wardsScorePerTime"]
                    sum_of_playerstat_dict_of_the_game["goldEarnedPerTime"] = sum_of_playerstat_dict_of_the_game["goldEarnedPerTime"] + playerstat["goldEarnedPerTime"]
                average_of_playerstat_dict_of_the_game["kda"] = sum_of_playerstat_dict_of_the_game["kda"] / number_of_past_games_of_player
                average_of_playerstat_dict_of_the_game["championDamageShare"] = sum_of_playerstat_dict_of_the_game["championDamageShare"] / number_of_past_games_of_player
                average_of_playerstat_dict_of_the_game["creepScorePerTime"] = sum_of_playerstat_dict_of_the_game["creepScorePerTime"] / number_of_past_games_of_player
                average_of_playerstat_dict_of_the_game["wardsScorePerTime"] = sum_of_playerstat_dict_of_the_game["wardsScorePerTime"] / number_of_past_games_of_player
                average_of_playerstat_dict_of_the_game["goldEarnedPerTime"] = sum_of_playerstat_dict_of_the_game["goldEarnedPerTime"] / number_of_past_games_of_player
                for j in range(number_of_past_games_of_player, RANGE_OF_RECENT_GAME):
                    playerstat_list.append(average_of_playerstat_dict_of_the_game)
            if i == 0:  # 첫번째선수니까 데이터프레임을 새로 만들고
                #print("playerstat_list : ", playerstat_list)
                player_form = pd.DataFrame(playerstat_list)
                player_form.reset_index(inplace=True)
                #print("player_form : ", player_form)
                player_form.rename(columns = {"index":"recentGameNumber"}, inplace=True)
            else:       # 아니면 위아래로 이어붙이는 작업
                #print(player_form)
                temp_player_form = pd.DataFrame(playerstat_list)
                temp_player_form.reset_index(inplace=True)
                temp_player_form.rename(columns = {"index":"recentGameNumber"}, inplace=True)
                player_form = pd.concat([player_form, temp_player_form], ignore_index=True)
        #print(player_form)
        # 나온 선수별 폼을 팀별 승률과 이어붙이는 곳
        columns_of_role = []
        for i in range(2):  # 블루팀과 레드팀 2개
            columns_of_role.extend(["Top" for j in range(PARTICIPANT_NUMBER_OF_A_TEAM)])
            columns_of_role.extend(["Jgl" for j in range(PARTICIPANT_NUMBER_OF_A_TEAM)])
            columns_of_role.extend(["Mid" for j in range(PARTICIPANT_NUMBER_OF_A_TEAM)])
            columns_of_role.extend(["Adc" for j in range(PARTICIPANT_NUMBER_OF_A_TEAM)])
            columns_of_role.extend(["Spt" for j in range(PARTICIPANT_NUMBER_OF_A_TEAM)])
        
        each_team_winrate_extended = [blueteam_winrate for i in range(PARTICIPANT_NUMBER_OF_A_TEAM * 5)] # 역할군 갯수가 5개, 총 25개만큼 복제
        each_team_winrate_extended.extend([redteam_winrate for i in range(PARTICIPANT_NUMBER_OF_A_TEAM * 5)])
        columns_of_each_team_winrate_extended = ["Blue" for i in range(PARTICIPANT_NUMBER_OF_A_TEAM * 5)]
        columns_of_each_team_winrate_extended.extend(["Red" for i in range(PARTICIPANT_NUMBER_OF_A_TEAM * 5)])
        headtohead_winrate_extended = [headtohead_winrate for i in range(PARTICIPANT_NUMBER_OF_A_TEAM * 5 * 2)]
        winnerside_extended = [row["winner_side"] for i in range(PARTICIPANT_NUMBER_OF_A_TEAM * 5 * 2)]
        
        each_team_winrate_dict = {                                  # 50개 행으로 만들 예정
            "HeadtoHeadWinrate" : headtohead_winrate_extended,
            "winnerSide" : winnerside_extended,                     # 라벨, !!!! 제 일 중 요 !!!!
            "Side" : columns_of_each_team_winrate_extended,         # "Blue" 또는 "Red", 피벗테이블의 컬럼으로 만들 예정
            "TeamWinrate" : each_team_winrate_extended,             # Side에 따라 다른 값
            "Role" : columns_of_role
        }
        dataset_of_a_game_df = pd.DataFrame(each_team_winrate_dict)
        dataset_of_a_game_df = pd.concat([dataset_of_a_game_df, player_form], axis=1, ignore_index=True)
        dataset_of_a_game_df.columns = (["gameId", "HeadtoHeadWinrate", "winner", "Side", "TeamWinrate", "Role", "recentGameNumber", "kda", "championDamageShare", "creepScorePerTime", "wardsScorePerTime", "goldEarnedPerTime"])
        #print(dataset_of_a_game_df)
        if pre_make_pivot_table_df is None:
            pre_make_pivot_table_df = dataset_of_a_game_df
        else:
            pre_make_pivot_table_df = pd.concat([pre_make_pivot_table_df, dataset_of_a_game_df], ignore_index=True)
    # 인덱스는 for문 밖에서 독립적으로 만들어서 잇자, 왜냐하면 현재 기준 테이블 만들 때 코드 같이쓰게.
    # 그럴라그랬는데 귀찮다... 일단 인덱스 만들어서 확인하자
pre_make_pivot_table_df.to_excel("pre_make_pivot_table.xlsx", index=False)    
