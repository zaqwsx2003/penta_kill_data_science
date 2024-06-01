import pandas as pd
import requests
import time
from tqdm import tqdm
import numpy as np

# get_game_detail.py에서 2024년 5월 31일에 복사, 이거 이러지말고 모듈화해서 import 하고 싶은데 get_game_detail.py에 main()부분이 없어야 하는 건가?
def requestWithHandlingHttperr(url, headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}):
    RETRY_COUNT = 12                # 기본 반복 12회
    RETRY_DELAY_SEC = 10            # 대기 10초
    ERRNO_10054 = 10054
    ERRNO_500 = 500
    ERRNO_503 = 503
    ERRNO_504 = 504

    REQUEST_INTERVAL_SEC = 0.1

    #headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}  # 서버에 내 신분을 속이기 위한 유저에이전트... 자세히는 잘 모릅니다

    time.sleep(REQUEST_INTERVAL_SEC)    # 먼저 0.1초 쉬고

    for i in range(RETRY_COUNT):
        try:
            result = requests.get(url, headers = headers)       # API에 request 요청
            result.raise_for_status()                           # http에러가 나오면 예외를 발생시킴 -> except로 점프
            return result
        except requests.exceptions.ConnectionError as e:
            if isinstance(e.args[0], ConnectionResetError) and e.args[0].winerror == ERRNO_10054:
                print(f"Attempt {i + 1} failed with error 10054. Retrying in {RETRY_DELAY_SEC} seconds...")
                time.sleep(RETRY_DELAY_SEC)
            else:                           # 다른 http 에러면
                raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == ERRNO_500:
                print(f"Attempt {i + 1} failed with 500 Internal Server Error. Retrying in {RETRY_DELAY_SEC} seconds...")
                time.sleep(RETRY_DELAY_SEC)
            elif e.response.status_code == ERRNO_503:
                print(f"Attempt {i + 1} failed with 503 Service Unavailable. Retrying in {RETRY_DELAY_SEC} seconds...")
                time.sleep(RETRY_DELAY_SEC)
            elif e.response.status_code == ERRNO_504:
                print(f"Attempt {i + 1} failed with 504 Gateway Timeout. Retrying in {RETRY_DELAY_SEC} seconds...")
                time.sleep(RETRY_DELAY_SEC)
            else:  # 다른 HTTPError 예외 처리
                raise
    game_id = url[url.rfind("/") + 1:]
    print(f"Failed to fetch data from game ID : {game_id} after {RETRY_COUNT} attempts.")
    raise Exception(f"Failed to fetch data from game ID : {game_id} after {RETRY_COUNT} attempts")

def getGameIds():
    headers = {
        "x-api-key" : "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
    }
    resultlist = []
    tournaments = pd.read_excel("../data/pentakill 경기 상세데이터 수집기록.xlsx", sheet_name= "경기 세부 링크")["id"]
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
                                "matchId": match["id"],
                                "bestof": match["strategy"]["count"],
                                "blueteam_name" : blueteam["name"],
                                "blueteam_code" : blueteam["code"],
                                "blueteam_win" : blueteam["result"]["gameWins"],
                                "redteam_name" : redteam["name"],
                                "redteam_code" : redteam["code"],
                                "redteam_win" : redteam["result"]["gameWins"],
                                "gameNumberInAMatch": idx,
                                "gameId": game["id"]
                            }
                            resultlist.append(game_data)
        time.sleep(1)
    game_ids_df = pd.DataFrame(resultlist)
    return game_ids_df

######## 아래부턴 실행되는 부분 #######

result = []
game_ids = getGameIds() # 게임아이디가 들어간 리스트
for idx, row in tqdm(game_ids.iterrows(), total = 9293):
    window_url = f"https://feed.lolesports.com/livestats/v1/window/{row["gameId"]}"
    apiResult = requestWithHandlingHttperr(window_url)
    if apiResult.status_code == 200:
        json_data = apiResult.json()
        if 'gameMetadata' in json_data and len(json_data['gameMetadata']) > 0:
            game = json_data["gameMetadata"]
            if game.get("patchVersion") is not None:
                patch_ver = game["patchVersion"]
                where = patch_ver.find(".")
                patch_ver = patch_ver[:patch_ver[where+1:].find(".")+where+1] # [where+1:]부터 "."의 위치를 찾았으니까 인덱스가 예상한것보다 한 칸 앞으로 당겨져 있을것이므로 +1을 넣어 보정.
                row["patch"] = patch_ver
            else:
                row["patch"] = np.nan
            result.append(row)

result_df = pd.DataFrame(result)
result_df = result_df.astype({"matchId":"str", "gameId":"str"})
result_df.to_excel("../data/game_ids_with_patch.xlsx")

# game_ids.to_excel("../data/game_ids.xlsx", index=None)