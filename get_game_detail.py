import os
import json
import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
import ast
from requestWithHandlingHttperr import requestWithHandlingHttperr
from common_constants import PARTICIPANTS_NUMBER_OF_A_TEAM

# 응답을 컬럼에맞춰 넣어 딕셔너리형태로 반환하는 함수입니다.
# data 에는 request를 통해 얻은 데이터가 들어있고, flag에는 무슨 목적으로 이 함수를 호출했는지를 구분할 목적의 정수가 들어갑니다.
# flag      0 : getDetails를 요청해 받은 데이터일 경우
#           1 : getWindow를 통해 받은 데이터일 경우
#           2 : getWindow에서 플레이어 정보만 얻고 싶을 때
def jsonParser(data, flag):
    result_data = {}                                                                # 결과데이터가 들어갈 리스트 초기화
    # JSON 데이터 파싱
    json = data.json()
    if flag == 0:                                                                   # getDetails을 통해 받은 응답일 경우 flag : 0
        # 필요한 데이터 추출 (여기서는 참가자 데이터만 추출하여 리스트에 추가)
        if 'frames' in json and len(json['frames']) > 0:                            # 데이터 덩어리가 들어 있는지 검사
            frame = json['frames'][0]                                               # 커서를 frame쪽으로 옮겨주고
            result_data["timestamp"] = frame['rfc460Timestamp'][:19] + "Z"          # 시간
            for idx, participant in enumerate(frame['participants']):                                   # 모든 participant(여기서는 블루팀5명, 레드팀 5명 총 10명)에 대해
                    result_data[f"level_{idx}"] =  participant['level']                                 # 챔피언 레벨
                    result_data[f"kills_{idx}"] = participant['kills']                                  # 킬수
                    result_data[f"deaths_{idx}"] = participant['deaths']                                # 데스 수
                    result_data[f"assists_{idx}"] = participant['assists']                              # 어시 수
                    result_data[f"totalGoldEarned_{idx}"] = participant['totalGoldEarned']              # 벌어들인 골드
                    result_data[f"creepScore_{idx}"] = participant['creepScore']                        # CS
                    result_data[f"killParticipation_{idx}"] = participant['killParticipation']          # 킬 관여율
                    result_data[f"championDamageShare_{idx}"] = participant['championDamageShare']      # 데미지 기여율
                    result_data[f"wardsPlaced_{idx}"] = participant['wardsPlaced']                      # 와드 놓은 횟수
                    result_data[f"wardsDestroyed_{idx}"] = participant['wardsDestroyed']                # 상대편의 와드를 부순 횟수
                    result_data[f"attackDamage_{idx}"] = participant['attackDamage']                    # 일반 공격력
                    result_data[f"abilityPower_{idx}"] = participant['abilityPower']                    # ap 공격력
                    result_data[f"criticalChance_{idx}"] = participant['criticalChance']                # 치명타율
                    result_data[f"attackSpeed_{idx}"] = participant['attackSpeed']                      # 공격 속도
                    result_data[f"lifeSteal_{idx}"] = participant['lifeSteal']                          # 피 흡수
                    result_data[f"armor_{idx}"] = participant['armor']                                  # 물리 방어력
                    result_data[f"magicResistance_{idx}"] = participant['magicResistance']              # 마법 방어력
                    result_data[f"tenacity_{idx}"] = participant['tenacity']                            # cc 저항력? 이라는데 맞나요?
                    result_data[f"items_{idx}"] = participant['items']                                  # 보유한 아이템
                    result_data[f"perkMetadata_{idx}"] = participant['perkMetadata']                    # 어... 특성 같은건가?
                    result_data[f"abilities_{idx}"] = participant['abilities']                          # 스킬 찍은 순서
                
    elif flag == 1:                                                                         # getWindow를 통해 받은 응답일 경우 flag : 1
         # 필요한 데이터 추출(팀 데이터)
        if 'frames' in json and len(json['frames']) > 0:                                    # 데이터 덩어리가 들어 있는지 검사
            frame = json['frames'][0]                                                       # 커서를 frame으로 옮겨줌
            blueteam = frame["blueTeam"]
            redteam = frame["redTeam"]
            result_data["timestamp"] = frame['rfc460Timestamp'][:19] + "Z"                  # 시간 데이터, 중복검사를 위해 넣음
            result_data["blue_totalGold"] = blueteam["totalGold"]                           # 블루팀의 골드 획득량
            result_data["blue_inhibitors"] = blueteam["inhibitors"]                         # 블루팀이 부순 억제기 갯수
            result_data["blue_towers"] = blueteam["towers"]                                 # 블루팀이 부순 타워 갯수
            result_data["blue_barons"] = blueteam["barons"]                                 # 블루팀이 먹은 바론 갯수
            result_data["blue_totalKills"] = blueteam["totalKills"]                         # 블루팀 총 킬 수
            result_data["blue_dragons"] = blueteam["dragons"]                               # 블루팀이 먹은 드래곤 (리스트)
            result_data["red_totalGold"] = redteam["totalGold"]                             # 레드팀의 골드 획득량
            result_data["red_inhibitors"] = redteam["inhibitors"]                           # 레드팀이 부순 억제기 갯수
            result_data["red_towers"] = redteam["towers"]                                   # 레드팀이 부순 타워 갯수
            result_data["red_barons"] = redteam["barons"]                                   # 레드팀이 먹은 바론 갯수
            result_data["red_totalKills"] = redteam["totalKills"]                           # 레드팀 총 킬 수
            result_data["red_dragons"] = redteam["dragons"]                                 # 레드팀이 먹은 드래곤(리스트)
            result_data["gameState"] = frame["gameState"]
            for idx, participant in enumerate(blueteam['participants']):
                result_data[f"currentHealth_{idx}"] = participant["currentHealth"]                  # 선수의 현재 체력
                result_data[f"maxHealth_{idx}"] = participant["maxHealth"]                          # 선수의 최대 체력(풀피)
            for idx, participant in enumerate(redteam['participants']):
                result_data[f"currentHealth_{idx + PARTICIPANTS_NUMBER_OF_A_TEAM}"] = participant["currentHealth"]                  # 선수의 현재 체력
                result_data[f"maxHealth_{idx + PARTICIPANTS_NUMBER_OF_A_TEAM}"] = participant["maxHealth"]                          # 선수의 최대 체력(풀피)
                
    elif flag == 2:                                                                 # getWindow에서 플레이어 정보를 얻고 싶을때는 flag : 2
        # 필요한 데이터 추출
        if 'gameMetadata' in json and len(json['gameMetadata']) > 0:                # gameMetadata 데이터 덩어리가 있으면
            game = json['gameMetadata']
            
            blueteam = game['blueTeamMetadata']
            blueteamplayers = blueteam['participantMetadata']
            redteam = game['redTeamMetadata']
            redteamplayers = redteam['participantMetadata']
            result_data["esportsTeamId_Blue"] = blueteam["esportsTeamId"]               # 블루팀 고유 ID
            result_data["esportsTeamId_Red"] = redteam["esportsTeamId"]                 # 레드팀 고유 ID
            for idx, player in enumerate(blueteamplayers):                              # 모든 블루팀 선수에 대해
                summonerName = player["summonerName"]
                blank_where = summonerName.find(" ")
                team = summonerName[:blank_where]                                       # 팀 코드
                name = summonerName[blank_where + 1:]                                   # 소환사명
                result_data[f"esportsPlayerId_{idx}"] = np.nan
                if player.get("esportsPlayerId") is not None:
                    result_data[f"esportsPlayerId_{idx}"] = player["esportsPlayerId"]       # 선수의 고유 ID
                result_data[f"teamCode_{idx}"] = team                                   # 팀 코드
                result_data[f"summonerName_{idx}"] = name                               # 소환사명
                result_data[f"side_{idx}"] = "Blue"                                     # 블루 진영이라는 뜻
                result_data[f"role_{idx}"] = player["role"]                             # 포지션(탑, 정글 등)
                result_data[f"championName_{idx}"] = player["championId"]               # 챔피언 이름
            
            for idx, player in enumerate(redteamplayers):
                summonerName = player["summonerName"]
                blank_where = summonerName.find(" ")
                team = summonerName[:blank_where]                                       # 팀 코드
                name = summonerName[blank_where + 1:]                                   # 소환사명
                result_data[f"esportsPlayerId_{idx + PARTICIPANTS_NUMBER_OF_A_TEAM}"] = np.nan
                if player.get("esportsPlayerId") is not None:
                    result_data[f"esportsPlayerId_{idx + PARTICIPANTS_NUMBER_OF_A_TEAM}"] = player["esportsPlayerId"]    # 선수의 고유 ID
                result_data[f"teamCode_{idx + PARTICIPANTS_NUMBER_OF_A_TEAM}"] = team                                # 팀 코드
                result_data[f"summonerName_{idx + PARTICIPANTS_NUMBER_OF_A_TEAM}"] = name                            # 소환사명
                result_data[f"side_{idx + PARTICIPANTS_NUMBER_OF_A_TEAM}"] = "Red"                                   # 레드 진영이라는 뜻
                result_data[f"role_{idx + PARTICIPANTS_NUMBER_OF_A_TEAM}"] = player["role"]                          # 포지션(탑, 정글 등)
                result_data[f"championName_{idx + PARTICIPANTS_NUMBER_OF_A_TEAM}"] = player["championId"]            # 챔피언 이름

    return result_data

# gameID를 받아 request 요청을 보내고, api로부터 데이터를 받아 중복검사 이후 데이터프레임으로 리턴하는 함수입니다.
def getGameStatusOrderedbyTime(game_id):
    # URL 설정
    getDetails_url = f"https://feed.lolesports.com/livestats/v1/details/{game_id}"  # getDetails 요청 cf. https://vickz84259.github.io/lolesports-api-docs/#operation/getDetails
    getWindow_url = f"https://feed.lolesports.com/livestats/v1/window/{game_id}"    # getWindow 요청 cf. https://vickz84259.github.io/lolesports-api-docs/#operation/getWindow
    
    # 결과 저장 리스트
    game_table = []
    
    # 중복검사용 변수 세팅 및 초기화
    previous_data = None
    INITIAL_COLLECTION_PERIOD = 60  # 중복 검사를 시작하기 전에 수집할 초기 데이터 수

    HTTP_OK = 200
    
    # 경기시작 시간 알아내기
    apiResult = requestWithHandlingHttperr(f"{getDetails_url}")
        
    if apiResult.status_code == HTTP_OK:
        starting_time = datetime.datetime.strptime(jsonParser(apiResult, 0)["timestamp"][:19], "%Y-%m-%dT%H:%M:%S")     # Zulu time 표시를 빼고 앞부분만 쓰기 위해 19까지 슬라이스.
        starting_time = starting_time - datetime.timedelta(seconds = starting_time.second % 10)                         # 이유는 모르겠는데 10초 단위로만 요청할 수 있는 것 같다. 
                                                                                                                        # 34초 데이터 주세요 이런거 요청하면 400 에러 뜸. 그래서 초를 10초단위로 끊음.
        
        max_end_time = starting_time + datetime.timedelta(hours = 5)                                                    # 아무리그래도 한경기에 퍼즈포함 5시간 걸리진 않겠지
        max_end_time_str = max_end_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z" # 형식 맞춰주기
    else:
        print(f"Failed to fetch data from game ID : {game_id}, Status code {apiResult.status_code}")
        return [str(game_id), apiResult.status_code] # 비정상 응답이 온 game id를 리턴
    
    # 최대 2시간 동안 10초 단위로 데이터 수집
    for i in tqdm(range(720), desc=f"Collecting Data Of GameID : {game_id}", leave = False):
        # 요청할 시간 계산
        query_time = starting_time + datetime.timedelta(seconds=i * 10)
        query_time_str = query_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z" # 형식 맞춰주기
        
        detailsApiResponse = requestWithHandlingHttperr(f"{getDetails_url}?startingTime={query_time_str}") # API에서 getDetails 요청
        windowApiResponse = requestWithHandlingHttperr(f"{getWindow_url}?startingTime={query_time_str}")  # API에서 getWindow 요청
        if detailsApiResponse.status_code == HTTP_OK and windowApiResponse.status_code == HTTP_OK:
            details = jsonParser(detailsApiResponse, 0)         # get으로 받은 결과를 넘겨주고 리스트를 받는 함수. 2번째 인수로 무슨 타입인지 구분(0 : getDetails, 1 : getWindow)
            window = jsonParser(windowApiResponse, 1)           # get으로 받은 결과를 넘겨주고 리스트를 받는 함수. 2번째 인수로 무슨 타입인지 구분(0 : getDetails, 1 : getWindow)
            if details["timestamp"] == window["timestamp"]:
                window.pop("timestamp")
                details.update(window)
                if i < INITIAL_COLLECTION_PERIOD:   # 처음 조금동안은 중복검사를 하지 않습니다.
                    game_table.append(details)
                else:                               # 중복 데이터 확인 및 반복 카운트
                    if previous_data is not None and (previous_data["timestamp"] == details["timestamp"]): # == 만으로는 중복데이터 확인이 안 되어 시간을 비교
                        if jsonParser(requestWithHandlingHttperr(f"{getWindow_url}?startingTime={max_end_time_str}"),1)["timestamp"] == details["timestamp"]:   # 5시간 이후 데이터랑 같으면
                            if details["blue_inhibitors"] > 0 or details["red_inhibitors"] > 0:                 # 억제기가 하나라도 부숴졌으면 정상종료
                                break
                            else:
                                return [str(game_id), detailsApiResponse.status_code, details["gameState"], query_time_str]     # 종료조건에 맞지 않는데 중복값이 너무 많이 발생하면 invalid로 처리.
                    else:
                        previous_data = details
                        if details["totalGoldEarned_0"] != 0:      # 게임 시작 시 잠깐동안 전부 0으로 나오는 데이터는 포함하지 않음.
                            game_table.append(details)
        else:                                       # 응답에 뭔가 문제가 생겼을 때
            print(f"Failed to fetch data for {query_time_str} from game ID : {game_id}, Status code {detailsApiResponse.status_code}")
            return [str(game_id), detailsApiResponse.status_code, query_time_str] # 비정상 응답이 온 game id를 리턴
        
    return pd.DataFrame(game_table)

# getWindow 요청을 보내 api로부터 선수 정보를 받아옵니다. (딕셔너리 형태)
def getParticipantInfo(game_id):
    HTTP_OK = 200
    
    # URL 설정
    window_url = f"https://feed.lolesports.com/livestats/v1/window/{game_id}" # getWindow 요청 cf. https://vickz84259.github.io/lolesports-api-docs/#operation/getWindow)

    # 요청 날리기
    apiResult = requestWithHandlingHttperr(f"{window_url}")
    
    # 응답이 정상이면
    if apiResult.status_code == HTTP_OK:
        return jsonParser(apiResult, 2)
    else:
        print(f"Failed to fetch data from game ID : {game_id},  Status code {apiResult.status_code}")
        return [str(game_id), apiResult.status_code]                # 비정상 응답이 온 game id를 리턴
    
# 팀명과 소환사명이 공백 없이 붙어서 나와 문제가 생긴 데이터들이 일부 있습니다. 그걸 팀명과 소환사명으로 분리하기 위한 코드입니다.
# 각 팀 5명의 선수에 대해 공통적으로 앞에 붙은 문자열은 팀명으로 간주합니다.
# 일치하는 부분이 없으면 "", 0을 리턴합니다. 파라미터가 문자열이 아니면 "", -1을 리턴합니다.
def find_common_prefix(strings):
    if not strings:
        return "", -1

    # 짧은 문자 찾기
    shortest = min(strings, key=len)

    # 짧은 문자의 가장 긴 것으로 max값을 잡아 놓고
    end_index = len(shortest)

    for i in range(len(shortest)):  # 문자열의 첫 글자부터
        current_char = shortest[i]
        for string in strings:
            if string[i] != current_char:
                end_index = i
                break
        if end_index != len(shortest):
            break

    common_prefix = shortest[:end_index]
    return common_prefix, end_index

# 팀 코드를 summonerName에서 공백으로 구분된 것으로 추출하려고 하였으나, 개중 공백없이 그냥 붙어서 들어오는 데이터도 일부 있음. 그래서 common_prefix를 찾아 구분해 코드명을 추출하기 위한 코드.
def seperateTeamNameFromSummonerName(df):
    blueSummonerNames = []
    redSummonerNames = []
    needed = True
    
    for i in range(PARTICIPANTS_NUMBER_OF_A_TEAM):
        blueteam = str(df.at[0, f"teamCode_{i}"])
        bluename = str(df.at[0, f"summonerName_{i}"])
        redteam = str(df.at[0, f"teamCode_{i + PARTICIPANTS_NUMBER_OF_A_TEAM}"])
        redname = str(df.at[0, f"summonerName_{i+PARTICIPANTS_NUMBER_OF_A_TEAM}"])
        # 플레이어 이름이 숫자라 int64타입으로 오는 녀석도 있음 (e.g. 500 걍 소환사이름이 500임)
        if len(blueteam) == 0 or len(bluename) == 0 or len(redteam) == 0 or len(redname) == 0:      # 팀명이나 소환사명이 비어있는 경우는 고려하지 않는다.
            needed = False
            continue
        if blueteam != bluename[:-1]: needed = False        # 공백으로 구분되어있지 않은 데이터 특징은 팀명으로 들어갈 칸이 소환사명에서 끝자리 하나 잘린것과 같이 나온다. 내가 데이터 추출을 어떻게 한 걸까.
        blueSummonerNames.append(bluename)

        if redteam != redname[:-1]: needed = False
        redSummonerNames.append(redname)

    if needed == True:
        blueteamName, blueteamWhere = find_common_prefix(blueSummonerNames)
        redteamName, redteamWhere = find_common_prefix(redSummonerNames)            # 모든 선수가 이름 앞에 공통적으로 달고 나오는 문자들을 팀 코드라 간주.

        for i in range(PARTICIPANTS_NUMBER_OF_A_TEAM):
            if blueteamWhere > 0:
                df[f"teamCode_{i}"] = blueteamName
                df[f"summonerName_{i}"] = df[f"summonerName_{i}"].apply(lambda x : x[redteamWhere:])
            if redteamWhere > 0:
                df[f"teamCode_{i+PARTICIPANTS_NUMBER_OF_A_TEAM}"] = redteamName
                df[f"summonerName_{i+PARTICIPANTS_NUMBER_OF_A_TEAM}"] = df[f"summonerName_{i+PARTICIPANTS_NUMBER_OF_A_TEAM}"].apply(lambda x : x[redteamWhere:])
    return df

# request에 대한 응답으로 원하지 않는 데이터가 들어온 것을 찾아내 걸러내고. 드래곤 잡은 데이터가 리스트 형태의 문자열로 나오는 걸 드래곤 잡은 누적 숫자로 변환시킨 컬럼을 추가한다.
def removeAbnormalRows(df):
    df = df.astype({"esportsTeamId_Blue":"str", "esportsTeamId_Red":"str", "blue_dragons":"str", "red_dragons":"str",\
        "esportsPlayerId_0":"str", "esportsPlayerId_1":"str", "esportsPlayerId_2":"str", "esportsPlayerId_3":"str", "esportsPlayerId_4":"str",\
            "esportsPlayerId_5":"str", "esportsPlayerId_6":"str", "esportsPlayerId_7":"str", "esportsPlayerId_8":"str", "esportsPlayerId_9":"str"})
    df["timestamp"] = df["timestamp"].apply(lambda x : datetime.datetime.strptime(x[:19], "%Y-%m-%dT%H:%M:%S"))
    blue_dragons_count = df["blue_dragons"].apply(lambda x : len(ast.literal_eval(x)))
    df = pd.concat([df, blue_dragons_count.rename("blue_dragons_count")], axis=1)
    red_dragons_count = df["red_dragons"].apply(lambda x : len(ast.literal_eval(x)))
    df = pd.concat([df, red_dragons_count.rename("red_dragons_count")], axis=1)
    df = df.copy()
    non_zero_df = df[df["totalGoldEarned_0"] != 0]
    drop_weird_second_df = non_zero_df[non_zero_df["timestamp"].dt.second % 10 == 0].reset_index(drop = True)
    drop_weird_second_df["duration"] = drop_weird_second_df.index * 10
    return drop_weird_second_df

###### 아래부턴 실행되는 부분 ######
id_list = [0] # <- 요 부분에 원하는 숫자 넣고 돌리시면 됩니다.
TARGET_PATH = "../data/collected_data/"
#TARGET_PATH = "../data/collected_data_test/"
for i in id_list:
    game_ids = pd.read_excel(f"../data/game_ids/game_id_{i}.xlsx") 
    #game_ids = pd.read_excel(f"../data/game_ids_for_test/game_id_for_test_{i}.xlsx")

    for idx, row in tqdm(game_ids.iterrows(), desc=f"Progress of game_id_{i}", total = len(game_ids)):  # 게임 번호를 하나씩 row에 넣어 분기를 돌립니다.
        game_id = row["gameId"]
        playerinfo = getParticipantInfo(game_id)                        # 플레이어 정보를 뽑아냄
        playerStatus = getGameStatusOrderedbyTime(game_id)              # 게임 상세 데이터를 뽑아냄
        playerinfo_list = []
        
        # data폴더 내에 xlsx 파일로 저장
        os.makedirs('../data', exist_ok=True)
        os.makedirs(TARGET_PATH, exist_ok=True)

        if type(playerinfo) is list:                                # 정상적인 데이터가 모이지 않았을 때 getParticipantInfo()와 getGameStatusOrderedbyTime()은 List를 반환합니다.
            df = pd.Series(playerinfo).to_frame().T
            if df.shape[1] == 2:                                    # 데이터 요청 처음부터 망했을 때
                df.columns = ["game_id", "status_code"]
            elif df.shape[1] == 3:                                  # 데이터를 한참 시간순서대로 받는 도중에 http에러로 망했을 때
                df.columns = ["game_id", "status_code", "timestamp"]
            elif df.shape[1] == 4:                                  # 데이터를 한참 시간순서대로 받는 도중에 중복값이 많아 망했을 때
                df.columns = ["game_id", "status_code", "last_game_state", "timestamp"]
            df.to_excel(f'{TARGET_PATH}{game_id}_invalid.xlsx', index=False)
        elif type(playerStatus) is list:
            df = pd.Series(playerStatus).to_frame().T
            if df.shape[1] == 2:                                    # 데이터 요청 처음부터 망했을 때
                df.columns = ["game_id", "status_code"]
            elif df.shape[1] == 3:                                  # 데이터를 한참 시간순서대로 받는 도중에 http에러로 망했을 때
                df.columns = ["game_id", "status_code", "timestamp"]
            elif df.shape[1] == 4:                                  # 데이터를 한참 시간순서대로 받는 도중에 중복값이 많아 망했을 때
                df.columns = ["game_id", "status_code", "last_game_state", "timestamp"]
            df.to_excel(f'{TARGET_PATH}{game_id}_invalid.xlsx', index=False)
        else:                                                       # 정상이면
            for j in range(playerStatus.shape[0]):                  # concat을 위해 playerinfo를 아래로 복제해줌
                playerinfo_list.append(playerinfo)
            playerinfo_df = pd.DataFrame(playerinfo_list)
            df = pd.concat([playerStatus, playerinfo_df], axis = 1)
            df = seperateTeamNameFromSummonerName(df)
            df = removeAbnormalRows(df)
            if df.iloc[-1]["duration"] > 600: # 10분이내 끝난 경기는 제외함.
                df.to_excel(f'{TARGET_PATH}{game_id}.xlsx', index=False)   
            else:
                df.to_excel(f'{TARGET_PATH}{game_id}_tooshort.xlsx', index=False)
    #print(f"Collecting data from game_id_{i} is completed!")