from playwright.sync_api import sync_playwright


def test_topup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. נווט לאתר
        page.goto("https://hahishook.com/")
        page.wait_for_selector("text=החישוק - מיזם חברתי כלכלי שמשנה את חוקי המשחק")
        assert page.locator("text=החישוק - מיזם חברתי כלכלי שמשנה את חוקי המשחק").is_visible()

        # לחץ על הקישור "החשבון שלי"
        page.click("li#menu-item-938 a")
        response = page.request.get("https://hahishook.com/my-account/")
        assert response.status == 200
        assert "החשבון שלי" in response.text()

        # לחץ על כפתור "התחברות עם סיסמה"
        page.click("//button[contains(text(),'התחברות עם סיסמה')]")
        page.wait_for_selector("//input[@id='username']")
        page.wait_for_selector("//input[@id='password']")

        # מלא את פרטי ההתחברות
        page.fill("//input[@id='username']","yanirqa10@gmail.com")
        page.fill("//input[@id='password']", "patel0025!")
        page.click("//button[contains(text(),'שלח שם וסיסמה')]")


        page.click("//a[contains(text(),'הארנק שלי')]")
        response = page.request.get("https://hahishook.com/my-account/woo-wallet/")
        assert response.status == 200
        assert "יתרה" in response.text()

        # לחיצה על טעינת כפתור סיבוס
        page.click("//p[contains(text(),'טעינה עם סיבוס')]")
        page.wait_for_selector("//input[@id='woo_wallet_balance_to_add']")
        page.fill("//input[@id='woo_wallet_balance_to_add']", "4")
        page.wait_for_selector("//input[@value='0']")
        # בחר שהחישוק ישלם (radio button עם value='0')
        page.check("//input[@value='0']")
        # לחץ על כפתור טעינה עם סיבוס (מעבר באותו הטאב)
        page.click("//button[contains(text(), 'טעינה עם סיבוס')]")
        # המתן שהכתובת תשתנה ותיטען לכתובת הסיבוס עם הטוקן
        page.wait_for_url("https://myconsumers.pluxee.co.il/**", wait_until="domcontentloaded")
        assert "myconsumers.pluxee.co.il" in page.url
        page.wait_for_selector("//h1[@id='hTitle']")
        assert page.locator("//h1[@id='hTitle']").is_visible()


        cibus_username_selector = "//input[@id='txtUserName']"
        page.fill(cibus_username_selector, "")  # מנקה את השדה
        page.fill(cibus_username_selector, "יניר פטל")
        cibuspassword_selector = "//input[@id='txtPassword']"
        page.fill(cibuspassword_selector, "")
        page.fill(cibuspassword_selector, "Patel0025!")
        cibus_company_selector = "//input[@id='txtCompany']"
        page.fill(cibus_company_selector, "מגער")
        page.click("//input[@id='btnSubmit']")
        page.wait_for_selector("text= יניר פטל")
        assert "יניר פטל" in page.content()

        # --- בדיקת יתרה יומית לפי ערך מדויק ₪100.0 ---
        try:
            #page.wait_for_selector("//big[contains(text(),'₪100.0')]", timeout=5000)
            balance_text = page.inner_text("//big[contains(text(),'₪100.0')]")
            print("balance_text:", balance_text)

            balance_value = float(balance_text.replace("₪", "").strip())
            print("יתרה מזוהה:", balance_value, "₪")

            if balance_value == 100.0:
                print("✅ יתרה היא 100 ש״ח — מבצע טעינת כרטיס...")
                page.click("//input[@id='btnPay']")
                page.wait_for_timeout(2000)
            elif balance_value < 100.0:
                print("❌ יתרה קטנה מ-100 ש״ח — לא מבצע טעינה לסיבוס, סוגר דפדפן.")
                assert False, "הטענת הכרטיס לא בוצעה כי היתרה קטנה מ-100 ש״ח"
            else:
                print(f"⚠️ יתרה לא צפויה: {balance_value} ש״ח")
                assert False, f"הטענת הכרטיס נכשלה עם יתרה לא צפויה: {balance_value}"

        except Exception as e:
            print("⚠️ לא הצלחנו לזהות את היתרה היומית:", e)
            assert False, f"שגיאה בזיהוי יתרה: {e}"
