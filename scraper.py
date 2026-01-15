import os
import time
import json
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_pto_status(text):
    if not text: return "IDLE"
    # חיזוק מילות המפתח - כל מה שיכול להעיד על עבודה
    keywords = ["פתוח", "עבודה", "PTO", "פעיל", "מנוף", "ON"]
    if any(word in text for word in keywords):
        return "OPEN"
    return "CLOSED"

def run_scraper():
    user = os.getenv('ITURAN_USER')
    password = os.getenv('ITURAN_PASS')
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🚀 מתחבר למערכת...")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        # לוגין
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.ID, "txtUserName"))).send_keys(user)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()
        
        print("🔓 לחיצה בוצעה. ממתין 60 שניות לטעינה מלאה של כל הרכבים...")
        time.sleep(60) 

        # --- החיזוק: חיפוש רב-שכבתי ---
        current_scan = {}
        
        # 1. חיפוש לפי קלאסים נפוצים באיתורן
        elements = driver.find_elements(By.CSS_SERVER, ".StatOnMap, .v-marker, [id*='veh'], [class*='vehicle']")
        
        # 2. אם לא מצא, ננסה "לגרד" את כל ה-Divים שיש להם טקסט
        if not elements:
            print("🔍 מנסה שיטת סריקה עמוקה...")
            elements = driver.find_elements(By.XPATH, "//div[@title] | //div[@data-tooltip]")

        print(f"🔎 נמצאו {len(elements)} אלמנטים חשודים כרכבים.")

        for el in elements:
            try:
                # חילוץ מידע מכל מקום אפשרי באלמנט
                v_id = el.get_attribute("id") or el.get_attribute("name")
                info_text = el.get_attribute("title") or el.get_attribute("data-tooltip") or el.text
                
                if not v_id or len(v_id) < 3: continue # דילוג על אלמנטים לא רלוונטיים

                status = get_pto_status(info_text)
                
                current_scan[v_id] = {
                    "status": status,
                    "last_seen": datetime.datetime.now().isoformat(),
                    "debug_info": info_text[:50] # לשמירה ב-Log
                }
            except: continue

        if current_scan:
            # עדכון ה-JSON (וודא שפונקציית update_local_db קיימת בקובץ)
            update_local_db(current_scan)
            print(f"✅ הצלחנו! עודכנו {len(current_scan)} רכבים.")
        else:
            print("❌ עדיין לא נמצאו נתונים. מצלם מסך לניתוח...")
            driver.save_screenshot("debug_map_empty.png")

    except Exception as e:
        print(f"⚠️ שגיאה: {str(e)}")
    finally:
        driver.quit()
