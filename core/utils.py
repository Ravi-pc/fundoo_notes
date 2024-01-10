import smtplib
import ssl
from datetime import datetime, timedelta
import jwt
from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from email.message import EmailMessage
from .settings import settings
from .model import User, get_db

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = "HS256"
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY


def create_access_token(data: dict):
    expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(data, JWT_SECRET_KEY, algorithm=ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt


def decode_token(token):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        raise e


def authorization(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get('authorization')
    token_decode = decode_token(token)
    user_id = token_decode.get('user_id')
    user = db.query(User).filter_by(id=user_id).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized User')
    request.state.user = user


def email_verification(token: str, user_email):
    sender = settings.Sender
    password = settings.Password
    subject = 'Email Verification'
    body = f"Click the link to verify your email: http://127.0.0.1:8080/user/verify?token={token}"
    e_mail = EmailMessage()
    e_mail['From'] = sender
    e_mail['To'] = user_email
    e_mail['Subject'] = subject
    e_mail.set_content(body)
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, user_email, e_mail.as_string())
            print("Successfully")
            smtp.quit()

    except Exception as ex:
        print(ex)
