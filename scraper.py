import os
import time
import json
import datetime
from dotenv import load_dotenv # טעינת משתני סביבה
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# טעינת המשתנים מקובץ .env הממוקם באותה תיקייה
load_dotenv()

def run_scraper():
    # --- בדיקת תקינות המשתנים ---
    user = os.getenv('ITURAN_USER')
    password = os.getenv('ITURAN_PASS')
    
    if not user or not password:
        print("❌ שגיאה: המשתנים ITURAN_USER או ITURAN_PASS חסרים בקובץ .env!")
        print("אנא וודא שהקובץ קיים ומכיל את הפרטים הנכונים.")
        return # עצירת הריצה

    print(f"✅ הפרטים נטענו. מתחיל תהליך כניסה עבור משתמש: {user}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    try:
        print("🚀 ניסיון גישה לדף הכניסה...")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        # חיפוש שדות הכניסה
        print("Waiting for txtUserName...")
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        pass_input = driver.find_element(By.ID, "txtPassword")
        
        user_input.send_keys(user)
        pass_input.send_keys(password)
        
        driver.find_element(By.ID, "btnLogin").click()
        print("🔓 כפתור כניסה נלחץ. טוען נתונים...")
        
        time.sleep(20)
        print(f"✅ מחובר. כתובת נוכחית: {driver.current_url}")
        
    except Exception as e:
        print(f"⚠️ שגיאה: {str(e)}")
        driver.save_screenshot("ituran_error.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
