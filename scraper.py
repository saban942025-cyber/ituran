import os
import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

class IturanUltimateSniffer:
    def __init__(self):
        self.db_file = 'fleet_db.json'
        self.driver = self._setup_driver()

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        return webdriver.Chrome(options=chrome_options, desired_capabilities=caps)

    def extract_from_network(self):
        logs = self.driver.get_log('performance')
        for entry in logs:
            log = json.loads(entry['message'])['message']
            if 'Network.responseReceived' in log['method']:
                url = log['params']['response']['url']
                # חיפוש קריאות ה-XHR שיוצרות את הטבלה שראינו
                if any(k in url.lower() for k in ['report', 'grid', 'getdata', 'units']):
                    try:
                        req_id = log['params']['requestId']
                        body = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': req_id})
                        return json.loads(body['body'])
                    except: continue
        return None

    def run(self):
        try:
            print("🚀 מתחבר ומתחבר למערכת...")
            self.driver.get("https://www.ituran.com/iweb2/login.aspx")
            
            # לוגין (עובד)
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.ID, "txtUserName"))).send_keys(os.getenv('ITURAN_USER'))
            self.driver.find_element(By.ID, "txtPassword").send_keys(os.getenv('ITURAN_PASS'))
            self.driver.find_element(By.ID, "btnLogin").click()
            
            # מעבר לדוח הספציפי
            print("📅 ניווט לדף הדוחות...")
            time.sleep(5)
            self.driver.get("https://www.ituran.com/iweb2/PeleReports/Pelereports.aspx")
            
            # חיזוק: לחיצה על כפתור "הצג" או "רענן" כדי להפעיל את הרשת
            try:
                print("🖱️ מפעיל את הדוח (לחיצה על כפתור תצוגה)...")
                view_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value*='הצג'], .btn-view, #btnShow")))
                view_button.click()
            except:
                print("⚠️ לא נמצא כפתור לחיצה, ממשיך בהאזנה פסיבית...")

            # האזנה לרשת
            data = None
            for _ in range(15):
                data = self.extract_from_network()
                if data: 
                    print("✅ נתונים נתפסו ברשת!")
                    break
                time.sleep(4)

            if data:
                # שימוש בפונקציית העדכון הקיימת שלך
                self.process_and_save(data)
            else:
                print("❌ עדיין אין נתונים. הבוט לא 'שומע' את ה-API.")

        except Exception as e:
            print(f"⚠️ תקלה: {str(e)}")
        finally:
            self.driver.quit()

    def process_and_save(self, data):
        # לוגיקת העיבוד שלך ל-fleet_db.json
        print(f"DEBUG: Processing {len(str(data))} bytes of data")
        # ... (כאן באה פונקציית העדכון שכתבנו)

if __name__ == "__main__":
    IturanUltimateSniffer().run()
