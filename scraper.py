import os
import json
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_pto_status(tooltip_text):
    if "פתיחת PTO" in tooltip_text:
        return "OPEN"
    if "סגירת PTO" in tooltip_text:
        return "CLOSED"
    return "OFF"

def run_scraper():
    # הגדרות דפדפן לסביבת GitHub
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # התחברות (משתמש ב-Secrets שהגדרת ב-GitHub)
        driver.get("https://fleet.ituran.com") # וודא שזו הכתובת המדויקת
        
        # כאן הסקריפט ימלא את הפרטים (צריך לוודא ID של שדות ה-Login)
        wait = WebDriverWait(driver, 20)
        user_field = wait.until(EC.presence_of_element_located((By.NAME, "username"))) # שנה ל-ID הנכון
        user_field.send_keys(os.environ['USER'])
        driver.find_element(By.NAME, "password").send_keys(os.environ['PASS'])
        driver.find_element(By.ID, "login_btn").click()

        # המתנה לטעינת הטבלה
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "StatOnMap")))
        
        # שליפת נתונים
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        current_data = {}
        
        for el in elements:
            try:
                # ה-ID ששלחת לי: id="3001985-stat-1"
                raw_id = el.get_attribute("id").split('-')[0]
                tooltip = el.get_attribute("data_tooltip")
                status = get_pto_status(tooltip)
                
                current_data[raw_id] = {
                    "status": status,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "raw_info": tooltip
                }
            except: continue

        # עדכון בסיס הנתונים (השוואה למצב קודם)
        update_db(current_data)

    finally:
        driver.quit()

def update_db(current_scan):
    db_path = 'fleet_db.json'
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)

    for vehicle_id, info in current_scan.items():
        if vehicle_id not in db['vehicles']:
            db['vehicles'][vehicle_id] = {"current_status": "OFF", "logs": []}
        
        prev_status = db['vehicles'][vehicle_id]["current_status"]
        
        # לוגיקת התראות/ספירה
        if info['status'] == "OPEN" and prev_status != "OPEN":
            print(f"ALERT: PTO Opened for {vehicle_id}")
            db['vehicles'][vehicle_id]["logs"].append({"event": "OPEN", "time": info['timestamp']})
        
        elif info['status'] == "CLOSED" and prev_status == "OPEN":
            print(f"ALERT: PTO Closed for {vehicle_id}")
            db['vehicles'][vehicle_id]["logs"].append({"event": "CLOSE", "time": info['timestamp']})

        db['vehicles'][vehicle_id]["current_status"] = info['status']

    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper()
