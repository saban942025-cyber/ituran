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
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)

    try:
        print("Starting... Accessing Ituran Official Login")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        time.sleep(10) # המתנה לטעינה ראשונית

        # פונקציית עזר לחדירה לפריימים
        def find_login_fields():
            print("Searching for login fields in current context...")
            try:
                # ניסיון למצוא את המשתמש
                u = driver.find_element(By.ID, "txtUserName")
                p = driver.find_element(By.ID, "txtPassword")
                b = driver.find_element(By.ID, "btnLogin")
                return u, p, b
            except:
                return None

        # שלב 1: חיפוש בפריימים
        login_elements = find_login_fields()
        if not login_elements:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Elements not found in main. Found {len(iframes)} iframes. Searching inside...")
            for index, frame in enumerate(iframes):
                driver.switch_to.default_content()
                driver.switch_to.frame(index)
                login_elements = find_login_fields()
                if login_elements:
                    print(f"Success! Found fields in iframe index {index}")
                    break
        
        if not login_elements:
            print("ERROR: Could not find login fields in any frame. Saving screenshot.")
            driver.save_screenshot("debug_no_fields.png")
            return

        user_input, pass_input, login_btn = login_elements
        
        # הזנת פרטים
        user_val = os.getenv('USER') or os.getenv('ITURAN_USER')
        pass_val = os.getenv('PASS') or os.getenv('ITURAN_PASS')
        
        user_input.send_keys(user_val)
        pass_input.send_keys(pass_val)
        login_btn.click()
        print("Login clicked. Waiting for dashboard...")

        # שלב 2: המתנה לטעינת הנתונים
        time.sleep(30)
        driver.switch_to.default_content() # חזרה למבנה הראשי

        # חילוץ נתונים
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
        print(f"Error during run: {str(e)}")
        driver.save_screenshot("critical_error.png")
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
