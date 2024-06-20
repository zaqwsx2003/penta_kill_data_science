from flask import Flask, jsonify, request
import json
import pickle
import pandas as pd
import requests
from calculateColumnsForModel import numberToRoleName
from pitcheranalyze import pitcheranalyze
import joblib
import logging

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

# 모델 가져오기
try:
    with open('data/present_data.pkl', 'rb') as f:
        present_data = pickle.load(f)
    model, scaler, X_columns = joblib.load('data/model_draft5_2_1.pkl')
    logging.info("모델 가져오기 성공")
except Exception as e:
    present_data = None
    model, scaler, X_columns = None
    logging.error(f"모델 가져오기 실패: {e}")

# JSON 파일 가져오기 (테스트 용도로 필요시 사용)
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        logging.info("JSON을 가져오기 성공")
        return data
    except Exception as e:
        logging.error(f"JSON 가져오기 실패: {e}")
        return None

# 중간 값 계산
def getMedian(role):
    role = role % 5
    if role == 0:
        median = {
            "kda": 3.93333333333333,
            "killsPerTime": 0.0012396694214876,
            "deathsPerTime": 0.00136986301369863,
            "assistsPerTime": 0.0023972602739726,
            "championDamageShare": 0.228523154923377,
            "creepScorePerTime": 0.133996402877698,
            "wardsScorePerTime": 0.0128080095122445,
            "goldEarnedPerTime": 6.4429331869941
        }
    elif role == 1:
        median = {
            "kda": 5.0,
            "killsPerTime": 0.00122448979591837,
            "deathsPerTime": 0.00145348837209302,
            "assistsPerTime": 0.00348360655737705,
            "championDamageShare": 0.144554837154089,
            "creepScorePerTime": 0.0917910447761194,
            "wardsScorePerTime": 0.0148372890472669,
            "goldEarnedPerTime": 5.60251262626263
        }
    elif role == 2:
        median = {
            "kda": 5.3,
            "killsPerTime": 0.00161290322580645,
            "deathsPerTime": 0.00124223602484472,
            "assistsPerTime": 0.0028125,
            "championDamageShare": 0.261571385007903,
            "creepScorePerTime": 0.143388523991972,
            "wardsScorePerTime": 0.0131656804733728,
            "goldEarnedPerTime": 6.70846681695934
        }
    elif role == 3:
        median = {
            "kda": 5.79285714285714,
            "killsPerTime": 0.00202312138728324,
            "deathsPerTime": 0.00112107623318386,
            "assistsPerTime": 0.00251396648044693,
            "championDamageShare": 0.272831173686407,
            "creepScorePerTime": 0.155673758865248,
            "wardsScorePerTime": 0.016043778434033,
            "goldEarnedPerTime": 7.26228078187797
        }
    elif role == 4:
        median = {
            "kda": 4.83333333333333,
            "killsPerTime": 0.000297619047619048,
            "deathsPerTime": 0.0014792899408284,
            "assistsPerTime": 0.0044793720078851,
            "championDamageShare": 0.0746235333980816,
            "creepScorePerTime": 0.0183673469387755,
            "wardsScorePerTime": 0.0441531378196736,
            "goldEarnedPerTime": 4.00327956989247
        }
    return median

# 모델 예측 데이터 처리
def getPredictData(match):
    try:
        PITCHERS_NUMBER_OF_A_PLAYER = 8  # 플레이어 스탯 갯수
        players_form_df = None
        STAT_MEDIAN_MULTIPLIER = 0.7

        teams = match["teams"]
        blueteam = teams[0]
        redteam = teams[1]
        blueteam_id = blueteam["esportsTeamId"]
        redteam_id = redteam["esportsTeamId"]
        blueteam_players = blueteam["participantMetadata"]
        redteam_players = redteam["participantMetadata"]

        blue_winrate = present_data['team_history'][blueteam_id]["self"]["winrate"] if present_data["team_history"].get(blueteam_id) else 0.5
        blue_golddiff = present_data['team_history'][blueteam_id]["self"]["golddiff"] if present_data["team_history"].get(blueteam_id) else 0
        blue_killdiff = present_data['team_history'][blueteam_id]["self"]["killdiff"] if present_data["team_history"].get(blueteam_id) else 0

        headtohead_winrate = present_data['team_history'][blueteam_id][redteam_id]["winrate"] if present_data["team_history"].get(blueteam_id) and present_data["team_history"][blueteam_id].get(redteam_id) else 0.5
        headtohead_golddiff = present_data['team_history'][blueteam_id][redteam_id]["golddiff"] if present_data["team_history"].get(blueteam_id) and present_data["team_history"][blueteam_id].get(redteam_id) else 0
        headtohead_killdiff = present_data['team_history'][blueteam_id][redteam_id]["killdiff"] if present_data["team_history"].get(blueteam_id) and present_data["team_history"][blueteam_id].get(redteam_id) else 0

        red_winrate = present_data['team_history'][redteam_id]["self"]["winrate"] if present_data["team_history"].get(redteam_id) else 0.5
        red_golddiff = present_data['team_history'][redteam_id]["self"]["golddiff"] if present_data["team_history"].get(redteam_id) else 0
        red_killdiff = present_data['team_history'][redteam_id]["self"]["killdiff"] if present_data["team_history"].get(redteam_id) else 0

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
            "matchId": matchid_extended,
            "side": columns_of_each_team_side,
            "role": columns_of_role
        }
        columns_df = pd.DataFrame(columns_dict)

        for idx, player in enumerate(blueteam_players):
            player_id = player["esportsPlayerId"]
            role = player["role"]
            role_idx = ["top", "jungle", "mid", "bottom", "support"].index(role)
            if present_data["player_form"][numberToRoleName(role_idx)].get(player_id) is not None:
                player_form = present_data["player_form"][numberToRoleName(role_idx)][player_id]
            else:
                median_player_dict = getMedian(role_idx)
                player_form = pd.DataFrame(median_player_dict, index=[0]).T
                player_form.reset_index(inplace=True)
                player_form.columns = ["elements", "formvalue"]
            if players_form_df is None:
                players_form_df = player_form
            else:
                players_form_df = pd.concat([players_form_df, player_form], ignore_index=True)

        for idx, player in enumerate(redteam_players):
            player_id = player["esportsPlayerId"]
            role = player["role"]
            role_idx = ["top", "jungle", "mid", "bottom", "support"].index(role)
            if present_data["player_form"][numberToRoleName(role_idx)].get(player_id) is not None:
                player_form = present_data["player_form"][numberToRoleName(role_idx)][player_id]
            else:
                median_player_dict = {key: value * STAT_MEDIAN_MULTIPLIER for key, value in getMedian(role_idx).items()}
                player_form = pd.DataFrame(median_player_dict, index=[0]).T
                player_form.reset_index(inplace=True)
                player_form.columns = ["elements", "formvalue"]
            if players_form_df is None:
                players_form_df = player_form
            else:
                players_form_df = pd.concat([players_form_df, player_form], ignore_index=True)

        players_form_df = pd.concat([columns_df, players_form_df], axis=1, ignore_index=True)
        players_form_df.columns = ["matchId", "side", "role", "elements", "formvalue"]
        players_form_df = pd.pivot_table(
            players_form_df,
            values="formvalue",
            index=["matchId"],
            columns=["side", "role", "elements"]
        ).reset_index()
        players_form_df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in players_form_df.columns]
        players_form_df["Blue_Winrate"] = blue_winrate
        players_form_df["Blue_GoldDiff"] = blue_golddiff
        players_form_df["Blue_KillDiff"] = blue_killdiff
        players_form_df["Red_Winrate"] = red_winrate
        players_form_df["Red_GoldDiff"] = red_golddiff
        players_form_df["Red_KillDiff"] = red_killdiff
        players_form_df["headtoHeadWinrate"] = headtohead_winrate
        players_form_df["headtoHeadGoldDiff"] = headtohead_golddiff
        players_form_df["headtoHeadKillDiff"] = headtohead_killdiff
        players_form_df.rename(columns={"matchId__": "matchId"}, inplace=True)

        players_form_df = pitcheranalyze(players_form_df)
        players_form_df = players_form_df.drop(["matchId"], axis=1)
        players_form_df = players_form_df[X_columns]
        players_form_df = scaler.transform(players_form_df)

        predict = model.predict_proba(players_form_df)
        return predict
    except Exception as e:
        logging.error(f"데이터 처리 중 오류 발생: {e}")
        raise

# 예측 결과 형식화
def format_prediction_result(result):
    return {
        "team1": {
            "win_rate": round(result[0][0] * 100, 2)
        },
        "team2": {
            "win_rate": round(result[0][1] * 100, 2)
        }
    }

# 예측 엔드포인트
@app.route('/predict', methods=['POST'])
def predict_endpoint():
    input_data = request.json
    if input_data is None:
        logging.error("No JSON data received or failed to decode JSON object")
        return jsonify({"error": "No JSON data received or failed to decode JSON object"}), 400
    try:
        logging.debug("Received JSON data:")
        logging.debug(json.dumps(input_data, indent=4))

        processed_data = getPredictData(input_data)
        formatted_result = format_prediction_result(processed_data)

        return jsonify(formatted_result)

    except Exception as e:
        logging.error(f"예측 처리 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
