import requests
import json
import time

def get_comments(place_id, start_comment_id=None):
    base_url = "https://place.map.kakao.com/commentlist/v/"
    url = f"{base_url}{place_id}/{start_comment_id}" if start_comment_id else f"{base_url}{place_id}"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "referer": f"https://place.map.kakao.com/{place_id}",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def scrape_all_comments(place_id):
    all_comments = []
    last_comment_id = None

    while True:
        data = get_comments(place_id, last_comment_id)

        if not data or "list" not in data["comment"]:
            break

        comments = data["comment"]["list"]
        all_comments.extend(comments)

        # 다음 페이지로 넘어갈 `commentid` 설정
        last_comment_id = comments[-1]["commentid"]

        print(f"Fetched {len(comments)} comments. Total: {len(all_comments)}")

        # 서버에 부담을 줄이기 위한 딜레이
        time.sleep(1)

    return all_comments

# 실행
place_id = "10332413"  # 명동교자 본점 ID
comments = scrape_all_comments(place_id)

# 결과 저장
with open("comments.json", "w", encoding="utf-8") as f:
    json.dump(comments, f, ensure_ascii=False, indent=4)

print(f"총 {len(comments)}개의 리뷰를 크롤링했습니다.")
