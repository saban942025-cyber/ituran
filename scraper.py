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
        driver.get("https://fleet.ituran.com") # וודא שזו הכתובת המדויקת של דף הכניסה
        
        wait = WebDriverWait(driver, 30)
        
        # שלב הכניסה - וודא שמות שדות ה-Input באתר (NAME או ID)
        user_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        pass_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        
        user_input.send_keys(os.environ['USER'])
        pass_input.send_keys(os.environ['PASS'])
        
        # חיפוש כפתור כניסה ולחיצה
        login_btn = driver.find_element(By.XPATH, "//button | //input[@type='submit'] | //a[contains(@class, 'login')]")
        login_btn.click()

        # המתנה לטעינת טבלת הרכבים
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "StatOnMap")))
        time.sleep(5) # זמן נוסף לטעינת כל האייקונים

        # סריקת כל הרכבים בטבלה
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        current_data = {}
        
        for el in elements:
            try:
                # חילוץ מזהה הרכב והסטטוס מה-Tooltip שראינו בתמונה
                v_id = el.get_attribute("id").split('-')[0]
                tooltip = el.get_attribute("data_tooltip")
                status = get_pto_status(tooltip)
                
                current_data[v_id] = {
                    "status": status,
                    "last_seen": datetime.datetime.now().isoformat(),
                    "info": tooltip
                }
            except: continue

        update_local_db(current_data)

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
        
        # לוגיקת ספירת זמן פתיחת מנוף
        if info['status'] == "OPEN" and db['vehicles'][vid]["current_status"] != "OPEN":
            db['vehicles'][vid]["history"].append({"event": "STARTED", "time": info['last_seen']})
        elif info['status'] == "CLOSED" and db['vehicles'][vid]["current_status"] == "OPEN":
            db['vehicles'][vid]["history"].append({"event": "ENDED", "time": info['last_seen']})

        db['vehicles'][vid]["current_status"] = info['status']

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper()
