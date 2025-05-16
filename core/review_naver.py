from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time

def scrape_reviews(page_url: str, review_class: str, button_xpath: str, max_reviews: int = 100):
    """
    Scrapes reviews from a dynamic page by scrolling and clicking a 'Load More' button.

    :param page_url: The URL of the page to scrape.
    :param review_class: The class name of the review elements.
    :param button_xpath: The XPath of the 'Load More' button.
    :param max_reviews: Maximum number of reviews to scrape.
    :return: A list of reviews.
    """
    reviews = []
    previous_review_count = 0

    # Initialize WebDriver
    driver = webdriver.Chrome()
    driver.get(page_url)
    driver.maximize_window()

    try:
        while len(reviews) < max_reviews:
            # Extract reviews from the current page
            review_elements = driver.find_elements(By.CLASS_NAME, review_class)
            for review in review_elements:
                review_text = review.text
                if review_text not in reviews:  # Avoid duplicates
                    reviews.append(review_text)
                if len(reviews) >= max_reviews:
                    break

            # Check if new reviews are loaded
            if len(reviews) == previous_review_count:
                print("No new reviews loaded. Stopping.")
                break

            previous_review_count = len(reviews)

            # Find and click 'Load More' button if available
            try:
                load_more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, button_xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", load_more_button)  # Scroll to the button
                time.sleep(3)  # Allow time for scrolling
                load_more_button.click()
                time.sleep(10)  # Wait for new content to load
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
    page_url = "https://pcmap.place.naver.com/restaurant/11592650/review/visitor"
    review_class = "pui__vn15t2"
    button_xpath = "//*[@id=\"app-root\"]/div/div/div/div[6]/div[3]/div[3]/div[2]/div/a/span"

    collected_reviews = scrape_reviews(page_url, review_class, button_xpath, max_reviews=10000)

    print("Reviews:")
    for i, review in enumerate(collected_reviews, 1):
        print(f"{i}: {review}")

    # JSON 파일로 저장
    with open("naver_review.csv", "w", encoding="utf-8") as f:
        json.dump(collected_reviews, f, ensure_ascii=False, indent=4)
