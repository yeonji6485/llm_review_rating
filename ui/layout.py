import tkinter as tk
from tkinter import messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json

def safe_log(message):
    """
    Safely log messages to the log_text widget if available.
    If log_text is not initialized, print to the console.
    """
    if log_text:
        log_text.insert(tk.END, message + "\n")  # self-referencing 제거
        log_text.see(tk.END)  # 자동 스크롤
    else:
        print(message)

# Action List to store user-defined actions
action_list = []
log_text = None  # 초기화
if log_text:
    safe_log("Message here.\n")

# Extract Class Name Function
def extract_class_name(input_text):
    try:
        match = re.search(r'class\s*=\s*"([^"]+)"', input_text)
        if match:
            return match.group(1).split()[0]
        return input_text
    except Exception as e:
        if 'log_text' in globals():
            safe_log(f"Error extracting class name: {str(e)}\n")
        return None

# Scroll and Load Function
def scroll_to_load(driver, xpath=None, class_name=None, start_idx=0, end_idx=None):
    """
    Scrolls until the required number of elements are loaded or no more content is available.
    """
    try:
        prev_height = driver.execute_script("return document.body.scrollHeight")
        collected_data = []

        while True:
            # Scroll to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for the page height to change
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.body.scrollHeight") > prev_height
            )
            prev_height = driver.execute_script("return document.body.scrollHeight")

            # Collect elements
            elements = []
            if xpath:
                elements = driver.find_elements(By.XPATH, xpath)
            elif class_name:
                elements = driver.find_elements(By.CLASS_NAME, class_name)

            if end_idx and len(elements) >= end_idx:
                collected_data = elements[start_idx:end_idx]
                break

            safe_log(f"Collected {len(elements)} items so far.")

        safe_log(f"Completed scrolling. Collected {len(collected_data)} items.")
        return collected_data

    except Exception as e:
        safe_log(f"Error during scrolling: {str(e)}")
        return []

# Handle Element Actions
def handle_element_actions(driver, action_xpath=None, action_class_name=None, action_type="click"):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, action_xpath)) if action_xpath else
            EC.presence_of_element_located((By.CLASS_NAME, action_class_name))
        )
        if action_type == "click":
            element.click()
        elif action_type == "hover":
            ActionChains(driver).move_to_element(element).perform()

        safe_log(f"Action '{action_type}' performed successfully.")
        return True
    except Exception as e:
        safe_log(f"Error performing action: {str(e)}")
        return False



# Hide Elements
def hide_elements(driver, class_name=None, xpath=None):
    try:
        if class_name:
            elements = driver.find_elements(By.CLASS_NAME, class_name)
            for element in elements:
                driver.execute_script("arguments[0].style.display = 'none';", element)
            safe_log(f"Hid elements with class name: {class_name}")

        if xpath:
            elements = driver.find_elements(By.XPATH, xpath)
            for element in elements:
                driver.execute_script("arguments[0].style.display = 'none';", element)
            safe_log(f"Hid elements with XPath: {xpath}")

    except Exception as e:
        safe_log(f"Error hiding elements: {str(e)}")

# Selenium Crawling
def selenium_crawling(driver, xpath=None, class_name=None, start_idx=0, end_idx=None):
    """
    Crawls the page and collects data until the required number of elements are loaded.
    """
    try:
        elements = scroll_to_load(driver, xpath=xpath, class_name=class_name, start_idx=start_idx, end_idx=end_idx)

        if not elements:
            safe_log("No elements found for crawling.")
            return []

        collected_data = [element.text for element in elements]
        safe_log(f"Collected {len(collected_data)} items.")
        return collected_data

    except Exception as e:
        safe_log(f"Error during crawling: {str(e)}")
        return []

import requests


# Function to call API and return URLs
def call_api(method, url, headers=None, payload=None):
    """
    요청 메서드를 동적으로 처리하는 함수.

    Parameters:
        method (str): 요청 메서드 ("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD" 등)
        url (str): 요청 URL
        headers (dict): 요청 헤더
        payload (dict): 요청 데이터 (JSON 또는 params)

    Returns:
        dict or None: 응답 데이터 (JSON 파싱 가능 시), 그렇지 않으면 None
    """
    try:
        method = method.upper()  # 메서드 이름 대문자로 변환
        if method == "GET":
            response = requests.get(url, headers=headers, params=payload)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=payload)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=payload)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=payload)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, json=payload)
        elif method == "OPTIONS":
            response = requests.options(url, headers=headers)
        elif method == "HEAD":
            response = requests.head(url, headers=headers)
        else:
            raise ValueError(f"지원되지 않는 HTTP 메서드입니다: {method}")
        
        # 응답 상태 코드 확인
        response.raise_for_status()

        # HEAD 요청의 경우 본문이 없으므로 None 반환
        if method == "HEAD":
            return response.headers

        # OPTIONS 요청의 경우 지원 메서드 정보를 반환
        if method == "OPTIONS":
            return response.headers.get('Allow', '지원 메서드 정보를 확인할 수 없습니다.')

        # 응답 데이터가 JSON 형태일 경우 파싱
        try:
            return response.json()
        except ValueError:
            # JSON이 아닌 경우 None 반환
            return response.text if method not in ["HEAD", "OPTIONS"] else None

    except requests.exceptions.HTTPError as http_err:
        safe_log(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        safe_log(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        safe_log(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        safe_log(f"General API error occurred: {req_err}")
    except Exception as e:
        safe_log(f"Unexpected error: {e}")

    return None

# 5. flatten_dict 개선
def flatten_dict(d, parent_key='', sep='.'):
    try:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    except Exception as e:
        if log_text:
            safe_log(f"Flatten error: {str(e)}\n")
        return {}

# Function to extract URLs from API response
def extract_urls_from_response(response, key_path):
    try:
        keys = key_path.split(".")
        for key in keys:
            response = response.get(key, {})
        return response if isinstance(response, list) else []
    except AttributeError:
        safe_log(f"Invalid response structure for key path: {key_path}")
        return []

# Updated Click Action
def handle_click(driver, xpath=None, class_name=None, delay=1):
    try:
        if xpath:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        elif class_name:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
        else:
            raise ValueError("XPath or class_name must be provided for click.")
        
        element.click()
        time.sleep(delay)
        return True  # Indicate success

    except Exception as e:
        print(f"Click failed: {e}")
        return False

# New Click-List Action
def handle_click_list(driver, urls, actions, delay=1):
    for url in urls:
        try:
            driver.get(url)
            time.sleep(delay)

            for action in actions:
                action_type = action["type"]
                target = action.get("target", {})
                if action_type == "click":
                    handle_click(
                        driver,
                        xpath=target.get("xpath"),
                        class_name=target.get("class_name"),
                        delay=action.get("delay", 1),
                    )
                elif action_type == "click-list":
                    nested_urls = extract_urls_from_response(driver.page_source, action["url_key"])
                    handle_click_list(driver, nested_urls, action.get("actions", []), delay)

        except Exception as e:
            print(f"Error in handle_click_list: {e}")

def add_action():
    action_type = action_type_var.get()
    target_xpath = action_xpath_entry.get().strip()
    target_class = action_class_entry.get().strip()
    delay = int(delay_entry.get().strip())
    start_idx = int(start_idx_entry.get().strip() or 0)
    end_idx = int(end_idx_entry.get().strip() or 0)
    valid_action_types = ["click", "hide", "delay", "crawl", "click-list"]
    if action_type not in valid_action_types:
        messagebox.showerror("Input Error", f"Invalid action type: {action_type}")
        return


    # 추가된 필드 가져오기
    request_method = request_method_var.get()  # 선택된 요청 메서드
    pagination_size = int(pagination_size_entry.get().strip() or 30)
    key_path = key_path_entry.get().strip()

    if target_class:
        target_class = extract_class_name(target_class)

    if not action_type:
        messagebox.showerror("Input Error", "Action Type is required.")
        return

    action = {
        "type": action_type,
        "delay": delay,
        "start_idx": start_idx,
        "end_idx": end_idx,
        "request_method": request_method,  # 요청 메서드 추가
        "pagination_size": pagination_size,  # 페이지 크기 추가
        "key_path": key_path,  # Key Path 추가
    }
    if target_xpath:
        action["target"] = {"xpath": target_xpath}
    elif target_class:
        action["target"] = {"class_name": target_class}
    else:
        messagebox.showerror("Input Error", "Either XPath or Class-name must be provided.")
        return

    action_list.append(action)
    action_log_text.insert(tk.END, f"Action added: {action}\n")

# Synchronize Action List from Log
def sync_action_list_from_log():
    try:
        log_content = action_log_text.get("1.0", tk.END).strip()
        global action_list
        action_list = []
        actions = log_content.splitlines()
        for line in actions:
            if "Action added:" in line:
                action = json.loads(line.split("Action added:")[1].strip())
                action_list.append(action)
    except Exception as e:
        if log_text:
            safe_log(f"Sync error: {str(e)}\n")


# Function to recursively iterate over all combinations of indices for any website
def perform_action_for_combinations(driver, action, start_idx_sets, end_idx_sets, current_indices=None, delay=1):
    if current_indices is None:
        current_indices = []

    # Base case: If the current_indices has reached the number of dimensions, perform the action
    if len(current_indices) == len(start_idx_sets):
        safe_log(f"Performing action for combination: {current_indices}\n")
        perform_action(driver, current_indices, action, delay)
        return

    # Recursive case: Loop through the current dimension's range
    current_dim = len(current_indices)
    for idx in range(start_idx_sets[current_dim], end_idx_sets[current_dim] + 1):
        # Append the current index and recurse for the next dimension
        perform_action_for_combinations(driver, action, start_idx_sets, end_idx_sets,
                                         current_indices + [idx], delay)


# General action function that can handle clicking, crawling, or other actions
def perform_action(driver, indices, action, delay=1):
    try:
        # Create a dynamic XPath or class name based on the current indices
        xpath = create_dynamic_xpath(indices)  # Example: dynamically create XPath based on indices

        # Perform the action (click, crawl, etc.)
        if action['type'] == 'click':
            click_element(driver, xpath, delay)
        elif action['type'] == 'crawl':
            crawl_data(driver, xpath, action, delay)
        
        time.sleep(delay)

    except Exception as e:
        safe_log(f"Error performing action for {indices}: {str(e)}\n")


# Function to create a dynamic XPath based on indices
def create_dynamic_xpath(indices, template="//div[@class='item-class'][{0}][{1}]"):
    return template.format(*indices)

# Function to click an element given the dynamic XPath
def click_element(driver, xpath, delay):
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    element.click()
    safe_log(f"Clicked element with XPath: {xpath}\n")
    time.sleep(delay)

    # Wait for the page to load after clicking
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Reload the main page to get the updated list
    reload_main_page(driver)


# Function to crawl data from an element given the dynamic XPath
def crawl_data(driver, xpath, action, delay):
    try:
        elements = driver.find_elements(By.XPATH, xpath)
        collected_data = []
        for element in elements:
            collected_data.append(element.text)
        
        safe_log(f"Collected data: {collected_data}\n")
    except Exception as e:
        safe_log(f"Error collecting data from {xpath}: {str(e)}\n")

# Reload the main page using the URL input after each action
def reload_main_page(driver, class_name):
    try:
        url = url_entry.get()  # URL 입력값 가져오기
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        safe_log("Main page reloaded successfully.")
    except Exception as e:
        safe_log(f"Error reloading main page: {str(e)}")


# Execute Crawling
def execute_crawling(headers, payload, api_url, key_path, actions):
    try:
        # Step 1: Fetch URLs using API
        response = call_api("POST", api_url, headers=headers, payload=payload)
        urls = extract_urls_from_response(response, key_path)
        if not urls:
            print("No URLs found.")
            return

        # Step 2: Initiate WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(cache_valid_range=7).install()))

        # Step 3: Loop through URLs and execute actions
        for url in urls:
            driver.get(url)
            time.sleep(2)  # Allow page to load

            for action in actions:
                if action["type"] == "click":
                    handle_click(
                        driver,
                        xpath=action.get("target", {}).get("xpath"),
                        class_name=action.get("target", {}).get("class_name"),
                        delay=action.get("delay", 1),
                    )
                elif action["type"] == "click-list":
                    nested_urls = extract_urls_from_response(driver.page_source, action["url_key"])
                    handle_click_list(driver, nested_urls, action.get("actions", []), delay=1)

        print("Crawling completed.")

    except Exception as e:
        print(f"Error in execute_crawling: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

def flatten_dict(d, parent_key='', sep='.'):
    """
    Flattens a nested dictionary into a single dictionary with dot-separated keys.
    
    Parameters:
        d (dict): The original dictionary to flatten.
        parent_key (str): The base key to prepend (used for recursion).
        sep (str): Separator for nested keys.
    
    Returns:
        dict: A flattened dictionary.
    """
    try:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                if len(v) > 0:
                    for i, item in enumerate(v):
                        if isinstance(item, (dict, list)):
                            items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                        else:
                            items.append((f"{new_key}[{i}]", item))
                else:
                    items.append((new_key, []))  # Handle empty list
            else:
                items.append((new_key, v))
        return dict(items)
    except Exception as e:
        safe_log(f"Flatten error: {str(e)}")
        return {}


def execute_crawling_with_actions():
    """
    Executes the actions defined in the action list with Pagination, Key Path, and Request Method.
    """
    try:
        url = url_entry.get()
        if not url:
            messagebox.showerror("Input Error", "URL is required.")
            return

        driver = webdriver.Chrome(service=Service(ChromeDriverManager(cache_valid_range=7).install()))
        driver.get(url)
        safe_log(f"URL loaded: Waiting for the page to load...\n")

        # Explicit wait for the page to load
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            safe_log("Page load complete.\n")
        except Exception as e:
            safe_log(f"Error waiting for page load: {str(e)}\n")
            return

        # Execute each action in the action list
        for action in action_list:
            action_type = action.get("type")
            target = action.get("target", {})
            delay = action.get("delay", 1)

            # 추가된 필드 가져오기
            request_method = action.get("request_method", "GET")
            pagination_size = action.get("pagination_size", 30)
            key_path = action.get("key_path", "")

            safe_log(f"Executing action: {action}\n")

            try:
                if action_type == "crawl":
                    # API 호출에 추가된 필드 반영
                    headers = {}  # Add any headers if needed
                    payload = {"page_size": pagination_size}  # Example payload with Pagination
                    response = call_api(request_method, url, headers=headers, payload=payload)
                    if response:
                        # 평탄화된 딕셔너리 생성
                        flattened_data = flatten_dict(response)
                        # Key Path에 해당하는 데이터 추출
                        results = [v for k, v in flattened_data.items() if key_path in k]
                        results_text.insert(tk.END, "\n".join(map(str, results)) + "\n")
                    else:
                        safe_log("No data found.\n")

                elif action_type in ["click", "hover"]:
                    handle_element_actions(
                        driver,
                        action_xpath=target.get("xpath"),
                        action_class_name=target.get("class_name"),
                        delay=delay,
                        action_type=action_type,
                    )

            except Exception as e:
                safe_log(f"Error executing action {action}: {str(e)}\n")
                continue

        safe_log("All actions completed.\n")

    except Exception as e:
        messagebox.showerror("Error", f"Error occurred: {str(e)}")

    finally:
        if driver:
            driver.quit()


# GUI Setup
root = tk.Tk()
root.title("Crawling Tool")
root.attributes('-topmost', True)  # Always on top
root.geometry("800x600")  # 정적 크기 설정


# URL Input Section
url_frame = tk.LabelFrame(root, text="URL", padx=10, pady=10)
url_frame.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="ew")

url_entry = tk.Entry(url_frame)
url_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

# Action Settings
action_frame = tk.LabelFrame(root, text="Action Settings", padx=10, pady=10)
action_frame.grid(row=1, column=0, columnspan=1, padx=10, pady=10, sticky="ew")

action_frame.columnconfigure(1, weight=1)  # 내부 열 확장 가능
action_type_var = tk.StringVar(value="click")  # 초기화

# Action Type - 다섯 개 라디오 버튼
tk.Label(action_frame, text="Action Type:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
tk.Radiobutton(action_frame, text="Click", variable=action_type_var, value="click").grid(row=0, column=1, sticky="w")
tk.Radiobutton(action_frame, text="Hide", variable=action_type_var, value="hide").grid(row=0, column=2, sticky="w")
tk.Radiobutton(action_frame, text="Delay", variable=action_type_var, value="delay").grid(row=0, column=3, sticky="w")
tk.Radiobutton(action_frame, text="Crawl", variable=action_type_var, value="crawl").grid(row=0, column=4, sticky="w")
tk.Radiobutton(action_frame, text="Click-List", variable=action_type_var, value="click-list").grid(row=0, column=5, sticky="w")

tk.Label(action_frame, text="Action XPath:", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
action_xpath_entry = tk.Entry(action_frame)
action_xpath_entry.grid(row=1, column=1, columnspan=5, pady=5, sticky="ew")

tk.Label(action_frame, text="Action Class-name:", font=("Arial", 10)).grid(row=2, column=0, sticky="w")
action_class_entry = tk.Entry(action_frame)
action_class_entry.grid(row=2, column=1, columnspan=5, pady=5, sticky="ew")


# Delay
tk.Label(action_frame, text="Delay (Seconds):", font=("Arial", 10)).grid(row=3, column=0, sticky="w")
delay_entry = tk.Entry(action_frame, width=10)
delay_entry.insert(0, "1")
delay_entry.grid(row=3, column=1, pady=5)

# Start and End Index
tk.Label(action_frame, text="Start Index:", font=("Arial", 10)).grid(row=4, column=0, sticky="w")
start_idx_entry = tk.Entry(action_frame, width=10)
start_idx_entry.grid(row=4, column=1, pady=5)

tk.Label(action_frame, text="End Index:", font=("Arial", 10)).grid(row=4, column=2, sticky="w")
end_idx_entry = tk.Entry(action_frame, width=10)
end_idx_entry.grid(row=4, column=3, pady=5)

# Request Method (HTTP Method Selection)
tk.Label(action_frame, text="Request Method:", font=("Arial", 10)).grid(row=6, column=0, sticky="w")
request_method_var = tk.StringVar(value="POST")  # Default method is POST
request_method_dropdown = tk.OptionMenu(action_frame, request_method_var, 
                                         "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD")
request_method_dropdown.grid(row=6, column=1, pady=5)

tk.Label(action_frame, text="Pagination Size:", font=("Arial", 10)).grid(row=7, column=0, sticky="w")
pagination_size_entry = tk.Entry(action_frame, width=10)  # Pagination Size 입력 필드
pagination_size_entry.insert(0, "30")
pagination_size_entry.grid(row=7, column=1, pady=5)

tk.Label(action_frame, text="Key Path:", font=("Arial", 10)).grid(row=8, column=0, sticky="w")
key_path_entry = tk.Entry(action_frame, width=50)  # JSON Key Path 입력 필드
key_path_entry.grid(row=8, column=1, columnspan=3, pady=5)


# Action Log Section
action_log_frame = tk.LabelFrame(root, text="Action Log", padx=10, pady=10)
action_log_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

action_log_text = scrolledtext.ScrolledText(action_log_frame, height=10, width=70)  # 폭을 기준으로 설정
action_log_text.grid(row=0, column=0, columnspan=5, pady=5)

# Log Section
log_frame = tk.LabelFrame(root, text="Log", padx=10, pady=10)
log_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5, sticky="nsew")

log_frame.columnconfigure(0, weight=1)  # 프레임 내부 요소 조정
log_text = scrolledtext.ScrolledText(log_frame, height=25, width=70)
log_text.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

# Results Section
results_frame = tk.LabelFrame(root, text="Results", padx=10, pady=10)
results_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="nsew")

results_frame.columnconfigure(0, weight=1)  # 프레임 내부 요소 조정
results_text = scrolledtext.ScrolledText(results_frame, height=25, width=70)
results_text.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

# Buttons
add_action_button = tk.Button(action_frame, text="Add Action", command=add_action, bg="green", fg="white", width=15)
add_action_button.grid(row=9, column=0, padx=10, pady=5)

sync_button = tk.Button(action_log_frame, text="Sync from Log", command=sync_action_list_from_log, bg="orange", fg="white", width=15)
sync_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")     # 동기화 버튼 다음

clear_log_button = tk.Button(
    action_log_frame,
    text="Clear Log",
    command=lambda: [
        action_log_text.delete(1.0, tk.END),
        log_text.delete(1.0, tk.END) if log_text else None,  # log_text가 초기화 가능한지 체크 후 삭제
        safe_log("Logs have been cleared.")  # 로그 초기화 메시지 추가
    ],
    bg="red",
    fg="white",
    width=15,
)
clear_log_button.grid(row=1, column=2, padx=10, pady=10, sticky="ew")  # 로그 초기화 버튼 마지막

execute_button = tk.Button(action_log_frame, text="Execute Crawling", command=execute_crawling_with_actions, bg="blue", fg="white", width=15)
execute_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")  # 실행 버튼을 첫 번째로 배치

# Adjust dynamic dimensions
root.columnconfigure(0, weight=1)  # Action Settings 크기 고정
root.columnconfigure(1, weight=1)  # Log 크기 고정
root.columnconfigure(2, weight=1)  # Results 크기 고정
root.rowconfigure(2, weight=1)

# Set initial window size
root.update_idletasks()
initial_width = 70 * 10 + 40  # 각 컬럼 폭에 맞게 초기 크기 설정 (폭 * 글자 수 + 여백)
initial_height = action_frame.winfo_reqheight() + log_frame.winfo_reqheight() + 80  # 높이 계산
root.geometry(f"{initial_width}x{initial_height}")

# Start GUI loop
root.mainloop()