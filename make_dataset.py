from pitcheranalyze import pitcheranalyze
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib

pre_make_pivot_table_df = pd.read_excel("../data/pre_make_pivot_table_draft7.xlsx", dtype = {"gameId":"str"})

teamdata_df = pre_make_pivot_table_df[["gameId", "side", "teamWinrate", "teamGoldDiff", "teamKillDiff"]].drop_duplicates(["gameId", "side"])
teamdata_df = teamdata_df.pivot(index='gameId', columns='side', values=['teamWinrate', "teamGoldDiff", "teamKillDiff"])

teamdata_df.columns = [f"{col[1]}_{col[0]}".replace('team', '').replace('__', '_').strip() for col in teamdata_df.columns.values] # 평탄화. 결국 '_'로 컬럼을 나눌 수 있는데 의의를 두는걸로.
headtohead_and_winner_df = pre_make_pivot_table_df[["gameId", "headtoHeadWinrate", "headtoHeadGoldDiff", "headtoHeadKillDiff", "winner"]].drop_duplicates(["gameId"])
formvalue_pivot = pd.pivot_table(
    pre_make_pivot_table_df,
    values = "formvalue",
    index = ["gameId"],
    columns = ["side", "role","elements"]
).reset_index()
formvalue_pivot.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in formvalue_pivot.columns] # 피벗 테이블 만들고 평탄화...
formvalue_pivot.rename(columns = {"gameId__" : "gameId"}, inplace = True)

formvalue_pivot = formvalue_pivot.merge(teamdata_df, on = "gameId", how = "left")
formvalue_pivot = formvalue_pivot.merge(headtohead_and_winner_df, on = "gameId", how = "left")

formvalue_pivot = pitcheranalyze(formvalue_pivot)

# 같은 속성을 가진 피처들을 비교하기 위해 모든 속성들이 들어간 리스트를 짜놓음. 이걸 pitcheranalyze에서 리턴받는 게 더 깔끔하려나..?
suffix_list = ["assistsPerTime", "championDamageShare", "creepScorePerTime", "deathsPerTime", "goldEarnedPerTime", "kda", "killsPerTime", "wardsScorePerTime", "Winrate", "GoldDiff", "KillDiff",
               "wardsScorePerTimeDiff", "assistsPerTimeDiff", "kdaDiff", "killsPerTimeDiff", "deathsPerTimeDiff", "creepScorePerTimeDiff", "goldEarnedPerTimeDiff"]
scaler_dict = {}
for suffix in suffix_list:
    filtered_columns = [col for col in formvalue_pivot.columns if col.split('_')[-1] in suffix]     # Blue_Adc_assistsPerTime 이런거에서 assistsPerTime을 뽑아내는 코드.
    if len(filtered_columns) != 0:
        filtered_df = formvalue_pivot[filtered_columns]
        scaler_dict[suffix] = StandardScaler()          # suffix별로 scaler를 만들어 속성별 공통의 평균과 표준편차를 저장하려고 한다.
        data_have_common_suffix_list = []
        for column in filtered_df.columns:
            data_have_common_suffix_list.extend(filtered_df[column].values)     # 속성이 같은 모든 데이터들을 한 리스트에 몰아준 뒤
        data_have_common_suffix_list = np.array(data_have_common_suffix_list).reshape(-1,1)
        scaler_dict[suffix] = scaler_dict[suffix].fit(data_have_common_suffix_list)             # fit. 이러면 속성별 평균과 표준편차가 scaler에 저장됨.
        for column in filtered_df.columns:
            formvalue_pivot[column] = scaler_dict[suffix].transform(formvalue_pivot[column].values.reshape(-1, 1))  # 공통 scaler에 맞춰 각자 transform.
                                                                                                                    # 컬럼별 평균이 0, 편차가 1이 아니지만 이쪽이 데이터의 의미를 더 잘 표현한 방법이라 생각한다.

# 나머지 피처들은 그냥 컬럼별 표준화. 평균은 0, 표준편차는 1이 됨.
scaler_dict["headtoHeadWinrate"] = StandardScaler()
formvalue_pivot["headtoHeadWinrate"] = scaler_dict["headtoHeadWinrate"].fit_transform(formvalue_pivot["headtoHeadWinrate"].values.reshape(-1, 1))
scaler_dict["headtoHeadGoldDiff"] = StandardScaler()
formvalue_pivot["headtoHeadGoldDiff"] = scaler_dict["headtoHeadGoldDiff"].fit_transform(formvalue_pivot["headtoHeadGoldDiff"].values.reshape(-1, 1))
scaler_dict["headtoHeadKillDiff"] = StandardScaler()
formvalue_pivot["headtoHeadKillDiff"] = scaler_dict["headtoHeadKillDiff"].fit_transform(formvalue_pivot["headtoHeadKillDiff"].values.reshape(-1, 1))
scaler_dict["teamWinrateDiff"] = StandardScaler()
formvalue_pivot["teamWinrateDiff"] = scaler_dict["teamWinrateDiff"].fit_transform(formvalue_pivot["teamWinrateDiff"].values.reshape(-1, 1))
scaler_dict["teamGoldDiff"] = StandardScaler()
formvalue_pivot["teamGoldDiff"] = scaler_dict["teamGoldDiff"].fit_transform(formvalue_pivot["teamGoldDiff"].values.reshape(-1, 1))
scaler_dict["teamKillDiff"] = StandardScaler()
formvalue_pivot["teamKillDiff"] = scaler_dict["teamKillDiff"].fit_transform(formvalue_pivot["teamKillDiff"].values.reshape(-1, 1))

joblib.dump((formvalue_pivot, scaler_dict), "../data/dataset_draft7_1.pkl")     # joblib으로 출력 후 마무리.