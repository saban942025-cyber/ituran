import os
import time
import json
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_scraper():
    user = os.getenv('ITURAN_USER')
    password = os.getenv('ITURAN_PASS')
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    # הוספת User Agent כדי להיראות כמו דפדפן אמיתי ולא בוט
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🚀 מתחבר למערכת...")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        wait = WebDriverWait(driver, 30)
        # הזנת פרטים (כבר עובד)
        wait.until(EC.presence_of_element_located((By.ID, "txtUserName"))).send_keys(user)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()
        
        print("🔓 לחיצה בוצעה. ממתין 60 שניות לטעינת כל שכבות המפה...")
        time.sleep(60) 

        # --- חיזוק: חיפוש רחב במיוחד ---
        current_scan = {}
        
        # חיפוש כל אלמנט שיש לו ID שמתחיל ב-veh (נפוץ באיתורן) או Class של רכב
        # אנחנו מחפשים גם בתוך iFrames במידה ויש
        search_targets = [
            "div.StatOnMap", 
            "div[id*='veh']", 
            "div[class*='vehicle']", 
            "img[src*='vehicle']",
            "div[title]" # כל דיב עם כותרת הוא חשוד
        ]
        
        found_elements = []
        for target in search_targets:
            found_elements.extend(driver.find_elements(By.CSS_SELECTOR, target))
        
        print(f"🔎 נמצאו {len(found_elements)} אלמנטים חשודים כרכבים.")

        for el in found_elements:
            try:
                # חילוץ מזהה רכב - אם אין ID, נשתמש בטקסט או במיקום
                v_id = el.get_attribute("id") or el.get_attribute("title")
                if not v_id or len(v_id) < 2: continue

                # לקיחת כל המידע הגולמי לטובת ה"מלשינון"
                raw_info = el.get_attribute("title") or el.text or "No Info"
                
                # זיהוי סטטוס PTO
                status = "CLOSED"
                if any(word in raw_info for word in ["פתוח", "עבודה", "PTO", "פעיל"]):
                    status = "OPEN"
                
                current_scan[v_id] = {
                    "status": status,
                    "last_seen": datetime.datetime.now().isoformat(),
                    "debug_info": raw_info[:100] # המלשינון יציג לנו את זה
                }
            except: continue

        if current_scan:
            # עדכון הקובץ (שימוש בפונקציה הקיימת אצלך)
            update_local_db(current_scan)
            print(f"✅ הצלחה! עודכנו {len(current_scan)} רכבים ב-JSON.")
        else:
            print("❌ הכשל נמשך: לא נמצאו רכבים גם בחיפוש רחב. שומר צילום מסך.")
            driver.save_screenshot("kשל_מפה.png")

    except Exception as e:
        print(f"⚠️ שגיאה: {str(e)}")
    finally:
        driver.quit()
