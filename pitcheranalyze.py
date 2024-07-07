from calculateColumnsForModel import numberToRoleName
import pandas as pd

# 피쳐들 간의 관계를 분석해 새로운 피쳐를 만들어주고 필요하지 않아 보이는 피쳐는 빼는 함수.
# 근데 이게 물이 좀 빠진게 이미 CalculateColumnsForModel에서 약간 domain knowledge를 반영한 피쳐를 만들어 버렸다. kda나.. wardsscore, 그리고 누적되는 경향이 강한 데이터 처리 같은 것들.
# 여기서는 블루팀과 레드팀 간의 관계를 집중적으로 보고 있다.
def pitcheranalyze(dataset):
    for i in range(4):
        dataset[f"{numberToRoleName(i)}_kdaDiff"] = dataset[f"Blue_{numberToRoleName(i)}_kda"] - dataset[f"Red_{numberToRoleName(i)}_kda"]
        dataset[f"{numberToRoleName(i)}_killsPerTimeDiff"] = dataset[f"Blue_{numberToRoleName(i)}_killsPerTime"] - dataset[f"Red_{numberToRoleName(i)}_killsPerTime"]
        dataset[f"{numberToRoleName(i)}_deathsPerTimeDiff"] = dataset[f"Blue_{numberToRoleName(i)}_deathsPerTime"] - dataset[f"Red_{numberToRoleName(i)}_deathsPerTime"]
        dataset[f"{numberToRoleName(i)}_assistsPerTimeDiff"] = dataset[f"Blue_{numberToRoleName(i)}_assistsPerTime"] - dataset[f"Red_{numberToRoleName(i)}_assistsPerTime"]
        dataset[f"{numberToRoleName(i)}_creepScorePerTimeDiff"] = dataset[f"Blue_{numberToRoleName(i)}_creepScorePerTime"] - dataset[f"Red_{numberToRoleName(i)}_creepScorePerTime"]
        dataset[f"{numberToRoleName(i)}_goldEarnedPerTimeDiff"] = dataset[f"Blue_{numberToRoleName(i)}_goldEarnedPerTime"] - dataset[f"Red_{numberToRoleName(i)}_goldEarnedPerTime"]

    dataset["Spt_assistsPerTimeDiff"] = dataset[f"Blue_Spt_assistsPerTime"] - dataset[f"Red_Spt_assistsPerTime"]
    
    for i in range(5):
        dataset[f"{numberToRoleName(i)}_wardsScorePerTimeDiff"] = dataset[f"Blue_{numberToRoleName(i)}_wardsScorePerTime"] - dataset[f"Red_{numberToRoleName(i)}_wardsScorePerTime"]
        dataset.drop([f"Blue_{numberToRoleName(i)}_kda", f"Red_{numberToRoleName(i)}_kda"], axis=1, inplace=True)
        dataset.drop([f"Blue_{numberToRoleName(i)}_creepScorePerTime", f"Red_{numberToRoleName(i)}_creepScorePerTime"], axis=1, inplace=True)
        dataset.drop([f"Blue_{numberToRoleName(i)}_goldEarnedPerTime", f"Red_{numberToRoleName(i)}_goldEarnedPerTime"], axis=1, inplace=True)
        dataset.drop([f"Blue_{numberToRoleName(i)}_wardsScorePerTime", f"Red_{numberToRoleName(i)}_wardsScorePerTime"], axis=1, inplace=True)
        dataset.drop([f"Blue_{numberToRoleName(i)}_championDamageShare", f"Red_{numberToRoleName(i)}_championDamageShare"], axis=1, inplace=True)   # championdamageshare 다 지우고

    dataset.drop(["Blue_Spt_killsPerTime", f"Red_Spt_killsPerTime"], axis=1, inplace=True)
    dataset.drop(["Blue_Spt_deathsPerTime", f"Red_Spt_deathsPerTime"], axis=1, inplace=True)
    

    dataset["teamWinrateDiff"] = dataset["Blue_Winrate"] - dataset["Red_Winrate"]
    dataset["teamGoldDiff"] = dataset["Blue_GoldDiff"] - dataset["Red_GoldDiff"]
    dataset["teamKillDiff"] = dataset["Blue_KillDiff"] - dataset["Red_KillDiff"]

    return dataset