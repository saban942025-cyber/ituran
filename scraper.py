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
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("--- שלב 1: ניסיון גישה לכתובת המאומתת ---")
        # הכתובת המדויקת שמצאת ב-Network Tab
        driver.get("https://www.ituran.com/iweb2/login.aspx") 
        
        wait = WebDriverWait(driver, 30)
        
        print("Locating login fields...")
        # באיתורן iweb2 השדות הם txtUserName ו-txtPassword
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        pass_input = driver.find_element(By.ID, "txtPassword")
        
        # שימוש ב-Secrets מה-GitHub
        user_val = os.getenv('USER') or os.getenv('ITURAN_USER')
        pass_val = os.getenv('PASS') or os.getenv('ITURAN_PASS')
        
        if not user_val or not pass_val:
            print(f"ERROR: Credentials missing! User: {bool(user_val)}, Pass: {bool(pass_val)}")
            return

        user_input.send_keys(user_val)
        pass_input.send_keys(pass_val)
        
        # כפתור הכניסה הרשמי
        login_btn = driver.find_element(By.ID, "btnLogin")
        login_btn.click()
        print("Login clicked. Waiting for dashboard...")

        # המתנה לטעינת ה-PeleGrid והאייקונים של ה-PTO
        time.sleep(25) 
        
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        print(f"Found {len(elements)} vehicles.")

        current_data = {}
        for el in elements:
            try:
                v_id = el.get_attribute("id").split('-')[0]
                tooltip = el.get_attribute("data_tooltip")
                status = get_pto_status(tooltip)
                
                current_data[v_id] = {
                    "status": status,
                    "last_seen": datetime.datetime.now().isoformat(),
                    "info": tooltip
                }
            except: continue

        if current_data:
            update_local_db(current_data)
            print("--- שלב 3: נתונים עודכנו ב-fleet_db.json ---")
        else:
            print("Warning: No vehicle elements found. Check page load.")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        driver.save_screenshot("debug_error.png")
        raise e
    finally:
        driver.quit()

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
        
        prev_status = db['vehicles'][vid]["current_status"]
        if info['status'] == "OPEN" and prev_status != "OPEN":
            db['vehicles'][vid]["history"].append({"event": "OPEN", "time": info['last_seen']})
        elif info['status'] == "CLOSED" and prev_status == "OPEN":
            db['vehicles'][vid]["history"].append({"event": "CLOSE", "time": info['last_seen']})

        db['vehicles'][vid]["current_status"] = info['status']

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper()
