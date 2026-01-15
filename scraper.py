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
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🚀 מתחבר לאיתורן...")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        # לוגין (כבר עובד אצלך)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.ID, "txtUserName"))).send_keys(user)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()
        
        print("🔓 לחיצה בוצעה, ממתין לטעינה מלאה (60 שניות)...")
        time.sleep(60) # זמן אקסטרה לטעינה כבדה

        # חיפוש רכבים בשיטה רחבה (מחפש כל DIV שיש לו ID שמכיל מספר רכב)
        # איתורן משתמשת בדרך כלל ב-Class 'StatOnMap' או 'v-marker'
        potential_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='Stat'], div[id*='veh']")
        print(f"🔍 נמצאו {len(potential_elements)} אלמנטים פוטנציאליים על המפה.")

        current_scan = {}
        for el in potential_elements:
            try:
                v_id = el.get_attribute("id")
                # מנסה למצוא טקסט בכל מקום אפשרי (title, alt, text)
                info = el.get_attribute("title") or el.text or el.get_attribute("outerHTML")
                
                status = "CLOSED"
                if "פתוח" in info or "עבודה" in info or "PTO" in info:
                    status = "OPEN"
                
                if v_id:
                    current_scan[v_id] = {
                        "status": status,
                        "last_seen": datetime.datetime.now().isoformat(),
                        "info": info[:100] # שומר רק התחלה של הטקסט לדיבאג
                    }
            except: continue

        if current_scan:
            # כאן אנחנו משתמשים בפונקציה שכתבנו לעדכון ה-JSON
            update_local_db(current_scan)
            print(f"💾 הצלחנו! נשמרו {len(current_scan)} רכבים.")
        else:
            print("❌ לא נמצאו נתונים. מצלם מסך לבדיקה.")
            driver.save_screenshot("debug_map.png")

    except Exception as e:
        print(f"⚠️ שגיאה: {str(e)}")
    finally:
        driver.quit()

# וודא שפונקציית update_local_db קיימת אצלך בקוד (כפי שכתבנו קודם)
