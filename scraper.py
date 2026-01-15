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
    
    # הוספת User-Agent כדי להיראות כמו דפדפן אמיתי ולמנוע חסימות
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Starting... Accessing Ituran Official Page")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        wait = WebDriverWait(driver, 45) # הגדלנו את זמן ההמתנה ל-45 שניות

        # שלב בדיקת iFrame - אם השדות נמצאים בתוך חלון פנימי
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        if frames:
            print(f"Detected {len(frames)} iframes. Switching context...")
            driver.switch_to.frame(0) # מעבר ל-iFrame הראשון

        print("Waiting for txtUserName...")
        try:
            # ניסיון גמיש למצוא את שדה המשתמש
            user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        except:
            print("Trying alternative: looking for any text input...")
            user_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))

        pass_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'], #txtPassword")
        
        user_val = os.getenv('USER') or os.getenv('ITURAN_USER')
        pass_val = os.getenv('PASS') or os.getenv('ITURAN_PASS')
        
        user_input.send_keys(user_val)
        pass_input.send_keys(pass_val)
        
        # לחיצה על כפתור הכניסה
        login_btn = driver.find_element(By.CSS_SELECTOR, "#btnLogin, input[type='submit']")
        login_btn.click()
        print("Login button clicked. Waiting for dashboard...")

        # המתנה ארוכה לטעינת הדאשבורד
        time.sleep(25)
        
        elements = driver.find_elements(By.CLASS_NAME, "StatOnMap")
        print(f"Found {len(elements)} vehicles.")

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
            print("Successfully updated database.")
        else:
            print("Warning: Logged in but no vehicle elements found.")

    except Exception as e:
        print(f"Error during run: {str(e)}")
        # שמירת צילום מסך כדי שנראה בדיוק מה הבוט ראה
        driver.save_screenshot("debug_view.png")
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
            db['vehicles'][vid]["history"].append({"event": "STARTED", "time": info['last_seen']})
        elif info['status'] == "CLOSED" and prev_status == "OPEN":
            db['vehicles'][vid]["history"].append({"event": "ENDED", "time": info['last_seen']})
        db['vehicles'][vid]["current_status"] = info['status']

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper()
