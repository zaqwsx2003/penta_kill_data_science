import pandas as pd
from calculateColumnsForModel import numberToRoleName
from pitcheranalyze import pitcheranalyze
import joblib
from common_constants import PITCHERS_NUMBER_OF_A_PLAYER, STAT_MEDIAN_MULTIPLIER

def getMedian(flag, role):
    role = role % 5
    if flag == 0:       # 모델 만들 데이터
        if role == 0:
            median = {
                "kda" : 3.93333333333333,
                "killsPerTime" : 0.0012396694214876,
                "deathsPerTime" : 0.00136986301369863,
                "assistsPerTime" : 0.0023972602739726,
                "championDamageShare" : 0.228523154923377,
                "creepScorePerTime" : 0.133996402877698,
                "wardsScorePerTime" : 0.0128080095122445,
                "goldEarnedPerTime" : 6.4429331869941
            }
        elif role == 1:
            median = {
                "kda" : 5.0,
                "killsPerTime" : 0.00122448979591837,
                "deathsPerTime" : 0.00145348837209302,
                "assistsPerTime" : 0.00348360655737705,
                "championDamageShare" : 0.144554837154089,
                "creepScorePerTime" : 0.0917910447761194,
                "wardsScorePerTime" : 0.0148372890472669,
                "goldEarnedPerTime" : 5.60251262626263
            }
        elif role == 2:
            median = {
                "kda" : 5.3,
                "killsPerTime" : 0.00161290322580645,
                "deathsPerTime" : 0.00124223602484472,
                "assistsPerTime" : 0.0028125,
                "championDamageShare" : 0.261571385007903,
                "creepScorePerTime" : 0.143388523991972,
                "wardsScorePerTime" : 0.0131656804733728,
                "goldEarnedPerTime" : 6.70846681695934
            }
        elif role == 3:
            median = {
                "kda" : 5.79285714285714,
                "killsPerTime" : 0.00202312138728324,
                "deathsPerTime" : 0.00112107623318386,
                "assistsPerTime" : 0.00251396648044693,
                "championDamageShare" : 0.272831173686407,
                "creepScorePerTime" : 0.155673758865248,
                "wardsScorePerTime" : 0.016043778434033,
                "goldEarnedPerTime" : 7.26228078187797
            }
        elif role == 4:
            median = {
                "kda" : 4.83333333333333,
                "killsPerTime" : 0.000297619047619048,
                "deathsPerTime" : 0.0014792899408284,
                "assistsPerTime" : 0.0044793720078851,
                "championDamageShare" : 0.0746235333980816,
                "creepScorePerTime" : 0.0183673469387755,
                "wardsScorePerTime" : 0.0441531378196736,
                "goldEarnedPerTime" : 4.00327956989247
            }
    else:               # 테스트용 2군데이터의 중간값들.
        if role == 0:
            median = {
                "kda" : 3.83333333333333,
                "killsPerTime" : 0.00128205128205128,
                "deathsPerTime" : 0.0014367816091954,
                "assistsPerTime" : 0.00247524752475248,
                "championDamageShare" : 0.220507199421588,
                "creepScorePerTime" : 0.131198347107438,
                "wardsScorePerTime" : 0.0115942028985507,
                "goldEarnedPerTime" : 6.41656626506024
            }
        elif role == 1:
            median = {
                "kda" : 4.8,
                "killsPerTime" : 0.00129032258064516,
                "deathsPerTime" : 0.00159574468085106,
                "assistsPerTime" : 0.00377777777777778,
                "championDamageShare" : 0.152753601644056,
                "creepScorePerTime" : 0.0904371584699454,
                "wardsScorePerTime" : 0.0118852459016393,
                "goldEarnedPerTime" : 5.63806818181818
            }
        elif role == 2:
            median = {
                "kda" : 5.25,
                "killsPerTime" : 0.001875,
                "deathsPerTime" : 0.00135135135135135,
                "assistsPerTime" : 0.00283842794759825,
                "championDamageShare" : 0.262517327620449,
                "creepScorePerTime" : 0.14,
                "wardsScorePerTime" : 0.0119642857142857,
                "goldEarnedPerTime" : 6.7061403508772
            }
        elif role == 3:
            median = {
                "kda" : 5.65,
                "killsPerTime" : 0.00217391304347826,
                "deathsPerTime" : 0.00127118644067797,
                "assistsPerTime" : 0.00272727272727273,
                "championDamageShare" : 0.265917010918836,
                "creepScorePerTime" : 0.147445255474453,
                "wardsScorePerTime" : 0.0133435582822086,
                "goldEarnedPerTime" : 7.12632743362832
            }
        elif role == 4:
            median = {
                "kda" : 4.75,
                "killsPerTime" : 0.000324675324675325,
                "deathsPerTime" : 0.00157068062827225,
                "assistsPerTime" : 0.00496688741721854,
                "championDamageShare" : 0.0780657798483896,
                "creepScorePerTime" : 0.0168269230769231,
                "wardsScorePerTime" : 0.0384868421052632,
                "goldEarnedPerTime" : 4.05771604938272
            }
        
    return median

def getPredictData(match):
    players_form_df = None
    present_data = joblib.load('../data/present_data.pkl')                  # 현재기준 팀과 선수의 수치를 모아놓은 딕셔너리파일
    #present_data = joblib.load('../data/present_data_for_test.pkl')
    model, scaler, X_columns = joblib.load('../data/model_draft7_1_2.pkl')  # 모델을 불러옴.
    teams = match["teams"]
    blueteam = teams[0]
    redteam = teams[1]
    blueteam_id = blueteam["esportsTeamId"]
    redteam_id = redteam["esportsTeamId"]
    blueteam_players = blueteam["participantMetadata"]
    redteam_players = redteam["participantMetadata"]            # 입력 json데이터를 읽어들여 변수에 저장.

    # 입력된 팀이 우리 present_data 딕셔너리에 있으면 가져오고, 없으면 중간값을 넣어줌.
    blue_winrate = present_data['team_history'][blueteam_id]["self"]["winrate"] if present_data["team_history"].get(blueteam_id) else 0.5
    blue_golddiff = present_data['team_history'][blueteam_id]["self"]["golddiff"] if present_data["team_history"].get(blueteam_id) else 0
    blue_killdiff = present_data['team_history'][blueteam_id]["self"]["killdiff"] if present_data["team_history"].get(blueteam_id) else 0
    headtohead_winrate = present_data['team_history'][blueteam_id][redteam_id]["winrate"] if present_data["team_history"].get(blueteam_id) and present_data["team_history"][blueteam_id].get(redteam_id) else 0.5
    headtohead_golddiff = present_data['team_history'][blueteam_id][redteam_id]["golddiff"] if present_data["team_history"].get(blueteam_id) and present_data["team_history"][blueteam_id].get(redteam_id) else 0
    headtohead_killdiff = present_data['team_history'][blueteam_id][redteam_id]["killdiff"] if present_data["team_history"].get(blueteam_id) and present_data["team_history"][blueteam_id].get(redteam_id) else 0
    red_winrate = present_data['team_history'][redteam_id]["self"]["winrate"] if present_data["team_history"].get(redteam_id) else 0.5
    red_golddiff = present_data['team_history'][redteam_id]["self"]["golddiff"] if present_data["team_history"].get(redteam_id) else 0
    red_killdiff = present_data['team_history'][redteam_id]["self"]["killdiff"] if present_data["team_history"].get(redteam_id) else 0

    # 이 부분은 피벗테이블을 만들기 위해 컬럼이 될 부분을 인위적으로 데이터프레임 형식으로 만들어 붙여준 부분인데, 지금 생각해보니 피벗테이블이 필요 없었을지도 모르겠다. 양쪽 다 번거로울 수 있겠지만.
    columns_of_role = []
    for i in range(2):  # 블루팀과 레드팀 2개
        columns_of_role.extend(["Top" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
        columns_of_role.extend(["Jgl" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
        columns_of_role.extend(["Mid" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
        columns_of_role.extend(["Adc" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
        columns_of_role.extend(["Spt" for j in range(PITCHERS_NUMBER_OF_A_PLAYER)])
    columns_of_each_team_side = ["Blue" for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)]
    columns_of_each_team_side.extend(["Red" for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5)])
    matchid_extended = [match["matchId"] for i in range(PITCHERS_NUMBER_OF_A_PLAYER * 5 * 2)]
    columns_dict = {
        "matchId" : matchid_extended,
        "side" : columns_of_each_team_side,
        "role" : columns_of_role
    }
    columns_df = pd.DataFrame(columns_dict)

    for idx, player in enumerate(blueteam_players):     # 블루팀 선수 5명
        player_id = player["esportsPlayerId"]
        if present_data["player_form"].get(numberToRoleName(idx)) and present_data["player_form"][numberToRoleName(idx)].get(player_id, None) is not None:
            player_form = present_data["player_form"][numberToRoleName(idx)][player_id]     # 선수 데이터가 있으면 불러옴.
        else:
            median_player_dict = {key: value * STAT_MEDIAN_MULTIPLIER for key, value in getMedian(0, idx).items()}    # 없으면 중간값의 0.7만큼을 채워줌
            #median_player_dict = {key: value * STAT_MEDIAN_MULTIPLIER for key, value in getMedian(1, idx).items()}
            player_form = pd.DataFrame(median_player_dict, index=[0]).T     # 피벗 테이블을 위해 형식 맞춰주는 부분.
            player_form.reset_index(inplace = True)
            player_form.columns = ["elements", "formvalue"]
        if players_form_df is None:
            players_form_df = player_form
        else:
            players_form_df = pd.concat([players_form_df, player_form], ignore_index = True)
    for idx, player in enumerate(redteam_players):
        player_id = player["esportsPlayerId"]
        if present_data["player_form"].get(numberToRoleName(idx)) and present_data["player_form"][numberToRoleName(idx)].get(player_id, None) is not None:
            player_form = present_data["player_form"][numberToRoleName(idx)][player_id]     # 선수 데이터가 있으면 불러옴.
        else:
            median_player_dict = {key: value * STAT_MEDIAN_MULTIPLIER for key, value in getMedian(0, idx).items()}    # 없으면 중간값의 0.7만큼을 채워줌.
            #median_player_dict = {key: value * STAT_MEDIAN_MULTIPLIER for key, value in getMedian(1, idx).items()}
            player_form = pd.DataFrame(median_player_dict, index=[0]).T     # 피벗 테이블을 위해 형식 맞춰주는 부분.
            player_form.reset_index(inplace = True)
            player_form.columns = ["elements", "formvalue"]
        if players_form_df is None:
            players_form_df = player_form
        else:
            players_form_df = pd.concat([players_form_df, player_form], ignore_index = True)
    players_form_df = pd.concat([columns_df, players_form_df], axis=1, ignore_index=True)
    players_form_df.columns = ["matchId", "side", "role", "elements", "formvalue"]
    players_form_df = pd.pivot_table(                           # 만들었다. 피벗테이블. 나중에 안 거지만 기계학습엔 평탄화된 테이블이 더 좋다고 한다.
        players_form_df,
        values="formvalue",
        index=["matchId"],
        columns=["side", "role", "elements"]
    ).reset_index()
    players_form_df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in players_form_df.columns] # 기껏 피벗테이블 만들어놓고 바로 평탄화...
    players_form_df["Blue_Winrate"] = blue_winrate
    players_form_df["Blue_GoldDiff"] = blue_golddiff
    players_form_df["Blue_KillDiff"] = blue_killdiff
    players_form_df["Red_Winrate"] = red_winrate
    players_form_df["Red_GoldDiff"] = red_golddiff
    players_form_df["Red_KillDiff"] = red_killdiff
    players_form_df["headtoHeadWinrate"] = headtohead_winrate
    players_form_df["headtoHeadGoldDiff"] = headtohead_golddiff
    players_form_df["headtoHeadKillDiff"] = headtohead_killdiff
    players_form_df.rename(columns = {"matchId__" : "matchId"}, inplace = True)
    players_form_df = pitcheranalyze(players_form_df)           # 피쳐 중 뺄건 빼고 넣을건 넣는 작업.
    players_form_df = players_form_df.drop(["matchId"], axis=1)
    players_form_df = players_form_df[X_columns]
    for column in players_form_df.columns:
        if column.find("_") != -1:
            suffix = column.split("_")[-1]
            players_form_df[column] = scaler[suffix].transform(players_form_df[column].values.reshape(-1, 1))       # 이게 사실 피벗테이블을 통해 달성하고자 했던 부분인데
                                                                                                                    # 표준화 할 때 기계적으로 모든 컬럼의 평균과 편차를 구한 것이 아니라 kda면 kda, 골드면 골드 이렇게 같은 속성 전체를 묶어 평균과 편차를 구해 표준화를 시켰다.
                                                                                                                    # 같은 suffix끼리 묶어 transform한 부분. fit은 데이터셋을 만들 때 했다.
    players_form_df["headtoHeadWinrate"] = scaler["headtoHeadWinrate"].transform(players_form_df["headtoHeadWinrate"].values.reshape(-1, 1))
    players_form_df["headtoHeadGoldDiff"] = scaler["headtoHeadGoldDiff"].transform(players_form_df["headtoHeadGoldDiff"].values.reshape(-1, 1))
    players_form_df["headtoHeadKillDiff"] = scaler["headtoHeadKillDiff"].transform(players_form_df["headtoHeadKillDiff"].values.reshape(-1, 1))
    players_form_df["teamWinrateDiff"] = scaler["teamWinrateDiff"].transform(players_form_df["teamWinrateDiff"].values.reshape(-1, 1))
    players_form_df["teamGoldDiff"] = scaler["teamGoldDiff"].transform(players_form_df["teamGoldDiff"].values.reshape(-1, 1))
    players_form_df["teamKillDiff"] = scaler["teamKillDiff"].transform(players_form_df["teamKillDiff"].values.reshape(-1, 1))
    predict = model.predict_proba(players_form_df)          # 확률을 뽑아내는 부분.
    return predict