import os
from playwright.sync_api import sync_playwright
from utils.email_utils import get_cibus_otp_from_email


def test_topup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # --- טען משתנים רגישים מהסביבה ---
        hahishook_username = os.getenv("HAHISHOOK_USERNAME")
        hahishook_password = os.getenv("HAHISHOOK_PASSWORD")
        cibus_username = os.getenv("CIBUS_USERNAME")
        cibus_password = os.getenv("CIBUS_PASSWORD")
        cibus_company = os.getenv("CIBUS_COMPANY")
        EMAIL = os.getenv("EMAIL_ADDRESS")
        PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
        IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
        IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", 993))
        SENDER_DOMAIN = os.getenv("CIBUS_SENDER_DOMAIN", "notifications.pluxee.co.il")
        SUBJECT_FILTER = os.getenv("CIBUS_SUBJECT_FILTER", "קוד האימות שלך בסיבוס")

        # --- גש לאתר הראשי ---
        page.goto("https://hahishook.com/")
        page.wait_for_selector("text=החישוק - מיזם חברתי כלכלי שמשנה את חוקי המשחק")
        assert page.locator("text=החישוק - מיזם חברתי כלכלי שמשנה את חוקי המשחק").is_visible()

        # --- התחברות לחשבון החישוק ---
        page.click("li#menu-item-938 a")
        response = page.request.get("https://hahishook.com/my-account/")
        assert response.status == 200
        assert "החשבון שלי" in response.text()

        page.click("//button[contains(text(),'התחברות עם סיסמה')]")
        page.wait_for_selector("//input[@id='username']")
        page.wait_for_selector("//input[@id='password']")

        page.fill("//input[@id='username']", hahishook_username)
        page.fill("//input[@id='password']", hahishook_password)
        page.click("//button[contains(text(),'שלח שם וסיסמה')]")

        # --- גישה לארנק ---
        page.click("//a[contains(text(),'הארנק שלי')]")
        response = page.request.get("https://hahishook.com/my-account/woo-wallet/")
        assert response.status == 200
        assert "יתרה" in response.text()

        # --- טעינה עם סיבוס ---
        page.click("//p[contains(text(),'טעינה עם סיבוס')]")
        page.wait_for_selector("//input[@id='woo_wallet_balance_to_add']")
        page.fill("//input[@id='woo_wallet_balance_to_add']", "4")
        page.wait_for_selector("//input[@value='0']")
        page.check("//input[@value='0']")
        page.click("//button[contains(text(), 'טעינה עם סיבוס')]")
        page.wait_for_url("https://myconsumers.pluxee.co.il/**", wait_until="domcontentloaded")
        assert "myconsumers.pluxee.co.il" in page.url
        page.wait_for_selector("//h1[@id='hTitle']")
        assert page.locator("//h1[@id='hTitle']").is_visible()

        # --- התחברות לסיבוס ---
        page.fill("//input[@id='txtUserName']", "")
        page.fill("//input[@id='txtUserName']", cibus_username)
        page.fill("//input[@id='txtPassword']", "")
        page.fill("//input[@id='txtPassword']", cibus_password)
        page.fill("//input[@id='txtCompany']", cibus_company)
        page.click("//input[@id='btnSubmit']")

        # --- המתן ל־OTP, שלוף מהמייל והזן ---
        page.wait_for_selector("input[type='tel']", timeout=15000)
        otp = get_cibus_otp_from_email(
            email_address=EMAIL,
            app_password=PASSWORD,
            imap_server=IMAP_SERVER,
            imap_port=IMAP_PORT,
            sender_domain=SENDER_DOMAIN,
            subject_filter=SUBJECT_FILTER
        )
        print("📨 OTP שהתקבל מהמייל:", otp)
        page.fill("input[type='tel']", otp)
        page.click("text=שימוש בקוד")  # ודא שהטקסט תואם לכפתור בפועל

        # --- בדיקת יתרה וטעינה ---
        try:
            page.wait_for_selector("//big[contains(text(),'₪100.0')]", timeout=5000)
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
            print("⚠️ היתרה קטנה מ 100 שקל , בוצע טעינה או שימוש היום:", e)
            assert False, f"היתרה קטנה מ 100 שקל , בוצע טעינה או שימוש היום: {e}"
