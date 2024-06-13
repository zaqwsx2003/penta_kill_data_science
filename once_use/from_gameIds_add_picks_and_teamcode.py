# 수정이 필요하다. pick_last_row_of_collected_datas.py를 통해 각 디테일의 마지막 줄을 쭉 불러온 데이터가 있으니 매번 collected_data안에서 read_excel을 할 필요가 없다.

import pandas as pd
from tqdm import tqdm, tqdm_pandas
import numpy as np
import os

game_ids = pd.read_excel("../data/game_ids.xlsx")
game_ids = game_ids.astype({"tournamentId":"str","matchId":"str", "gameId":"str"})

def addPicksAndTeamCode(row):
    PARTICIPANT_NUMBER_OF_A_TEAM = 5
    gameId = row["gameId"]
    
    DETAIL_PATH = "../data/collected_data/"
    file_list = os.listdir(DETAIL_PATH)
    if gameId + ".xlsx" in file_list:
        detail_data = pd.read_excel(DETAIL_PATH + gameId + ".xlsx")
        for i in range(PARTICIPANT_NUMBER_OF_A_TEAM * 2):
            row[f"pick_{i}"] = detail_data.at[0, f"championName_{i}"]
        for j in range(PARTICIPANT_NUMBER_OF_A_TEAM * 2):
            row[f"summonerName_{j}"] = detail_data.at[0, f"summonerName_{j}"]
        for k in range(PARTICIPANT_NUMBER_OF_A_TEAM * 2):
            row[f"esportsPlayerId_{k}"] = str(detail_data.at[0, f"esportsPlayerId_{k}"])
        row["teamcode_blue_on_detail"] = detail_data.at[0, "teamCode_0"]
        row["teamcode_red_on_detail"] = detail_data.at[0, "teamCode_5"]
    else:
        for i in range(PARTICIPANT_NUMBER_OF_A_TEAM * 2):
            row[f"pick_{i}"] = np.nan
        for j in range(PARTICIPANT_NUMBER_OF_A_TEAM * 2):
            row[f"summonerName_{j}"] = np.nan
        for k in range(PARTICIPANT_NUMBER_OF_A_TEAM * 2):
            row[f"esportsPlayerId_{k}"] = np.nan
        row["teamcode_blue_on_detail"] = np.nan
        row["teamcode_red_on_detail"] = np.nan
    if len(row) != 47:
        print(f"gameId: {gameId}, row length: {len(row)}")
    return row

tqdm.pandas()
game_ids = game_ids.progress_apply(lambda row : addPicksAndTeamCode(row), axis = 1)
game_ids.to_excel("../data/game_ids.xlsx", index=None)