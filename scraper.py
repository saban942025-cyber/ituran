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
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # כאן התיקון הקריטי - הכתובת שמצאנו ב-Network Tab
        print("Connecting to Ituran Official Login...")
        driver.get("https://www.ituran.com/iweb2/login.aspx") 
        
        wait = WebDriverWait(driver, 30)
        
        # משיכת פרטים מה-Secrets
        user_val = os.getenv('USER') or os.getenv('ITURAN_USER')
        pass_val = os.getenv('PASS') or os.getenv('ITURAN_PASS')
        
        if not user_val or not pass_val:
            print("ERROR: Missing Credentials in GitHub Secrets!")
            return

        # זיהוי השדות לפי המבנה של איתורן
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        pass_input = driver.find_element(By.ID, "txtPassword")
        
        user_input.send_keys(user_val)
        pass_input.send_keys(pass_val)
        
        login_btn = driver.find_element(By.ID, "btnLogin")
        login_btn.click()
        
        print("Login clicked. Checking if we are in...")
        time.sleep(20) 
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
