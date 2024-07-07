# 선수의 게임 한판 기록을 보기 위해서 일일히 collected_data 찾아가서 게임번호 찾아 들어가려니까 너무 시간이 오래걸린다.
# 이럴바에 기록은 어차피 마지막줄에만 나오니까 마지막줄의 기록들을 전부 한곳에 모아두는 코드를 하나 짠다.

import pandas as pd
import os
from tqdm import tqdm
from common_constants import PARTICIPANTS_NUMBER_OF_A_TEAM

DETAIL_PATH = "../data/collected_data/"
#DETAIL_PATH = "../data/collected_data_test/"
file_list = os.listdir(DETAIL_PATH)
table = []
strcolumn_dict = {"esportsTeamId_Blue":"str", "esportsTeamId_Red":"str"}
temp1 = [f"esportsPlayerId_{i}" for i in range(10)]
temp2 = ["str" for i in range(10)]
esportsPlayerId_type_dict = dict(zip(temp1, temp2))
strcolumn_dict.update(esportsPlayerId_type_dict)        # ID 들이 str로 들어오지 않으면 값이 잘리는 문제가 있다. ID들을 str로 읽어오는 작업.

for file in tqdm(file_list):
    if file.find("_") == -1 and file.find("xlsx") != -1:    # 정상적인 파일들에 대해서(invalid, tooshort가 아닌 것들)
        game_id = base_name = os.path.splitext(file)[0]     # 파일명만 따와
        row_list = [game_id]                                # 게임 id만 들어간 리스트를 만들어 초기화. (나중에 데이터들 이어붙일거임)
        row_series = pd.Series(game_id, index = ["gameId"]) # 시리즈로 변환
        df = pd.read_excel(DETAIL_PATH + file, dtype = strcolumn_dict)
        columns = ["duration", "esportsTeamId_Blue", "esportsTeamId_Red",\
            "blue_totalGold", "blue_inhibitors", "blue_towers", "blue_barons", "blue_totalKills", "blue_dragons_count",\
                "red_totalGold", "red_inhibitors", "red_towers", "red_barons", "red_totalKills", "red_dragons_count"]
        for i in range(PARTICIPANTS_NUMBER_OF_A_TEAM * 2):
            columns.extend([f"esportsPlayerId_{i}", f"teamCode_{i}", f"summonerName_{i}", f"championName_{i}"])
            columns.extend([f"level_{i}", f"maxHealth_{i}", f"kills_{i}", f"deaths_{i}", f"assists_{i}", f"totalGoldEarned_{i}",\
                f"creepScore_{i}", f"killParticipation_{i}", f"championDamageShare_{i}", f"wardsPlaced_{i}", f"wardsDestroyed_{i}"])
        last_row = list(df.iloc[-1][columns])   # 마지막 데이터에서 필요한 데이터만 뽑아 저장.
        row_list.extend(last_row)
        table.append(row_list)      # 데이터프레임에 들어갈 각 줄들을 리스트형식으로 저장해둠
last_row_df = pd.DataFrame(table)
columns_for_df = ["gameId"]
columns_for_df.extend(columns)
last_row_df.columns = columns_for_df

last_row_df.to_excel("../data/last_row_of_collected_datas.xlsx", index = False)
#last_row_df.to_excel("../data/last_row_of_collected_datas_of_test.xlsx", index = False)
        
        