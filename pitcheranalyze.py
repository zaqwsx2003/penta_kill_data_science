from calculateColumnsForModel import numberToRoleName
import pandas as pd

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