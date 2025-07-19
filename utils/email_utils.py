import imaplib
import email
import re
import time
import os

def get_cibus_otp_from_email(
    email_address=os.getenv("EMAIL_ADDRESS"),
    app_password=os.getenv("EMAIL_APP_PASSWORD"),
    imap_server=os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com"),
    imap_port=int(os.getenv("EMAIL_IMAP_PORT", 993)),
    sender_domain="notifications.pluxee.co.il",
    subject_filter="קוד האימות שלך בסיבוס",
    timeout=60
):
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    mail.login(email_address, app_password)
    mail.select("inbox")

    start_time = time.time()

    while time.time() - start_time < timeout:
        result, data = mail.search(None, 'UNSEEN')
        if result != "OK":
            time.sleep(5)
            continue

        ids = data[0].split()
        for email_id in reversed(ids):
            result, msg_data = mail.fetch(email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            from_header = msg.get("From", "")
            subject = msg.get("Subject", "")

            if sender_domain in from_header and subject_filter in subject:
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                match = re.search(r"\b\d{6}\b", body)
                if match:
                    return match.group(0)

        time.sleep(5)

    raise TimeoutError("לא נמצא קוד אימות תוך 60 שניות.")
