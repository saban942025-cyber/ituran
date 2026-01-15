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
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Starting... Accessing Ituran")
        driver.get("https://fleet.ituran.com")
        
        wait = WebDriverWait(driver, 20)
        
        # ניסיון גמיש למצוא את שדות הכניסה
        try:
            user_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            pass_input = driver.find_element(By.NAME, "password")
        except:
            print("Trying alternative selectors for login...")
            user_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            pass_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        
        # שימוש ב-Secrets (וודא שהשמות תואמים למה שהגדרת ב-GitHub)
        user_val = os.getenv('USER') or os.getenv('ITURAN_USER')
        pass_val = os.getenv('PASS') or os.getenv('ITURAN_PASS')
        
        user_input.send_keys(user_val)
        pass_input.send_keys(pass_val)
        
        print("Logged in, waiting for dashboard...")
        login_btn = driver.find_element(By.XPATH, "//button | //input[@type='submit'] | //*[contains(text(), 'כניסה')]")
        login_btn.click()

        # המתנה לטעינה
        time.sleep(10)
        print(f"Current URL after login attempt: {driver.current_url}")
        
        # כאן ננסה למצוא את האלמנטים שראינו בתמונה
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        print(f"Found {len(elements)} vehicle elements.")
        
        # ... המשך הלוגיקה של העדכון ...

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        # צילום מסך של השגיאה (יעזור לנו מאוד)
        driver.save_screenshot("error_screenshot.png")
        raise e
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
