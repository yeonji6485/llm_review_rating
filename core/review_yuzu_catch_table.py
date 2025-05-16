from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def fetch_reviews(target_count):
    # Selenium WebDriver 설정
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    # 크롤링 대상 URL
    url = "https://app.catchtable.co.kr/ct/shop/Y2F0Y2hfV0FhQTRRNTVTVFhYS1owL2J1UDN0dz09?type=DINING&foodKeywords=%EC%9C%A0%EC%A6%88+%EB%9D%BC%EB%A9%98"
    driver.get(url)

    # 페이지 로드 대기
    time.sleep(5)

    # 리뷰를 저장할 리스트
    reviews = []

    # 무한 스크롤
    fetched_count = 0
    previous_height = 0

    while fetched_count < target_count:
        # 숨겨진 요소 표시
        driver.execute_script("""
            let elements = document.querySelectorAll('.x9vxc45');
            elements.forEach(el => el.style.display = 'block');
        """)

        # 페이지 소스 파싱
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        new_reviews = soup.find_all(class_="__review-post")

        # 중복되지 않은 리뷰만 추가
        for review in new_reviews:
            text = review.get_text(strip=True)
            if text not in reviews:
                reviews.append(text)
                fetched_count += 1
                if fetched_count >= target_count:
                    break

        # 스크롤 실행 및 대기
        previous_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        current_height = driver.execute_script("return document.body.scrollHeight")

        # 더 이상 새로운 데이터가 로드되지 않으면 종료
        if previous_height == current_height:
            print("더 이상 로드할 리뷰가 없습니다.")
            break

    # 드라이버 종료
    driver.quit()

    return reviews[:target_count]
import csv
import json

# 크롤링 실행
target_count = 235
reviews = fetch_reviews(target_count)

# 결과 출력
for idx, review in enumerate(reviews, start=1):
    print(f"Review {idx}: {review}")

# Save to JSON file
with open("catch_yuzu_review.csv", "w", encoding="utf-8") as f:
    json.dump(reviews, f, ensure_ascii=False, indent=4)