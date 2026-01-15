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

class IturanSniffer:
    def __init__(self):
        self.db_file = 'fleet_db.json'
        self.driver = self._setup_driver()

    def _setup_driver(self):
        """הגדרת דפדפן עם יכולת האזנה לרשת"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # הפעלת Performance Logging לקריאת ה-Network Logs
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        return webdriver.Chrome(options=chrome_options, desired_capabilities=caps)

    def extract_from_network(self):
        """חילוץ JSON של רכבים מתוך תעבורת הרשת"""
        print("🔍 סורק תעבורת רשת לאיתור JSON של הצי...")
        logs = self.driver.get_log('performance')
        
        for entry in logs:
            log = json.loads(entry['message'])['message']
            if 'Network.responseReceived' in log['method']:
                url = log['params']['response']['url']
                # איתור קריאות API רלוונטיות לדוחות
                if any(k in url.lower() for k in ['report', 'units', 'positions', 'getdata']):
                    try:
                        req_id = log['params']['requestId']
                        body_data = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': req_id})
                        raw_json = json.loads(body_data['body'])
                        print(f"✅ נתונים זוהו בכתובת: {url}")
                        return raw_json
                    except:
                        continue
        return None

    def update_db(self, raw_data):
        """עיבוד הנתונים והזרמתם ל-fleet_db.json"""
        if not raw_data: return
        
        # נירמול הנתונים - מותאם למבנה שראינו בדוח המלא
        fleet = {"vehicles": {}, "last_sync": datetime.datetime.now().isoformat()}
        
        # חילוץ רשימת הרכבים (משתנה לפי סוג ה-API)
        units = raw_data if isinstance(raw_data, list) else raw_data.get('d', {}).get('rows', [])
        
        for u in units:
            # מזהה רכב לפי השדות שראינו בדוח (תג זיהוי/שם נהג)
            v_id = str(u.get('UnitID') or u.get('UnitName') or u.get('TagID') or "unknown")
            
            # זיהוי סטטוס עבודה (PTO)
            status_text = str(u.get('Status') or u.get('PtoStatus') or "").lower()
            status = "OPEN" if any(word in status_text for word in ["פתוח", "עבודה", "פעיל"]) else "CLOSED"
            
            fleet["vehicles"][v_id] = {
                "status": status,
                "location": u.get('Address') or u.get('Location'),
                "last_seen": datetime.datetime.now().isoformat()
            }

        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(fleet, f, indent=4, ensure_ascii=False)
        print(f"💾 הנתונים נשמרו: {len(fleet['vehicles'])} רכבים עודכנו.")

    def run(self):
        try:
            print("🚀 מתחבר למערכת הדוחות...")
            self.driver.get("https://www.ituran.com/iweb2/login.aspx")
            
            # לוגין (עובד תקין)
            self.driver.find_element(By.ID, "txtUserName").send_keys(os.getenv('ITURAN_USER'))
            self.driver.find_element(By.ID, "txtPassword").send_keys(os.getenv('ITURAN_PASS'))
            self.driver.find_element(By.ID, "btnLogin").click()
            
            # ניווט ישיר לדוח המלא שצילמת
            time.sleep(10)
            self.driver.get("https://www.ituran.com/iweb2/PeleReports/Pelereports.aspx")
            
            # המתנה חכמה לנתוני רשת
            data = None
            for _ in range(10):
                data = self.extract_from_network()
                if data: break
                time.sleep(5)

            if data:
                self.update_db(data)
            else:
                print("❌ כשל: לא זוהתה קריאת API עם נתוני רכבים.")

        except Exception as e:
            print(f"⚠️ שגיאה: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    IturanSniffer().run()
