import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

USER = os.getenv("ITURAN_USER")
PASS = os.getenv("ITURAN_PASS")

DOWNLOAD_DIR = "/home/runner/work/ituran/ituran"

def run():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 40)

    try:
        print("🔐 מתחבר...")
        driver.get("https://www.ituran.com/iweb2/login.aspx")

        wait.until(EC.presence_of_element_located((By.ID,"txtUserName"))).send_keys(USER)
        driver.find_element(By.ID,"txtPassword").send_keys(PASS)
        driver.find_element(By.ID,"btnLogin").click()

        print("✅ לוגין הצליח")

        # מעבר לדוחות
        driver.get("https://www.ituran.com/iweb2/reports.aspx")

        print("📊 פותח דוח רכבים")

        # דוגמה – כפתור ייצוא
        export_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH,"//button[contains(.,'Export')]"))
        )
        export_btn.click()

        print("⬇️ ממתין להורדה...")
        time.sleep(15)

        parse_csv()

    finally:
        driver.quit()

def parse_csv():
    print("📂 קורא CSV...")

    file = "vehicles.csv"

    with open(file, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(row)

if __name__ == "__main__":
    run()
