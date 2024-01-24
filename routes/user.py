from sqlalchemy.exc import IntegrityError
import warnings
from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from core.model import get_db, User
from core.schema import UserDetails, UserLogin
from core.utils import email_verification, create_access_token, decode_token, hash_password, verify_password, logger

warnings.filterwarnings("ignore")

router = APIRouter()


@router.post('/post', status_code=status.HTTP_201_CREATED, tags=['User'])
def add_user(user: UserDetails, response: Response, db: Session = Depends(get_db)):
    """
        Description: add_user function is used to add a user to the database.

        Parameter: User details, response, get_db.

        Return: response and status code.

    """
    try:
        user_data = user.model_dump()
        user_data['password'] = hash_password(user_data['password'])
        user = User(**user_data)
        db.add(user)
        db.commit()
        token = create_access_token({'user_id': user.id})
        email_verification(token, user.email)
        db.refresh(user)
        return {'status': 201, 'message': 'User Added'}
    except IntegrityError as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': 'Username or email already exists', 'status': 400}
    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        logger.exception(ex)
        return {'message': str(ex), 'status': 400}


@router.post('/login', status_code=status.HTTP_200_OK, tags=['User'])
def user_login(user_schema: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
        Description: user_login function is used to validate a user login by it user_name and password.

        Parameter: User Schema, response, get_db.

        Return: response and status code.

    """
    try:
        valid_user = db.query(User).filter_by(user_name=user_schema.user_name).one_or_none()
        if valid_user.is_verified is True:
            if not valid_user or not verify_password(valid_user.password, user_schema.password):
                raise HTTPException(detail="Invalid Credentials", status_code=401)
            token = create_access_token({'user_id': valid_user.id})
            return {'message': 'Login Successful', 'status': 200, 'token': token}
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'message': 'User Not Verified', 'status': 401, 'data': {}}

    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        logger.exception(ex)
        return {'message': str(ex), 'status': 400}


@router.get('/verify_user', status_code=status.HTTP_200_OK)
def verify_user(token: str, db: Session = Depends(get_db)):
    """
        Description: verify_user function is to validate the user.

        Parameter: token, get_db as a Session object.

        Return: response and status code.

    """
    decode = decode_token(token)
    user_id = decode.get('user_id')
    user = db.query(User).filter_by(id=user_id).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized User')
    user.is_verified = True
    db.commit()
    return {'status': 200, 'message': 'User Verified Successfully'}
