import requests
import time

# request요청 시 상정한 에러가 들어오면 조금 대기한 후 다시 요청하는 걸 반복하는 함수입니다.
def requestWithHandlingHttperr(url, headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}):
    RETRY_COUNT = 12                # 기본 반복 12회
    RETRY_DELAY_SEC = 10            # 대기 10초
    ERRNO_10054 = 10054
    ERRNO_500 = 500
    ERRNO_503 = 503
    ERRNO_504 = 504
    ERRNO_404 = 404

    REQUEST_INTERVAL_SEC = 0.1

    time.sleep(REQUEST_INTERVAL_SEC)    # 먼저 0.1초 쉬고

    for i in range(RETRY_COUNT):        # 최대 반복 횟수 만큼
        try:
            result = requests.get(url, headers = headers)       # API에 request 요청
            result.raise_for_status()                           # http에러가 나오면 예외를 발생시킴 -> except로 점프
            return result
        except requests.exceptions.ConnectionError as e:
            if isinstance(e.args[0], ConnectionResetError) and e.args[0].winerror == ERRNO_10054:       # 10054에러이면 상대가 연결을 강제로 종료한 케이스이므로, 너무 요청을 많이 보내서일 가능성이 크다.
                                                                                                        # 이럴땐 조금 기다렸다 다시 요청하는 방법이 먹힐 가능성이 크다.
                print(f"Attempt {i + 1} failed with error 10054. Retrying in {RETRY_DELAY_SEC} seconds...")
                time.sleep(RETRY_DELAY_SEC)                 # 어느정도 시간을 기다림.
            else:                           # 다른 http 에러면
                raise
        except requests.exceptions.HTTPError as e:          # 500, 503, 504 에러는 일시적일 가능성이 커서 여기서도 조금 기다렸다 다시 요청하는 루틴을 씀.
            if e.response.status_code == ERRNO_500:         # Internal Server Error
                print(f"Attempt {i + 1} failed with 500 Internal Server Error. Retrying in {RETRY_DELAY_SEC} seconds...")
                time.sleep(RETRY_DELAY_SEC)
            elif e.response.status_code == ERRNO_503:       # Service Unavailable
                print(f"Attempt {i + 1} failed with 503 Service Unavailable. Retrying in {RETRY_DELAY_SEC} seconds...")
                time.sleep(RETRY_DELAY_SEC)
            elif e.response.status_code == ERRNO_504:       # Gateway Timed Out.
                print(f"Attempt {i + 1} failed with 504 Gateway Timeout. Retrying in {RETRY_DELAY_SEC} seconds...")
                time.sleep(RETRY_DELAY_SEC)
            else:  # 다른 HTTPError 예외 처리
                raise
    # game_id = url[url.rfind("/") + 1:]
    print(f"Failed to fetch data from url : {url} after {RETRY_COUNT} attempts.")
    raise Exception(f"Failed to fetch data from url : {url} after {RETRY_COUNT} attempts")