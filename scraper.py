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
    if "פתיחת PTO" in tooltip_text: return "OPEN"
    elif "סגירת PTO" in tooltip_text: return "CLOSED"
    return "IDLE"

def run_scraper():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # התחזות לדפדפן רגיל כדי למנוע חסימות
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 45) # הגדלת זמן המתנה ל-45 שניות

    try:
        print("Starting... Accessing Ituran Official Login")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        # שלב 1: טיפול ב-iFrames (קריטי באיתוראן)
        time.sleep(5)
        if len(driver.find_elements(By.TAG_NAME, "iframe")) > 0:
            print("Iframe detected, switching context...")
            driver.switch_to.frame(0)

        # שלב 2: איתור שדות גמיש
        print("Waiting for login fields...")
        try:
            user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        except:
            print("ID not found, trying CSS selector...")
            user_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            
        pass_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        
        # שימוש ב-Secrets
        user_input.send_keys(os.environ.get('USER') or os.environ.get('ITURAN_USER'))
        pass_input.send_keys(os.environ.get('PASS') or os.environ.get('ITURAN_PASS'))
        
        login_btn = driver.find_element(By.CSS_SELECTOR, "#btnLogin, input[type='submit']")
        login_btn.click()
        print("Login clicked, waiting for dashboard...")

        # שלב 3: המתנה לטעינת הנתונים
        time.sleep(25)
        driver.switch_to.default_content() # חזרה מה-iFrame אם נכנסנו

        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        print(f"Found {len(elements)} vehicle elements.")

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
            print("Database updated successfully.")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        driver.save_screenshot("debug_error.png") # שמירת צילום מסך לניתוח
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
        
        prev = db['vehicles'][vid]["current_status"]
        if info['status'] == "OPEN" and prev != "OPEN":
            db['vehicles'][vid]["history"].append({"event": "STARTED", "time": info['last_seen']})
        elif info['status'] == "CLOSED" and prev == "OPEN":
            db['vehicles'][vid]["history"].append({"event": "ENDED", "time": info['last_seen']})
        db['vehicles'][vid]["current_status"] = info['status']

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper()
