import os
import json
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_scraper():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 60) # סבלנות של דקה שלמה

    try:
        print("--- שלב 1: התחברות לשרת איתורן ---")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        # טיפול בפריימים - איתורן מחביאים את הטופס בתוך פריים
        time.sleep(10)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"Detected {len(iframes)} iframes. Searching for login fields inside...")
            driver.switch_to.frame(0)

        # ניסיון איתור שדות המשתמש
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        pass_input = driver.find_element(By.ID, "txtPassword")
        
        # משיכת הנתונים שסידרנו ב-Secrets
        user_val = os.getenv('ITURAN_USER')
        pass_val = os.getenv('ITURAN_PASS')
        
        if not user_val or not pass_val:
            print("ERROR: Credentials missing in environment variables!")
            return

        user_input.send_keys(user_val)
        pass_input.send_keys(pass_val)
        
        login_btn = driver.find_element(By.ID, "btnLogin")
        login_btn.click()
        print("Login button clicked. Waiting for dashboard...")

        # המתנה לטעינת הנתונים (הטבלה של בורהאן וחכמת)
        time.sleep(30)
        driver.switch_to.default_content()

        # כאן הסקריפט יחפש את הרכבים
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        print(f"Found {len(elements)} vehicles on screen.")

    except Exception as e:
        print(f"FAILED: {str(e)}")
        driver.save_screenshot("ituran_debug.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
