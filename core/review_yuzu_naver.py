from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
import re
from tqdm import tqdm  # tqdm 추가


def scrape_reviews(page_url: str, review_class: str, button_xpath: str, value_xpath_template: str, max_reviews: int = 100):
    reviews = []
    previous_review_count = 0

    # Initialize WebDriver
    driver = webdriver.Chrome()
    driver.get(page_url)
    driver.maximize_window()
    time.sleep(4)

    try:
        # tqdm으로 진행률 표시 추가
        with tqdm(total=max_reviews, desc="Scraping Reviews", unit="review") as pbar:
            while len(reviews) < max_reviews:
                # Extract reviews
                review_elements = driver.find_elements(By.CLASS_NAME, review_class)
                for index, review in enumerate(review_elements):
                    review_text = review.text.strip()

                    # Extract value for the current review
                    try:
                        dynamic_value_xpath = value_xpath_template.format(index + 1)
                        value_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, dynamic_value_xpath))
                        )
                        value_text = value_element.text.strip()
                        match = re.search(r'\d+', value_text)
                        value = int(match.group()) if match else None
                    except TimeoutException:
                        print(f"Value element not found for review {index + 1}.")
                        value = None
                    except Exception as e:
                        print(f"Failed to extract value for review {index + 1}: {e}")
                        value = None

                    # Add review and value as a dictionary
                    review_data = {"review": review_text, "value": value}
                    if review_data not in reviews:  # Avoid duplicates
                        reviews.append(review_data)
                        pbar.update(1)  # Update tqdm progress bar

                    if len(reviews) >= max_reviews:
                        break

                # Check if new reviews loaded
                if len(reviews) == previous_review_count:
                    print("No new reviews loaded. Stopping.")
                    break

                previous_review_count = len(reviews)

                # Click 'Load More' button
                try:
                    load_more_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, button_xpath))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                    time.sleep(3)
                    load_more_button.click()
                    time.sleep(8)
                except TimeoutException:
                    print("No 'Load More' button found or clickable. Stopping.")
                    break

        print(f"Collected {len(reviews)} reviews.")

    except Exception as e:
        print(f"An error occurred during scraping: {e}")

    finally:
        driver.quit()

    return reviews


# Example usage
if __name__ == "__main__":
    page_url = "https://pcmap.place.naver.com/restaurant/1557353265/review/visitor"
    review_class = "pui__vn15t2"
    button_xpath = "//*[@id=\"app-root\"]/div/div/div/div[6]/div[3]/div[3]/div[2]/div/a/span"
    value_xpath_template = "//*[@id=\"app-root\"]/div/div/div/div[6]/div[3]/div[3]/div[1]/ul/li[{}]/div[7]/div[2]/div/span[2]"  # Dynamic XPath

    collected_reviews = scrape_reviews(
        page_url, review_class, button_xpath, value_xpath_template, max_reviews=80
    )

    # Print reviews and values
    print("Reviews and Values:")
    for i, review_data in enumerate(collected_reviews, 1):
        print(f"{i}: Review: {review_data['review']}, Value: {review_data['value']}")

    # Save to JSON file
    with open("naver_yuzu_review_80.csv", "w", encoding="utf-8") as f:
        json.dump(collected_reviews, f, ensure_ascii=False, indent=4)
