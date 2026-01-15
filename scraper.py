import os
import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# טעינת משתני סביבה
from dotenv import load_dotenv
load_dotenv()

def update_local_db(new_data):
    """מעדכן את ה-JSON עם נתונים אמיתיים בלבד"""
    db_file = 'fleet_db.json'
    if not new_data:
        print("DEBUG: No data found to update.")
        return

    # מבנה נתונים סופי לסיכום הכלכלי
    processed_fleet = {"vehicles": {}, "last_sync": datetime.datetime.now().isoformat()}
    
    # נירמול הנתונים מה-API/JS (מותאם למבנה איתורן נפוץ)
    vehicles_list = new_data if isinstance(new_data, list) else new_data.get('vehicles', [])
    
    for v in vehicles_list:
        v_id = str(v.get('id') or v.get('UnitID') or "unknown")
        # זיהוי סטטוס עבודה (PTO)
        is_working = v.get('pto') or v.get('is_active') or False
        status = "OPEN" if is_active else "CLOSED"
        
        processed_fleet["vehicles"][v_id] = {
            "status": status,
            "last_seen": datetime.datetime.now().isoformat(),
            "raw_debug": str(v)[:50] # לשליחת מידע למלשינון
        }

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(processed_fleet, f, indent=4, ensure_ascii=False)
    print(f"💾 הצלחה: {len(processed_fleet['vehicles'])} רכבים נכתבו לקובץ.")

def run_scraper():
    user = os.getenv('ITURAN_USER')
    password = os.getenv('ITURAN_PASS')
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    
    # הפעלת Performance Logging לקריאת ה-Network
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    
    driver = webdriver.Chrome(options=chrome_options, desired_capabilities=caps)
    
    try:
        print("🚀 שלב 1: התחברות חוקית...")
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        
        driver.find_element(By.ID, "txtUserName").send_keys(user)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "btnLogin").click()
        
        print("🔓 שלב 2: סריקת מקורות מידע (Network & JS)...")
        
        # המתנה חכמה לטעינת הנתונים (עד 60 שניות)
        data = None
        for _ in range(12): 
            # אופציה B: שליפה מזיכרון JS
            data = driver.execute_script("return window.__vehicles || window.units || window.map_data || null;")
            
            if not data:
                # אופציה A: חיפוש ב-Network Logs
                logs = driver.get_log('performance')
                for entry in logs:
                    log = json.loads(entry['message'])['message']
                    if 'Network.responseReceived' in log['method']:
                        url = log['params']['response']['url']
                        if 'Get' in url and 'Vehicles' in url: # דוגמה ל-URL API של איתורן
                            req_id = log['params']['requestId']
                            body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': req_id})
                            data = json.loads(body['body'])
                            break
            
            if data:
                print("✅ נתונים זוהו במקור פנימי!")
                break
            time.sleep(5)

        if data:
            print(f"DEBUG DATA FOUND: {json.dumps(data, indent=2)[:200]}...")
            update_local_db(data)
        else:
            print("❌ כשל: הבוט נשאר עיוור - לא נמצאו נתוני API או JS.")

    except Exception as e:
        print(f"⚠️ שגיאה: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
