import os
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
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # בדיקה קריטית אם ה-Secrets הגיעו
        user = os.getenv('ITURAN_USER')
        password = os.getenv('ITURAN_PASS')
        
        if not user or not password:
            print(f"CRITICAL ERROR: Credentials are missing! User exists: {bool(user)}, Password exists: {bool(password)}")
            return

        print("Connecting to Ituran Official Login...")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        wait = WebDriverWait(driver, 40)
        
        # חיפוש שדה המשתמש
        print("Waiting for txtUserName...")
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        pass_input = driver.find_element(By.ID, "txtPassword")
        
        user_input.send_keys(user)
        pass_input.send_keys(password)
        
        driver.find_element(By.ID, "btnLogin").click()
        print("Login clicked! Checking dashboard...")
        
        time.sleep(20)
        print("Success! Current URL:", driver.current_url)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        driver.save_screenshot("ituran_debug.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
