import pandas as pd
import time
from tqdm import tqdm, tqdm_pandas
import numpy as np
import os
from requestWithHandlingHttperr import requestWithHandlingHttperr

# 토너먼트 리스트에서 상세데이터를 뽑아오기 위한 게임id를 추출하는 코드.
def getGameIds():
    headers = {
        "x-api-key" : "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z",   # https://vickz84259.github.io/lolesports-api-docs/ 에 공개된 key라 코드에 넣어도 괜찮다.
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
    }
    resultlist = []
    tournaments = pd.read_excel("../data/pentakill 경기 상세데이터 수집기록.xlsx", sheet_name= "경기 세부 링크")["id"] # 본 데이터
    #tournaments = pd.read_excel("../data/target_tournament_for_test.xlsx")["id"]        # 테스트 데이터 토너먼트 자료
    for tournament in tqdm(tournaments):
        apiResult = requestWithHandlingHttperr(f"https://prod-relapi.ewp.gg/persisted/gw/getCompletedEvents?hl=en-US&tournamentId={tournament}", headers=headers)
        if apiResult.status_code == 200:
            json = apiResult.json()
            if 'data' in json and len(json['data']) > 0:
                events = json["data"]['schedule']['events']
                for event in events:
                    match = event["match"]
                    games = event["games"]
                    blueteam = match["teams"][0]
                    redteam = match["teams"][1]
                    for idx, game in enumerate(games):
                        if "vods" in game and len(game["vods"]) > 0:
                            game_data = {
                                "startTime(match)" : event["startTime"][:19]+"Z",
                                "tournamentId" : str(tournament),
                                "blockName" : event["blockName"],
                                "leagueName": event["league"]["name"],
                                "matchId": str(match["id"]),
                                "bestof": match["strategy"]["count"],
                                "blueteam_name" : blueteam["name"],
                                "blueteam_code" : blueteam["code"],
                                "blueteam_win" : blueteam["result"]["gameWins"],
                                "redteam_name" : redteam["name"],
                                "redteam_code" : redteam["code"],
                                "redteam_win" : redteam["result"]["gameWins"],
                                "gameNumberInAMatch": idx,
                                "gameId": str(game["id"])
                            }
                            resultlist.append(game_data)
        time.sleep(1)
    game_ids_df = pd.DataFrame(resultlist)
    game_ids_df = game_ids_df.astype({"matchId":"str", "gameId":"str"})
    return game_ids_df

def addPatch(gameId):
    window_url = f"https://feed.lolesports.com/livestats/v1/window/{gameId}"
    apiResult = requestWithHandlingHttperr(window_url)
    if apiResult.status_code == 200:
        json_data = apiResult.json()
        if 'gameMetadata' in json_data and len(json_data['gameMetadata']) > 0:
            game = json_data["gameMetadata"]
            if game.get("patchVersion") is not None:
                patch_ver = game["patchVersion"]
                where = patch_ver.find(".")
                patch_ver = patch_ver[:patch_ver[where+1:].find(".")+where+1] # [where+1:]부터 "."의 위치를 찾았으니까 인덱스가 예상한것보다 한 칸 앞으로 당겨져 있을것이므로 +1을 넣어 보정.
                return patch_ver
    return np.nan
"""
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
"""
######## 아래부턴 실행되는 부분 #######

tqdm.pandas()
game_ids = getGameIds() # 게임아이디가 들어간 리스트

game_ids["patch"] = game_ids.progress_apply(lambda row : addPatch(row["gameId"]), axis=1)
#game_ids = game_ids.progress_apply(lambda row : addPicksAndTeamCode(row), axis = 1)

game_ids.to_excel("../data/game_ids.xlsx", index=None)     # 본 데이터 뽑을 때
#game_ids.to_excel("../data/game_ids_for_test.xlsx", index=None) # 테스트 데이터 뽑을 때