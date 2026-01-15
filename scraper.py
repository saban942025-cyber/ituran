import os
import json
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_pto_status(tooltip_text):
    if not tooltip_text: return "IDLE"
    if "פתיחת PTO" in tooltip_text:
        return "OPEN"
    elif "סגירת PTO" in tooltip_text:
        return "CLOSED"
    return "IDLE"

def run_scraper():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # ריצה ללא מסך (חובה ל-GitHub)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("--- שלב 1: ניסיון גישה לכתובת המעודכנת ---")
        # הכתובת הרשמית והנכונה
        driver.get("https://www.ituran.com/iweb2/iweb2p.aspx") 
        
        wait = WebDriverWait(driver, 30)
        
        # שלב 2: איתור שדות הכניסה לפי המבנה המדויק של איתורן
        print("Waiting for login fields...")
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        pass_input = driver.find_element(By.ID, "txtPassword")
        
        # משיכת פרטים מה-Secrets (תומך בשני השמות שהגדרנו)
        user_val = os.getenv('USER') or os.getenv('ITURAN_USER')
        pass_val = os.getenv('PASS') or os.getenv('ITURAN_PASS')
        
        if not user_val or not pass_val:
            print("ERROR: Missing login credentials in Secrets!")
            return

        user_input.send_keys(user_val)
        pass_input.send_keys(pass_val)
        
        # לחיצה על כפתור הכניסה לפי ה-ID באתר
        login_btn = driver.find_element(By.ID, "btnLogin")
        login_btn.click()
        print("Login clicked. Waiting for dashboard...")

        # המתנה לטעינת המפה והטבלה
        time.sleep(20) 
        
        # סריקת הרכבים בטבלה (מבוסס על ה-Class שראינו בתמונה)
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        print(f"Found {len(elements)} vehicle status elements.")

        current_data = {}
        for el in elements:
            try:
                # חילוץ ID וסטטוס מה-Tooltip
                raw_id = el.get_attribute("id").split('-')[0]
                tooltip = el.get_attribute("data_tooltip")
                status = get_pto_status(tooltip)
                
                current_data[raw_id] = {
                    "status": status,
                    "last_seen": datetime.datetime.now().isoformat(),
                    "info": tooltip
                }
            except: continue

        if current_data:
            update_local_db(current_data)
            print("--- שלב 3: נתונים נשמרו בהצלחה ---")
        else:
            print("Warning: No vehicle data found after login. Check if page loaded correctly.")

    except Exception as e:
        print(f"FAILED: {str(e)}")
        # צילום מסך במידה ויש שגיאה (עוזר לדיבאגינג)
        driver.save_screenshot("error_page.png")
        raise e
    finally:
        driver.quit()

def update_local_db(new_scan):
    db_file = 'fleet_db.json'
    # יצירת קובץ במידה ולא קיים
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
        
        prev_status = db['vehicles'][vid]["current_status"]
        
        # לוגיקת זיהוי אירועי PTO
        if info['status'] == "OPEN" and prev_status != "OPEN":
            db['vehicles'][vid]["history"].append({"event": "PTO_OPENED", "time": info['last_seen']})
        elif info['status'] == "CLOSED" and prev_status == "OPEN":
            db['vehicles'][vid]["history"].append({"event": "PTO_CLOSED", "time": info['last_seen']})

        db['vehicles'][vid]["current_status"] = info['status']

    # שמירה חזרה לקובץ
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper()
