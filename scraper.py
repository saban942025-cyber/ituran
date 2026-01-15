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
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🚀 מתחבר למערכת איתורן...")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        wait = WebDriverWait(driver, 40)
        # כניסה למערכת
        wait.until(EC.presence_of_element_located((By.ID, "txtUserName"))).send_keys(user)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()
        
        print("🔓 לוגין בוצע. ממתין 60 שניות לטעינה מלאה של המפה והרכבים...")
        time.sleep(60) 

        # --- מנגנון "פצצת עומק" למציאת רכבים ---
        current_scan = {}
        
        # פונקציית עזר לסריקת פריימים
        def scan_context():
            # חיפוש לפי כל קלאס או ID שקשור לרכב באיתורן
            targets = driver.find_elements(By.CSS_SELECTOR, "div[class*='Stat'], div[id*='veh'], div[id*='unit'], [title*='רכב']")
            for el in targets:
                try:
                    v_id = el.get_attribute("id") or el.get_attribute("title")
                    if not v_id or len(v_id) < 3: continue
                    
                    raw_info = el.get_attribute("title") or el.get_attribute("data_tooltip") or el.text
                    status = "CLOSED"
                    if any(word in raw_info for word in ["פתוח", "עבודה", "PTO", "פעיל"]):
                        status = "OPEN"
                    
                    current_scan[v_id] = {
                        "status": status,
                        "last_seen": datetime.datetime.now().isoformat(),
                        "debug_info": raw_info[:150] # נשלח למלשינון
                    }
                except: continue

        # סריקה בדף הראשי
        scan_context()
        
        # אם עדיין ריק, סורק בתוך כל ה-iframes
        if not current_scan:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"🔎 לא נמצאו רכבים בדף הראשי. סורק {len(iframes)} פריימים...")
            for i in range(len(iframes)):
                try:
                    driver.switch_to.default_content()
                    driver.switch_to.frame(i)
                    scan_context()
                    if current_scan: 
                        print(f"✅ נמצאו רכבים בפריים {i}!")
                        break
                except: continue

        if current_scan:
            # עדכון ה-JSON הקיים
            update_local_db(current_scan)
            print(f"💾 הצלחה! עודכנו {len(current_scan)} רכבים.")
        else:
            print("❌ הכשל נמשך: המפה נראית ריקה לבוט.")
            driver.save_screenshot("empty_map_debug.png")

    except Exception as e:
        print(f"⚠️ שגיאה: {str(e)}")
    finally:
        driver.quit()
