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
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("--- שלב 1: ניסיון גישה לאתר איתורן ---")
        driver.get("https://www.ituran.com/iweb2/login.aspx") 
        
        wait = WebDriverWait(driver, 20)
        
        # זיהוי שדות לוגין - שיטה גמישה
        user_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input#user_id")))
        pass_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'], input#password")
        
        # שימוש ב-Secrets - וודא שהגדרת אותם בדיוק ככה ב-GitHub
        user_val = os.getenv('USER') or os.getenv('ITURAN_USER')
        pass_val = os.getenv('PASS') or os.getenv('ITURAN_PASS')
        
        if not user_val or not pass_val:
            print("ERROR: Missing login credentials in Secrets!")
            return

        user_input.send_keys(user_val)
        pass_input.send_keys(pass_val)
        
        # לחיצה על כפתור הכניסה
        login_btn = driver.find_element(By.XPATH, "//button | //input[@type='submit'] | //a[contains(@class, 'login')]")
        login_btn.click()
        print("--- שלב 2: לוגין בוצע, ממתין לטעינת הדאשבורד ---")

        # המתנה לטעינה של האייקונים שראינו בתמונה
        time.sleep(15) 
        
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        print(f"נמצאו {len(elements)} רכבים בטבלה.")

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
            print("--- שלב 3: נתונים נשמרו בהצלחה ---")
        else:
            print("Warning: No data found during scan.")

    except Exception as e:
        print(f"שגיאה בתהליך: {str(e)}")
        raise e
    finally:
        driver.quit()

def update_local_db(new_scan):
    db_file = 'fleet_db.json'
    if not os.path.exists(db_file):
        db = {"vehicles": {}}
    else:
        with open(db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)

    for vid, info in new_scan.items():
        if vid not in db['vehicles']:
            db['vehicles'][vid] = {"current_status": "UNKNOWN", "history": []}
        
        if info['status'] == "OPEN" and db['vehicles'][vid]["current_status"] != "OPEN":
            db['vehicles'][vid]["history"].append({"event": "STARTED", "time": info['last_seen']})
        elif info['status'] == "CLOSED" and db['vehicles'][vid]["current_status"] == "OPEN":
            db['vehicles'][vid]["history"].append({"event": "ENDED", "time": info['last_seen']})

        db['vehicles'][vid]["current_status"] = info['status']

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper()
