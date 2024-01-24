import smtplib
import ssl
from datetime import datetime, timedelta
import jwt
from fastapi import Request, Depends, HTTPException
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy.orm import Session
from email.message import EmailMessage
from core.settings import settings
from core.model import User, get_db, RequestLog
import redis
import logging

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
redis_obj = redis.Redis(host='localhost', port=6379, decode_responses=True)

logging.basicConfig(filename='./fundoo_notes.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%y %I:%M:%S %p')
logger = logging.getLogger()


def hash_password(password: str):
    return pbkdf2_sha256.hash(password)


def verify_password(hashed_password: str, raw_password: str):
    return pbkdf2_sha256.verify(raw_password, hashed_password)


def create_access_token(data: dict):
    """
        Description: create_access_token function to create the token.

        Parameter: data in the dictionary format.

        Return: token.

    """
    expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(data, JWT_SECRET_KEY, algorithm=ALGORITHM)
    # print(encoded_jwt)
    return encoded_jwt


def decode_token(token):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        logger.exception(e)


def authorization(request: Request, db: Session = Depends(get_db)):
    """
        Description: authorization function is used to determine whether the
                        user is verified or not.

        Parameter: Request, Session.

        Return: None.

    """

    token = request.headers.get('authorization')
    token_decode = decode_token(token)
    user_id = token_decode.get('user_id')
    user = db.query(User).filter_by(id=user_id).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized User')
    request.state.user = user


def email_verification(token: str, user_email):
    """
        Description: email_verification function is used to send the verification link
                        to the registered user e-mail id.

        Parameter: token, user_email.

        Return: None.

    """

    sender = settings.Sender
    password = settings.Password
    subject = 'Email Verification'
    body = f"Click the link to verify your email: http://127.0.0.1:8080/user/verify_user?token={token}"
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
        logger.exception(ex)


class Redis:

    @staticmethod
    def add_redis(name, key, value):
        return redis_obj.hset(name, key, value)

    @staticmethod
    def get_redis(name):
        return redis_obj.hgetall(name)

    @staticmethod
    def del_redis(name, key):
        return redis_obj.hdel(name, key)


def request_logger(request):
    """
        Description: request_logger function is used to update the middleware table
                     in the database.

        Parameter: request.

        Return: None.

    """

    session = get_db()
    db = next(session)
    log = db.query(RequestLog).filter_by(request_method=request.method,
                                         request_path=request.url.path).one_or_none()
    if not log:
        log = RequestLog(request_method=request.method, request_path=request.url.path, count=1)
        db.add(log)
    else:
        log.count += 1
    db.commit()
