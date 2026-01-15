import os
import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# טעינת משתני סביבה (תמיכה ב-.env וב-GitHub Secrets)
from dotenv import load_dotenv
load_dotenv()

class IturanAutomation:
    def __init__(self):
        self.user = os.getenv('ITURAN_USER')
        self.password = os.getenv('ITURAN_PASS')
        self.db_file = 'fleet_db.json'
        self.driver = self._setup_driver()

    def _setup_driver(self):
        """הגדרת דפדפן עם Performance Logging"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # הגדרה שמאפשרת לסלניום לקרוא את ה-Network Logs
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)
        return driver

    def get_network_data(self):
        """פונקציה לקריאת Network logs וזיהוי JSON של רכבים"""
        print("🔍 סורק תעבורת רשת (Network Analysis)...")
        logs = self.driver.get_log('performance')
        
        for entry in logs:
            log = json.loads(entry['message'])['message']
            if 'Network.responseReceived' in log['method']:
                url = log['params']['response']['url']
                # זיהוי קריאות רלוונטיות לפי מילות מפתח ב-URL
                if any(k in url.lower() for k in ['vehicles', 'units', 'positions', 'fleet', 'getdata']):
                    try:
                        request_id = log['params']['requestId']
                        # שליפת גוף התגובה (Response Body)
                        body = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                        data = json.loads(body['body'])
                        print(f"✅ נמצא מקור נתונים ב-URL: {url}")
                        return data
                    except:
                        continue
        return None

    def get_js_memory_data(self):
        """פונקציה לשליפת משתני JS מתוך הזיכרון (window context)"""
        print("🧠 בודק משתנים גלובליים בזיכרון (JS Context)...")
        scripts = [
            "return window.vehicles;",
            "return window.units;",
            "return window.mapData;",
            "return typeof ituranApp !== 'undefined' ? ituranApp.getFleet() : null;"
        ]
        for script in scripts:
            try:
                result = self.driver.execute_script(script)
                if result:
                    print(f"✅ נתונים נשלפו מזיכרון ה-JS באמצעות: {script}")
                    return result
            except:
                continue
        return None

    def update_db(self, raw_data):
        """עיבוד הנתונים ושמירה ל-JSON מסודר"""
        if not raw_data: return
        
        # כאן מתבצע הניקוי (Parsing) - מותאם למבנה ה-JSON של איתורן
        current_data = {}
        # הערה: המבנה כאן גנרי ויותאם ל-JSON הספציפי שיימצא ב-Network
        vehicles_list = raw_data if isinstance(raw_data, list) else raw_data.get('vehicles', [])
        
        for v in vehicles_list:
            v_id = v.get('id') or v.get('UnitID') or v.get('Name')
            if not v_id: continue
            
            # זיהוי סטטוס (מבוסס על שדות נפוצים ב-API)
            is_active = v.get('is_active') or v.get('pto') or False
            status = "OPEN" if is_active else "CLOSED"
            
            current_data[str(v_id)] = {
                "status": status,
                "lat": v.get('lat'),
                "lng": v.get('lng'),
                "last_seen": datetime.datetime.now().isoformat(),
                "raw_info": str(v)[:100]
            }

        # שמירה לקובץ (מבוסס על הלוגיקה הקיימת שלך)
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump({"vehicles": current_data}, f, indent=4, ensure_ascii=False)
        print(f"💾 בסיס הנתונים עודכן עם {len(current_data)} רכבים.")

    def run(self):
        try:
            print("🚀 מתחבר למערכת...")
            self.driver.get("https://www.ituran.com/iweb2/login.aspx")
            
            # לוגין (כבר הוכח כעובד)
            self.driver.find_element(By.ID, "txtUserName").send_keys(self.user)
            self.driver.find_element(By.ID, "txtPassword").send_keys(self.password)
            self.driver.find_element(By.ID, "btnLogin").click()

            # המתנה חכמה: לופ בדיקה עד שהנתונים מופיעים באחד המקורות
            start_time = time.time()
            data = None
            while time.time() - start_time < 90: # Timeout של 90 שניות
                data = self.get_network_data() or self.get_js_memory_data()
                if data: break
                time.sleep(5) # בדיקה כל 5 שניות במקום המתנה עיוורת

            if data:
                self.update_db(data)
            else:
                print("❌ כשל: לא נמצאו נתוני רשת או זיכרון בפרק הזמן שהוקצב.")

        except Exception as e:
            print(f"⚠️ שגיאה קריטית: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    bot = IturanAutomation()
    bot.run()
