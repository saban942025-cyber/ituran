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
    chrome_options.add_argument("--window-size=1920,1080") # חובה כדי לראות את כל הטבלה
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Starting... Accessing Ituran")
        driver.get("https://www.ituran.com/iweb2/login.aspx") # הכתובת המאומתת
        
        wait = WebDriverWait(driver, 30)
        
        # התחברות
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        pass_input = driver.find_element(By.ID, "txtPassword")
        
        user_input.send_keys(os.environ.get('USER') or os.environ.get('ITURAN_USER'))
        pass_input.send_keys(os.environ.get('PASS') or os.environ.get('ITURAN_PASS'))
        
        login_btn = driver.find_element(By.ID, "btnLogin")
        login_btn.click()
        print("Login clicked, waiting for data...")

        # המתנה ארוכה יותר לטעינת הנתונים האמיתיים
        time.sleep(20) 

        # ניסיון חילוץ נתונים
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        print(f"Found {len(elements)} vehicles on screen.") # זה ידפיס לנו ב-Log כמה הוא מצא

        current_data = {}
        for el in elements:
            try:
                v_id = el.get_attribute("id").split('-')[0]
                tooltip = el.get_attribute("data_tooltip") or ""
                status = get_pto_status(tooltip)
                
                current_data[v_id] = {
                    "status": status,
                    "last_seen": datetime.datetime.now().isoformat(),
                    "info": tooltip
                }
            except: continue

        if current_data:
            update_local_db(current_data)
            print(f"Successfully updated {len(current_data)} vehicles in JSON.")
        else:
            print("Warning: No vehicle data captured. Check selectors.")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise e
    finally:
        driver.quit()

def update_local_db(new_scan):
    db_file = 'fleet_db.json'
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
        
        # זיהוי שינוי סטטוס
        if info['status'] == "OPEN" and db['vehicles'][vid]["current_status"] != "OPEN":
            db['vehicles'][vid]["history"].append({"event": "STARTED", "time": info['last_seen']})
        elif info['status'] == "CLOSED" and db['vehicles'][vid]["current_status"] == "OPEN":
            db['vehicles'][vid]["history"].append({"event": "ENDED", "time": info['last_seen']})

        db['vehicles'][vid]["current_status"] = info['status']

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper()
