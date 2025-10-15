from fastapi_mail import FastMail, MessageSchema
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
from pytz import utc


conf = ConnectionConfig(
    MAIL_USERNAME="ali.ghannadi218@gmail.com",
    MAIL_PASSWORD="ftwtacoeaygwwwav",
    MAIL_FROM="ali.ghannadi218@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True

)

async def send_verification_email(email: str, subject: str, message: str):
    if not email or not isinstance(email, str):
        raise ValueError('Invalid email')
    fm = FastMail(conf)
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=message,
        subtype='plain'         
    )        
    await fm.send_message(message)
    return {"message": "Email has been sent"}


emailstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///emails.db')
}

scheduler = BackgroundScheduler(jobstores=emailstores)
scheduler.start()

def send_email_job(email: str, subject: str, message: str):
     import asyncio
     asyncio.run(send_verification_email(email, subject, message))

def schedule_email(email: str, subject: str, message: str, scheduled_time: datetime):
    if scheduled_time.tzinfo is None:
        scheduled_time = scheduled_time.replace(tzinfo=utc)
    else:
        scheduled_time = scheduled_time.astimezone(utc)
    scheduler.add_job(
        func=send_email_job,
        trigger='date',
        run_date=scheduled_time,
        id=f"email_{email}_{scheduled_time.timestamp()}",
        args=[email, subject, message]
    )