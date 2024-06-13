import os
import pandas as pd

# 디렉토리 설정 
invalid_directory = 'data/invalid_check/'

# 결과를 데이터 프레임 초기화 하기.
invalid_3_or_4 = pd.DataFrame()
invalid_2_not_204 = pd.DataFrame()

# 디렉토리 내의 모든 파일을 돌리기
for filename in os.listdir(invalid_directory):
    # 파일명에 'invalid' 이 퍼함되고 .xlsx인 파일만
    if 'invalid' in filename and filename.endswith('.xlsx'):
        # 데이터프레임 읽기
        df = pd.read_excel(os.path.join(invalid_directory, filename))
        # 숫자를 고정 소수점 형식의 문자열로 변환 <-이거엿네 ㅋㅋㅋ아 이거없음 숫자 바보됨
        df = df.applymap(lambda x: '{:.0f}'.format(x) if isinstance(x, (int, float)) else x)

        
        # 열의 수가 3 또는 4인 경우만 처리
        if df.shape[1] == 3 or df.shape[1] == 4:
            print(f"Processing file (3 or 4 columns): {filename}")
            print(df.shape)
            # 결과 데이터프레임에 추가
            invalid_3_or_4 = pd.concat([invalid_3_or_4, df])
        # 열의 수가 2이면서 status_code가 204가 아닌 경우만 처리
        elif df.shape[1] == 2 and df["status_code"].any() != 204:
            print(f"Processing file (2 columns, status_code not 204): {filename}")
            print(df.shape)
            # 결과 데이터프레임에 추가
            invalid_2_not_204 = pd.concat([invalid_2_not_204, df])

# 결과를 엑셀 파일로 저장
invalid_3_or_4.to_excel('data_3_or_4.xlsx', index=False)
invalid_2_not_204.to_excel('data_2_not_204.xlsx', index=False)
