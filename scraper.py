# שלב 1: גישה לכתובת המעודכנת
        driver.get("https://www.ituran.com/iweb2/iweb2p.aspx")
        
        wait = WebDriverWait(driver, 30)
        
        # שלב 2: איתור שדות הכניסה לפי המבנה של איתורן
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txtUserName")))
        pass_input = driver.find_element(By.ID, "txtPassword")
        
        # הזנת פרטים מה-Secrets
        user_input.send_keys(os.environ.get('USER') or os.environ.get('ITURAN_USER'))
        pass_input.send_keys(os.environ.get('PASS') or os.environ.get('ITURAN_PASS'))
        
        # לחיצה על כפתור הכניסה
        login_btn = driver.find_element(By.ID, "btnLogin")
        login_btn.click()
