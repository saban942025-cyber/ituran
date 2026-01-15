import os
import time
import json
import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

def get_pto_status(tooltip_text):
    if not tooltip_text: return "IDLE"
    # חיפוש מילות מפתח בתוך הטקסט של איתורן
    if "פתוח" in tooltip_text or "עבודה" in tooltip_text or "PTO" in tooltip_text:
        return "OPEN"
    return "CLOSED"

def update_local_db(new_scan):
    db_file = 'fleet_db.json'
    if not os.path.exists(db_file):
        db = {"vehicles": {}}
    else:
        with open(db_file, 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except: db = {"vehicles": {}}

    for vid, info in new_scan.items():
        if vid not in db['vehicles']:
            db['vehicles'][vid] = {"current_status": "UNKNOWN", "history": []}
        
        prev_status = db['vehicles'][vid].get("current_status", "UNKNOWN")
        if info['status'] == "OPEN" and prev_status != "OPEN":
            db['vehicles'][vid]["history"].append({"event": "STARTED", "time": info['last_seen']})
        elif info['status'] == "CLOSED" and prev_status == "OPEN":
            db['vehicles'][vid]["history"].append({"event": "ENDED", "time": info['last_seen']})

        db['vehicles'][vid]["current_status"] = info['status']
        db['vehicles'][vid]["last_update"] = info['last_seen']

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

def run_scraper():
    user = os.getenv('ITURAN_USER')
    password = os.getenv('ITURAN_PASS')
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 40)
    
    try:
        print(f"🚀 מתחבר לאיתורן...")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        # התחברות
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        user_input.send_keys(user)
        driver.find_element(By.ID, "btnLogin").click()
        
        print("🔓 ממתין לטעינת המפה (45 שניות)...")
        time.sleep(45) # זמן ארוך יותר לטעינת כל הצי

        # ניסיון למצוא רכבים בתוך כל פריים אפשרי
        found_vehicles = []
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"נמצאו {len(iframes)} פריימים בדף. סורק...")

        # סריקת הדף הראשי
        found_vehicles = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        
        # אם לא מצא בדף הראשי, עובר על הפריימים
        if not found_vehicles:
            for index, iframe in enumerate(iframes):
                driver.switch_to.default_content()
                driver.switch_to.frame(index)
                found_vehicles = driver.find_elements(By.CLASS_NAME, "StatOnMap")
                if found_vehicles:
                    print(f"✅ רכבים נמצאו בפריים מספר {index}")
                    break

        current_scan = {}
        for el in found_vehicles:
            try:
                v_id = el.get_attribute("id") or "unknown"
                # איתורן לפעמים שומרת את המידע ב-title או ב-alt
                tooltip = el.get_attribute("title") or el.get_attribute("data_tooltip") or ""
                status = get_pto_status(tooltip)
                
                current_scan[v_id] = {
                    "status": status,
                    "last_seen": datetime.datetime.now().isoformat(),
                    "info": tooltip
                }
            except: continue

        if current_scan:
            update_local_db(current_scan)
            print(f"💾 הצלחנו! נשמרו {len(current_scan)} רכבים ב-JSON.")
        else:
            print("❌ לא נמצאו רכבים על המפה. מצלם מסך לדיבאג.")
            driver.save_screenshot("no_vehicles_debug.png")
        
    except Exception as e:
        print(f"⚠️ תקלה: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
