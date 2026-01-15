import os
import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from dotenv import load_dotenv

load_dotenv()

class IturanSniffer:
    def __init__(self):
        self.db_file = 'fleet_db.json'
        self.user = os.getenv('ITURAN_USER')
        self.password = os.getenv('ITURAN_PASS')
        self.driver = self._setup_driver()

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # הפעלת האזנה לתעבורת רשת (Performance Logging)
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        return webdriver.Chrome(options=chrome_options, desired_capabilities=caps)

    def extract_data_from_network(self):
        """דג נתונים אמיתיים מתוך תעבורת ה-XHR/Fetch"""
        print("🔍 סורק תעבורת רשת לאיתור JSON של הצי...")
        logs = self.driver.get_log('performance')
        
        for entry in logs:
            log = json.loads(entry['message'])['message']
            if 'Network.responseReceived' in log['method']:
                url = log['params']['response']['url']
                # איתור קריאות API של דוחות או רכבים (מבוסס על ה-URL שראינו)
                if any(k in url.lower() for k in ['report', 'units', 'positions', 'getdata']):
                    try:
                        req_id = log['params']['requestId']
                        body_data = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': req_id})
                        return json.loads(body_data['body'])
                    except: continue
        return None

    def update_fleet_db(self, raw_data):
        """מעבד את ה-JSON הגולמי ושומר ל-fleet_db.json"""
        if not raw_data: return
        
        fleet = {"vehicles": {}, "last_sync": datetime.datetime.now().isoformat()}
        # חילוץ הרשימה (מותאם למבנה איתורן: מחפש ב-d או ב-rows)
        units = raw_data if isinstance(raw_data, list) else raw_data.get('d', {}).get('rows', [])
        
        for u in units:
            v_id = str(u.get('UnitID') or u.get('UnitName') or u.get('TagID') or "unknown")
            status_text = str(u.get('Status') or u.get('PtoStatus') or "").lower()
            
            # זיהוי סטטוס עבודה (פתיחת PTO)
            is_open = any(word in status_text for word in ["פתוח", "עבודה", "פעיל", "working"])
            status = "OPEN" if is_open else "CLOSED"
            
            fleet["vehicles"][v_id] = {
                "status": status,
                "location": u.get('Address') or u.get('Location'),
                "last_seen": datetime.datetime.now().isoformat(),
                "raw_debug": str(u)[:50] # מידע למלשינון
            }

        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(fleet, f, indent=4, ensure_ascii=False)
        print(f"💾 הנתונים נשמרו: {len(fleet['vehicles'])} רכבים עודכנו.")

    def run(self):
        try:
            print("🚀 מתחבר למערכת...")
            self.driver.get("https://www.ituran.com/iweb2/login.aspx")
            
            # לוגין (כבר הוכח כעובד ב-Workflow)
            self.driver.find_element(By.ID, "txtUserName").send_keys(self.user)
            self.driver.find_element(By.ID, "txtPassword").send_keys(self.password)
            self.driver.find_element(By.ID, "btnLogin").click()
            
            # ניווט ישיר לדוח שבו מופיעים הנתונים
            print("📅 עובר לדף הדוח המלא...")
            time.sleep(10)
            self.driver.get("https://www.ituran.com/iweb2/PeleReports/Pelereports.aspx")
            
            # האזנה לרשת למשך 60 שניות (בדיקה כל 5 שניות)
            data = None
            for _ in range(12):
                data = self.extract_data_from_network()
                if data: 
                    print("✅ נתוני API זוהו בהצלחה!")
                    break
                time.sleep(5)

            if data:
                self.update_fleet_db(data)
            else:
                print("❌ כשל: לא נמצאו נתוני API ב-Network Logs.")

        except Exception as e:
            print(f"⚠️ שגיאה: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    IturanSniffer().run()
