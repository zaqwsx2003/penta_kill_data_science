import pandas as pd
from tqdm import tqdm, tqdm_pandas
from common_constants import PARTICIPANTS_NUMBER_OF_A_TEAM, PITCHERS_NUMBER_OF_A_PLAYER

# 선수 정보가 역할군 순서대로 들어오고 있으니 번호에따라 이름을 부여하는 함수.
def numberToRoleName(number):
    if number == 0 or number == 5:
        return "Top"
    elif number == 1 or number == 6:
        return "Jgl"
    elif number == 2 or number == 7:
        return "Mid"
    elif number == 3 or number == 8:
        return "Adc"
    else:
        return "Spt"

# 게임 상세데이터에서 모델 학습데이터에 필요한 추가 피처를 만들어 추가로 붙인 뒤 반환하는 함수.
# 아쉬운점 : 피쳐 분석이 여기서도 들어가고 있다. 예를들어 kda와 와드스코어를 계산해서 넣은 점. 여기서 계산하지 말고 pitcheranalyze.py에서 계산했으면 조금 더 깔끔할 뻔했다.
def calculateColumnsForModel(row): # last_row_of_collected_data.xlsx의 각 줄을 입력받아 추가정보를 반환합니다.
    for i in range(PARTICIPANTS_NUMBER_OF_A_TEAM * 2):  # 경기에 참여하는 선수 10명에 대해서
        kills = row[f"kills_{i}"]
        deaths = row[f"deaths_{i}"]
        assists = row[f"assists_{i}"]
        if deaths == 0:                         # 0으로 나누는 것 방지
            kda = (kills + assists) * 1.2   # LCK에서는 노데스로 끝난 선수에게는 1데스시 kda의 1.2배를 곱한 값을 kda로 표시해주고 있다.
        else:
            kda = (kills + assists) / deaths
        row[f"kda_{i}"] = kda
        
        row[f"killsPerTime_{i}"] = row[f"kills_{i}"] / row["duration"]              # duration을 나눠준 이유는 경기가 길어질수록 누적되는 경향이 강한 피처이기 때문이다.
        row[f"deathsPerTime_{i}"] = row[f"deaths_{i}"] / row["duration"]
        row[f"assistsPerTime_{i}"] = row[f"assists_{i}"] / row["duration"]
        row[f"creepScorePerTime_{i}"] = row[f"creepScore_{i}"] / row["duration"]
        wardsPlacedScore = row[f"wardsPlaced_{i}"] * 1.5        # 공식 시야점수를 계산하는 계산식에서는 와드를 놓은 게 와드를 지운 것보다 더 중요하다고 한다.
        row[f"wardsScorePerTime_{i}"] = (wardsPlacedScore + row[f"wardsDestroyed_{i}"]) / row["duration"]
        row[f"goldEarnedPerTime_{i}"] = row[f"totalGoldEarned_{i}"] / row["duration"]
    
    
    for i in range(PARTICIPANTS_NUMBER_OF_A_TEAM):      # 이부분은 선수들 스탯의 중간값계산 시 사용하고 있다.
        row[f"kdaof{numberToRoleName(i)}"] = (row[f"kda_{i}"] + row[f"kda_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]) / 2
        row[f"killsPerTimeof{numberToRoleName(i)}"] = (row[f"killsPerTime_{i}"] + row[f"killsPerTime_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]) / 2
        row[f"deathsPerTimeof{numberToRoleName(i)}"] = (row[f"deathsPerTime_{i}"] + row[f"deathsPerTime_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]) / 2
        row[f"assistsPerTimeof{numberToRoleName(i)}"] = (row[f"assistsPerTime_{i}"] + row[f"assistsPerTime_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]) / 2
        row[f"championDamageShareof{numberToRoleName(i)}"] = (row[f"championDamageShare_{i}"] + row[f"championDamageShare_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]) / 2
        row[f"creepScorePerTimeof{numberToRoleName(i)}"] = (row[f"creepScorePerTime_{i}"] + row[f"creepScorePerTime_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]) / 2
        row[f"wardsScorePerTimeof{numberToRoleName(i)}"] = (row[f"wardsScorePerTime_{i}"] + row[f"wardsScorePerTime_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]) / 2
        row[f"goldEarnedPerTimeof{numberToRoleName(i)}"] = (row[f"goldEarnedPerTime_{i}"] + row[f"goldEarnedPerTime_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"]) / 2
    return row

def getMedianOfCollectedData(): # 미리 저장된 파일을 불러와서 시리즈 형태로 포지션 별 중간값을 내보낸다
    strcolumn_dict = {"gameId":"str", "esportsTeamId_Blue":"str", "esportsTeamId_Red":"str"}
    temp1 = [f"esportsPlayerId_{i}" for i in range(PARTICIPANTS_NUMBER_OF_A_TEAM * 2)]
    temp2 = ["str" for i in range(PARTICIPANTS_NUMBER_OF_A_TEAM * 2)]
    esportsPlayerId_type_dict = dict(zip(temp1, temp2))
    strcolumn_dict.update(esportsPlayerId_type_dict)
    df = pd.read_excel("../data/last_row_of_collected_datas.xlsx", dtype = strcolumn_dict)
    #df = pd.read_excel("../data/last_row_of_collected_datas_of_test.xlsx", dtype = strcolumn_dict)
    tqdm.pandas()
    new_df = df.progress_apply(lambda row : calculateColumnsForModel(row), axis=1)
    desired_columns_of_new_df = new_df.iloc[:, -1 * (PARTICIPANTS_NUMBER_OF_A_TEAM * PITCHERS_NUMBER_OF_A_PLAYER):]
    medians = desired_columns_of_new_df.median()[-1 * (PARTICIPANTS_NUMBER_OF_A_TEAM * PITCHERS_NUMBER_OF_A_PLAYER):]   # 뒤쪽 40개 컬럼의 중간값을 구함.
    #medians.to_excel("../data/median_of_collected_datas.xlsx")
    return medians