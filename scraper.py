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

# טעינת המשתנים (יעבוד במחשב, ב-GitHub זה יילקח מה-Secrets)
load_dotenv()

def get_pto_status(tooltip_text):
    if not tooltip_text: return "IDLE"
    if "פתיחת PTO" in tooltip_text or "עבודה" in tooltip_text:
        return "OPEN"
    elif "סגירת PTO" in tooltip_text:
        return "CLOSED"
    return "IDLE"

def update_local_db(new_scan):
    db_file = 'fleet_db.json'
    # בדיקה אם הקובץ קיים, אם לא יוצר מבנה בסיסי
    if not os.path.exists(db_file):
        db = {"vehicles": {}}
    else:
        with open(db_file, 'r', encoding='utf-8') as f:
            try:
                db = json.load(f)
            except:
                db = {"vehicles": {}}

    for vid, info in new_scan.items():
        if vid not in db['vehicles']:
            db['vehicles'][vid] = {"current_status": "UNKNOWN", "history": []}
        
        # זיהוי שינוי סטטוס לצורך דוח כלכלי
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
    
    if not user or not password:
        print("❌ שגיאה: חסרים פרטי התחברות (USER/PASS)")
        return

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 35)
    
    try:
        print(f"🚀 מתחבר עבור משתמש: {user}")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        # התחברות
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        pass_input = driver.find_element(By.ID, "txtPassword")
        user_input.send_keys(user)
        pass_input.send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()
        
        print("🔓 טוען נתוני צי...")
        time.sleep(25) # זמן טעינה למפה

        # איסוף רכבים מהמפה
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        print(f"📊 נמצאו {len(elements)} רכבים פעילים.")

        current_scan = {}
        for el in elements:
            try:
                v_id = el.get_attribute("id").split('-')[0]
                tooltip = el.get_attribute("data_tooltip") or ""
                status = get_pto_status(tooltip)
                
                current_scan[v_id] = {
                    "status": status,
                    "last_seen": datetime.datetime.now().isoformat(),
                    "info": tooltip
                }
            except: continue

        if current_scan:
            update_local_db(current_scan)
            print("💾 הנתונים נשמרו בהצלחה ב-fleet_db.json")
        
    except Exception as e:
        print(f"⚠️ תקלה: {str(e)}")
        driver.save_screenshot("ituran_debug.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
