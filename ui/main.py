import tkinter as tk
from tkinter import messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def dynamic_url_xpath_processing(url1, url2, xpath1, xpath2):
    """두 URL 또는 XPath를 비교하여 바뀌는 부분을 {n}으로 처리"""
    url_template, xpath_template = url1, xpath1
    if url1 and url2:
        for i in range(len(url1)):
            if url1[i] != url2[i]:
                url_template = url1[:i] + "{n}" + url1[i + 1:]
                break
    if xpath1 and xpath2:
        for i in range(len(xpath1)):
            if xpath1[i] != xpath2[i]:
                xpath_template = xpath1[:i] + "{n}" + xpath1[i + 1:]
                break
    return url_template, xpath_template


def selenium_test_run(url, xpath=None, class_name=None):
    """단일 URL과 XPath/Class-name으로 테스트 실행"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    result = ""
    try:
        driver.get(url)
        time.sleep(2)

        if xpath:
            try:
                element = driver.find_element(By.XPATH, xpath)
                result = f"XPath 테스트 성공: {element.text}"
            except Exception as e:
                result = f"XPath 테스트 실패: {str(e)}"
        elif class_name:
            try:
                element = driver.find_element(By.CLASS_NAME, class_name)
                result = f"Class-name 테스트 성공: {element.text}"
            except Exception as e:
                result = f"Class-name 테스트 실패: {str(e)}"
        else:
            result = "XPath 또는 Class-name이 필요합니다."
    finally:
        driver.quit()
    return result


def selenium_crawling(url_template, xpath_template, start_idx, end_idx, class_name=None):
    """동적 URL 및 XPath 처리 크롤링"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    results = []
    try:
        for n in range(start_idx, end_idx + 1):
            url = url_template.replace("{n}", str(n))
            driver.get(url)
            time.sleep(2)

            try:
                if xpath_template:
                    dynamic_xpath = xpath_template.replace("{n}", str(n))
                    element = driver.find_element(By.XPATH, dynamic_xpath)
                    results.append(element.text)
                elif class_name:
                    element = driver.find_element(By.CLASS_NAME, class_name)
                    results.append(element.text)
            except Exception as e:
                results.append(f"오류 발생 (URL: {url}, {n}): {str(e)}")
    finally:
        driver.quit()
    return results


def execute_crawling():
    """GUI에서 실행 버튼을 눌렀을 때 호출"""
    try:
        url1 = url_entry1.get()
        url2 = url_entry2.get()
        xpath1 = xpath_entry1.get()
        xpath2 = xpath_entry2.get()
        class_name = class_entry.get()
        start_idx = int(start_entry.get())
        end_idx = int(end_entry.get())

        if not url1 or (not xpath1 and not class_name):
            messagebox.showerror("입력 오류", "URL과 XPath 또는 Class-name 중 하나를 입력하세요.")
            return

        # Test Run
        if not url2 and (not xpath2 or not class_name):
            test_result = selenium_test_run(url1, xpath1, class_name)
            results_text.insert(tk.END, f"테스트 결과:\n{test_result}\n")
            return

        # 동적 URL 및 XPath 처리
        url_template, xpath_template = dynamic_url_xpath_processing(url1, url2, xpath1, xpath2)
        log_text.insert(tk.END, f"URL 템플릿: {url_template}\nXPath 템플릿: {xpath_template}\n")

        # 크롤링 실행
        results = selenium_crawling(url_template, xpath_template, start_idx, end_idx, class_name)
        results_text.insert(tk.END, "\n".join(results) + "\n")
        log_text.insert(tk.END, "크롤링 완료!\n")
    except Exception as e:
        messagebox.showerror("오류", f"오류 발생: {str(e)}")


# Tkinter GUI 설정
root = tk.Tk()
root.title("크롤링 툴")
root.geometry("700x600")

# URL 입력
tk.Label(root, text="URL 1:", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
url_entry1 = tk.Entry(root, width=50)
url_entry1.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="URL 2 (Optional):", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
url_entry2 = tk.Entry(root, width=50)
url_entry2.grid(row=1, column=1, padx=10, pady=5)

# XPath 입력
tk.Label(root, text="XPath 1:", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
xpath_entry1 = tk.Entry(root, width=50)
xpath_entry1.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="XPath 2 (Optional):", font=("Arial", 10)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
xpath_entry2 = tk.Entry(root, width=50)
xpath_entry2.grid(row=3, column=1, padx=10, pady=5)

# Class-name 입력
tk.Label(root, text="Class-name (Optional):", font=("Arial", 10)).grid(row=4, column=0, padx=10, pady=5, sticky="w")
class_entry = tk.Entry(root, width=50)
class_entry.grid(row=4, column=1, padx=10, pady=5)

# 반복 범위
tk.Label(root, text="Start Index:", font=("Arial", 10)).grid(row=5, column=0, padx=10, pady=5, sticky="w")
start_entry = tk.Entry(root, width=10)
start_entry.grid(row=5, column=1, sticky="w", padx=10, pady=5)

tk.Label(root, text="End Index:", font=("Arial", 10)).grid(row=6, column=0, padx=10, pady=5, sticky="w")
end_entry = tk.Entry(root, width=10)
end_entry.grid(row=6, column=1, sticky="w", padx=10, pady=5)

# 로그 및 결과 창
tk.Label(root, text="Log:", font=("Arial", 10)).grid(row=7, column=0, padx=10, pady=5, sticky="nw")
log_text = scrolledtext.ScrolledText(root, height=10, width=80)
log_text.grid(row=7, column=1, padx=10, pady=5)

tk.Label(root, text="Results:", font=("Arial", 10)).grid(row=8, column=0, padx=10, pady=5, sticky="nw")
results_text = scrolledtext.ScrolledText(root, height=10, width=80)
results_text.grid(row=8, column=1, padx=10, pady=5)

# 실행 버튼
execute_button = tk.Button(root, text="Execute Crawling", command=execute_crawling, bg="blue", fg="white")
execute_button.grid(row=9, column=1, pady=20)

root.mainloop()
