import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_scraper():
    # הגדרות דפדפן עם "אוזניים" לרשת
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    
    driver = webdriver.Chrome(options=chrome_options, desired_capabilities=caps)
    wait = WebDriverWait(driver, 30)

    try:
        # התחברות (החלק שעובד)
        driver.get("https://www.ituran.com/iweb2/login.aspx")
        driver.find_element(By.ID, "txtUserName").send_keys(os.getenv('ITURAN_USER'))
        driver.find_element(By.ID, "txtPassword").send_keys(os.getenv('ITURAN_PASS'))
        driver.find_element(By.ID, "btnLogin").click()

        # פתרון העיוורון: מעבר לדוח והפעלתו
        print("🕵️ מנווט לדוח המלא...")
        driver.get("https://www.ituran.com/iweb2/PeleReports/Pelereports.aspx")
        
        # שלב קריטי: לחיצה על "הצג דוח" או בחירת הדוח הראשון ברשימה
        time.sleep(10)
        try:
            # מחפש את הכפתור שמייצר את הטבלה שראית בתמונה
            show_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'], #btnShow, .btn-primary")))
            show_btn.click()
            print("👆 לחיצה על הפקת דוח בוצעה.")
        except:
            print("⚠️ לא נמצא כפתור לחיצה, מנסה לשלוף מהזיכרון...")

        # שלב החילוץ מה-Network
        time.sleep(15)
        logs = driver.get_log('performance')
        data_found = False

        for entry in logs:
            log = json.loads(entry['message'])['message']
            if 'Network.responseReceived' in log['method']:
                url = log['params']['response']['url']
                # מחפש את כתובת ה-API שמחזירה את הרכבים
                if "Get" in url or "Report" in url or "Json" in url:
                    try:
                        resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': log['params']['requestId']})
                        raw_data = json.loads(resp['body'])
                        
                        # כתיבה ל-JSON
                        with open('fleet_db.json', 'w', encoding='utf-8') as f:
                            json.dump(raw_data, f, indent=4, ensure_ascii=False)
                        
                        print(f"✅ העיוורון נפתר! נתונים נשמרו מכתובת: {url}")
                        data_found = True
                        break
                    except: continue

        if not data_found:
            print("❌ הבוט עדיין לא רואה. נדרש זיהוי ידני של כתובת ה-API.")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
