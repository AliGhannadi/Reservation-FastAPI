from datetime import datetime, timedelta
import smtplib
import ssl
from email.message import EmailMessage

# In-memory store for verification codes: { email: (code, expires_at) }
verification_codes = {}

async def send_verification_email(email: str, code: str):
    if not email or not isinstance(email, str):
        raise ValueError('Invalid email')
    subject = "Your verification code"
    body = f"Your email verification code is: {code}"

    msg = EmailMessage()
    msg["From"] = "ali.ghannadi218@gmail.com"
    msg["To"] = email
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login("ali.ghannadi218@gmail.com", "ftwtacoeaygwwwav")
        server.send_message(msg)
    return {"message": "Email has been sent"}

def store_verification_code(email: str, code: str, ttl_minutes: int = 10) -> bool:
    if not email or not code:
        return False
    expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
    verification_codes[email] = (code, expires_at)
    return True

def verify_verification_code(email: str, code: str) -> bool:
    stored = verification_codes.get(email)
    if not stored:
        return False
    stored_code, expires_at = stored
    if datetime.now() > expires_at:
        # Expired; clean up
        verification_codes.pop(email, None)
        return False
    if stored_code != code:
        return False
    # Success; consume the code
    verification_codes.pop(email, None)
    return True