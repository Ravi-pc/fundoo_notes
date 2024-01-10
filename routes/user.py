from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from core.model import get_db, User, verify_password, hash_password
from core.schema import UserDetails, UserLogin


router = APIRouter()


@router.post('/post', status_code=status.HTTP_201_CREATED)
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
        db.refresh(user)
        return {'message': 'User Added', 'status': 201, 'data': user}
    except Exception as ex:
        response.status_code = 400
        return {'message': str(ex), 'status': 400}


@router.post('/login', status_code=status.HTTP_200_OK)
def user_login(user_schema: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
        Description: user_login function is used to validate a user login by it user_name and password.

        Parameter: User Schema, response, get_db.

        Return: response and status code.

    """
    try:
        valid_user = db.query(User).filter_by(user_name=user_schema.user_name).one_or_none()

        if not valid_user:
            raise HTTPException(detail='User Not Found', status_code=401)
        if not verify_password(valid_user.password, user_schema.password):
            raise HTTPException(detail="Invalid Credentials", status_code=401)

        return {'message': 'Login Successful', 'status': 200}

    except Exception as ex:
        response.status_code = 400
        return {'message': str(ex), 'status': 400}
